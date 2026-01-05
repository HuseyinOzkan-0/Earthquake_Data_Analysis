import React from 'react';
import { AlertTriangle } from 'lucide-react';

function EarthquakeList({ data }) {
  // Filter for anomalies to show them prominently
  const anomalies = data.filter(eq => eq.is_anomaly);

  return (
    <div className="data-list">
      <h3>Recent Events</h3> 
        {data.slice(0, 20).map((eq, i) => ( <div key={i} className="list-item"> 
        <span className="mag">{eq.mag}</span> <span className="loc">{eq.location}
        </span> <span className="time">{eq.time}</span> 
        </div>
        ))}
        <hr />
        <h3>⚠️ Detected Anomalies ({anomalies.length})</h3>
      <p className="subtitle">Events with unusual magnitude/depth ratio.</p>
      <div className="scroll-area">
        {anomalies.map((eq, i) => (
          <div key={i} className="list-item anomaly">
            <AlertTriangle size={16} color="orange" />
            <span className="mag">{eq.mag}</span>
            <span className="loc">{eq.location}</span>
            <span className="time">{eq.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EarthquakeList;