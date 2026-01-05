import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
import io
from analysis import detect_anomalies, predict_next_events

app = Flask(__name__)
CORS(app)

def scrape_kandilli():
    url = "http://www.koeri.boun.edu.tr/scripts/lst2.asp"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        raw_data = soup.find("pre").text
        lines = raw_data.split('\n')
        
        processed_list = []
        for line in lines:
            # Data lines always start with a date like '2026.01.05'
            # We check if the first character is a digit to skip headers/empty lines
            if len(line) > 100 and line[0].isdigit():
                try:
                    # We use strip() and slice carefully
                    mag_val = line[60:63].strip()
                    lat_val = line[21:28].strip()
                    lng_val = line[30:37].strip()
                    depth_val = line[43:49].strip()

                    processed_list.append({
                        "date": line[0:10].strip(),
                        "time": line[11:19].strip(),
                        "lat": float(lat_val),
                        "lng": float(lng_val),
                        "depth": float(depth_val),
                        "mag": float(mag_val),
                        "location": line[71:121].strip()
                    })
                except ValueError:
                    # If a specific line is still messy, skip just that line
                    continue
                    
        return pd.DataFrame(processed_list)
    except Exception as e:
        print(f"Scraping error: {e}")
        return pd.DataFrame()

@app.route('/api/earthquakes', methods=['GET'])
def get_data():
    df = scrape_kandilli()
    df = detect_anomalies(df) # Add anomaly labels
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    df = scrape_kandilli()
    predictions = predict_next_events(df)
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True, port=5000)