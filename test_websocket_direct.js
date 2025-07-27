// Simple WebSocket test to debug connection to Pi
const WebSocket = require('ws');

const PI_WEBSOCKET_URL = 'ws://192.168.1.12:9001';

console.log(`🔌 Testing WebSocket connection to: ${PI_WEBSOCKET_URL}`);

const ws = new WebSocket(PI_WEBSOCKET_URL, {
  timeout: 5000,  // 5 second timeout
  perMessageDeflate: false
});

let connectionAttempted = false;

ws.on('open', function open() {
  console.log('✅ WebSocket connection established!');
  connectionAttempted = true;
  
  // Request current data
  const message = {
    type: 'get_current_data',
    timestamp: Date.now()
  };
  
  console.log('📤 Sending request for current data...');
  ws.send(JSON.stringify(message));
});

ws.on('message', function message(data) {
  try {
    const parsed = JSON.parse(data);
    console.log('📥 Received message:', JSON.stringify(parsed, null, 2));
  } catch (error) {
    console.log('📥 Received raw message:', data.toString());
  }
});

ws.on('close', function close(code, reason) {
  console.log(`❌ WebSocket closed: ${code} - ${reason.toString()}`);
  if (!connectionAttempted) {
    console.log('💡 Connection never opened - possible handshake failure');
  }
});

ws.on('error', function error(err) {
  console.error('❌ WebSocket error:', err);
  console.error('❌ Error details:', {
    message: err.message,
    code: err.code,
    errno: err.errno,
    syscall: err.syscall,
    address: err.address,
    port: err.port
  });
});

// Keep the script running for 10 seconds
setTimeout(() => {
  if (!connectionAttempted) {
    console.log('⏰ Timeout: Connection not established after 10 seconds');
  }
  console.log('🛑 Closing test connection...');
  ws.close();
  process.exit(0);
}, 10000);
