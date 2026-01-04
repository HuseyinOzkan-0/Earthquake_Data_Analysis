import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MapView from './MapView';
import EarthquakeList from './EarthquakeList';
import './App.css';
import 'leaflet/dist/leaflet.css';

function App() {
  const [view, setView] = useState('live'); 
  const [data, setData] = useState([]);
  const [possibleData, setPossibleData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const liveRes = await axios.get('http://127.0.0.1:8000/api/earthquakes');
        setData(liveRes.data);
        const possibleRes = await axios.get('http://127.0.0.1:8000/api/possible-earthquakes');
        setPossibleData(possibleRes.data);
      } catch (err) {
        console.error("Backend Error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="App">
      <nav className="navbar">
        <button className={view === 'live' ? 'active' : ''} onClick={() => setView('live')}>
          Live Earthquakes
        </button>
        <button className={view === 'possible' ? 'active' : ''} onClick={() => setView('possible')}>
          Possible Risks (Prediction)
        </button>
      </nav>

      <main className="dashboard">
        {view === 'live' ? (
          <>
            <div className="map-section"><MapView earthquakes={data} /></div>
            <div className="list-section"><EarthquakeList earthquakes={data} /></div>
          </>
        ) : (
          <>
            <div className="map-section"><MapView earthquakes={possibleData} isPrediction={true} /></div>
            <div className="list-section">
              <div className="prediction-info">
                <h3>Risk Analysis</h3>
                <p>Based on cluster density and historical pressure points.</p>
                <EarthquakeList earthquakes={possibleData} />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
} // <--- The function ends here!

export default App; // <--- The export is now at the TOP LEVEL