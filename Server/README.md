# Noise Mapping System - Server Components

This directory contains the server-side WebSocket server for the Noise Mapping System.

## Architecture

```
ESP32 Sensors → MQTT Broker (Pi) → fixed_websocket_server.py → React UI
                  Mosquitto         WebSocket Server (9001)
```

## Core Server

### `fixed_websocket_server.py` (Main)
Production WebSocket server that:
- Connects to Mosquitto MQTT broker on Raspberry Pi
- Subscribes to `noise/#` MQTT topics
- Forwards real-time sensor data to React UI clients
- Handles connections/disconnections gracefully

**Features:**
- Async WebSocket with `websockets` library
- Thread-safe message queuing (MQTT → WebSocket)
- Ping/pong keepalive (20s)
- Real-time logging

## Prerequisites

### On Raspberry Pi
```bash
# Install Mosquitto
sudo apt update
sudo apt install -y mosquitto mosquitto-clients

# Enable and start
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Verify it's running
sudo systemctl status mosquitto
netstat -an | grep 1883
```

### Configuration
Edit `../config.ini`:
```ini
[pi]
pi_ip = 192.168.208.242     # Your Pi's IP
mqtt_port = 1883             # MQTT port
websocket_port = 9001        # WebSocket port
```

## Installation

```bash
cd Server
pip install -r requirements.txt
```

## Running

### Start on Pi
```bash
python3 fixed_websocket_server.py
```

### Expected Output
```
📋 Pi configuration loaded:
   MQTT broker: 192.168.208.242:1883
   WebSocket server: 0.0.0.0:9001
🦟 Pi MQTT client started
✅ Pi WebSocket server running!
```

### Start React UI Connection
```bash
# React should connect to:
ws://192.168.208.242:9001
```

## Dependencies

- **paho-mqtt** - MQTT client library
- **websockets** - Async WebSocket server

## Supporting Files

- `config_loader.py` - Configuration management
- `local_dev_server.py` - Virtual sensor simulator (dev only)

## Troubleshooting

### MQTT Connection Failed (rc=-2)
```bash
# On Pi, verify Mosquitto is running
sudo systemctl status mosquitto

# If not running, start it
sudo systemctl start mosquitto

# Allow firewall
sudo ufw allow 1883/tcp
```

### Test MQTT Connection
```bash
# From Pi
mosquitto_sub -h localhost -t "noise/#" -v

# From ESP32 network
mosquitto_pub -h 192.168.208.242 -t "test" -m "hello"
```

### WebSocket Clients Not Receiving Data
1. Verify sensors publishing: `mosquitto_sub -h localhost -t "noise/#"`
2. Check server logs for errors
3. Verify React UI WebSocket URL uses correct Pi IP

### Port Already in Use
```bash
# Change port in config.ini or
lsof -i :9001  # Find process
kill -9 <PID>  # Kill it
```

## Data Flow

1. **ESP32** publishes JSON to `noise/esp32-{id}`
2. **Mosquitto** receives on Pi (1883)
3. **fixed_websocket_server.py** subscribes and queues messages
4. **WebSocket** (9001) sends to React UI
5. **React** displays real-time noise map

## MQTT Message Format

```json
{
  "device_id": "esp32-001",
  "location_name": "Entc",
  "lat": 6.796436,
  "lon": 79.901152,
  "db": 65.5,
  "timestamp": 1702483920000
}
```

## Quick Start Checklist

- [ ] Mosquitto running on Pi: `sudo systemctl start mosquitto`
- [ ] Firewall allows 1883: `sudo ufw allow 1883/tcp`
- [ ] config.ini has correct Pi IP
- [ ] WebSocket server started: `python3 fixed_websocket_server.py`
- [ ] ESP32 can reach Pi IP (same WiFi)
- [ ] React UI connects to `ws://Pi-IP:9001`
