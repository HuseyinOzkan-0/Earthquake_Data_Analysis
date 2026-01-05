import requests
import io
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from analysis import detect_anomalies, predict_next_events

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
    app.run(debug=True, port=5000)