# Smart Noise Mapping System Setup Guide

## 🏠 Local Testing (No Hardware Required)

**For development and testing without ESP32 sensors or Raspberry Pi:**

👉 **See [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) for complete local setup**

### Quick Local Start
```cmd
# Windows - One command setup
start_local_system.bat

# This starts: MQTT broker + WebSocket server + Fake sensors + React UI
```

**Access:** http://localhost:3000 (with simulated sensor data)

---

## 🏭 Production Setup (With Hardware)

### Automated Setup
```bash
# Start the complete Python-based system on Raspberry Pi
cd Server
python start_noise_system.py
```

This automatically starts:
- **Mosquitto MQTT broker** (port 1883)
- **WebSocket server** (port 9001) 
- **Data processing service**
- **System monitoring and auto-restart**

### Start React UI
```bash
cd mqtt-noise-map-ui
npm start
```

### Access Application
- **Web Interface:** http://localhost:3000
- **Real-time data** from physical ESP32 sensors

## 🧪 Test with Simulated Sensors

```bash
# Start 5 ESP32 simulators (for testing without hardware)
python fake_esp32.py
```

### Simulated Sensor Locations (Testing Only)

| Device ID | Coordinates | 
|-----------|-------------|
| esp32-001 | 6.7964, 79.9012 |
| esp32-002 | 6.7960, 79.9010 |
| esp32-003 | 6.7964, 79.9007 |
| esp32-004 | 6.7965, 79.9017 |
| esp32-005 | 6.7968, 79.9006 |

> **For Real Deployment:** ESP32 devices automatically determine their coordinates using built-in GPS modules and transmit them along with noise sensor data. No manual location configuration required.

## 📋 Setup Options Summary

| Setup Type | Use Case | Hardware Required | Complexity |
|------------|----------|-------------------|------------|
| **🏠 Local Testing** | Development, demos, learning | None | ⭐ Easy |
| **🏭 Production** | Real deployment | ESP32 + Raspberry Pi | ⭐⭐⭐ Advanced |
| **🧪 Hybrid** | Testing with some real sensors | Some ESP32 devices | ⭐⭐ Medium |

### Choose Your Setup:
- **New to the project?** → [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)
- **Deploying for real use?** → Continue with Production Setup below
- **Have some ESP32s?** → Mix real sensors with `fake_esp32.py`

---

## Manual Setup (Advanced)

### Prerequisites

1. **Install Python dependencies:**
```bash
cd Server
pip install -r requirements.txt
```

2. **Install Mosquitto MQTT broker:**
```bash
# Ubuntu/Debian/Raspberry Pi OS
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Windows (using Chocolatey)
choco install mosquitto

# macOS (using Homebrew)
brew install mosquitto
```

3. **Install Node.js dependencies:**
```bash
cd mqtt-noise-map-ui
npm install
```

### Manual Component Start

```bash
# Terminal 1: Start MQTT broker
mosquitto -c mosquitto.conf -v

# Terminal 2: Start WebSocket server
cd Server
python mqtt_broker_server.py

# Terminal 3: Start data processor
cd Server
python simple_noise_processor.py

# Terminal 4: Start React UI
cd mqtt-noise-map-ui
npm start

# Terminal 5: Start sensor simulators
python fake_esp32.py
```

## System Verification

✅ **MQTT Broker** - Check port 1883 is listening  
✅ **WebSocket Server** - Check port 9001 is active  
✅ **React UI** - Should show sensor locations and data  
✅ **Real-time Updates** - Noise levels should update continuously  
✅ **Status Indicators** - Sensors show online/offline status  

## Troubleshooting

### Connection Issues
```bash
# Test MQTT connection
mosquitto_sub -h localhost -t "noise/+"

# Test WebSocket port
netstat -an | findstr 9001

# Check system logs
cd Server
type mqtt_broker.log
```

### Performance Issues
- **Reduce update interval** in config.py
- **Lower interpolation resolution** 
- **Check system resources** (RAM, CPU)

### React UI Issues
- **Clear browser cache**
- **Check WebSocket connection** in dev tools
- **Verify backend is running** on port 9001

## Migration from Node.js

This system has been **fully migrated** from Node.js to Python:

### ✅ What Changed:
- **Backend:** Node.js → Python (faster, more reliable)
- **Connection:** Direct MQTT → WebSocket proxy
- **Management:** Manual startup → Automated orchestration

### ✅ What Stayed the Same:
- **React UI:** Same interface and features
- **ESP32 sensors:** No code changes needed
- **MQTT topics:** Same message structure
- **Data format:** Compatible JSON payloads

The system is now **more robust, maintainable, and feature-rich** while maintaining full compatibility with existing components.
- Interactive map markers

## Troubleshooting

### Heat Map Not Updating

If the sensor dots update with colors but the heat map overlay doesn't update properly:

1. **Check Browser Console**: Open F12 Developer Tools and look for:
   - `🔧 Interpolating data for X sensors` - confirms interpolation is running
   - `🎨 Creating overlay` - confirms heat map is being generated
   - `✅ Heat map overlay added to map` - confirms overlay is applied

2. **Verify All Sensors**: Heat map requires at least 2 sensors to work properly
   - Check that all 5 sensors show as "ACTIVE" in the Live Sensor Status panel
   - Wait 10-15 seconds for all sensors to start sending data

3. **Clear Browser Cache**: Sometimes the overlay canvas gets cached
   ```
   Ctrl+Shift+R (hard refresh) or clear browser cache completely
   ```

4. **Restart System**: If issues persist:
   ```powershell
   # Stop all processes
   Get-Job | Stop-Job -PassThru | Remove-Job
   Stop-Process -Name "node","python" -Force -ErrorAction SilentlyContinue
   
   # Restart everything
   .\start-complete-system.ps1
   ```

### Heat Map Location Mismatch

If heat map colors appear at wrong locations (e.g., ESP2 noise affecting ESP4 location):

1. **Check Console for Coordinate Debug**: Look for:
   - `🔍 Sample interpolation points` - shows corner coordinates and values
   - `📐 Bounds details` - shows the geographic bounds being used
   - Any warnings about reversed bounds

2. **Verify Sensor Coordinates**: In console, check that sensor locations match the table above:
   ```javascript
   // In browser console, you should see:
   // 🔧 Interpolating data for 5 sensors: esp32-001: XXdB at (20.594, 78.963), esp32-002: XXdB at (28.614, 77.209), ...
   ```

3. **Hard Refresh**: The coordinate mapping fix requires a hard refresh:
   ```
   Ctrl+Shift+R or clear browser cache completely
   ```

### Sensor Location Issues

If esp32-005 (or any sensor) shows incorrect location:
1. Stop all processes
2. Clear browser cache  
3. Restart using `.\start-complete-system.ps1`
4. Wait for all 5 sensors to appear online in the UI

### Debug Mode

To enable detailed logging, open browser console and run:
```javascript
localStorage.setItem('debug', 'true');
// Refresh the page
```

The sensors start with a 0.5-second stagger, so it may take 2-3 seconds for all 5 to appear.
