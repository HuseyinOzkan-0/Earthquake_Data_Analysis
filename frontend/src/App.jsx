import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import EarthquakeMap from './components/EarthquakeMap';
import EarthquakeList from './components/EarthquakeList';
import Predictions from './components/Predictions';
import { MapPinned, Map as MapIcon, BarChart3 } from 'lucide-react';

function App() {
  const [earthquakes, setEarthquakes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEarthquake, setSelectedEarthquake] = useState(null);

  useEffect(() => {
    const fetchData = () => {
      axios.get('http://127.0.0.1:5000/api/earthquakes')
        .then(res => {
          setEarthquakes(res.data);
          setLoading(false);
        })
        .catch(err => console.error('Error fetching data:', err));
    };

    // Initial fetch
    fetchData();

    // Poll every 5 minutes (300000 ms)
    const interval = setInterval(fetchData, 300000);

    // Subscribe to server-sent events to get immediate updates when backend scrapes new data
    let es;
    try {
      es = new EventSource('http://127.0.0.1:5000/api/stream');
      es.onmessage = (e) => {
        // Server notifies with a small payload; refresh immediately
        try { const payload = JSON.parse(e.data); console.log('SSE event:', payload); } catch (err) {}
        fetchData();
      };
      es.onerror = (err) => { console.warn('SSE connection error', err); es.close(); };
    } catch (err) {
      console.warn('SSE not supported or connection failed', err);
    }

    return () => { clearInterval(interval); if (es) es.close(); };
  }, []);

  if (loading) return <div className="loading">Scraping Kandilli Data...</div>;

  return (
    <Router>
      <div className="app-container">
        <nav className="navbar">
          <h1><MapPinned size={30} color="#ffffffff" /> Türkiye Deprem Haritası</h1>
          <div className="nav-links">
            <Link to="/"><MapIcon size={18} /> Map & Anomalies</Link>
            <Link to="/predictions"><BarChart3 size={18} /> Predictions</Link>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={
            <div className="main-layout">
              <div className="map-section">
                <EarthquakeMap data={earthquakes} selectedEarthquake={selectedEarthquake} />
              </div>
              <div className="list-section">
                <EarthquakeList data={earthquakes} onEarthquakeSelect={setSelectedEarthquake} />
              </div>
            </div>
          } />
          <Route path="/predictions" element={<Predictions />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;