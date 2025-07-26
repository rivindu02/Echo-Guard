# Local Testing Guide - No Central Device Required

## 🏠 Overview

This guide shows how to test the **Smart Noise Mapping System** locally on a single computer without requiring a Raspberry Pi or central device. Perfect for development, testing, and demonstration purposes.

## 🚀 Quick Local Setup

### One-Command Start
```cmd
# Windows - Automated startup
start_local_system.bat

# Linux/macOS - Manual setup below
```

This automatically configures and starts:
- ✅ Local MQTT broker (Mosquitto on port 1883)
- ✅ Python WebSocket server (port 9001)
- ✅ Fake ESP32 sensor simulators
- ✅ React UI development server (port 3000)

### Access Your Local System
- **🌐 Web Interface:** http://localhost:3000
- **📊 Real-time Map:** Shows simulated sensor data
- **🔄 Live Updates:** Every 3-5 seconds

## 🔧 Manual Local Setup

### Step 1: Start MQTT Broker
```cmd
# Terminal 1: Start Mosquitto locally
cd "D:\Documents\GitHub\Noise-mapping"
mosquitto -c mosquitto.conf -v
```

### Step 2: Start WebSocket Server
```cmd
# Terminal 2: Start Python server
cd "D:\Documents\GitHub\Noise-mapping\Server"
python mqtt_broker_server.py
```
**Expected Output:**
```
🚀 Starting MQTT Broker Server with WebSocket support...
✅ Connected to MQTT broker successfully
🌐 WebSocket server listening on ws://localhost:9001
📍 Ready to receive ESP32 sensor data and serve React UI
```

### Step 3: Start Sensor Simulators
```cmd
# Terminal 3: Start fake ESP32 devices
cd "D:\Documents\GitHub\Noise-mapping"
python fake_esp32.py --devices 5 --interval 3
```

### Step 4: Start React UI
```cmd
# Terminal 4: Start web interface
cd mqtt-noise-map-ui
npm start
```

## 🤖 Simulator vs Real ESP32 Devices

### 🧪 Fake ESP32 Simulator (`fake_esp32.py`)
- ✅ **Hardcoded coordinates** - Fixed test locations for consistent testing
- ✅ **Simulated noise patterns** - Generates realistic but fake noise data  
- ✅ **No hardware required** - Pure software simulation
- ✅ **Instant setup** - No GPS wait time or calibration needed

### 📡 Real ESP32 Devices (Production)
- 🌐 **GPS auto-detection** - Built-in GPS modules determine actual coordinates
- 🎤 **Real noise sensors** - Actual microphone readings from environment
- ⚙️ **Hardware setup required** - Physical device deployment and configuration
- 📍 **Dynamic positioning** - Can be moved and will auto-update location

### Data Format (Both Send Same Structure)
```json
{
  "device_id": "esp32-001",
  "lat": 6.7964368148947765,    // GPS coords (real) vs hardcoded (sim)
  "lon": 79.90115269520993,     // GPS coords (real) vs hardcoded (sim)  
  "db": 75.2,                   // Sensor reading (real) vs generated (sim)
  "timestamp": 1738051234567    // Both use actual system time
}
```

## 📍 Simulated Test Data

### Virtual Sensor Locations (Simulator Only)

| Device ID | Coordinates | Noise Range |
|-----------|-------------|-------------|
| esp32-001 | 6.7964, 79.9012 | 60-90 dB |
| esp32-002 | 6.7960, 79.9010 | 70-95 dB |
| esp32-003 | 6.7964, 79.9007 | 25-45 dB |
| esp32-004 | 6.7965, 79.9017 | 50-80 dB |
| esp32-005 | 6.7968, 79.9006 | 40-85 dB |

> **Note:** These are hardcoded coordinates in `fake_esp32.py` for testing only. Real ESP32 devices use built-in GPS modules to automatically determine and transmit their actual coordinates.

### Sample Data Flow
```json
{
  "device_id": "esp32-001",
  "lat": 6.7964368148947765,
  "lon": 79.90115269520993,
  "db": 75.2,
  "timestamp": 1738051234567
}
```

## 🔍 Verification Steps

### 1. Check Services Are Running
```cmd
# Verify ports are listening
netstat -an | findstr "1883 9001 3000"
```
**Expected Output:**
```
TCP    0.0.0.0:1883           0.0.0.0:0              LISTENING
TCP    127.0.0.1:9001         0.0.0.0:0              LISTENING
TCP    127.0.0.1:3000         0.0.0.0:0              LISTENING
```

### 2. Test MQTT Connection
```cmd
# Subscribe to sensor data
mosquitto_sub -h localhost -t "noise/+"
```
**Expected Output:**
```
{"device_id": "esp32-001", "lat": 6.7964, "lon": 79.9012, "db": 78.5, "timestamp": 1738051234567}
{"device_id": "esp32-002", "lat": 6.7960, "lon": 79.9010, "db": 82.1, "timestamp": 1738051237890}
```

### 3. Test WebSocket Connection
```cmd
# Run WebSocket test
python test_websocket_connection.py
```
**Expected Output:**
```
✅ WebSocket connection successful
📊 Receiving sensor data from 5 devices
🔄 Real-time updates working
```

### 4. Verify React UI
- 🌐 Open http://localhost:3000
- 🗺️ Should show a map with sensor markers
- ✅ Connection status should show "Connected"
- 📊 Noise levels should update every few seconds

## 📋 Environment Configuration

### Local .env Settings
Your `mqtt-noise-map-ui/.env.local` should contain:
```bash
# Local testing configuration
REACT_APP_MQTT_BROKER_URL=ws://localhost:9001
REACT_APP_WEBSOCKET_URL=ws://localhost:9001
REACT_APP_MQTT_TOPIC_PREFIX=noise

# Map centered on test area
REACT_APP_DEFAULT_MAP_CENTER_LAT=6.7964
REACT_APP_DEFAULT_MAP_CENTER_LON=79.9012
REACT_APP_DEFAULT_MAP_ZOOM=15

# Features for testing
REACT_APP_ENABLE_NOTIFICATIONS=true
REACT_APP_AUTO_REFRESH_INTERVAL=3000
REACT_APP_DEBUG_MODE=true
```

## 🐛 Local Testing Troubleshooting

### ❌ "Connection error - Check your MQTT broker"

**Solution 1: Check Service Order**
```cmd
# Start in this exact order:
1. mosquitto -c mosquitto.conf
2. python Server\mqtt_broker_server.py
3. python fake_esp32.py
4. npm start (in mqtt-noise-map-ui folder)
```

**Solution 2: Check Ports**
```cmd
# Kill any conflicting processes
taskkill /f /im mosquitto.exe
taskkill /f /im python.exe
taskkill /f /im node.exe

# Restart services
```

**Solution 3: Verify WebSocket URL**
- Ensure `.env.local` has `REACT_APP_WEBSOCKET_URL=ws://localhost:9001`
- Restart React app after changing environment variables

### ❌ No Sensor Data on Map

**Check Fake ESP32:**
```cmd
# Verify simulators are sending data
python fake_esp32.py --devices 3 --interval 2 --verbose
```

**Check MQTT Messages:**
```cmd
# Monitor all noise topics
mosquitto_sub -h localhost -t "noise/#" -v
```

### ❌ WebSocket Connection Failed

**Test Direct Connection:**
```cmd
# Test WebSocket server
python test_websocket_connection.py
```

**Check Server Logs:**
```cmd
# View detailed logs
type Server\mqtt_broker.log
```

## 🎯 Local vs Production Differences

### Local Testing Setup
- ✅ **Single Computer:** All services on localhost
- ✅ **Simulated Sensors:** Python fake_esp32.py
- ✅ **No Hardware:** No ESP32 or Raspberry Pi required
- ✅ **Fast Iteration:** Instant restart and testing

### Production Setup (Reference)
- 🏭 **Central Device:** Raspberry Pi as MQTT broker
- 📡 **Real Sensors:** Physical ESP32 devices
- 🌐 **Network Setup:** WiFi configuration required
- ⚙️ **Hardware Config:** Microphone calibration needed

## 📖 Development Workflow

### 1. Code → Test → Debug Cycle
```cmd
# Make changes to code
# Restart only affected services:

# For Python server changes:
python Server\mqtt_broker_server.py

# For React UI changes:
npm start

# For sensor simulation changes:
python fake_esp32.py --devices 5
```

### 2. Testing Different Scenarios
```cmd
# Test with 1 sensor
python fake_esp32.py --devices 1 --interval 1

# Test with many sensors  
python fake_esp32.py --devices 10 --interval 0.5

# Test connection loss simulation
python fake_esp32.py --devices 3 --dropout-rate 0.2
```

### 3. Performance Testing
```cmd
# Monitor resource usage
# Windows Task Manager or:
wmic process where name="python.exe" get processid,percentprocessortime
wmic process where name="node.exe" get processid,percentprocessortime
```

## 🔗 Related Guides

- 📋 [SETUP.md](SETUP.md) - Complete system setup
- 🔧 [PI_SETUP_GUIDE.md](PI_SETUP_GUIDE.md) - Production Raspberry Pi setup  
- 🌐 [CONNECTION_GUIDE.md](CONNECTION_GUIDE.md) - Network configuration
- 🔍 [README.md](README.md) - Project overview

---

## ✅ Local Testing Checklist

- [ ] Mosquitto MQTT broker running on port 1883
- [ ] Python WebSocket server running on port 9001  
- [ ] Fake ESP32 simulators sending data
- [ ] React UI accessible at http://localhost:3000
- [ ] Connection status shows "Connected" 
- [ ] Map displays sensor markers
- [ ] Noise levels update in real-time
- [ ] No error messages in browser console
- [ ] All services respond to Ctrl+C shutdown

**🎉 If all items are checked, your local testing environment is ready!**
