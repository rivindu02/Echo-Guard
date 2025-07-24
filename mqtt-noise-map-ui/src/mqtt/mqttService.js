import mqtt from 'precompiled-mqtt';

// Configuration
const CONFIG = {
  // Read from environment or use defaults
  BROKER_URL: process.env.REACT_APP_MQTT_BROKER_URL || 'ws://localhost:9001',
  TOPIC_PREFIX: process.env.REACT_APP_MQTT_TOPIC_PREFIX || 'noise',
  CLIENT_ID_PREFIX: 'noise_ui_',
  RECONNECT_PERIOD: 3000,
  KEEPALIVE: 60,
  QOS: 0,
  CONNECTION_TIMEOUT: 30000,
  MAX_RECONNECT_ATTEMPTS: 10
};

class MQTTService {
  constructor() {
    this.client = null;
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    this.messageHandler = null;
    this.statusHandler = null;
    this.reconnectAttempts = 0;
    this.subscriptions = new Set();
  }

  /**
   * Connect to MQTT broker
   * @param {Function} onMessage - Callback function for incoming messages
   * @param {Function} onStatusChange - Callback function for connection status changes
   */
  async connect(onMessage, onStatusChange) {
    return new Promise((resolve, reject) => {
      try {
        this.messageHandler = onMessage;
        this.statusHandler = onStatusChange;

        // Generate unique client ID
        const clientId = CONFIG.CLIENT_ID_PREFIX + Math.random().toString(16).substr(2, 8);
        
        console.log(`🔌 Connecting to MQTT broker: ${CONFIG.BROKER_URL}`);
        console.log(`📡 Client ID: ${clientId}`);

        const options = {
          clientId: clientId,
          keepalive: CONFIG.KEEPALIVE,
          reconnectPeriod: CONFIG.RECONNECT_PERIOD,
          connectTimeout: CONFIG.CONNECTION_TIMEOUT,
          clean: true,
          will: {
            topic: `${CONFIG.TOPIC_PREFIX}/client/status`,
            payload: JSON.stringify({
              client_id: clientId,
              status: 'offline',
              timestamp: Date.now()
            }),
            retain: true,
            qos: 1
          }
        };

        // Create MQTT client
        this.client = mqtt.connect(CONFIG.BROKER_URL, options);

        // Connection successful
        this.client.on('connect', () => {
          console.log('✅ MQTT Connected successfully');
          this.isConnected = true;
          this.connectionStatus = 'connected';
          this.reconnectAttempts = 0;
          
          // Subscribe to noise sensor topics
          this.subscribeToTopics();
          
          // Publish client online status
          this.publishClientStatus('online');
          
          if (this.statusHandler) {
            this.statusHandler('connected');
          }
          
          resolve();
        });

        // Handle incoming messages
        this.client.on('message', (topic, message) => {
          try {
            const messageStr = message.toString();
            console.log(`📨 Received message on ${topic}:`, messageStr);
            
            // Parse JSON payload
            const payload = JSON.parse(messageStr);
            
            // Validate payload structure
            if (this.validatePayload(payload)) {
              if (this.messageHandler) {
                this.messageHandler(payload);
              }
            } else {
              console.warn('⚠️ Invalid payload structure:', payload);
            }
          } catch (error) {
            console.error('❌ Error parsing MQTT message:', error);
          }
        });

        // Handle connection errors
        this.client.on('error', (error) => {
          console.error('❌ MQTT Connection error:', error);
          this.connectionStatus = 'error';
          this.isConnected = false;
          
          if (this.statusHandler) {
            this.statusHandler('error');
          }
          
          if (this.reconnectAttempts === 0) {
            reject(error);
          }
        });

        // Handle disconnection
        this.client.on('close', () => {
          console.log('🔌 MQTT Connection closed');
          this.isConnected = false;
          this.connectionStatus = 'disconnected';
          
          if (this.statusHandler) {
            this.statusHandler('disconnected');
          }
        });

        // Handle reconnection attempts
        this.client.on('reconnect', () => {
          this.reconnectAttempts++;
          console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${CONFIG.MAX_RECONNECT_ATTEMPTS})...`);
          this.connectionStatus = 'connecting';
          
          if (this.statusHandler) {
            this.statusHandler('connecting');
          }

          // Stop reconnecting after max attempts
          if (this.reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) {
            console.error('❌ Max reconnection attempts reached');
            this.client.end(true);
            this.connectionStatus = 'error';
            
            if (this.statusHandler) {
              this.statusHandler('error');
            }
          }
        });

        // Handle offline status
        this.client.on('offline', () => {
          console.log('📴 MQTT Client offline');
          this.isConnected = false;
          this.connectionStatus = 'disconnected';
          
          if (this.statusHandler) {
            this.statusHandler('disconnected');
          }
        });

      } catch (error) {
        console.error('❌ Failed to create MQTT client:', error);
        reject(error);
      }
    });
  }

  /**
   * Subscribe to noise sensor topics
   */
  subscribeToTopics() {
    const topics = [
      `${CONFIG.TOPIC_PREFIX}/+/data`,     // noise/esp32-001/data
      `${CONFIG.TOPIC_PREFIX}/+`,          // noise/esp32-001 (legacy format)
      `${CONFIG.TOPIC_PREFIX}/sensor/+`,   // noise/sensor/esp32-001
      `${CONFIG.TOPIC_PREFIX}/device/+`,   // noise/device/esp32-001
    ];

    topics.forEach(topic => {
      this.client.subscribe(topic, { qos: CONFIG.QOS }, (error) => {
        if (error) {
          console.error(`❌ Failed to subscribe to ${topic}:`, error);
        } else {
          console.log(`📡 Subscribed to topic: ${topic}`);
          this.subscriptions.add(topic);
        }
      });
    });
  }

  /**
   * Validate incoming payload structure
   * @param {Object} payload - The payload to validate
   * @returns {boolean} - True if payload is valid
   */
  validatePayload(payload) {
    // Check required fields
    const requiredFields = ['device_id', 'db', 'lat', 'lon'];
    const hasRequiredFields = requiredFields.every(field => payload.hasOwnProperty(field));
    
    if (!hasRequiredFields) {
      return false;
    }

    // Validate data types
    if (typeof payload.device_id !== 'string' ||
        typeof payload.db !== 'number' ||
        typeof payload.lat !== 'number' ||
        typeof payload.lon !== 'number') {
      return false;
    }

    // Validate ranges
    if (payload.db < 0 || payload.db > 200 ||
        payload.lat < -90 || payload.lat > 90 ||
        payload.lon < -180 || payload.lon > 180) {
      return false;
    }

    return true;
  }

  /**
   * Publish client status
   * @param {string} status - online/offline
   */
  publishClientStatus(status) {
    if (!this.client || !this.isConnected) return;

    const statusMessage = {
      client_id: this.client.options.clientId,
      status: status,
      timestamp: Date.now(),
      subscriptions: Array.from(this.subscriptions)
    };

    this.client.publish(
      `${CONFIG.TOPIC_PREFIX}/client/status`,
      JSON.stringify(statusMessage),
      { retain: true, qos: 1 }
    );
  }

  /**
   * Publish a test message (for debugging)
   * @param {Object} testData - Test sensor data
   */
  publishTestMessage(testData) {
    if (!this.client || !this.isConnected) {
      console.warn('⚠️ Cannot publish: MQTT not connected');
      return;
    }

    const topic = `${CONFIG.TOPIC_PREFIX}/${testData.device_id}/data`;
    this.client.publish(topic, JSON.stringify(testData), { qos: CONFIG.QOS });
    console.log(`📤 Published test message to ${topic}:`, testData);
  }

  /**
   * Disconnect from MQTT broker
   */
  disconnect() {
    if (this.client) {
      console.log('🔌 Disconnecting from MQTT broker...');
      
      // Publish offline status
      this.publishClientStatus('offline');
      
      // Close connection
      this.client.end(true);
      this.client = null;
      this.isConnected = false;
      this.connectionStatus = 'disconnected';
      this.subscriptions.clear();
      
      console.log('✅ MQTT Disconnected');
    }
  }

  /**
   * Get current connection status
   * @returns {string} - Connection status
   */
  getConnectionStatus() {
    return this.connectionStatus;
  }

  /**
   * Check if currently connected
   * @returns {boolean} - True if connected
   */
  isClientConnected() {
    return this.isConnected && this.client && this.client.connected;
  }

  /**
   * Get client information
   * @returns {Object} - Client info
   */
  getClientInfo() {
    return {
      isConnected: this.isConnected,
      connectionStatus: this.connectionStatus,
      reconnectAttempts: this.reconnectAttempts,
      subscriptions: Array.from(this.subscriptions),
      clientId: this.client ? this.client.options.clientId : null,
      brokerUrl: CONFIG.BROKER_URL
    };
  }

  /**
   * Manually trigger reconnection
   */
  reconnect() {
    if (this.client) {
      console.log('🔄 Manual reconnection triggered');
      this.client.reconnect();
    }
  }
}

// Create singleton instance
const mqttService = new MQTTService();

// Export functions for easier usage
export const connect = (onMessage, onStatusChange) => 
  mqttService.connect(onMessage, onStatusChange);

export const disconnect = () => 
  mqttService.disconnect();

export const getConnectionStatus = () => 
  mqttService.getConnectionStatus();

export const isConnected = () => 
  mqttService.isClientConnected();

export const getClientInfo = () => 
  mqttService.getClientInfo();

export const publishTestMessage = (testData) => 
  mqttService.publishTestMessage(testData);

export const reconnect = () => 
  mqttService.reconnect();

export default mqttService;


// import mqtt from 'precompiled-mqtt';

// const BROKER_URL = 'ws://YOUR_PI_IP:9001';

// class EnhancedMQTTService {
//   constructor() {
//     this.client = null;
//     this.onDataCallback = null;
//     this.onInterpolatedDataCallback = null;
//   }

//   connect(onDataCallback, onInterpolatedDataCallback) {
//     this.onDataCallback = onDataCallback;
//     this.onInterpolatedDataCallback = onInterpolatedDataCallback;
    
//     this.client = mqtt.connect(BROKER_URL);
    
//     this.client.on('connect', () => {
//       console.log('Connected to MQTT broker');
//       // Subscribe to both raw sensor data and processed interpolated data
//       this.client.subscribe('noise/+');
//       this.client.subscribe('noise/processed');
//     });

//     this.client.on('message', (topic, message) => {
//       try {
//         const payload = JSON.parse(message.toString());
        
//         if (topic === 'noise/processed') {
//           // Handle interpolated data
//           if (this.onInterpolatedDataCallback) {
//             this.onInterpolatedDataCallback(payload);
//           }
//         } else if (topic.startsWith('noise/') && topic !== 'noise/processed') {
//           // Handle raw sensor data
//           if (this.onDataCallback) {
//             this.onDataCallback(payload);
//           }
//         }
//       } catch (err) {
//         console.error('Error parsing MQTT message:', err);
//       }
//     });
//   }

//   disconnect() {
//     if (this.client) {
//       this.client.end();
//     }
//   }
// }

// export default new EnhancedMQTTService();
