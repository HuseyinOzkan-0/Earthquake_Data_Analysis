# Earthquake Data Analysis Platform

## Project Overview

This project is a comprehensive full-stack application designed to scrape, analyze, and visualize real-time earthquake data from the Kandilli Observatory. It features an automated data pipeline, machine learning-based anomaly detection, and an interactive modern web dashboard.

## Technical Architecture

The solution uses a decoupled architecture for robustness and maintainability:

*   **Backend:** Python 3.10+, Flask, SQLAlchemy (SQLite), APScheduler.
*   **Frontend:** React.js (Vite), Leaflet Maps, Server-Sent Events (SSE).
*   **Data Science:** Pandas, Scikit-learn (Isolation Forest), Matplotlib/Seaborn.
*   **DevOps:** Cross-platform support (Windows/macOS/Linux), Virtual Environments.

## Features

*   **Automated Data Ingestion:**
    *   Real-time scraping of messy HTML data from the source.
    *   Intelligent parsing and cleaning pipeline.
    *   Duplicate detection and data normalization.
*   **Advanced Analysis:**
    *   **Anomaly Detection:** Uses `Isolation Forest` to identify unusual seismic events based on magnitude, depth, and location.
    *   **Risk Prediction:** Statistical analysis of historical clusters to estimate future activity density.
*   **Modern Visualization:**
    *   Interactive React dashboard with real-time updates.
    *   Geospatial mapping of events and anomalies.
    *   Responsive design for various devices.

## Prerequisites

Ensure the following are installed on your system:

1.  **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
    *   *Note:* Ensure "Add Python to PATH" is selected during installation.
2.  **Node.js (LTS version)**: [Download Node.js](https://nodejs.org/)
    *   Required for the React frontend build tools.

## Installation & Setup

### 1. Backend Initialization

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Frontend Initialization

```bash
cd frontend
npm install
```

## Running the Application

For the full experience, run the backend and frontend in parallel using two terminal windows.

**Terminal 1: Backend Service**
```bash
# Ensure virtual environment is active (.venv)
cd backend
python app.py
```
*The server will start on port 5000 and begin the background scraping job.*

**Terminal 2: Frontend Dashboard**
```bash
cd frontend
npm run dev
```
*   Access the dashboard at: `http://localhost:5173`
*   **Tip:** Use Ctrl+Click on the URL in the terminal to open it instantly.

## Data Cleaning & Processing Pipeline

Consistent with data science best practices, the `KandilliScraper` class performs the following step-by-step cleaning on the messy raw input:

1.  **Raw Ingestion (Scraping):** 
    *   Fetches the raw HTML content from the Kandilli Observatory via HTTP request.
    *   Extracts the inner text of the `<pre>` tag containing the unstructured data table.
2.  **Structuring & Parsing:** 
    *   Splits the raw text block into individual lines.
    *   Iterates through each line and applies fixed-width slicing to extract fields:
        *   `Date` (Chars 0-10) & `Time` (11-19)
        *   `Latitude` (21-28) & `Longitude` (30-37)
        *   `Depth` (43-49) & `Magnitude` (60-63)
        *   `Location` (71-121)
3.  **Data Cleaning & Normalization:**
    *   **Type Conversion:** Converts string coordinates and measurements to `float`.
    *   **Whitespace Removal:** Trims leading/trailing whitespace from location strings.
    *   **Error Handling:** Discards lines that fail validation or don't start with a digit (headers/footers).
4.  **Database Integration & Deduplication:** 
    *   Checks each parsed record against the SQLite database using a composite key (`Date` + `Time` + `Location`).
    *   Discards records that already exist to prevent duplication.
5.  **Anomaly Scoring (Data Science):** 
    *   Passes new, clean records through the `SeismologicalAnalyzer`.
    *   Uses **Isolation Forest** (Unsupervised ML) to score and flag anomalous events before saving.

## Reproducibility & Testing

### Unit Tests
The project includes a test suite to ensure robustness.
```bash
python -m unittest discover backend/tests
```

### Static Reports
To generate analysis artifacts without running the web server:
```bash
python backend/generate_report.py
```
Outputs are saved to `reports/` (Histograms, Scatter Plots, Offline Maps).


