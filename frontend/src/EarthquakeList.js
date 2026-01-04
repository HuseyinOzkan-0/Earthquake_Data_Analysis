import React from 'react';

function EarthquakeList({ earthquakes }) {
  return (
    <div className="earthquake-list">
      <h3>Live Feed</h3>
      <div className="scroll-container">
        {earthquakes.map((eq, i) => (
          <div key={i} className={`list-card ${eq.is_anomaly ? 'anomaly' : ''}`}>
            <div className="card-header">
              <span className="mag-tag" style={{backgroundColor: getBadgeColor(eq.mag)}}>
                {eq.mag.toFixed(1)}
              </span>
              <span className="location">{eq.location}</span>
            </div>
            <div className="card-footer">
              <span>{eq.date_time}</span>
              <span>Depth: {eq.depth}km</span>
            </div>
            {eq.is_anomaly && <div className="anomaly-warning">⚠️ Anomaly Detected</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

const getBadgeColor = (mag) => {
  if (mag >= 5.0) return "#ff0000";
  if (mag >= 4.0) return "#ff8c00";
  if (mag >= 3.0) return "#ccac00";
  return "#27ae60";
};

export default EarthquakeList;