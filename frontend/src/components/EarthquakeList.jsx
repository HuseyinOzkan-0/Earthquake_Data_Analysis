import React from 'react';
import { AlertTriangle } from 'lucide-react';

function EarthquakeList({ data, onEarthquakeSelect }) {
  // Sort data by date and time (newest first)
  const sortedData = [...data].sort((a, b) => {
    const dateA = `${a.date}${a.time}`;
    const dateB = `${b.date}${b.time}`;
    return dateB.localeCompare(dateA); // Descending order (newest first)
  });
  
  // Filter for anomalies to show them prominently
  const anomalies = sortedData.filter(eq => eq.is_anomaly);
  const recentEvents = sortedData.slice(0, 20);

  return (
    <div className="data-list">
      <h3>Recent Events</h3>
      <div className="recent-events-container">
        {recentEvents.map((eq, i) => (
          <div key={i} className="list-item" onClick={() => onEarthquakeSelect && onEarthquakeSelect(eq)} style={{ cursor: 'pointer' }}>
            <span className="mag-badge">{eq.mag}</span>
            <span className="loc">{eq.location}</span>
            <span className="time">{eq.time}</span>
          </div>
        ))}
      </div>

      <h3>⚠️ Detected Anomalies ({anomalies.length})</h3>
      <p className="subtitle">Events with unusual magnitude/depth ratio.</p>
      <div className="anomalies-container">
        {anomalies.map((eq, i) => (
          <div key={i} className="list-item anomaly" onClick={() => onEarthquakeSelect && onEarthquakeSelect(eq)} style={{ cursor: 'pointer' }}>
            <AlertTriangle size={16} color="orange" />
            <span className="mag-badge">{eq.mag}</span>
            <span className="loc">{eq.location}</span>
            <span className="time">{eq.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EarthquakeList;