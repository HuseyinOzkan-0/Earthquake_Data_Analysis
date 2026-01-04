import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// COLOR SCALE LOGIC
const getColor = (mag) => {
  if (mag >= 6.0) return "#8B0000"; // Dark Red (Critical)
  if (mag >= 5.0) return "#FF0000"; // Red (Strong)
  if (mag >= 4.0) return "#FF8C00"; // Dark Orange (Moderate)
  if (mag >= 3.0) return "#FFD700"; // Gold (Noticeable)
  if (mag >= 2.0) return "#ADFF2F"; // GreenYellow (Minor)
  return "#00FF00"; // Lime (Micro)
};

function MapView({ earthquakes }) {
  return (
    <MapContainer center={[39.0, 35.0]} zoom={6} style={{ height: "100%", width: "100%", borderRadius: "8px" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {earthquakes.map((eq, i) => (
        <CircleMarker 
          key={i} 
          center={[eq.lat, eq.lon]} 
          radius={eq.mag * 4} 
          pathOptions={{ 
            color: getColor(eq.mag), 
            fillColor: getColor(eq.mag), 
            fillOpacity: 0.6,
            weight: 2 
          }}
        >
          <Popup>
            <strong>{eq.location}</strong><br/>
            Magnitude: {eq.mag}<br/>
            Depth: {eq.depth}km<br/>
            {eq.is_anomaly && <span style={{color: 'red'}}>⚠️ Statistical Anomaly</span>}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}

export default MapView;