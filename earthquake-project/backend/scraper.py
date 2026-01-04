import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.ensemble import IsolationForest

def get_cleaned_data():
    url = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_text = soup.find('pre').text
    lines = raw_text.split('\n')
    
    clean_data = []
    # Data starts after the dashed line (usually index 50+)
    start_parsing = False
    for line in lines:
        if '--------------' in line:
            start_parsing = True
            continue
        if start_parsing and len(line) > 70:
            try:
                # Fixed-width slicing (Standard for Kandilli format)
                row = {
                    "date": line[0:10].strip().replace('.', '-'),
                    "time": line[11:19].strip(),
                    "lat": float(line[21:28].strip()),
                    "lon": float(line[31:38].strip()),
                    "depth": float(line[43:49].strip()),
                    "mag": float(line[60:63].strip()) if line[60:63].strip() != '-.-' else 0.0,
                    "location": line[71:121].strip()
                }
                clean_data.append(row)
            except ValueError:
                continue
                
    df = pd.DataFrame(clean_data)
    
    # --- DATA SCIENCE: ANOMALY DETECTION ---
    # Detects unusual earthquakes based on Magnitude and Depth
    if not df.empty:
        model = IsolationForest(contamination=0.05) 
        df['anomaly'] = model.fit_predict(df[['mag', 'depth']])
        # Convert -1 (anomaly) to True/False for JSON
        df['is_anomaly'] = df['anomaly'] == -1
        
    return df.to_dict(orient="records")