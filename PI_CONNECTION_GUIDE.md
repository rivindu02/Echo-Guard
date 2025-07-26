# Pi-Based Noise Mapping Setup Guide

This guide shows how to use your Raspberry Pi as the MQTT broker while keeping the React UI running on your laptop.

## 🎯 System Architecture

```
Laptop (fake_esp32.py) → Pi (MQTT Broker) → Laptop (React UI)
     📡 WiFi                🥧 Processing        💻 Display
```

## 🚀 Quick Setup

### Method 1: One-Command Setup
```cmd
# Configure IP address (run once)
configure_ip.bat

# Connect to Pi (run each time)
connect_to_pi.bat
```

### Method 2: Manual Setup

#### Step 1: Configure Your Pi IP
Edit `config.ini`:
```ini
[pi_connection]
pi_ip = 192.168.1.12  # Your Pi's IP address
```

#### Step 2: On Raspberry Pi
```bash
# Start the MQTT broker and WebSocket server
cd Server
python3 start_noise_system.py
```

#### Step 3: On Your Laptop
```cmd
# Send fake sensor data to Pi
python fake_esp32.py --pi

# Start React UI (in new terminal)
cd mqtt-noise-map-ui
npm start
```

## 📱 Usage Examples

### Connect to Pi with Default Settings
```cmd
python fake_esp32.py --pi
```

### Connect to Pi with Custom Settings
```cmd
python fake_esp32.py --broker 192.168.1.12 --devices 3 --interval 5
```

### Use Config File for Everything
```cmd
python fake_esp32.py --config
```

### Switch Back to Localhost
```cmd
connect_to_localhost.bat
```

## 🔧 Configuration Files

### `config.ini` - Main Configuration
```ini
[pi_connection]
pi_ip = 192.168.1.12
mqtt_port = 1883
websocket_port = 9001

[fake_esp32]
device_count = 5
publish_interval = 3
```

### `mqtt-noise-map-ui/.env` - React UI Configuration
```properties
# For Pi connection
REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001

# For localhost (comment out Pi line above)
#REACT_APP_WEBSOCKET_URL=ws://localhost:9001
```

## 🌐 Access Points

- **React UI:** http://localhost:3000 (on your laptop)
- **Pi WebSocket:** ws://192.168.1.12:9001
- **Pi MQTT:** 192.168.1.12:1883

## 🔄 Switching Between Setups

### To Pi Setup:
```cmd
configure_ip.bat  # Set Pi IP
connect_to_pi.bat # Start Pi connection
```

### To Localhost Setup:
```cmd
connect_to_localhost.bat    # Configure localhost
start_local_system.bat      # Start local system
```

## 🐛 Troubleshooting

### Cannot Connect to Pi
1. Check Pi IP: `ping 192.168.1.12`
2. Check Pi services: `python3 start_noise_system.py`
3. Check firewall on Pi: `sudo ufw status`

### React UI Not Updating
1. Check WebSocket connection in browser console
2. Verify `.env` file has correct Pi IP
3. Restart React UI: `npm start`

### Fake ESP32 Connection Failed
1. Check config.ini has correct Pi IP
2. Try: `python fake_esp32.py --broker 192.168.1.12`
3. Check Pi MQTT broker is running

## 📊 Data Flow

1. **fake_esp32.py** → Sends sensor data to Pi MQTT broker (port 1883)
2. **Pi MQTT Broker** → Receives and processes data
3. **Pi WebSocket Server** → Broadcasts data (port 9001)
4. **React UI** → Connects to Pi WebSocket and displays data

## 🎛️ Advanced Configuration

### Custom Device Locations
Edit the coordinates in `fake_esp32.py` around line 220:
```python
device_locations = [
    ("esp32-001", YOUR_LAT, YOUR_LON, "Location 1"),
    # Add more locations...
]
```

### Different Pi IP
```cmd
python fake_esp32.py --broker YOUR_PI_IP
```

### Multiple Devices
```cmd
python fake_esp32.py --pi --devices 10 --interval 2
```
