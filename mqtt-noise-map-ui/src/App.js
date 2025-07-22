import React, { useState, useEffect } from 'react';
import NoiseMap from './components/NoiseMap';
import { connect, disconnect, getConnectionStatus } from './mqtt/mqttService';
import './App.css';

function App() {
  const [sensorData, setSensorData] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const [settings, setSettings] = useState({
    showNotifications: true,
    autoRefresh: true,
    soundAlerts: false,
    darkMode: true,
  });
  const [appStats, setAppStats] = useState({
    totalSensors: 0,
    activeSensors: 0,
    avgNoiseLevel: 0,
    maxNoiseLevel: 0,
  });
  const [notifications, setNotifications] = useState([]);

  // MQTT message handler
  const handleMessage = (payload) => {
    try {
      // Validate payload structure
      if (!payload.device_id || payload.db === undefined || !payload.lat || !payload.lon) {
        console.warn('Invalid sensor payload:', payload);
        return;
      }

      const newReading = {
        ...payload,
        timestamp: payload.timestamp || Date.now(),
        db: parseFloat(payload.db),
        lat: parseFloat(payload.lat),
        lon: parseFloat(payload.lon),
      };

      // Update sensor data
      setSensorData(prevData => {
        const existingIndex = prevData.findIndex(sensor => sensor.device_id === newReading.device_id);
        let newData;
        
        if (existingIndex >= 0) {
          // Update existing sensor
          newData = [...prevData];
          newData[existingIndex] = { ...newData[existingIndex], ...newReading };
        } else {
          // Add new sensor
          newData = [...prevData, newReading];
          if (settings.showNotifications) {
            showNotification(`New sensor connected: ${newReading.device_id}`, 'info');
          }
        }

        // Update statistics
        updateStats(newData);
        
        return newData;
      });

      // Check for noise level alerts
      if (newReading.db > 85 && settings.showNotifications) {
        showNotification(`High noise level detected: ${newReading.db} dB at ${newReading.device_id}`, 'warning');
        setNotificationCount(prev => prev + 1);
      }

    } catch (error) {
      console.error('Error handling MQTT message:', error);
      showNotification('Error processing sensor data', 'error');
    }
  };

  // Update app statistics
  const updateStats = (data) => {
    if (data.length === 0) {
      setAppStats({
        totalSensors: 0,
        activeSensors: 0,
        avgNoiseLevel: 0,
        maxNoiseLevel: 0,
      });
      return;
    }

    const now = Date.now();
    const activeSensors = data.filter(sensor => (now - sensor.timestamp) < 30000); // Active in last 30 seconds
    const avgNoise = data.reduce((sum, sensor) => sum + sensor.db, 0) / data.length;
    const maxNoise = Math.max(...data.map(sensor => sensor.db));

    setAppStats({
      totalSensors: data.length,
      activeSensors: activeSensors.length,
      avgNoiseLevel: avgNoise,
      maxNoiseLevel: maxNoise,
    });
  };

  // Show notification function
  const showNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setNotifications(prev => [notification, ...prev].slice(0, 5)); // Keep only last 5
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  // Initialize MQTT connection
  useEffect(() => {
    const initConnection = async () => {
      try {
        setConnectionStatus('connecting');
        showNotification('Connecting to MQTT broker...', 'info');
        
        await connect(handleMessage, (status) => {
          setConnectionStatus(status);
          if (status === 'connected') {
            showNotification('Connected to MQTT broker!', 'success');
          } else if (status === 'error') {
            showNotification('Failed to connect to MQTT broker', 'error');
          }
        });
      } catch (error) {
        console.error('Connection error:', error);
        setConnectionStatus('error');
        showNotification('Connection failed: ' + error.message, 'error');
      }
    };

    initConnection();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, []);

  // Auto-refresh connection status
  useEffect(() => {
    if (!settings.autoRefresh) return;

    const interval = setInterval(() => {
      const status = getConnectionStatus();
      setConnectionStatus(status);
    }, 5000);

    return () => clearInterval(interval);
  }, [settings.autoRefresh]);

  const handleSettingsToggle = (setting) => {
    setSettings(prev => ({
      ...prev,
      [setting]: !prev[setting],
    }));
  };

  const getConnectionStatusClass = () => {
    switch (connectionStatus) {
      case 'connected': return 'success';
      case 'connecting': return 'warning';
      case 'disconnected': return 'secondary';
      case 'error': return 'error';
      default: return 'secondary';
    }
  };

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected': return '📶';
      case 'connecting': return '🔄';
      case 'disconnected': return '📴';
      case 'error': return '❌';
      default: return '📴';
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <div className="top-navbar glass">
        <div className="navbar-left">
          <h1 className="app-title">Noise Map Dashboard</h1>
        </div>
        
        <div className="navbar-center">
          <div className="stats-chips">
            <div className="chip chip-primary">
              {appStats.activeSensors}/{appStats.totalSensors} Active
            </div>
            <div className="chip">
              Avg: {appStats.avgNoiseLevel.toFixed(1)} dB
            </div>
            {appStats.maxNoiseLevel > 0 && (
              <div className={`chip ${appStats.maxNoiseLevel > 85 ? 'chip-error' : ''}`}>
                Max: {appStats.maxNoiseLevel.toFixed(1)} dB
              </div>
            )}
          </div>
        </div>

        <div className="navbar-right">
          {/* Connection Status */}
          <div className={`connection-status chip chip-${getConnectionStatusClass()}`}>
            <span className="connection-icon">{getConnectionIcon()}</span>
            {connectionStatus.toUpperCase()}
          </div>

          {/* Notifications */}
          <button 
            className="notification-btn btn btn-secondary"
            onClick={() => setNotificationCount(0)}
          >
            🔔 {notificationCount > 0 && <span className="notification-badge">{notificationCount}</span>}
          </button>

          {/* Settings */}
          <button 
            className="settings-btn btn btn-secondary"
            onClick={() => setSettingsOpen(!settingsOpen)}
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* Main Content - Map */}
      <div className="main-content">
        <NoiseMap 
          sensorData={sensorData}
          connectionStatus={connectionStatus}
          settings={settings}
        />
      </div>

      {/* Settings Sidebar */}
      {settingsOpen && (
        <div className="settings-sidebar glass animate-slideInRight">
          <div className="sidebar-header">
            <h3>⚙️ Settings</h3>
            <button 
              className="btn-close"
              onClick={() => setSettingsOpen(false)}
            >
              ✕
            </button>
          </div>
          
          <div className="sidebar-content">
            <div className="setting-section">
              <h4>Notifications</h4>
              <label className="setting-item">
                <input 
                  type="checkbox"
                  checked={settings.showNotifications}
                  onChange={() => handleSettingsToggle('showNotifications')}
                />
                <span>Show Notifications</span>
              </label>
              
              <label className="setting-item">
                <input 
                  type="checkbox"
                  checked={settings.soundAlerts}
                  onChange={() => handleSettingsToggle('soundAlerts')}
                />
                <span>Sound Alerts</span>
              </label>
            </div>
            
            <div className="setting-section">
              <h4>Connection</h4>
              <label className="setting-item">
                <input 
                  type="checkbox"
                  checked={settings.autoRefresh}
                  onChange={() => handleSettingsToggle('autoRefresh')}
                />
                <span>Auto Refresh</span>
              </label>
            </div>

            <div className="setting-section">
              <h4>Status</h4>
              <div className="status-info">
                <div className="status-row">
                  <span>Connection:</span>
                  <span className={`text-${getConnectionStatusClass()}`}>
                    {connectionStatus.toUpperCase()}
                  </span>
                </div>
                <div className="status-row">
                  <span>Total Sensors:</span>
                  <span>{appStats.totalSensors}</span>
                </div>
                <div className="status-row">
                  <span>Active Sensors:</span>
                  <span className="text-success">{appStats.activeSensors}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notification Panel */}
      {notifications.length > 0 && (
        <div className="notification-panel">
          {notifications.map(notification => (
            <div 
              key={notification.id}
              className={`notification toast toast-${notification.type} animate-fadeIn`}
            >
              <div className="notification-content">
                <div className="notification-message">{notification.message}</div>
                <div className="notification-time">{notification.timestamp}</div>
              </div>
              <button 
                className="notification-close"
                onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Loading Overlay */}
      {connectionStatus === 'connecting' && (
        <div className="loading-overlay">
          <div className="loading-message glass">
            <div className="spinner"></div>
            <h3>Connecting to MQTT Broker</h3>
            <p>Please wait while we establish connection...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;