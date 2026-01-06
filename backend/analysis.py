# backend/analysis.py
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

class SeismologicalAnalyzer:
    """
    Class responsible for analyzing earthquake data using ML techniques.
    Implements anomaly detection and risk prediction.
    """
    
    @staticmethod
    def detect_anomalies(df):
        """Identifies 'outlier' earthquakes using the Isolation Forest algorithm."""
        if df.empty:
            return df
        
        features = df[['lat', 'lng', 'depth', 'mag']]
        model = IsolationForest(contamination=0.05, random_state=42)
        
        df['anomaly_score'] = model.fit_predict(features)
        df['is_anomaly'] = df['anomaly_score'] == -1
        
        return df

    @staticmethod
    def predict_next_events(df):
        """Analyzes historical clusters to estimate potential future activity."""
        if df.empty:
            return []
        
        stats = df.groupby('location').agg({
            'mag': 'mean',
            'date': 'count'
        }).rename(columns={'date': 'frequency'}).reset_index()

        if stats.empty:
            return []
        
        stats['risk_score'] = (stats['mag'] / stats['mag'].max()) * (stats['frequency'] / stats['frequency'].max())
        
        sorted_stats = stats.sort_values(by='risk_score', ascending=False)
        predictions = sorted_stats.head(10)
        return predictions.to_dict(orient='records')