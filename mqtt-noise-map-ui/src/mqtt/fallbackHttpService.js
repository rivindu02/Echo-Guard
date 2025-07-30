/**
 * HTTP Fallback Service for React UI
 * Provides HTTP REST API fallback when WebSocket connection fails
 */

// Configuration
const CONFIG = {
  // HTTP Fallback service is disabled since we're using WebSocket directly
  HTTP_API_URL: null,
  POLL_INTERVAL: 5000, // 5 seconds
  REQUEST_TIMEOUT: 10000, // 10 seconds
  MAX_RETRIES: 3
};

console.log('🌐 HTTP Fallback Service Config:', CONFIG);

class FallbackHTTPService {
  constructor() {
    console.log('🌐 FallbackHTTPService constructor called');
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    this.messageHandler = null;
    this.statusHandler = null;
    this.pollInterval = null;
    this.retryCount = 0;
    this.connectionInfo = {
      type: 'http',
      url: CONFIG.HTTP_API_URL,
      status: this.connectionStatus
    };
    
    console.log('🌐 FallbackHTTPService initialized');
  }

  getConnectionInfo() {
    return {
      ...this.connectionInfo,
      status: this.connectionStatus
    };
  }

  /**
   * Connect to HTTP API server
   * @param {Function} onMessage - Callback function for incoming messages
   * @param {Function} onStatusChange - Callback function for connection status changes
   */
  async connect(onMessage, onStatusChange) {
    console.log('🌐 HTTP Fallback connect() called');
    
    return new Promise(async (resolve, reject) => {
      console.log('⚠️ HTTP Fallback service is disabled');
      reject(new Error('HTTP Fallback service is disabled. Please use WebSocket connection.'));
        
        try {
          await this.makeRequest(testUrl);
          console.log('✅ HTTP API connected');
          this.isConnected = true;
          this.connectionStatus = 'connected';
          this.retryCount = 0;
          
          // Start polling for data
          this.startPolling();
          
          // Notify status change
          if (this.statusHandler) {
            this.statusHandler('connected');
          }
          
          resolve();
        } catch (error) {
          console.error('❌ HTTP API connection failed:', error);
          this.isConnected = false;
          this.connectionStatus = 'error';
          
          if (this.statusHandler) {
            this.statusHandler('error', error.message);
          }
          
          reject(error);
        }
      } catch (error) {
        console.error('❌ HTTP Fallback connection error:', error);
        reject(error);
      }
    });
  }

  /**
   * Make HTTP request with timeout and retry logic
   */
  async makeRequest(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Start polling for sensor data
   */
  startPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }

    this.pollInterval = setInterval(async () => {
      try {
        await this.fetchCurrentData();
      } catch (error) {
        console.error('❌ Polling error:', error);
        this.handleConnectionError(error);
      }
    }, CONFIG.POLL_INTERVAL);

    // Initial fetch
    this.fetchCurrentData();
  }

  /**
   * Fetch current sensor data
   */
  async fetchCurrentData() {
    try {
      const url = `${CONFIG.HTTP_API_URL}/api/sensors/current`;
      const data = await this.makeRequest(url);
      
      if (this.messageHandler && data) {
        // Format data to match WebSocket format
        const formattedData = {
          type: 'sensor_data',
          data: data,
          timestamp: Date.now()
        };
        
        this.messageHandler(formattedData);
      }
    } catch (error) {
      console.error('❌ Failed to fetch current data:', error);
      throw error;
    }
  }

  /**
   * Handle connection errors
   */
  handleConnectionError(error) {
    this.retryCount++;
    
    if (this.retryCount >= CONFIG.MAX_RETRIES) {
      console.error('❌ Max retries reached, disconnecting');
      this.disconnect();
      
      if (this.statusHandler) {
        this.statusHandler('error', 'Max retries reached');
      }
    } else {
      console.log(`🔄 Retrying connection (${this.retryCount}/${CONFIG.MAX_RETRIES})`);
      
      if (this.statusHandler) {
        this.statusHandler('reconnecting');
      }
    }
  }

  /**
   * Disconnect from the service
   */
  disconnect() {
    console.log('🔌 HTTP Fallback disconnecting...');
    
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    
    if (this.statusHandler) {
      this.statusHandler('disconnected');
    }
  }

  /**
   * Get current connection status
   */
  getConnectionStatus() {
    return this.connectionStatus;
  }

  /**
   * Check if connected
   */
  isServiceConnected() {
    return this.isConnected;
  }

  /**
   * Subscribe to topics (HTTP doesn't support subscriptions, so this is a no-op)
   */
  subscribe(topic) {
    console.log(`📝 HTTP Fallback: Subscribe to ${topic} (no-op for HTTP)`);
  }

  /**
   * Unsubscribe from topics (HTTP doesn't support subscriptions, so this is a no-op)
   */
  unsubscribe(topic) {
    console.log(`📝 HTTP Fallback: Unsubscribe from ${topic} (no-op for HTTP)`);
  }

  /**
   * Send message (HTTP doesn't support real-time messaging, so this logs the attempt)
   */
  sendMessage(message) {
    console.log(`📤 HTTP Fallback: Send message (not supported)`, message);
  }
}

// Export the class, not an instance (consistent with other services)
export default FallbackHTTPService;
