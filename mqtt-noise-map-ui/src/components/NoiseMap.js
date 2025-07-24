import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './NoiseMap.css';

// Fix Leaflet default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Color scale for noise levels
const getNoiseColor = (db) => {
  if (db < 30) return '#4caf50'; // Green - Very quiet
  if (db < 40) return '#8bc34a'; // Light green - Quiet
  if (db < 50) return '#cddc39'; // Yellow-green - Moderate
  if (db < 60) return '#ffeb3b'; // Yellow - Noticeable
  if (db < 70) return '#ff9800'; // Orange - Loud
  if (db < 80) return '#ff5722'; // Red-orange - Very loud
  return '#f44336'; // Red - Extremely loud
};

// Get noise level description
const getNoiseDescription = (db) => {
  if (db < 30) return 'Very Quiet';
  if (db < 40) return 'Quiet';
  if (db < 50) return 'Moderate';
  if (db < 60) return 'Noticeable';
  if (db < 70) return 'Loud';
  if (db < 80) return 'Very Loud';
  return 'Extremely Loud';
};

// Map style configurations
const mapStyles = {
  normal: {
    dark: {
      url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
    },
    light: {
      url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }
  },
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
  }
};

// Settings panel component
const SettingsPanel = ({ settings, onMapStyleChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="settings-panel">
      <button 
        className="settings-toggle btn btn-secondary"
        onClick={() => setIsOpen(!isOpen)}
      >
        ⚙️ Map Settings
      </button>
      
      {isOpen && (
        <div className="settings-dropdown glass animate-slideInRight">
          <h4>Map Style</h4>
          
          <div className="setting-group">
            <label>View:</label>
            <select 
              className="input"
              onChange={(e) => onMapStyleChange(e.target.value)}
              defaultValue="normal"
            >
              <option value="normal">Normal View</option>
              <option value="satellite">Satellite View</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

// Noise level legend component
const NoiseLegend = () => {
  const legendItems = [
    { range: '< 30 dB', color: '#4caf50', desc: 'Very Quiet' },
    { range: '30-40 dB', color: '#8bc34a', desc: 'Quiet' },
    { range: '40-50 dB', color: '#cddc39', desc: 'Moderate' },
    { range: '50-60 dB', color: '#ffeb3b', desc: 'Noticeable' },
    { range: '60-70 dB', color: '#ff9800', desc: 'Loud' },
    { range: '70-80 dB', color: '#ff5722', desc: 'Very Loud' },
    { range: '> 80 dB', color: '#f44336', desc: 'Extremely Loud' }
  ];

  return (
    <div className="noise-legend glass">
      <h4>🔊 Noise Levels</h4>
      <div className="legend-items">
        {legendItems.map((item, index) => (
          <div key={index} className="legend-item">
            <div 
              className="legend-color"
              style={{ backgroundColor: item.color }}
            ></div>
            <div className="legend-text">
              <span className="legend-range">{item.range}</span>
              <span className="legend-desc">{item.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Custom marker component
const AnimatedMarker = ({ sensor, index }) => {
  const [isActive, setIsActive] = useState(false);
  const markerRef = useRef(null);

  useEffect(() => {
    // Animate marker when data updates
    setIsActive(true);
    const timer = setTimeout(() => setIsActive(false), 1000);
    return () => clearTimeout(timer);
  }, [sensor.db, sensor.timestamp]);

  const color = getNoiseColor(sensor.db);
  const isRecent = (Date.now() - sensor.timestamp) < 30000; // Recent if within 30 seconds
  const opacity = isRecent ? 0.8 : 0.4;

  return (
    <CircleMarker
      key={sensor.device_id}
      center={[sensor.lat, sensor.lon]}
      radius={Math.max(8, Math.min(20, sensor.db / 4))} // Radius based on noise level
      pathOptions={{
        fillColor: color,
        color: isActive ? '#ffffff' : color,
        weight: isActive ? 3 : 2,
        fillOpacity: opacity,
        opacity: 1
      }}
      ref={markerRef}
      className={`noise-marker ${isActive ? 'active' : ''} ${isRecent ? 'recent' : 'old'}`}
    >
      <Popup>
        <div className="marker-popup">
          <div className="popup-header">
            <h4>📡 {sensor.device_id}</h4>
            <span className={`status-badge ${isRecent ? 'online' : 'offline'}`}>
              {isRecent ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          
          <div className="popup-content">
            <div className="noise-reading">
              <span className="noise-value" style={{ color }}>
                {sensor.db.toFixed(1)} dB
              </span>
              <span className="noise-desc">
                {getNoiseDescription(sensor.db)}
              </span>
            </div>
            
            <div className="sensor-details">
              <div className="detail-row">
                <span>📍 Location:</span>
                <span>{sensor.lat.toFixed(4)}, {sensor.lon.toFixed(4)}</span>
              </div>
              
              <div className="detail-row">
                <span>⏰ Last Update:</span>
                <span>{new Date(sensor.timestamp).toLocaleTimeString()}</span>
              </div>
              
              <div className="detail-row">
                <span>📶 Signal:</span>
                <span className={isRecent ? 'text-success' : 'text-error'}>
                  {isRecent ? 'Strong' : 'Weak/Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </Popup>
    </CircleMarker>
  );
};

// Main NoiseMap component
const NoiseMap = ({ sensorData, connectionStatus, settings }) => {
  const [mapStyle, setMapStyle] = useState('normal');
  const [mapCenter, setMapCenter] = useState([20.5937, 78.9629]); // India center
  const [mapZoom, setMapZoom] = useState(5);
  
  // Get current tile layer configuration based on style and dark mode
  const getCurrentTileLayer = () => {
    if (mapStyle === 'satellite') {
      return mapStyles.satellite;
    } else {
      // For normal view, use dark or light based on settings.darkMode
      return settings.darkMode ? mapStyles.normal.dark : mapStyles.normal.light;
    }
  };
  
  // Update map center based on sensor data
  useEffect(() => {
    if (sensorData.length > 0) {
      // Calculate center point of all sensors
      const lats = sensorData.map(s => s.lat);
      const lons = sensorData.map(s => s.lon);
      const avgLat = lats.reduce((sum, lat) => sum + lat, 0) / lats.length;
      const avgLon = lons.reduce((sum, lon) => sum + lon, 0) / lons.length;
      
      setMapCenter([avgLat, avgLon]);
      
      // Adjust zoom based on sensor spread
      if (sensorData.length > 1) {
        const latSpread = Math.max(...lats) - Math.min(...lats);
        const lonSpread = Math.max(...lons) - Math.min(...lons);
        const maxSpread = Math.max(latSpread, lonSpread);
        
        if (maxSpread < 0.01) setMapZoom(15);
        else if (maxSpread < 0.1) setMapZoom(12);
        else if (maxSpread < 1) setMapZoom(9);
        else setMapZoom(7);
      }
    }
  }, [sensorData]);

  const handleMapStyleChange = (style) => {
    setMapStyle(style);
  };

  return (
    <div className="noise-map-container">      
      {/* Settings Panel */}
      <SettingsPanel 
        settings={settings}
        onMapStyleChange={handleMapStyleChange}
      />
      
      {/* Noise Legend */}
      <NoiseLegend />
      
      {/* Main Map */}
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        attributionControl={true}
        className="noise-leaflet-map"
      >
        <TileLayer
          attribution={getCurrentTileLayer().attribution}
          url={getCurrentTileLayer().url}
        />
        
        {/* Render sensor markers */}
        {sensorData.map((sensor, index) => (
          <AnimatedMarker 
            key={sensor.device_id} 
            sensor={sensor} 
            index={index}
          />
        ))}
      </MapContainer>
      
      {/* Connection Status Overlay */}
      {connectionStatus !== 'connected' && (
        <div className="connection-overlay">
          <div className="connection-message glass">
            <div className="spinner"></div>
            <p>
              {connectionStatus === 'connecting' && '🔄 Connecting to sensors...'}
              {connectionStatus === 'disconnected' && '📡 Disconnected from sensors'}
              {connectionStatus === 'error' && '❌ Connection error - Check your MQTT broker'}
            </p>
          </div>
        </div>
      )}
      
      {/* No Data Message */}
      {sensorData.length === 0 && connectionStatus === 'connected' && (
        <div className="no-data-overlay">
          <div className="no-data-message glass animate-fadeIn">
            <h3>🔍 No Sensors Detected</h3>
            <p>Waiting for sensor data...</p>
            <p>Make sure your ESP32 sensors are:</p>
            <ul>
              <li>✅ Connected to WiFi</li>
              <li>✅ Publishing to the correct MQTT topic</li>
              <li>✅ Sending valid JSON data</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default NoiseMap;

// import React, { useState, useEffect, useRef } from 'react';
// import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
// import NoiseMapOverlay from './NoiseMapOverlay';
// import mqttService from '../mqtt/mqttService';
// import 'leaflet/dist/leaflet.css';

// const NoiseMap = () => {
//   const [sensorData, setSensorData] = useState([]);
//   const [interpolatedData, setInterpolatedData] = useState(null);
//   const [showOverlay, setShowOverlay] = useState(true);
//   const [overlayOpacity, setOverlayOpacity] = useState(0.6);
//   const mapRef = useRef(null);

//   useEffect(() => {
//     const handleSensorData = (payload) => {
//       setSensorData(prev => {
//         const updated = [...prev];
//         const existingIndex = updated.findIndex(d => d.device_id === payload.device_id);
        
//         if (existingIndex >= 0) {
//           updated[existingIndex] = payload;
//         } else {
//           updated.push(payload);
//         }
        
//         return updated;
//       });
//     };

//     const handleInterpolatedData = (payload) => {
//       setInterpolatedData(payload);
//     };

//     mqttService.connect(handleSensorData, handleInterpolatedData);

//     return () => {
//       mqttService.disconnect();
//     };
//   }, []);

//   const getMarkerColor = (db) => {
//     if (db < 40) return '#2dc937';
//     if (db < 60) return '#99c140';
//     if (db < 80) return '#e7b416';
//     return '#cc3232';
//   };

//   return (
//     <div style={{ position: 'relative', height: '100vh', width: '100vw' }}>
//       {/* Map Controls */}
//       <div style={{
//         position: 'absolute',
//         top: 10,
//         right: 10,
//         zIndex: 1000,
//         background: 'rgba(255, 255, 255, 0.9)',
//         padding: '10px',
//         borderRadius: '5px',
//         boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
//       }}>
//         <div style={{ marginBottom: '10px' }}>
//           <label>
//             <input
//               type="checkbox"
//               checked={showOverlay}
//               onChange={(e) => setShowOverlay(e.target.checked)}
//             />
//             {' '}Show Noise Map Overlay
//           </label>
//         </div>
//         <div>
//           <label>
//             Opacity: {Math.round(overlayOpacity * 100)}%
//             <input
//               type="range"
//               min="0"
//               max="1"
//               step="0.1"
//               value={overlayOpacity}
//               onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
//               style={{ width: '100px', marginLeft: '10px' }}
//             />
//           </label>
//         </div>
//       </div>

//       <MapContainer
//         center={[12.912, 77.675]}
//         zoom={13}
//         style={{ height: "100vh", width: "100vw" }}
//         ref={mapRef}
//       >
//         <TileLayer
//           attribution='&copy; OpenStreetMap contributors'
//           url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//         />
        
//         {/* Noise Map Overlay */}
//         {showOverlay && (
//           <NoiseMapOverlay
//             map={mapRef.current}
//             interpolatedData={interpolatedData}
//             opacity={overlayOpacity}
//           />
//         )}
        
//         {/* Sensor Points */}
//         {sensorData.map((data, idx) => (
//           <CircleMarker
//             key={data.device_id || idx}
//             center={[data.lat, data.lon]}
//             radius={8}
//             fillOpacity={0.8}
//             color={getMarkerColor(data.db)}
//             weight={2}
//           >
//             <Tooltip>
//               <div>
//                 <strong>Sensor:</strong> {data.device_id} <br />
//                 <strong>Noise:</strong> {data.db} dB(A) <br />
//                 <strong>Height:</strong> {data.height || 'N/A'} m <br />
//                 <strong>Time:</strong> {new Date(data.timestamp).toLocaleString()}
//               </div>
//             </Tooltip>
//           </CircleMarker>
//         ))}
//       </MapContainer>
//     </div>
//   );
// };

// export default NoiseMap;
