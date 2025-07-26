# 🥧 Raspberry Pi Central Setup - Quick Reference

## Your Configuration
- **Pi IP**: 192.168.1.12
- **MQTT Port**: 1883  
- **WebSocket Port**: 9001

## 🚀 Quick Start Commands

### 1. Configure Your PC for Pi (Run Once)
```cmd
# Update configuration
configure_connection.bat
# Choose option 2 (Raspberry Pi setup)

# Or direct setup
start_pi_system.bat
```

### 2. Start Pi Services (On Raspberry Pi)
```bash
# SSH to Pi
ssh pi@192.168.1.12

# Navigate to project
cd ~/Noise-mapping

# Start all services
python3 Server/start_noise_system.py
```

### 3. Start PC Services (On Your Windows PC)
```cmd
# Option A: Automated
start_pi_system.bat

# Option B: Manual
python fake_esp32.py --broker 192.168.1.12 --devices 5
cd mqtt-noise-map-ui && npm start
```

### 4. Access System
🌍 **Web Interface**: http://localhost:3000

## 🔍 Test Connection
```cmd
# Test if Pi is ready
python test_pi_connection.py

# Should show:
# ✅ Network connectivity: PASS
# ✅ MQTT broker (1883): PASS  
# ✅ WebSocket server (9001): PASS
```

## 📊 Expected Data Flow
```
PC (fake_esp32.py) → Pi (192.168.1.12:1883) → Pi (WebSocket :9001) → PC (React UI :3000)
      📡 ESP32 data         🔌 MQTT broker        ⚡ Real-time         🌐 Visualization
```

## ✅ Success Indicators

### On Pi Terminal:
```
🚀 Starting MQTT Broker Server with WebSocket support...
✅ Connected to MQTT broker successfully
🌐 WebSocket server listening on ws://0.0.0.0:9001
📍 Ready to receive ESP32 sensor data and serve React UI
```

### On PC ESP32 Simulator:
```
✅ Connected to MQTT broker at 192.168.1.12:1883
📡 esp32-001: 75.2 dB at (6.7964, 79.9012)
📡 esp32-002: 68.1 dB at (6.7960, 79.9010)
```

### On PC React UI:
- ✅ Connection status: "Connected"
- 🗺️ Map shows 5 sensor markers
- 📊 Noise levels update every 3 seconds
- 🌐 Browser console shows WebSocket connection to Pi

## 🐛 Quick Troubleshooting

### ❌ Cannot reach Pi
```cmd
ping 192.168.1.12
# If fails: Check Pi WiFi, power, IP address
```

### ❌ MQTT connection refused  
```bash
# On Pi
sudo systemctl start mosquitto
sudo netstat -tlnp | grep :1883
```

### ❌ WebSocket connection error
```bash
# On Pi - restart services
python3 Server/start_noise_system.py
```

### ❌ React UI shows "Connection Error"
```cmd
# Check .env.local
type mqtt-noise-map-ui\.env.local
# Should have: REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001
```

## 📁 Key Files
- **`config.ini`** - Pi IP configuration (192.168.1.12)
- **`start_pi_system.bat`** - Automated PC setup for Pi
- **`connect_to_pi.bat`** - Configure PC for Pi connection  
- **`test_pi_connection.py`** - Test Pi connectivity
- **`PI_CONNECTION_GUIDE.md`** - Detailed setup guide

---

## 🎯 Your Complete System is Now Ready!

✅ **Raspberry Pi (192.168.1.12)**: Central MQTT broker + WebSocket server  
✅ **PC fake_esp32.py**: Simulates ESP32 sensors sending to Pi  
✅ **PC React UI**: Connects to Pi WebSocket for real-time data  
✅ **Network**: All devices on same WiFi, communicating perfectly  

**Data flows from your PC → through Pi → back to PC for visualization! 🎉**
