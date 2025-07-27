# Noise Mapping System - Testing Guide

This guide covers how to test the Noise Mapping System in different configurations: local development and Raspberry Pi deployment.

## Quick Setup Overview

The system has two main testing modes:

1. **Local Development Mode**: Everything runs on your PC
2. **Pi Server Mode**: UI runs on PC, server runs on Raspberry Pi

## Configuration Files

### Main Configuration (`config.ini`)
```ini
[pi_connection]
# Raspberry Pi IP address (change this to your Pi's IP)
pi_ip = 172.20.10.2
mqtt_port = 1883
websocket_port = 9001

[local_connection]
# Local development settings
local_ip = localhost
mqtt_port = 1883
websocket_port = 9001
```

### UI Configuration (`mqtt-noise-map-ui/.env`)
```env
# WebSocket Configuration
# Switch between these URLs based on your setup:
# For Raspberry Pi: ws://172.20.10.2:9001
# For local testing: ws://localhost:9001
REACT_APP_WEBSOCKET_URL=ws://172.20.10.2:9001
```

## Testing Mode 1: Local Development (Everything on PC)

### Setup
1. **Update UI configuration for local mode:**
   ```bash
   # Edit mqtt-noise-map-ui/.env
   REACT_APP_WEBSOCKET_URL=ws://localhost:9001
   ```

2. **Start local development server:**
   ```bash
   cd Server
   python local_dev_server.py
   ```

3. **Start React UI:**
   ```bash
   cd mqtt-noise-map-ui
   npm start
   ```

### What happens:
- Local WebSocket server runs on port 9001
- 5 virtual ESP32 devices generate noise data
- React UI connects to localhost WebSocket
- No external MQTT broker needed

## Testing Mode 2: Pi Server Mode (Distributed)

### Prerequisites
- Raspberry Pi with MQTT broker running
- Pi accessible over network
- Pi IP address configured in `config.ini`

### Step 1: Update Pi IP Address
1. **Find your Pi's IP address:**
   ```bash
   # On Raspberry Pi
   hostname -I
   # or
   ip addr show
   ```

2. **Update config.ini:**
   ```ini
   [pi_connection]
   pi_ip = YOUR_PI_IP_HERE  # e.g., 192.168.1.100
   ```

3. **Update UI configuration:**
   ```bash
   # Edit mqtt-noise-map-ui/.env
   REACT_APP_WEBSOCKET_URL=ws://YOUR_PI_IP_HERE:9001
   ```

### Step 2: Start Pi Server Components
**On Raspberry Pi:**
```bash
# Start MQTT broker (if not already running)
sudo systemctl start mosquitto

# Start WebSocket server
cd Server
python3 fixed_websocket_server.py
```

### Step 3: Start Data Sources
**On your PC:**
```bash
# Start fake ESP32 devices (connects to Pi MQTT broker)
python fake_esp32.py

# Start React UI (connects to Pi WebSocket server)
cd mqtt-noise-map-ui
npm start
```

### Data Flow in Pi Mode:
```
fake_esp32.py (PC) → MQTT Broker (Pi) → fixed_websocket_server.py (Pi) → React UI (PC)
```

## Changing Pi IP Address

### Method 1: Edit Config Files
1. **Update `config.ini`:**
   ```ini
   [pi_connection]
   pi_ip = NEW_IP_ADDRESS
   ```

2. **Update `mqtt-noise-map-ui/.env`:**
   ```env
   REACT_APP_WEBSOCKET_URL=ws://NEW_IP_ADDRESS:9001
   ```

3. **Restart services:**
   - Stop fake_esp32.py (Ctrl+C)
   - Stop React UI (Ctrl+C)
   - Restart both

### Method 2: Environment Variables (Advanced)
```bash
# Set environment variable (overrides config.ini)
export PI_IP=NEW_IP_ADDRESS

# Run components
python fake_esp32.py
```

## Testing Different Scenarios

### Test 1: Local Development
```bash
# Terminal 1: Start local server
cd Server && python local_dev_server.py

# Terminal 2: Start UI (with localhost config)
cd mqtt-noise-map-ui && npm start
```

### Test 2: Pi Deployment
```bash
# Terminal 1: Start fake sensors (targeting Pi)
python fake_esp32.py

# Terminal 2: Start UI (with Pi config)
cd mqtt-noise-map-ui && npm start

# On Pi: Start WebSocket server
cd Server && python3 fixed_websocket_server.py
```

### Test 3: Mixed Testing
```bash
# Use real ESP32 devices + Pi server + PC UI
# Just ensure ESP32s are configured with Pi's IP
```

## Troubleshooting

### WebSocket Connection Issues
1. **Check IP address:** Ensure Pi IP is correct in both config files
2. **Check firewall:** Pi port 9001 should be open
3. **Check network:** PC and Pi should be on same network
4. **Check WebSocket server:** Ensure fixed_websocket_server.py is running on Pi

### MQTT Connection Issues
1. **Check MQTT broker:** Ensure Mosquitto is running on Pi
2. **Check port 1883:** Should be open on Pi
3. **Check fake_esp32.py logs:** Look for connection success/failure

### UI Issues
1. **Check .env file:** Ensure correct WebSocket URL
2. **Clear browser cache:** Force refresh the React app
3. **Check browser console:** Look for WebSocket errors

## Port Reference

| Service | Port | Description |
|---------|------|-------------|
| MQTT Broker | 1883 | Standard MQTT port |
| WebSocket Server | 9001 | Real-time data streaming |
| React UI | 3000 | Development server |

## Network Requirements

### For Local Testing
- All ports available on localhost
- No external network needed

### For Pi Deployment
- Pi and PC on same network
- Pi ports 1883 and 9001 accessible from PC
- Stable network connection between devices

## Common IP Configurations

### Home WiFi
```ini
pi_ip = 192.168.1.xxx  # Common home router range
```

### Hotspot/Mobile
```ini
pi_ip = 172.20.10.x    # Common mobile hotspot range
```

### University/Office
```ini
pi_ip = 10.x.x.x       # Common enterprise range
```

## Quick Commands Reference

```bash
# Find Pi IP
hostname -I

# Test connectivity
ping YOUR_PI_IP

# Check if ports are open
telnet YOUR_PI_IP 1883
telnet YOUR_PI_IP 9001

# View MQTT traffic (on Pi)
mosquitto_sub -h localhost -t "noise/#"

# Restart React UI with new config
cd mqtt-noise-map-ui && npm start
```
