import React, { useState, useEffect, useCallback } from 'react';
import NoiseMap from './components/NoiseMap';
import webSocketService from './mqtt/simpleWebSocketService';
import logoImage from './components/Smart Noise Monitoring System.png';
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

  // Show notification function
  const showNotification = useCallback((message, type = 'info') => {
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
  }, []);

  // MQTT message handler
  const handleMessage = useCallback((payload, messageType) => {
    try {
      // Handle different message types from WebSocket service
      if (messageType === 'sensor') {
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
          key: `${payload.device_id}_${Date.now()}`, // Add unique key
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
      } else if (messageType === 'interpolated') {
        // Handle interpolated data (noise map overlay)
        console.log('📈 Received interpolated data:', payload);
        // This will be handled by the NoiseMap component
      }

    } catch (error) {
      console.error('Error handling WebSocket message:', error);
      showNotification('Error processing sensor data', 'error');
    }
  }, [settings.showNotifications, showNotification]);

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

  // Initialize WebSocket connection
  useEffect(() => {
    const initConnection = async () => {
      try {
        setConnectionStatus('connecting');
        showNotification('Connecting to server...', 'info');
        
        await webSocketService.connect(handleMessage, (status) => {
          setConnectionStatus(status);
          if (status === 'connected') {
            showNotification('Connected to server!', 'success');
          } else if (status === 'error') {
            showNotification('Connection failed - Check if the server is running', 'error');
          } else if (status === 'disconnected') {
            showNotification('Disconnected from server - Attempting to reconnect...', 'warning');
          }
        });
      } catch (error) {
        console.error('Connection error:', error);
        setConnectionStatus('error');
        showNotification('Cannot connect to server. Make sure start_noise_system.py is running on the Pi', 'error');
      }
    };

    initConnection();

    // Cleanup on unmount
    return () => {
      webSocketService.disconnect();
    };
  }, [handleMessage, showNotification]);

  // Auto-refresh connection status
  useEffect(() => {
    if (!settings.autoRefresh) return;

    const interval = setInterval(() => {
      const status = webSocketService.getStatus();
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

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <div className="top-navbar-modern">
        <div className="navbar-brand">
          <div className="app-logo">
            <div className="logo-icon">
              <img src={logoImage} alt="Smart Noise Monitoring System" className="logo-image" />
            </div>
            <div className="brand-text">
              <h1 className="app-title">Echo Guard</h1>
              <span className="app-subtitle">Smart Noise Monitoring System</span>
            </div>
          </div>
        </div>
        
        <div className="navbar-actions">
          {/* Connection Status */}
          <div className={`connection-indicator status-${getConnectionStatusClass()}`}>
            <div className="connection-pulse"></div>
            <span className="connection-text">{connectionStatus}</span>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button 
              className="action-btn notification-btn"
              onClick={() => setNotificationCount(0)}
              title="Notifications"
            >
              <span className="btn-icon">🔔</span>
              {notificationCount > 0 && <span className="notification-dot">{notificationCount}</span>}
            </button>

            <button 
              className="action-btn settings-btn"
              onClick={() => setSettingsOpen(!settingsOpen)}
              title="Settings"
            >
              <span className="btn-icon">⚙️</span>
            </button>
          </div>
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