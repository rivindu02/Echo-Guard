import mqtt from 'mqtt';

const CONFIG = {
  // Use WSS for production, WS for development
  MQTT_URL: 'ws://172.20.10.2:9001',
  CLIENT_ID: `noise_ui_${Math.random().toString(16).substr(2, 8)}`,
  TOPICS: ['noise/#'],
  // MQTT protocol configuration
  CONNECT_OPTIONS: {
    clientId: `noise_ui_${Math.random().toString(16).substr(2, 8)}`,
    clean: true,
    keepalive: 30,
    protocolVersion: 4,
    reconnectPeriod: 1000,
    connectTimeout: 30 * 1000,
    will: {
      topic: 'noise/clients',
      payload: JSON.stringify({ status: 'disconnected' }),
      qos: 0,
      retain: false
    }
  }
};

class DirectMQTTService {
  constructor() {
    this.client = null;
    this.isConnected = false;
    this.handlers = {
      message: null,
      status: null
    };
  }

  connect(onMessage, onStatus) {
    return new Promise((resolve, reject) => {
      try {
        console.log('📡 Connecting to MQTT broker:', CONFIG.MQTT_URL);
        
        this.handlers = { message: onMessage, status: onStatus };
        
        // Create MQTT client with configured options
        this.client = mqtt.connect(CONFIG.MQTT_URL, {
          ...CONFIG.CONNECT_OPTIONS,
          // Override clientId to ensure uniqueness
          clientId: `noise_ui_${Math.random().toString(16).substr(2, 8)}`
        });

        this.client.on('connect', () => {
          console.log('✅ Connected to MQTT broker');
          this.isConnected = true;
          onStatus?.('connected');

          // Subscribe to topics
          CONFIG.TOPICS.forEach(topic => {
            this.client.subscribe(topic, (err) => {
              if (err) {
                console.error('❌ Failed to subscribe to', topic, err);
              } else {
                console.log('📩 Subscribed to', topic);
              }
            });
          });

          resolve();
        });

        this.client.on('message', (topic, message) => {
          try {
            const payload = JSON.parse(message.toString());
            console.log('📨 Received:', topic, payload);
            onMessage?.(payload, 'sensor');
          } catch (error) {
            console.error('❌ Failed to parse message:', error);
          }
        });

        this.client.on('error', (error) => {
          console.error('❌ MQTT Error:', error);
          onStatus?.('error');
        });

        this.client.on('close', () => {
          console.log('🔌 Disconnected from MQTT broker');
          this.isConnected = false;
          onStatus?.('disconnected');
        });

        this.client.on('reconnect', () => {
          console.log('🔄 Reconnecting...');
          onStatus?.('connecting');
        });

      } catch (error) {
        console.error('❌ Failed to connect:', error);
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.client) {
      this.client.end();
      this.client = null;
      this.isConnected = false;
    }
  }

  publish(topic, message) {
    if (this.client && this.isConnected) {
      this.client.publish(topic, JSON.stringify(message));
    }
  }

  getStatus() {
    return this.isConnected ? 'connected' : 'disconnected';
  }
}

const mqttService = new DirectMQTTService();
export default mqttService;
