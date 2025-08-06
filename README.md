# 🔊 Smart Noise Monitoring System

A real-time noise monitoring system using ESP32 sensors, Raspberry Pi server, and React web interface.

## 👨‍🏫 Canva Presentation 
-https://www.canva.com/design/DAGuD6Hi64o/7vyQ3UGEkZTetDRogWDefw/view?utm_content=DAGuD6Hi64o&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h5cc147a049

## 📋 System Overview

- **ESP32 Sensors**: Collect noise level data and send via MQTT
- **Raspberry Pi Server**: Runs MQTT broker and WebSocket server
- **React Web UI**: Real-time visualization with interactive map
- **WebSocket Bridge**: Connects MQTT data to web interface

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi with Python 3
- Node.js and npm for React UI
- ESP32 devices (or use fake simulator)

### 1. Pi Server Setup

```bash
# Install dependencies
sudo apt update
sudo apt install mosquitto mosquitto-clients python3-pip

# Install Python packages
pip3 install websockets paho-mqtt

# Start MQTT broker
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Run WebSocket server
cd Server
python3 fixed_websocket_server.py
```

### 2. React UI Setup

```bash
# Install dependencies
cd mqtt-noise-map-ui
npm install

# Start development server
npm start
```

### 3. Test with Fake Data

```bash
# Run fake ESP32 simulator
python3 fake_esp32.py --broker <PI_IP_ADDRESS>
```

## 📁 Project Structure

```
├── Server/
│   ├── fixed_websocket_server.py    # Main WebSocket server
│   ├── config_loader.py             # Configuration management
│   └── requirements.txt             # Python dependencies
├── mqtt-noise-map-ui/
│   ├── src/
│   │   ├── components/NoiseMap.js   # Map visualization
│   │   ├── mqtt/simpleWebSocketService.js  # WebSocket client
│   │   └── App.js                   # Main React app
│   └── package.json                 # Node.js dependencies
├── ESP32_Noise_Sensor/
│   └── ESP32_Noise_Sensor.ino       # Arduino code for ESP32
├── config.ini                       # System configuration
├── fake_esp32.py                    # ESP32 simulator for testing
└── test_mqtt_connection.py          # Connection testing tool
```

## ⚙️ Configuration

Edit `config.ini` to set your Raspberry Pi IP address:

```ini
[pi_connection]
pi_ip = 172.20.10.2  # Change to your Pi's IP
mqtt_port = 1883
websocket_port = 9001
```

## 🌐 System Architecture

1. **ESP32 Sensors** → MQTT (port 1883) → **Raspberry Pi**
2. **Raspberry Pi** → WebSocket (port 9001) → **React UI**
3. **React UI** displays real-time noise data on interactive map

## 📊 Features

- ✅ Real-time noise level monitoring
- ✅ Interactive map visualization
- ✅ Multiple sensor support
- ✅ Automatic reconnection
- ✅ Alert notifications for high noise levels
- ✅ Connection status monitoring

## 🔧 Troubleshooting

### Check MQTT Broker
```bash
python3 test_mqtt_connection.py <PI_IP>
```

### Check WebSocket Connection
Open browser console (F12) to see connection logs.

### Verify Fake Data
```bash
python3 fake_esp32.py --broker <PI_IP>
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
