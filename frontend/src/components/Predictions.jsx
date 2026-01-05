import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Predictions() {
  const [preds, setPreds] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/predictions')
      .then(res => setPreds(res.data));
  }, []);

  return (
    <div className="predictions-page">
      <h2>Scientific Analysis & Forecast</h2>
      <div className="prediction-grid">
        {preds.map((p, i) => (
          <div key={i} className="prediction-card">
            <h4>{p.location}</h4>
            <div className="risk-bar">
              <div 
                className="risk-fill" 
                style={{ width: `${p.risk_score * 100}%`, backgroundColor: p.risk_score > 0.6 ? '#ff4d4d' : '#ffcc00' }}
              ></div>
            </div>
            <p>Calculated Risk Score: {(p.risk_score * 10).toFixed(2)}/10</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Predictions;