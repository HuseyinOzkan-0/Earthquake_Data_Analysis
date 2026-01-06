"""Generate reproducible figures and a small report from the cleaned earthquake DB.

Usage:
  .venv\Scripts\Activate.ps1
  pip install -r backend/requirements.txt
  python backend/generate_report.py

Outputs saved to `reports/`:
  - `fig_mag_hist.png`  : magnitude distribution with anomalies highlighted
  - `fig_map.png`       : lat/lon scatter with anomalies highlighted
  - `map.html`          : interactive folium map showing events
"""
import os
import sqlite3
import pandas as pd
import matplotlib
# Use non-interactive backend to avoid Tk dependencies when saving files
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import folium

from analysis import detect_anomalies

DB_PATH = os.path.join('instance', 'earthquakes.db')
OUT_DIR = os.path.join('..', 'reports') if os.path.isdir('..\reports') else 'reports'
os.makedirs(OUT_DIR, exist_ok=True)

def load_db(db_path=DB_PATH):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB not found: {db_path}")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT date, time, lat, lng, depth, mag, location FROM Earthquake', conn)
    conn.close()
    return df

def save_mag_hist(df, out_path):
    plt.figure(figsize=(8,5))
    sns.histplot(df['mag'].dropna(), bins=30, kde=False, color='C0', label='All events')
    if 'is_anomaly' in df.columns:
        sns.histplot(df[df['is_anomaly']==True]['mag'].dropna(), bins=30, color='C3', label='Anomalies')
    plt.xlabel('Magnitude')
    plt.ylabel('Count')
    plt.legend()
    plt.title('Magnitude distribution (anomalies highlighted)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def save_scatter_map(df, out_path):
    plt.figure(figsize=(8,6))
    normal = df[df['is_anomaly']!=True]
    anom = df[df['is_anomaly']==True]
    plt.scatter(normal['lng'], normal['lat'], s=10, alpha=0.6, label='normal', c='C0')
    if not anom.empty:
        plt.scatter(anom['lng'], anom['lat'], s=20, alpha=0.9, label='anomaly', c='red')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.title('Event locations (anomalies in red)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def save_folium_map(df, out_path):
    # Center map on median location
    lat0 = df['lat'].median()
    lng0 = df['lng'].median()
    m = folium.Map(location=[lat0, lng0], zoom_start=6)
    for _, r in df.iterrows():
        color = 'red' if r.get('is_anomaly') else 'blue'
        folium.CircleMarker(location=[r['lat'], r['lng']], radius=3, color=color,
                            fill=True, fill_opacity=0.7,
                            popup=f"{r.get('date')} {r.get('time')} {r.get('mag')} {r.get('location')}")
        # Add marker
        folium.CircleMarker(location=[r['lat'], r['lng']], radius=3, color=color,
                            fill=True, fill_opacity=0.7).add_to(m)
    m.save(out_path)

def main():
    print('Loading DB...')
    df = load_db()
    print('Running anomaly detection...')
    df = detect_anomalies(df)
    # Ensure boolean column
    if 'is_anomaly' not in df.columns:
        df['is_anomaly'] = False

    mag_out = os.path.join(OUT_DIR, 'fig_mag_hist.png')
    map_out = os.path.join(OUT_DIR, 'fig_map.png')
    folium_out = os.path.join(OUT_DIR, 'map.html')

    print('Saving magnitude histogram ->', mag_out)
    save_mag_hist(df, mag_out)
    print('Saving scatter map ->', map_out)
    save_scatter_map(df, map_out)
    print('Saving interactive folium map ->', folium_out)
    save_folium_map(df, folium_out)

    print('Report generation complete. Files in', OUT_DIR)

if __name__ == '__main__':
    main()
