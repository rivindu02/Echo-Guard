/**
 * Simple WebSocket service - no MQTT.js, just direct WebSocket
 */

const CONFIG = {
  WEBSOCKET_URL: 'ws://172.20.10.2:9001',
  RECONNECT_DELAY: 3000,
  MAX_RECONNECT_ATTEMPTS: 10
};

class SimpleWebSocketService {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.messageHandler = null;
    this.statusHandler = null;
  }

  connect(onMessage, onStatus) {
    return new Promise((resolve, reject) => {
      try {
        console.log('🔌 Connecting to:', CONFIG.WEBSOCKET_URL);
        
        this.messageHandler = onMessage;
        this.statusHandler = onStatus;
        
        this.ws = new WebSocket(CONFIG.WEBSOCKET_URL);
        
        this.ws.onopen = () => {
          console.log('✅ WebSocket connected!');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          onStatus?.('connected');
          
          // Send a simple ping to confirm connection
          this.ws.send(JSON.stringify({ type: 'ping' }));
          
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            console.log('📨 Raw message:', event.data);
            
            // Try to parse as JSON first
            let data;
            try {
              data = JSON.parse(event.data);
            } catch {
              // If not JSON, treat as raw data
              data = { raw: event.data };
            }
            
            console.log('📨 Parsed message:', data);
            
            // Call the message handler
            if (onMessage && data) {
              onMessage(data, 'sensor');
            }
          } catch (error) {
            console.error('❌ Error handling message:', error);
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          onStatus?.('error');
        };
        
        this.ws.onclose = () => {
          console.log('🔌 WebSocket closed');
          this.isConnected = false;
          onStatus?.('disconnected');
          this.attemptReconnect();
        };
        
      } catch (error) {
        console.error('❌ Connection failed:', error);
        reject(error);
      }
    });
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) {
      console.error('❌ Max reconnection attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${CONFIG.MAX_RECONNECT_ATTEMPTS})`);
    
    setTimeout(() => {
      this.connect(this.messageHandler, this.statusHandler)
        .catch(() => this.attemptReconnect());
    }, CONFIG.RECONNECT_DELAY);
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }
  
  send(data) {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(data));
    }
  }
  
  getStatus() {
    return this.isConnected ? 'connected' : 'disconnected';
  }
}

const webSocketService = new SimpleWebSocketService();
export default webSocketService;
