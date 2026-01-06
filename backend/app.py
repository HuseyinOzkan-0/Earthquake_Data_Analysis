import requests
import io
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from analysis import detect_anomalies, predict_next_events
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os
import queue
import json
from flask import Response, stream_with_context
import hashlib
import threading

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earthquakes.db'
db = SQLAlchemy(app)

class Earthquake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(8), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    mag = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    is_anomaly = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Earthquake {self.location} - {self.mag}>"

def scrape_kandilli():
    url = "http://www.koeri.boun.edu.tr/scripts/lst2.asp"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        raw_data = soup.find("pre").text
        lines = raw_data.split('\n')
        
        new_count = 0
        
        for line in lines:
            # FIXED: Correct syntax for checking line length
            if len(line) > 100 and line[0].isdigit():
                try:
                    # Extract fields first
                    date_val = line[0:10].strip()
                    time_val = line[11:19].strip()
                    location_val = line[71:121].strip()
                    
                    # 1. CHECK FOR DUPLICATES
                    exists = db.session.query(Earthquake).filter_by(
                        date=date_val, 
                        time=time_val, 
                        location=location_val
                    ).first()

                    if exists:
                        continue  # Skip this one, we already have it

                    # 2. INSERT NEW DATA
                    mag_val = line[60:63].strip()
                    lat_val = line[21:28].strip()
                    lng_val = line[30:37].strip()
                    depth_val = line[43:49].strip()

                    earthquake = Earthquake(
                        date=date_val,
                        time=time_val,
                        lat=float(lat_val),
                        lng=float(lng_val),
                        depth=float(depth_val),
                        mag=float(mag_val),
                        location=location_val
                    )
                    db.session.add(earthquake)
                    new_count += 1
                except ValueError:
                    continue
        
        db.session.commit()
        print(f"Scraping complete. Added {new_count} new earthquakes.")

        # Notify connected SSE clients when new data was added
        if new_count > 0:
            try:
                payload = json.dumps({"new_count": new_count, "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'})
                notify_clients(payload)
            except Exception as _:
                pass
        
        # Return latest data for the dataframe
        earthquakes = Earthquake.query.all()
        processed_list = [{
            "date": eq.date, "time": eq.time, "lat": eq.lat, "lng": eq.lng, 
            "depth": eq.depth, "mag": eq.mag, "location": eq.location, "is_anomaly": eq.is_anomaly
        } for eq in earthquakes]
        
        # FIXED: Added space between return and pd
        return pd.DataFrame(processed_list)

    except Exception as e:
        print(f"Scraping error: {e}")
        db.session.rollback()
        return pd.DataFrame()


def _scheduled_scrape():
    try:
        with app.app_context():
            print(f"Scheduled scrape triggered at {datetime.datetime.utcnow().isoformat()}Z")
            scrape_kandilli()
    except Exception as e:
        print(f"Scheduled scrape error: {e}")


_watch_lock = threading.Lock()
LAST_HASH_PATH = os.path.join('instance', 'last_hash.txt')

def _read_last_hash():
    try:
        if os.path.exists(LAST_HASH_PATH):
            with open(LAST_HASH_PATH, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return None

def _write_last_hash(h):
    try:
        os.makedirs(os.path.dirname(LAST_HASH_PATH), exist_ok=True)
        with open(LAST_HASH_PATH, 'w') as f:
            f.write(h)
    except Exception:
        pass

def _check_remote_and_trigger():
    """Fetch the Kandilli page, compute hash of the <pre> content, and trigger scrape if changed."""
    url = "http://www.koeri.boun.edu.tr/scripts/lst2.asp"
    try:
        # prevent overlapping checks
        if not _watch_lock.acquire(blocking=False):
            return
        resp = requests.get(url, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        pre = soup.find('pre')
        if pre is None:
            return
        content = pre.text.strip()
        cur_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        last = _read_last_hash()
        if last != cur_hash:
            print(f"Remote content changed (last={last is not None}); triggering scrape")
            _write_last_hash(cur_hash)
            with app.app_context():
                try:
                    scrape_kandilli()
                except Exception as e:
                    print('Error scraping after remote change:', e)
    except Exception as e:
        print('Remote check error:', e)
    finally:
        try:
            _watch_lock.release()
        except Exception:
            pass



# Simple in-memory pub/sub for Server-Sent Events (SSE)
_clients = []

def notify_clients(message: str):
    # put message into each client's queue
    for q in list(_clients):
        try:
            q.put(message)
        except Exception:
            # ignore client queue errors; cleanup happens on disconnect
            pass


@app.route('/api/stream')
def stream():
    def event_stream():
        q = queue.Queue()
        _clients.append(q)
        try:
            while True:
                msg = q.get()
                yield f"data: {msg}\n\n"
        except GeneratorExit:
            try:
                _clients.remove(q)
            except ValueError:
                pass

    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')


# Setup background scheduler to run scraper every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(_scheduled_scrape, 'interval', minutes=5, id='kandilli_scrape', replace_existing=True)
scheduler.add_job(_check_remote_and_trigger, 'interval', seconds=60, id='kandilli_watch', replace_existing=True)

@app.route('/api/earthquakes', methods=['GET'])
def get_data():
    # If database is empty, scrape data first
    count = Earthquake.query.count()
    if count == 0:
        print("Database is empty, scraping new data...")
        scrape_kandilli()
        count = Earthquake.query.count()
        print(f"Scraped {count} earthquakes")
    
    # Fetch all earthquakes from database, sorted by date and time (newest first)
    earthquakes = Earthquake.query.order_by(
        Earthquake.date.desc(),
        Earthquake.time.desc()
    ).all()
    
    print(f"Returning {len(earthquakes)} earthquakes from database")
    
    df = pd.DataFrame([{
        "date": eq.date, "time": eq.time, "lat": eq.lat, "lng": eq.lng, 
        "depth": eq.depth, "mag": eq.mag, "location": eq.location
    } for eq in earthquakes])
    
    if df.empty:
        return jsonify([])
    
    # Apply anomaly detection
    df = detect_anomalies(df)
    
    # Update database with anomaly scores
    for idx, row in df.iterrows():
        eq = Earthquake.query.filter_by(
            date=row['date'], time=row['time'], location=row['location']
        ).first()
        if eq:
            eq.is_anomaly = row['is_anomaly']
    db.session.commit()
    
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    # If database is empty, scrape data first
    if Earthquake.query.count() == 0:
        scrape_kandilli()
    
    # Fetch all earthquakes from database
    earthquakes = Earthquake.query.all()
    df = pd.DataFrame([{
        "date": eq.date, "time": eq.time, "lat": eq.lat, "lng": eq.lng, 
        "depth": eq.depth, "mag": eq.mag, "location": eq.location
    } for eq in earthquakes])
    
    if df.empty:
        return jsonify([])
    
    predictions = predict_next_events(df)
    return jsonify(predictions)

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Endpoint to refresh earthquake data from Kandilli Observatory"""
    try:
        scrape_kandilli()
        count = Earthquake.query.count()
        return jsonify({"status": "success", "message": f"Loaded {count} earthquakes from Kandilli Observatory"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    # Start scheduler safely (avoid double-start with the reloader)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()
        print('Background scheduler started: scraping every 5 minutes')
    app.run(debug=True, port=5000)