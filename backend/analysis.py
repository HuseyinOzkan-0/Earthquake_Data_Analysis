# backend/analysis.py
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

def detect_anomalies(df):
    """
    Identifies 'outlier' earthquakes using the Isolation Forest algorithm.
    """
    if df.empty:
        return df
    
    # Selecting numerical features for the model
    features = df[['lat', 'lng', 'depth', 'mag']]
    
    # contamination=0.05 means we expect 5% of data to be anomalies
    model = IsolationForest(contamination=0.05, random_state=42)
    
    # Predict: 1 = normal, -1 = anomaly
    df['anomaly_score'] = model.fit_predict(features)
    df['is_anomaly'] = df['anomaly_score'] == -1
    
    return df

def predict_next_events(df):
    """
    Analyzes historical clusters to estimate potential future activity.
    """
    # Grouping by location to see where activity is densest
    stats = df.groupby('location').agg({
        'mag': 'mean',
        'date': 'count'
    }).rename(columns={'date': 'frequency'}).reset_index()

    # Simple logic: High frequency + High average magnitude = Higher Risk
    stats['risk_score'] = (stats['mag'] / stats['mag'].max()) * (stats['frequency'] / stats['frequency'].max())
    
    # Return top 5 "high risk" areas
    predictions=  sorted_stats = stats.sort_values(by='risk_score', ascending=False)
    predictions = sorted_stats[sorted_stats['risk_score'] > 0.5]
    return predictions.to_dict(orient='records')