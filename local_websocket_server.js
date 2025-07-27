#!/usr/bin/env node

/**
 * Local WebSocket Server for Testing
 * Simulates Pi WebSocket server responses
 */

const WebSocket = require('ws');
const http = require('http');

const PORT = 9001;

// Create HTTP server
const server = http.createServer();

// Create WebSocket server
const wss = new WebSocket.Server({ server });

console.log(`🚀 Starting local WebSocket server on port ${PORT}`);

// Sample noise data
const sampleDevices = [
  {
    device_id: 'esp32-001',
    lat: 6.7964,
    lon: 79.9012,
    db: 45.5,
    timestamp: Date.now(),
    location: 'ENTC'
  },
  {
    device_id: 'esp32-002',
    lat: 6.7960,
    lon: 79.9010,
    db: 72.3,
    timestamp: Date.now(),
    location: 'Landscape'
  },
  {
    device_id: 'esp32-003',
    lat: 6.7964,
    lon: 79.9007,
    db: 89.1,
    timestamp: Date.now(),
    location: 'Sentra-court'
  }
];

wss.on('connection', function connection(ws, req) {
  console.log(`✅ New WebSocket connection from ${req.socket.remoteAddress}`);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connection_status',
    status: 'connected',
    message: 'Connected to local test server',
    timestamp: Date.now()
  }));

  // Handle incoming messages
  ws.on('message', function incoming(message) {
    try {
      const data = JSON.parse(message);
      console.log('📨 Received:', data);

      // Handle different message types
      switch (data.type) {
        case 'get_current_data':
          // Send current device data
          sampleDevices.forEach(device => {
            ws.send(JSON.stringify({
              type: 'noise_data',
              data: {
                ...device,
                db: device.db + (Math.random() - 0.5) * 10, // Add some variation
                timestamp: Date.now()
              }
            }));
          });
          break;

        case 'subscribe':
          console.log(`📡 Client subscribed to: ${data.topic}`);
          break;

        default:
          console.log('❓ Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('❌ Error parsing message:', error);
    }
  });

  // Send periodic updates
  const updateInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      // Pick a random device and send update
      const device = sampleDevices[Math.floor(Math.random() * sampleDevices.length)];
      const noiseLevel = Math.max(30, Math.min(120, device.db + (Math.random() - 0.5) * 20));
      
      ws.send(JSON.stringify({
        type: 'noise_data',
        data: {
          ...device,
          db: Math.round(noiseLevel * 10) / 10,
          timestamp: Date.now()
        }
      }));
    }
  }, 3000); // Send update every 3 seconds

  ws.on('close', function close() {
    console.log('❌ WebSocket connection closed');
    clearInterval(updateInterval);
  });

  ws.on('error', function error(err) {
    console.error('❌ WebSocket error:', err);
    clearInterval(updateInterval);
  });
});

server.listen(PORT, function listening() {
  console.log(`🌐 Local WebSocket server listening on port ${PORT}`);
  console.log(`📱 React app should connect to: ws://localhost:${PORT}`);
});
