# Earthquake Data Analysis — Reproducible Report and Deliverables

## Overview

This project ingests earthquake event data from Kandilli Observatory, cleans and stores events in a local SQLite database, detects anomalous events, and provides both interactive visualization (React frontend) and reproducible analysis artifacts (notebook + scripts). The repository is structured to make grading and reproduction straightforward.

## Quickstart (Windows PowerShell)

1. Create and activate the virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install backend requirements:

```powershell
pip install -r backend/requirements.txt
```

3. Start the backend (scheduler and API):

```powershell
cd backend
python app.py
```

You should see a log line: "Background scheduler started: scraping every 5 minutes".

4. Start the frontend (in a separate terminal):

```powershell
cd frontend
npm install
npm run dev
```

Open the app in a browser (usually `http://localhost:5173/`) — the UI polls every 5 minutes and subscribes to server-sent events so it updates immediately when the backend scrapes new data.

## What to run to reproduce figures and tables

1. Generate the reproducible figures and an interactive map:

```powershell
python backend/generate_report.py
```

Outputs are written to the `reports/` folder:
- `reports/fig_mag_hist.png` — magnitude distribution (anomalies highlighted)
- `reports/fig_map.png` — static latitude/longitude scatter
- `reports/map.html` — interactive map (open in a browser)

2. The notebook `notebooks/repro_report.ipynb` demonstrates the same steps interactively and documents assumptions.

## Data cleaning — exact steps performed / recommended

The repository follows these reproducible cleaning steps (also documented in `notebooks/repro_report.ipynb`):

1. Ingest raw HTML from Kandilli and parse fixed-width columns (see `backend/app.py`). Raw content is preserved in the ingestion step where possible.
2. Parse timestamps with `pandas.to_datetime(..., errors='coerce')` and normalize to UTC.
3. Validate coordinates: drop or flag lat/lon outside valid ranges.
4. Normalize magnitudes and depth (store depths in kilometers). Flag negative/absurd depths as missing.
5. Deduplicate by `date`, `time`, and `location` at ingest — duplicates are skipped.
6. Add provenance columns: `source`, `raw_filename`, `ingest_time`, and `cleaning_notes` when applicable.
7. Save cleaned data to the database `backend/instance/earthquakes.db` and to `reports/` when exporting.

Example quick check (pandas):

```python
import pandas as pd
df = pd.read_parquet('data/cleaned/events-YYYY-MM-DD.parquet')
df['time'] = pd.to_datetime(df['time'], utc=True, errors='coerce')
df = df[df['time'].notna()]
```

## Anomaly detection (what I implemented)

- Method: Isolation Forest (see `backend/analysis.py`) using numeric features `lat`, `lng`, `depth`, `mag`.
- Output: boolean `is_anomaly` per event and `anomaly_score` for ranking.
- Tuning: the default contamination is set in code; you can change it when calling `detect_anomalies()`.

Minimal example (already used by the app):

```python
from backend.analysis import detect_anomalies
df = detect_anomalies(df)
```

## Advanced scientific reporting & reproducibility

- All analysis steps are captured in `notebooks/repro_report.ipynb` and in the script `backend/generate_report.py` which saves figures to `reports/`.
- Include environment snapshot:

```powershell
pip freeze > backend/requirements-freeze.txt
```

- For graders: run the Quickstart steps above, then `python backend/generate_report.py` and open `reports/map.html` and images.

## Files of interest

- Backend: [backend/app.py](backend/app.py) (scraper + API + scheduler)
- Analysis: [backend/analysis.py](backend/analysis.py) (anomaly detection + simple predictions)
- Reproducible report script: [backend/generate_report.py](backend/generate_report.py)
- Notebook: [notebooks/repro_report.ipynb](notebooks/repro_report.ipynb)
- Frontend: [frontend/src/App.jsx](frontend/src/App.jsx) (data fetching, SSE subscription)


