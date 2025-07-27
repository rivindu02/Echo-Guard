import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import L from 'leaflet';
import NoiseMapOverlay from './NoiseMapOverlay';
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
const SettingsPanel = React.memo(({ settings, onMapStyleChange, showOverlay, onToggleOverlay, overlayOpacity, onOpacityChange }) => {
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

          <h4>Noise Distribution</h4>
          
          <div className="setting-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={showOverlay}
                onChange={(e) => onToggleOverlay(e.target.checked)}
              />
              <span>Show Noise Map</span>
            </label>
          </div>

          {showOverlay && (
            <div className="setting-group">
              <label>Opacity: {Math.round(overlayOpacity * 100)}%</label>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                value={overlayOpacity}
                onChange={(e) => onOpacityChange(parseFloat(e.target.value))}
                className="slider"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// Live sensor stats component
const LiveSensorStats = React.memo(({ sensorData }) => {
  // Get current timestamp for checking if sensor is active
  const now = Date.now();
  const activeThreshold = 30000; // 30 seconds
  
  // Create sensor status array - memoized to prevent recalculation
  const sensorStats = useMemo(() => {
    // Create array of 5 sensors with predefined IDs (matching the fake_esp32.py format)
    const sensorIds = ['esp32-001', 'esp32-002', 'esp32-003', 'esp32-004', 'esp32-005'];
    
    return sensorIds.map(sensorId => {
      const sensorInfo = sensorData.find(sensor => sensor.device_id === sensorId);
      const isActive = sensorInfo && (now - sensorInfo.timestamp) < activeThreshold;
      
      return {
        id: sensorId,
        isActive,
        db: sensorInfo ? sensorInfo.db : 0,
        lastSeen: sensorInfo ? sensorInfo.timestamp : null,
        location: sensorInfo ? `${sensorInfo.lat.toFixed(3)}, ${sensorInfo.lon.toFixed(3)}` : 'Unknown'
      };
    });
  }, [sensorData, now, activeThreshold]);

  const getStatusIcon = (isActive) => isActive ? '🟢' : '🔴';
  const getStatusText = (isActive) => isActive ? 'ACTIVE' : 'OFFLINE';
  const getStatusClass = (isActive) => isActive ? 'status-active' : 'status-offline';

  return (
    <div className="live-sensor-stats glass">
      <div className="stats-header">
        <h4>Live Sensor Status</h4>
        <div className="stats-summary">
          <span className="active-count">
            {sensorStats.filter(s => s.isActive).length}/5 Active
          </span>
        </div>
      </div>
      
      <div className="sensor-list">
        {sensorStats.map((sensor, index) => (
          <div key={sensor.id} className={`sensor-item ${getStatusClass(sensor.isActive)}`}>
            <div className="sensor-header">
              <div className="sensor-id">
                {getStatusIcon(sensor.isActive)} {sensor.id}
              </div>
              <div className={`sensor-status ${getStatusClass(sensor.isActive)}`}>
                {getStatusText(sensor.isActive)}
              </div>
            </div>
            
            <div className="sensor-data">
              {sensor.isActive ? (
                <>
                  <div className="noise-reading">
                    <span className="noise-value" style={{ color: getNoiseColor(sensor.db) }}>
                      {sensor.db.toFixed(1)} dB
                    </span>
                    <span className="noise-desc">
                      {getNoiseDescription(sensor.db)}
                    </span>
                  </div>
                  <div className="sensor-meta">
                    <div className="last-update">
                      ⏰ {new Date(sensor.lastSeen).toLocaleTimeString()}
                    </div>
                  </div>
                </>
              ) : (
                <div className="offline-message">
                  <span>⚠️ No data received</span>
                  {sensor.lastSeen && (
                    <div className="last-seen">
                      Last seen: {new Date(sensor.lastSeen).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

// Custom marker component - optimized with memo
const AnimatedMarker = React.memo(({ sensor, index }) => {
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
      key={`marker_${sensor.device_id}_${sensor.timestamp}`}
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
}, (prevProps, nextProps) => {
  // Custom comparison to prevent unnecessary re-renders
  return (
    prevProps.sensor.device_id === nextProps.sensor.device_id &&
    prevProps.sensor.db === nextProps.sensor.db &&
    prevProps.sensor.timestamp === nextProps.sensor.timestamp &&
    prevProps.sensor.lat === nextProps.sensor.lat &&
    prevProps.sensor.lon === nextProps.sensor.lon
  );
});

// Main NoiseMap component
const NoiseMap = ({ sensorData, connectionStatus, settings }) => {
  const [mapStyle, setMapStyle] = useState('normal');
  const [mapCenter, setMapCenter] = useState([6.9271, 79.8612]); // Sri Lanka center
  const [mapZoom, setMapZoom] = useState(12);
  const [showOverlay, setShowOverlay] = useState(true);
  const [overlayOpacity, setOverlayOpacity] = useState(0.6);
  const [interpolatedData, setInterpolatedData] = useState(null);
  const [lastInterpolationTime, setLastInterpolationTime] = useState(0);
  const mapRef = useRef(null);
  const interpolationTimeoutRef = useRef(null);

  // Throttled interpolation function to create smooth noise distribution
  const interpolateNoiseData = useCallback((sensors) => {
    if (sensors.length < 2) return null;

    console.log(`🔧 Interpolating data for ${sensors.length} sensors:`, 
      sensors.map(s => `${s.device_id}: ${s.db}dB at (${s.lat.toFixed(3)}, ${s.lon.toFixed(3)})`));

    // Define grid bounds based on sensor locations with smaller padding
    const lats = sensors.map(s => s.lat);
    const lons = sensors.map(s => s.lon);
    
    // Use very small padding for tightly focused noise map coverage
    // 2% margin around sensors for minimal overlay area
    const sensorLatSpread = Math.max(...lats) - Math.min(...lats);
    const sensorLonSpread = Math.max(...lons) - Math.min(...lons);
    const basePadding = Math.max(sensorLatSpread, sensorLonSpread) * 0.02; // 0.2% margin
    const padding = Math.max(0.0005, basePadding); // Minimum 0.0005 degrees (~0.05km)
    
    const minLat = Math.min(...lats) - padding;
    const maxLat = Math.max(...lats) + padding;
    const minLon = Math.min(...lons) - padding;
    const maxLon = Math.max(...lons) + padding;

    console.log(`🗺️ Interpolation bounds: lat(${minLat.toFixed(3)}, ${maxLat.toFixed(3)}), lon(${minLon.toFixed(3)}, ${maxLon.toFixed(3)})`);

    // Adaptive grid size based on sensor spread
    const latSpread = maxLat - minLat;
    const lonSpread = maxLon - minLon;
    const maxSpread = Math.max(latSpread, lonSpread);
    
    // Use higher resolution for smaller areas, lower for larger areas
    let gridRes;
    if (maxSpread < 1) gridRes = 80;      // High resolution for local areas
    else if (maxSpread < 5) gridRes = 60; // Medium resolution for regional areas  
    else gridRes = 40;                    // Lower resolution for country-wide areas
    
    const gridSize = [gridRes, gridRes];
    const latStep = (maxLat - minLat) / gridSize[1];
    const lonStep = (maxLon - minLon) / gridSize[0];

    console.log(`📐 Using grid size: ${gridSize[0]}x${gridSize[1]}, resolution: ${gridRes}`);

    let minDb = Infinity;
    let maxDb = -Infinity;

    // Enhanced Inverse Distance Weighting (IDW) interpolation
    // Create a 2D array to properly handle coordinate mapping
    const grid = [];
    for (let i = 0; i < gridSize[1]; i++) {
      grid[i] = [];
    }
    
    for (let i = 0; i < gridSize[1]; i++) {
      for (let j = 0; j < gridSize[0]; j++) {
        // Important: Map grid coordinates to geographic coordinates properly
        // i=0 should be maxLat (north), i=gridSize[1]-1 should be minLat (south)
        // j=0 should be minLon (west), j=gridSize[0]-1 should be maxLon (east)
        const lat = maxLat - (i * latStep); // Flip latitude (north at top)
        const lon = minLon + (j * lonStep);   // Normal longitude (west to east)

        let weightedSum = 0;
        let weightSum = 0;

        sensors.forEach(sensor => {
          // Calculate actual geographic distance (approximation)
          const deltaLat = lat - sensor.lat;
          const deltaLon = lon - sensor.lon;
          const distanceSquared = deltaLat * deltaLat + (deltaLon * Math.cos(lat * Math.PI / 180)) * (deltaLon * Math.cos(lat * Math.PI / 180));
          
          // Improved weight calculation with power parameter
          const power = 2.0; // IDW power parameter
          const weight = distanceSquared === 0 ? 1e10 : 1 / Math.pow(distanceSquared + 1e-10, power);
          weightedSum += sensor.db * weight;
          weightSum += weight;
        });

        const interpolatedValue = weightedSum / weightSum;
        grid[i][j] = interpolatedValue;
        
        minDb = Math.min(minDb, interpolatedValue);
        maxDb = Math.max(maxDb, interpolatedValue);
      }
    }
    
    // Convert 2D grid to 1D array in proper order (row-major)
    const values = [];
    for (let i = 0; i < gridSize[1]; i++) {
      for (let j = 0; j < gridSize[0]; j++) {
        values.push(grid[i][j]);
      }
    }

    const result = {
      interpolated_grid: {
        bounds: [[minLat, minLon], [maxLat, maxLon]],
        grid_size: gridSize,
        values: values,
        min_db: minDb,
        max_db: maxDb
      }
    };

    console.log(`📊 Interpolation complete: ${values.length} points, dB range: ${minDb.toFixed(1)} - ${maxDb.toFixed(1)}`);
    
    // Debug: Log some sample grid points to verify coordinate mapping
    console.log(`🔍 Sample interpolation points:
      Top-left (${maxLat.toFixed(3)}, ${minLon.toFixed(3)}): ${grid[0][0].toFixed(1)}dB
      Top-right (${maxLat.toFixed(3)}, ${maxLon.toFixed(3)}): ${grid[0][gridSize[0]-1].toFixed(1)}dB
      Bottom-left (${minLat.toFixed(3)}, ${minLon.toFixed(3)}): ${grid[gridSize[1]-1][0].toFixed(1)}dB
      Bottom-right (${minLat.toFixed(3)}, ${maxLon.toFixed(3)}): ${grid[gridSize[1]-1][gridSize[0]-1].toFixed(1)}dB`);
    
    return result;
  }, []);

  // Throttled update function to limit interpolation frequency
  const updateInterpolatedData = useCallback((sensors) => {
    const now = Date.now();
    const timeSinceLastInterpolation = now - lastInterpolationTime;
    const minUpdateInterval = 200; // Reduced to 200ms for more responsive updates

    // Clear any pending timeout
    if (interpolationTimeoutRef.current) {
      clearTimeout(interpolationTimeoutRef.current);
    }

    if (timeSinceLastInterpolation >= minUpdateInterval) {
      // Update immediately if enough time has passed
      const startTime = performance.now();
      const interpolated = interpolateNoiseData(sensors);
      const endTime = performance.now();
      
      console.log(`🚀 Interpolation completed in ${(endTime - startTime).toFixed(2)}ms`);
      
      setInterpolatedData(interpolated);
      setLastInterpolationTime(now);
    } else {
      // Schedule update for later
      const delay = minUpdateInterval - timeSinceLastInterpolation;
      interpolationTimeoutRef.current = setTimeout(() => {
        const startTime = performance.now();
        const interpolated = interpolateNoiseData(sensors);
        const endTime = performance.now();
        
        console.log(`🚀 Delayed interpolation completed in ${(endTime - startTime).toFixed(2)}ms`);
        
        setInterpolatedData(interpolated);
        setLastInterpolationTime(Date.now());
      }, delay);
    }
  }, [interpolateNoiseData, lastInterpolationTime]);

  // Update interpolated data when sensor data changes (with throttling)
  useEffect(() => {
    if (sensorData.length >= 2) {
      updateInterpolatedData(sensorData);
    } else {
      setInterpolatedData(null);
    }
    
    // Cleanup timeout on unmount
    return () => {
      if (interpolationTimeoutRef.current) {
        clearTimeout(interpolationTimeoutRef.current);
      }
    };
  }, [sensorData, updateInterpolatedData]);
  
  // Memoized tile layer configuration
  const getCurrentTileLayer = useCallback(() => {
    if (mapStyle === 'satellite') {
      return mapStyles.satellite;
    } else {
      // For normal view, use dark or light based on settings.darkMode
      return settings.darkMode ? mapStyles.normal.dark : mapStyles.normal.light;
    }
  }, [mapStyle, settings.darkMode]);
  
  // Memoized map center and zoom calculation
  const mapCenterAndZoom = useMemo(() => {
    if (sensorData.length === 0) {
      return { center: [20.5937, 78.9629], zoom: 5 };
    }

    // Calculate center point of all sensors
    const lats = sensorData.map(s => s.lat);
    const lons = sensorData.map(s => s.lon);
    const avgLat = lats.reduce((sum, lat) => sum + lat, 0) / lats.length;
    const avgLon = lons.reduce((sum, lon) => sum + lon, 0) / lons.length;
    
    let zoom = 5;
    
    // Adjust zoom based on sensor spread
    if (sensorData.length > 1) {
      const latSpread = Math.max(...lats) - Math.min(...lats);
      const lonSpread = Math.max(...lons) - Math.min(...lons);
      const maxSpread = Math.max(latSpread, lonSpread);
      
      if (maxSpread < 0.01) zoom = 15;
      else if (maxSpread < 0.1) zoom = 12;
      else if (maxSpread < 1) zoom = 9;
      else zoom = 7;
    }

    return { center: [avgLat, avgLon], zoom };
  }, [sensorData]);
  
  // Update map center and zoom when calculated values change
  useEffect(() => {
    setMapCenter(mapCenterAndZoom.center);
    setMapZoom(mapCenterAndZoom.zoom);
  }, [mapCenterAndZoom]);

  // Memoized event handlers to prevent unnecessary re-renders
  const handleMapStyleChange = useCallback((style) => {
    setMapStyle(style);
  }, []);

  const handleToggleOverlay = useCallback((show) => {
    setShowOverlay(show);
  }, []);

  const handleOpacityChange = useCallback((opacity) => {
    setOverlayOpacity(opacity);
  }, []);

  // Memoized sensor markers to prevent unnecessary re-renders
  const sensorMarkers = useMemo(() => {
    return sensorData.map((sensor, index) => (
      <AnimatedMarker 
        key={sensor.device_id} 
        sensor={sensor} 
        index={index}
      />
    ));
  }, [sensorData]);

  return (
    <div className="noise-map-container">      
      {/* Settings Panel */}
      <SettingsPanel 
        settings={settings}
        onMapStyleChange={handleMapStyleChange}
        showOverlay={showOverlay}
        onToggleOverlay={handleToggleOverlay}
        overlayOpacity={overlayOpacity}
        onOpacityChange={handleOpacityChange}
      />
      
      {/* Live Sensor Stats */}
      <LiveSensorStats sensorData={sensorData} />
      
      {/* Main Map */}
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        attributionControl={true}
        className="noise-leaflet-map"
        ref={mapRef}
      >
        <TileLayer
          attribution={getCurrentTileLayer().attribution}
          url={getCurrentTileLayer().url}
        />
        
        {/* Noise Distribution Overlay */}
        {showOverlay && interpolatedData && (
          <NoiseMapOverlay
            interpolatedData={interpolatedData}
            opacity={overlayOpacity}
          />
        )}
        
        {/* Render sensor markers */}
        {sensorMarkers}
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

const MemoizedNoiseMap = React.memo(NoiseMap, (prevProps, nextProps) => {
  // Custom comparison to prevent unnecessary re-renders
  const sensorDataChanged = JSON.stringify(prevProps.sensorData) !== JSON.stringify(nextProps.sensorData);
  const connectionStatusChanged = prevProps.connectionStatus !== nextProps.connectionStatus;
  const settingsChanged = JSON.stringify(prevProps.settings) !== JSON.stringify(nextProps.settings);
  
  return !sensorDataChanged && !connectionStatusChanged && !settingsChanged;
});

export default MemoizedNoiseMap;
