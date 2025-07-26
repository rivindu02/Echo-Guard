# Noise Mapping System - Connection Guide

This guide explains how to easily switch between local and Raspberry Pi setups for the Noise Mapping System.

## 🏠 Local Setup (Development)

**What runs locally:**
- `fake_esp32.py` - Simulates ESP32 sensor devices
- `mqtt_broker_server.py` - MQTT broker + WebSocket server
- React UI - Web interface connecting to localhost

### Quick Start - Local
```bash
# Windows
./start_local_system.bat

# Manual setup
python fake_esp32.py --devices 3
python Server/mqtt_broker_server.py
cd mqtt-noise-map-ui && npm start
```

## 🥧 Raspberry Pi Setup

**What runs on Pi:**
- `start_noise_system.py` - Starts Mosquitto MQTT + Python services
- `mqtt_broker_server.py` - WebSocket server (on Pi)
- `simple_noise_processor.py` - Data processing (on Pi)

**What runs locally:**
- `fake_esp32.py --broker 192.168.1.11` - Simulates ESP32 connecting to Pi
- React UI - Web interface connecting to Pi's WebSocket

### Quick Start - Pi Connection
```bash
# On Raspberry Pi (192.168.1.11)
python3 start_noise_system.py

# On your local machine - Windows
./start_pi_connection.bat

# On your local machine - Manual
python fake_esp32.py --broker 192.168.1.11 --devices 3
cd mqtt-noise-map-ui && npm start
```

## ⚙️ Easy Configuration

### Using Configuration Scripts
```bash
# Windows
./configure_connection.bat

# Linux/Mac
./configure_connection.sh
```

### Manual Configuration

**For Local Setup:**
Edit `mqtt-noise-map-ui/.env`:
```properties
# Local setup
REACT_APP_WEBSOCKET_URL=ws://localhost:9001
```

**For Pi Setup:**
Edit `mqtt-noise-map-ui/.env`:
```properties
# Pi setup
REACT_APP_WEBSOCKET_URL=ws://192.168.1.11:9001
```

**For Custom IP:**
Edit `mqtt-noise-map-ui/.env`:
```properties
# Custom IP
REACT_APP_WEBSOCKET_URL=ws://YOUR_IP:9001
```

## 📡 ESP32/Sensor Connection

### Real ESP32 (when you get one)
Update your ESP32 code to use the Pi's IP:
```cpp
const char* mqtt_server = "192.168.1.11";  // Pi IP
```

### Fake ESP32 (for testing)
```bash
# Connect to localhost
python fake_esp32.py

# Connect to Pi
python fake_esp32.py --broker 192.168.1.11

# Connect to custom IP
python fake_esp32.py --broker YOUR_IP

# Multiple devices
python fake_esp32.py --broker 192.168.1.11 --devices 5 --interval 3
```

## 🔄 Switching Between Setups

### Method 1: Configuration Scripts
```bash
./configure_connection.bat  # Windows
./configure_connection.sh   # Linux
```

### Method 2: Quick Start Scripts
```bash
./start_local_system.bat     # Local development
./start_pi_connection.bat    # Connect to Pi
```

### Method 3: Manual .env Edit
Just uncomment/comment the appropriate line in `mqtt-noise-map-ui/.env`

## 🧪 Testing Scenarios

### 1. Full Local Development
- `fake_esp32.py` → `mqtt_broker_server.py` → React UI
- Everything on localhost

### 2. Pi with Simulated Sensors
- `fake_esp32.py --broker 192.168.1.11` → Pi services → React UI
- Sensors simulated locally, services on Pi

### 3. Pi with Real ESP32s (future)
- Real ESP32 devices → Pi services → React UI
- Physical sensors, services on Pi

## 🔍 Troubleshooting

### Can't connect to Pi
1. Check Pi IP: `ping 192.168.1.11`
2. Check Pi services: `ps aux | grep python3`
3. Check Pi ports: `netstat -tlnp | grep :1883` (MQTT) and `netstat -tlnp | grep :9001` (WebSocket)

### React UI not connecting
1. Check `.env` file has correct `REACT_APP_WEBSOCKET_URL`
2. Restart React app after changing `.env`
3. Check browser console for WebSocket errors

### Fake ESP32 not connecting
1. Check broker IP is reachable
2. Check MQTT broker is running on target
3. Use `python fake_esp32.py --broker IP` format

## 📝 Current Pi Status

After running `cleanup_and_install.sh` on your Pi, you should have:
- ✅ Python environment setup
- ✅ Required packages installed
- ✅ All Python files copied
- ✅ Ready to run `python3 start_noise_system.py`

## 🚀 Next Steps

1. **Test Pi Connection**: Use `./start_pi_connection.bat` to test connecting to your Pi
2. **Verify Data Flow**: Check that fake sensor data appears in React UI
3. **Plan Real ESP32**: When ready, update ESP32 code with Pi IP
4. **Scale Up**: Add more sensor locations using `--devices` parameter

## 🔧 Port Information

- **MQTT Broker**: Port 1883
- **WebSocket Server**: Port 9001  
- **React UI**: Port 3000 (development)

## 📁 Key Files

- `fake_esp32.py` - ESP32 simulator with `--broker` parameter
- `mqtt-noise-map-ui/.env` - React UI connection configuration
- `Server/start_noise_system.py` - Pi startup script
- `configure_connection.*` - Easy configuration scripts
- `start_local_system.bat` - Local development quick start
- `start_pi_connection.bat` - Pi connection quick start
