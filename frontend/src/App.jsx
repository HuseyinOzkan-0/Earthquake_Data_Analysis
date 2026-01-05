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

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/earthquakes')
      .then(res => {
        setEarthquakes(res.data);
        setLoading(false);
      })
      .catch(err => console.error("Error fetching data:", err));
  }, []);

  if (loading) return <div className="loading">Scraping Kandilli Data...</div>;

  return (
    <Router>
      <div className="app-container">
        <nav className="navbar">
          <h1><MapPinned size={30} color="#ffffffff" /> Türkiye Deprem Hartiası</h1>
          <div className="nav-links">
            <Link to="/"><MapIcon size={18} /> Map & Anomalies</Link>
            <Link to="/predictions"><BarChart3 size={18} /> Predictions</Link>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={
            <div className="main-layout">
              <div className="map-section">
                <EarthquakeMap data={earthquakes} />
              </div>
              <div className="list-section">
                <EarthquakeList data={earthquakes} />
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