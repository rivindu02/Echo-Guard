# 🔧 API Reference

## WebSocket API

### Connection
- **URL:** `ws://[PI_IP]:9001`
- **Protocol:** WebSocket (RFC 6455)
- **Format:** JSON messages

### Client Connection Flow
```javascript
// 1. Connect to WebSocket
const ws = new WebSocket('ws://172.20.10.2:9001');

// 2. Handle connection events
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => handleMessage(JSON.parse(event.data));
ws.onerror = (error) => console.error('Error:', error);
ws.onclose = () => console.log('Disconnected');
```

## Message Types

### 1. Welcome Message (Server → Client)
```json
{
  "type": "welcome",
  "message": "Connected to noise monitoring system"
}
```

### 2. Sensor Data (Server → Client)
```json
{
  "topic": "noise/esp32/esp32-001",
  "payload": {
    "device_id": "esp32-001",
    "lat": 6.796436814894777,
    "lon": 79.90115269520993,
    "db": 45.7,
    "timestamp": 1753645869497
  }
}
```

### 3. Echo Response (Server → Client)
```json
{
  "type": "echo",
  "data": {
    // Original client message data
  }
}
```

### 4. Ping (Client → Server)
```json
{
  "type": "ping",
  "timestamp": 1753645869497
}
```

## MQTT Topics

### Sensor Data Topics
- **Pattern:** `noise/esp32/{device_id}`
- **Example:** `noise/esp32/esp32-001`
- **QoS:** 0
- **Retain:** false

### Topic Structure
```
noise/
├── esp32/
│   ├── esp32-001      # Individual sensor data
│   ├── esp32-002
│   └── esp32-xxx
└── processed/         # Future: Processed/aggregated data
```

## Data Validation

### Sensor Data Validation
```javascript
function validateSensorData(payload) {
  return (
    payload.device_id &&           // Required: string
    typeof payload.lat === 'number' &&    // Required: number
    typeof payload.lon === 'number' &&    // Required: number
    typeof payload.db === 'number' &&     // Required: number
    payload.db >= 0 && payload.db <= 140  // Valid dB range
  );
}
```

### Coordinate Validation
```javascript
function validateCoordinates(lat, lon) {
  return (
    lat >= -90 && lat <= 90 &&     // Valid latitude
    lon >= -180 && lon <= 180      // Valid longitude
  );
}
```

## Error Codes

### WebSocket Errors
- **1000:** Normal closure
- **1001:** Going away (server shutdown)
- **1002:** Protocol error
- **1003:** Unsupported data type
- **1006:** Abnormal closure (network issue)

### Custom Error Messages
```json
{
  "type": "error",
  "code": "INVALID_DATA",
  "message": "Sensor data validation failed",
  "timestamp": 1753645869497
}
```

## Rate Limiting

### Current Limits
- **WebSocket connections:** No limit (development)
- **Message rate:** No limit (development)
- **Sensor data frequency:** 1-10 seconds per device

### Recommended Production Limits
- **Max connections per IP:** 10
- **Messages per second:** 100
- **Connection attempts per minute:** 60

## JavaScript Client Library

### Simple WebSocket Service
```javascript
class NoiseMonitoringClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.handlers = {};
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('✅ Connected to noise monitoring system');
        resolve();
      };
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };
      
      this.ws.onerror = reject;
    });
  }

  handleMessage(data) {
    if (data.type === 'welcome') {
      console.log('📡', data.message);
    } else if (data.topic && data.payload) {
      this.handlers.sensorData?.(data.payload);
    }
  }

  onSensorData(handler) {
    this.handlers.sensorData = handler;
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    this.ws?.close();
  }
}

// Usage
const client = new NoiseMonitoringClient('ws://172.20.10.2:9001');
client.onSensorData((sensor) => {
  console.log(`📊 ${sensor.device_id}: ${sensor.db} dB`);
});
client.connect();
```

## Python MQTT Client Example

### Publishing Sensor Data
```python
import paho.mqtt.client as mqtt
import json
import time

def publish_sensor_data():
    client = mqtt.Client()
    client.connect("172.20.10.2", 1883, 60)
    
    sensor_data = {
        "device_id": "esp32-001",
        "lat": 6.796436,
        "lon": 79.901152,
        "db": 45.7,
        "timestamp": int(time.time() * 1000)
    }
    
    topic = f"noise/esp32/{sensor_data['device_id']}"
    payload = json.dumps(sensor_data)
    
    client.publish(topic, payload)
    client.disconnect()

# Usage
publish_sensor_data()
```

### Subscribing to Sensor Data
```python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("noise/#")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"📊 {data['device_id']}: {data['db']} dB")
    except Exception as e:
        print(f"Error parsing message: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("172.20.10.2", 1883, 60)
client.loop_forever()
```

## Testing Tools

### WebSocket Test Client
```bash
# Install wscat
npm install -g wscat

# Connect and test
wscat -c ws://172.20.10.2:9001

# Send test message
{"type": "ping", "timestamp": 1753645869497}
```

### MQTT Test Commands
```bash
# Subscribe to all noise topics
mosquitto_sub -h 172.20.10.2 -t "noise/#" -v

# Publish test data
mosquitto_pub -h 172.20.10.2 -t "noise/esp32/test" \
  -m '{"device_id":"test","lat":6.796,"lon":79.901,"db":50,"timestamp":1753645869497}'

# Monitor broker statistics
mosquitto_sub -h 172.20.10.2 -t '$SYS/#'
```
