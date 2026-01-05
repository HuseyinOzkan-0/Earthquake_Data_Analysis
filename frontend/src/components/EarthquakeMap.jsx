import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const turkeyBounds = [
  [34.0, 25.0],
  [43.0, 46.0] 
];

const getColor = (mag) => {
  if (mag > 7) return "#8b0000";
  if (mag > 6) return "#ff0000";
  if (mag > 5) return "#ff6600";
  if (mag > 4) return "#ffa500";
  if (mag > 3) return "#ffff66";
  if (mag > 2) return "#a6ff00ff";
  if (mag > 1) return "#00ff22ff";
  return "#000000ff";              
};

function EarthquakeMap({ data }) {
  return (
    <MapContainer center={[39.0, 35.0]} zoom={6} style={{ height: "500px", width: "100%" }} minZoom={5} maxBounds={turkeyBounds}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {data.map((eq, idx) => (
        <CircleMarker 
          key={idx}
          center={[eq.lat, eq.lng]}
          radius={eq.mag * 3}
          fillColor={eq.is_anomaly ? "black" : getColor(eq.mag)}
          color="#000000ff"
          weight={eq.is_anomaly ? 3 : 1}
          fillOpacity={0.7}
        >
          <Popup>
            <strong>{eq.location}</strong><br/>
            Mag: {eq.mag} | Depth: {eq.depth}km <br/>
            {eq.is_anomaly && <span style={{color: 'red'}}>⚠️ ANOMALY DETECTED</span>}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}

export default EarthquakeMap;