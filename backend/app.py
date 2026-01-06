"""
Main Flask Application for Earthquake Data Analysis.
Provides API endpoints for earthquake data, scraping, and predictions.
"""

import os
import json
import datetime
import queue

import pandas as pd
from flask import Flask, jsonify, Response, stream_with_context
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

from analysis import SeismologicalAnalyzer
from scraper import KandilliScraper

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earthquakes.db'
db = SQLAlchemy(app)

class Earthquake(db.Model):
    """Database model representing an earthquake event."""
    # pylint: disable=too-few-public-methods
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

_clients = []

def notify_clients(message: str):
    """Push message to all connected SSE clients."""
    for q in list(_clients):
        try:
            q.put(message)
        except Exception: # pylint: disable=broad-exception-caught
            pass

def _notify_clients_of_update(new_count):
    """Helper to send SSE update to clients."""
    try:
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        payload = json.dumps({"new_count": new_count, "timestamp": timestamp})
        notify_clients(payload)
    except Exception: # pylint: disable=broad-exception-caught
        pass

def scrape_kandilli():
    """
    Orchestrates the scraping process: fetching, parsing, and saving unique earthquakes.
    Returns: a pandas DataFrame of all earthquakes.
    """
    try:
        html_content = KandilliScraper.fetch_data()
        parsed_data = KandilliScraper.parse_data(html_content)

        new_count = 0

        for item in parsed_data:
            exists = db.session.query(Earthquake).filter_by(
                date=item['date'],
                time=item['time'],
                location=item['location']
            ).first()

            if exists:
                continue

            earthquake = Earthquake(
                date=item['date'],
                time=item['time'],
                lat=item['lat'],
                lng=item['lng'],
                depth=item['depth'],
                mag=item['mag'],
                location=item['location']
            )
            db.session.add(earthquake)
            new_count += 1

        db.session.commit()
        if new_count > 0:
            print(f"Scraping complete. Added {new_count} new earthquakes.")
            _notify_clients_of_update(new_count)

        earthquakes = Earthquake.query.all()
        processed_list = [{
            "date": eq.date, "time": eq.time, "lat": eq.lat, "lng": eq.lng,
            "depth": eq.depth, "mag": eq.mag, "location": eq.location,
            "is_anomaly": eq.is_anomaly
        } for eq in earthquakes]

        return pd.DataFrame(processed_list)

    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Scraping error: {e}")
        db.session.rollback()
        return pd.DataFrame()

def _scheduled_scrape():
    """Job to run scraping and print status."""
    try:
        with app.app_context():
            scrape_kandilli()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Scheduled scrape error: {e}")

def _check_remote_and_trigger():
    """Checks if remote content changed and triggers scrape."""
    if KandilliScraper.has_updates():
        print("Remote content changed; triggering scrape")
        with app.app_context():
            scrape_kandilli()

@app.route('/api/stream')
def stream():
    """SSE endpoint for real-time updates."""
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

scheduler = BackgroundScheduler()
scheduler.add_job(_scheduled_scrape, 'interval', seconds=30,
                  id='kandilli_scrape', replace_existing=True)
scheduler.add_job(_check_remote_and_trigger, 'interval', seconds=60,
                  id='kandilli_watch', replace_existing=True)

@app.route('/api/earthquakes', methods=['GET'])
def get_data():
    """API endpoint to get earthquake data."""
    count = Earthquake.query.count()
    if count == 0:
        scrape_kandilli()

    earthquakes = Earthquake.query.order_by(
        Earthquake.date.desc(),
        Earthquake.time.desc()
    ).all()

    df = pd.DataFrame([{
        "date": eq.date, "time": eq.time, "lat": eq.lat, "lng": eq.lng,
        "depth": eq.depth, "mag": eq.mag, "location": eq.location
    } for eq in earthquakes])

    if df.empty:
        return jsonify([])

    df = SeismologicalAnalyzer.detect_anomalies(df)

    for _, row in df.iterrows():
        eq = Earthquake.query.filter_by(
            date=row['date'], time=row['time'], location=row['location']
        ).first()
        if eq:
            eq.is_anomaly = row['is_anomaly']
    db.session.commit()

    return jsonify(df.to_dict(orient='records'))

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """API endpoint to get risk predictions."""
    if Earthquake.query.count() == 0:
        scrape_kandilli()

    earthquakes = Earthquake.query.all()
    df = pd.DataFrame([{
        "date": eq.date, "time": eq.time, "lat": eq.lat, "lng": eq.lng,
        "depth": eq.depth, "mag": eq.mag, "location": eq.location
    } for eq in earthquakes])

    if df.empty:
        return jsonify([])

    predictions = SeismologicalAnalyzer.predict_next_events(df)
    return jsonify(predictions)

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Endpoint to manually refresh earthquake data."""
    try:
        scrape_kandilli()
        count = Earthquake.query.count()
        return jsonify({
            "status": "success",
            "message": f"Loaded {count} earthquakes from Kandilli Observatory"
        })
    except Exception as e: # pylint: disable=broad-exception-caught
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()
        print('Background scheduler started.')

    app.run(debug=True, port=5000)
