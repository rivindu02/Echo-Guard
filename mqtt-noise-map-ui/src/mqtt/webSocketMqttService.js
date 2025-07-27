/**
 * WebSocket-based MQTT Service for React UI
 * Connects to the Python WebSocket server instead of direct MQTT
 */

// Configuration
const CONFIG = {
  // WebSocket URL with MQTT protocol path for Mosquitto
  WEBSOCKET_URL: 'ws://172.20.10.2:9001/mqtt',
  CLIENT_ID_PREFIX: 'noise_ui_',
  RECONNECT_DELAY: 5000,
  MAX_RECONNECT_ATTEMPTS: 10,
  HEARTBEAT_INTERVAL: 30000,
  CONNECTION_TIMEOUT: 30000
};

// Log the environment variable for debugging
console.log('Environment variable value:', process.env.REACT_APP_WEBSOCKET_URL);

console.log('🌐 WebSocket MQTT Service Config:', CONFIG);

class WebSocketMQTTService {
  constructor() {
    console.log('🌐 WebSocketMQTTService constructor called');
    this.websocket = null;
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    this.messageHandler = null;
    this.statusHandler = null;
    this.reconnectAttempts = 0;
    this.subscriptions = new Set();
    this.heartbeatInterval = null;
    this.reconnectTimeout = null;
    
    // Generate unique client ID
    this.clientId = CONFIG.CLIENT_ID_PREFIX + Math.random().toString(16).substr(2, 8);
    
    console.log('🌐 WebSocketMQTTService initialized:', this.clientId);
  }

  /**
   * Connect to WebSocket server
   * @param {Function} onMessage - Callback function for incoming messages
   * @param {Function} onStatusChange - Callback function for connection status changes
   */
  async connect(onMessage, onStatusChange) {
    console.log('🌐 WebSocket connect() called');
    
    return new Promise((resolve, reject) => {
      try {
        this.messageHandler = onMessage;
        this.statusHandler = onStatusChange;

        console.log(`🔌 Connecting to WebSocket server: ${CONFIG.WEBSOCKET_URL}`);
        console.log(`📡 Client ID: ${this.clientId}`);

        // Set connection timeout
        const connectionTimeout = setTimeout(() => {
          if (this.websocket && this.websocket.readyState !== WebSocket.OPEN) {
            console.error('❌ WebSocket connection timeout');
            this.websocket.close();
            reject(new Error('Connection timeout'));
          }
        }, CONFIG.CONNECTION_TIMEOUT);

        // Create WebSocket connection with error handling
        try {
          this.websocket = new WebSocket(CONFIG.WEBSOCKET_URL);
        } catch (error) {
          console.error('❌ Failed to create WebSocket:', error);
          clearTimeout(connectionTimeout);
          reject(error);
          return;
        }

        // Set up error handler first
        this.websocket.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.handleDisconnection();
        };

        // Set up event handlers
        this.websocket.onopen = (event) => {
          console.log('✅ WebSocket connected');
          this.isConnected = true;
          this.connectionStatus = 'connected';
          this.reconnectAttempts = 0;
          
          // Start heartbeat
          this.startHeartbeat();
          
          // Request current data
          this.sendMessage({
            type: 'get_current_data'
          });
          
          // Notify status change
          if (this.statusHandler) {
            this.statusHandler('connected');
          }
          
          resolve();
        };

        this.websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
          }
        };

        this.websocket.onclose = (event) => {
          console.log('❌ WebSocket disconnected:', event.code, event.reason);
          this.handleDisconnection();
        };

        this.websocket.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.connectionStatus = 'error';
          if (this.statusHandler) {
            this.statusHandler('error');
          }
          reject(error);
        };

        // Set connection timeout
        setTimeout(() => {
          if (this.connectionStatus !== 'connected') {
            console.error('❌ WebSocket connection timeout');
            this.websocket.close();
            reject(new Error('Connection timeout'));
          }
        }, 10000);

      } catch (error) {
        console.error('❌ Error in WebSocket connect:', error);
        reject(error);
      }
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(data) {
    console.log('📨 WebSocket message received:', data);

    if (data.type === 'mqtt_message') {
      // Handle MQTT messages forwarded from the broker
      this.processMQTTMessage(data.topic, data.payload);
    } else if (data.type === 'sensor_data') {
      // Handle current sensor data
      this.processSensorData(data.payload);
    } else {
      console.log('🔍 Unknown message type:', data.type);
    }
  }

  /**
   * Process MQTT messages forwarded from the Python broker
   */
  processMQTTMessage(topic, payload) {
    console.log(`📤 Processing MQTT message - Topic: ${topic}`, payload);

    if (this.messageHandler) {
      // Handle sensor data
      if (topic.startsWith('noise/esp32/') || topic.startsWith('noise/')) {
        if (payload.device_id && payload.lat && payload.lon && payload.db) {
          this.messageHandler(payload, 'sensor');
        }
      }
      
      // Handle processed interpolation data
      else if (topic === 'noise/processed') {
        this.messageHandler(payload, 'interpolated');
      }
    }
  }

  /**
   * Process current sensor data
   */
  processSensorData(sensorArray) {
    console.log(`📊 Processing current sensor data: ${sensorArray.length} sensors`);
    
    if (this.messageHandler && Array.isArray(sensorArray)) {
      sensorArray.forEach(sensor => {
        if (sensor.device_id && sensor.lat && sensor.lon && sensor.db) {
          this.messageHandler(sensor, 'sensor');
        }
      });
    }
  }

  /**
   * Handle WebSocket disconnection
   */
  handleDisconnection() {
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    
    // Stop heartbeat
    this.stopHeartbeat();
    
    // Notify status change
    if (this.statusHandler) {
      this.statusHandler('disconnected');
    }
    
    // Attempt reconnection
    this.attemptReconnection();
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  attemptReconnection() {
    if (this.reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) {
      console.error('❌ Max reconnection attempts reached');
      if (this.statusHandler) {
        this.statusHandler('error');
      }
      return;
    }

    this.reconnectAttempts++;
    console.log(`🔄 Attempting reconnection ${this.reconnectAttempts}/${CONFIG.MAX_RECONNECT_ATTEMPTS}...`);
    
    if (this.statusHandler) {
      this.statusHandler('connecting');
    }

    this.reconnectTimeout = setTimeout(() => {
      this.connect(this.messageHandler, this.statusHandler)
        .catch(error => {
          console.error('❌ Reconnection failed:', error);
          this.attemptReconnection();
        });
    }, CONFIG.RECONNECT_DELAY);
  }

  /**
   * Send message to WebSocket server
   */
  sendMessage(message) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
    }
  }

  /**
   * Start heartbeat to keep connection alive
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.sendMessage({
        type: 'ping',
        timestamp: Date.now()
      });
    }, CONFIG.HEARTBEAT_INTERVAL);
  }

  /**
   * Stop heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Subscribe to a topic (for compatibility)
   */
  subscribe(topic) {
    console.log(`📡 Subscribing to topic: ${topic}`);
    this.subscriptions.add(topic);
    
    this.sendMessage({
      type: 'subscribe',
      topic: topic
    });
  }

  /**
   * Publish a message (for compatibility)
   */
  publish(topic, payload) {
    console.log(`📤 Publishing to topic: ${topic}`, payload);
    
    this.sendMessage({
      type: 'publish',
      topic: topic,
      payload: payload
    });
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    console.log('🔌 Disconnecting WebSocket...');
    
    this.stopHeartbeat();
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    this.reconnectAttempts = 0;
  }

  /**
   * Get connection status
   */
  getStatus() {
    return this.connectionStatus;
  }

  /**
   * Check if connected
   */
  isConnectedStatus() {
    return this.isConnected;
  }
}

// Create and export service instance
const webSocketMQTTService = new WebSocketMQTTService();

export default webSocketMQTTService;
