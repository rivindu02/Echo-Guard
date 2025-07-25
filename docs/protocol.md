# Smart Noise Mapping System - Technical Protocol

## System Architecture

### Overview
The Smart Noise Mapping System is a real-time environmental monitoring solution that collects noise data from distributed ESP32 sensors and visualizes it through a web interface.

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   ESP32     │    │   MQTT       │    │   Python    │    │   React     │
│  Sensors    │───▶│   Broker     │───▶│   Backend   │───▶│     UI      │
│             │    │ (Mosquitto)  │    │  (WebSocket)│    │             │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

### Data Flow

1. **ESP32 Sensors** → Measure noise levels and publish via MQTT
2. **MQTT Broker** → Receives and routes sensor data
3. **Python Backend** → Processes data and serves WebSocket API
4. **React Frontend** → Displays real-time data and interpolated maps

## Communication Protocols

### MQTT Protocol

**Broker Configuration:**
- **Host:** localhost
- **Port:** 1883 (TCP), 9001 (WebSocket)
- **Authentication:** Anonymous (development)

**Topic Structure:**
```
noise/
├── esp32/{device_id}        # Raw sensor data
├── process_request          # Interpolation requests
└── processed               # Interpolated results
```

### WebSocket Protocol

**Connection:**
- **URL:** `ws://localhost:9001`
- **Protocol:** JSON-based messaging
- **Reconnection:** Automatic with exponential backoff

**Message Types:**
```javascript
// Sensor data message
{
  "type": "sensor_data",
  "device_id": "esp32-001",
  "lat": 20.5937,
  "lon": 78.9629,
  "db": 65.2,
  "timestamp": 1643723400000
}

// Interpolation request
{
  "type": "interpolation_request",
  "grid_size": 60,
  "bounds": {
    "min_lat": 20.0,
    "max_lat": 21.0,
    "min_lon": 78.0,
    "max_lon": 79.0
  }
}

// Interpolated data response
{
  "type": "interpolated_data",
  "grid": [[45.2, 46.1, ...], ...],
  "bounds": {...},
  "timestamp": 1643723400000
}
```

## Data Formats

### Sensor Data Format
```json
{
  "device_id": "esp32-001",
  "lat": 20.5937,
  "lon": 78.9629,
  "db": 65.2,
  "timestamp": 1643723400000,
  "battery": 85,
  "signal_strength": -45
}
```

### Interpolation Grid Format
```json
{
  "grid": [
    [45.2, 46.1, 47.3, ...],
    [44.8, 45.9, 46.7, ...],
    ...
  ],
  "bounds": {
    "min_lat": 20.0,
    "max_lat": 21.0,
    "min_lon": 78.0,
    "max_lon": 79.0
  },
  "grid_size": 60,
  "timestamp": 1643723400000
}
```

## System Components

### ESP32 Sensor Nodes

**Hardware Requirements:**
- ESP32 microcontroller
- Sound sensor (e.g., MAX4466, INMP441)
- WiFi connectivity
- Power supply (battery or USB)

**Firmware Features:**
- WiFi connection management
- MQTT client with auto-reconnection
- Sensor data acquisition
- Low-power mode support

### Python Backend Services

#### 1. MQTT Broker Server (`mqtt_broker_server.py`)
- **Purpose:** WebSocket proxy for MQTT data
- **Functions:**
  - MQTT client connection
  - WebSocket server for React UI
  - Real-time data forwarding
  - Connection management

#### 2. Noise Processor (`simple_noise_processor.py`)
- **Purpose:** Data interpolation and analysis
- **Functions:**
  - IDW (Inverse Distance Weighting) interpolation
  - Grid generation for visualization
  - Noise contour calculations
  - Performance optimization

#### 3. System Orchestrator (`start_noise_system.py`)
- **Purpose:** Service management and monitoring
- **Functions:**
  - Mosquitto broker startup
  - Service health monitoring
  - Automatic restart on failure
  - Centralized logging

### React Web Interface

#### Key Components:
- **NoiseMap.js** - Interactive map visualization
- **NoiseMapOverlay.js** - Noise level overlays
- **webSocketMqttService.js** - WebSocket communication

#### Features:
- Real-time sensor status indicators
- Interactive noise level maps
- Historical data visualization
- Responsive design for mobile devices

## Network Requirements

### Port Configuration
- **1883** - MQTT TCP (sensor connections)
- **9001** - MQTT WebSocket & React WebSocket
- **3000** - React development server

### Firewall Rules
```bash
# Allow MQTT TCP
sudo ufw allow 1883/tcp

# Allow WebSocket
sudo ufw allow 9001/tcp

# Allow React dev server (development only)
sudo ufw allow 3000/tcp
```

## Performance Specifications

### Scalability Limits
- **Maximum Sensors:** 100+ concurrent connections
- **Update Frequency:** Up to 1Hz per sensor
- **WebSocket Clients:** 20+ concurrent connections
- **Interpolation Grid:** Up to 100x100 resolution

### Resource Requirements
- **CPU:** ARM Cortex-A72 (Raspberry Pi 4) or equivalent
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 8GB minimum (for logs and data persistence)
- **Network:** 100Mbps Ethernet or WiFi

### Performance Benchmarks
```
Raspberry Pi 4B (4GB RAM):
├── Sensor throughput: 50+ sensors @ 1Hz
├── Interpolation time: <200ms (60x60 grid)
├── Memory usage: ~100MB total
├── CPU usage: <15% average
└── WebSocket latency: <50ms local network
```

## Security Considerations

### Development Environment
- Anonymous MQTT access (no authentication)
- Unencrypted WebSocket connections
- Local network access only

### Production Deployment
- MQTT authentication with username/password
- TLS/SSL encryption for all connections
- VPN or firewall restrictions
- Regular security updates

## Error Handling

### Connection Failures
- **MQTT:** Automatic reconnection with exponential backoff
- **WebSocket:** Client-side reconnection with retry logic
- **Sensor:** Local data buffering during network outages

### Data Validation
- **Range checking:** Noise levels (0-120 dB)
- **Coordinate validation:** Latitude/longitude bounds
- **Timestamp verification:** Recent data filtering
- **Message format:** JSON schema validation

### Recovery Procedures
1. **Service failure:** Automatic restart via system orchestrator
2. **Data corruption:** Fallback to previous known good state
3. **Network partition:** Local caching and sync on reconnection

## Development and Testing

### Local Development Setup
```bash
# 1. Start Python backend
cd Server
python start_noise_system.py

# 2. Start React frontend
cd mqtt-noise-map-ui
npm start

# 3. Start sensor simulators
python fake_esp32.py
```

### Testing Procedures
1. **Unit Tests:** Component-level functionality
2. **Integration Tests:** End-to-end data flow
3. **Load Tests:** Multiple sensors and clients
4. **Network Tests:** Connection failure scenarios

### Debugging Tools
- **MQTT Explorer:** Topic monitoring and debugging
- **Browser DevTools:** WebSocket connection analysis
- **System logs:** Centralized logging with timestamps
- **Network analysis:** Wireshark for protocol debugging

## Deployment Guidelines

### Raspberry Pi Setup
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install mosquitto mosquitto-clients python3-pip

# 2. Install Python dependencies
cd Server
pip3 install -r requirements.txt

# 3. Configure system service
sudo cp etc/systemd/noise-processor.service /etc/systemd/system/
sudo systemctl enable noise-processor
sudo systemctl start noise-processor
```

### Production Configuration
- Use systemd services for automatic startup
- Configure log rotation to prevent disk space issues
- Set up monitoring and alerting for system health
- Implement backup procedures for configuration and data

This protocol documentation provides the technical foundation for understanding, deploying, and maintaining the Smart Noise Mapping System.