# 🎵 MQTT Noise Map Dashboard

A real-time web dashboard for visualizing environmental noise levels from ESP32 sensors via MQTT. Built with React and featuring a modern dark theme with glassmorphism UI effects.

![MQTT Noise Map Dashboard](https://img.shields.io/badge/status-active-brightgreen) ![React](https://img.shields.io/badge/react-18.2.0-blue) ![MQTT](https://img.shields.io/badge/mqtt-4.3.7-orange) ![Leaflet](https://img.shields.io/badge/leaflet-1.9.4-green)

## 🌟 Features

- **Real-time Data Visualization**: Live updates from MQTT-connected ESP32 sensors
- **Interactive Map**: Leaflet-based map with animated markers and multiple tile layers
- **Modern UI**: Dark theme with glassmorphism effects and smooth animations
- **Connection Management**: Automatic reconnection and connection status monitoring
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Noise Level Analytics**: Statistics panel with live sensor data
- **Alert System**: Visual and audio notifications for high noise levels
- **Settings Panel**: Customizable notifications and map preferences

## 📋 Prerequisites

- **Node.js** (v16 or newer)
- **npm** (comes with Node.js)
- **MQTT Broker** (e.g., Mosquitto running on Raspberry Pi)
- **ESP32 sensors** (optional for testing - can use Python simulator)

## 🚀 Quick Start

### 1. Create React App

```bash
npx create-react-app mqtt-noise-map-ui
cd mqtt-noise-map-ui
```

### 2. Install Dependencies

```bash
npm install leaflet react-leaflet mqtt framer-motion recharts
```

### 3. Replace Default Files

Replace the generated files with the custom ones provided:
- Copy all files from this project to your React app directory
- Ensure the folder structure matches the provided structure

### 4. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local` and set your MQTT broker details:
```env
REACT_APP_MQTT_BROKER_URL=ws://YOUR_PI_IP:9001
REACT_APP_MQTT_TOPIC_PREFIX=noise
```

### 5. Start Development Server

```bash
npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000)

## 🔧 Configuration

### MQTT Broker Setup (Raspberry Pi)

1. **Install Mosquitto**:
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
```

2. **Configure WebSocket Support**:
Edit `/etc/mosquitto/mosquitto.conf`:
```conf
# Standard MQTT port
listener 1883

# WebSocket port for browser clients  
listener 9001
protocol websockets

# Allow anonymous connections (adjust for production)
allow_anonymous true
```

3. **Start/Restart Mosquitto**:
```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

4. **Test Connection**:
```bash
# Subscribe to test topic
mosquitto_sub -h localhost -t test

# Publish test message (in another terminal)
mosquitto_pub -h localhost -t test -m "Hello MQTT"
```

### ESP32 Code

Example Arduino code for ESP32 sensors:

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi and MQTT settings
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";  
const char* mqtt_server = "YOUR_PI_IP";
const int mqtt_port = 1883;
const char* device_id = "esp32-001";

// Sensor location (change for each device)
const float sensor_lat = 12.912;
const float sensor_lon = 77.675;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // Connect to MQTT
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Read noise sensor (replace with actual sensor code)
  float noiseLevel = analogRead(A0) / 4096.0 * 100.0; // Example conversion
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["device_id"] = device_id;
  doc["lat"] = sensor_lat;
  doc["lon"] = sensor_lon;
  doc["db"] = noiseLevel;
  doc["timestamp"] = millis();
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  // Publish to MQTT
  String topic = "noise/" + String(device_id) + "/data";
  client.publish(topic.c_str(), buffer);
  
  delay(5000); // Send every 5 seconds
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect(device_id)) {
      Serial.println("MQTT Connected");
    } else {
      delay(5000);
    }
  }
}
```

## 🧪 Testing Without ESP32

Use the Python simulator to generate test data:

1. **Install MQTT client**:
```bash
pip install paho-mqtt
```

2. **Run simulator**:
```python
import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client()
client.connect("YOUR_PI_IP", 1883, 60)

while True:
    payload = {
        "device_id": "esp32-sim1",
        "lat": 12.91,
        "lon": 77.68, 
        "db": round(random.uniform(40, 80), 1),
        "timestamp": int(time.time() * 1000)
    }
    client.publish("noise/esp32-sim1/data", json.dumps(payload))
    print("Published:", payload)
    time.sleep(3)
```

## 📁 Project Structure

```
mqtt-noise-map-ui/
├── public/
│   └── index.html          # Custom HTML with loading animations
├── src/
│   ├── components/
│   │   ├── NoiseMap.js     # Interactive map component
│   │   └── NoiseMap.css    # Map styling
│   ├── mqtt/
│   │   └── mqttService.js  # MQTT client service
│   ├── App.js              # Main app component  
│   ├── App.css             # App styling
│   ├── index.js            # Entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
├── .env.example           # Environment configuration template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🎨 Customization

### Color Scheme
Modify CSS custom properties in `src/index.css`:
```css
:root {
  --primary-color: #00d4ff;
  --secondary-color: #ff6b35;
  --background-gradient: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 75%, #0f3460 100%);
}
```

### Map Styles
Change map tile layers in `src/components/NoiseMap.js`:
```javascript
const mapStyles = {
  dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
};
```

### Noise Level Colors
Adjust color scale in `src/components/NoiseMap.js`:
```javascript
const getNoiseColor = (db) => {
  if (db < 30) return '#4caf50'; // Green - Very quiet
  if (db < 50) return '#cddc39'; // Yellow - Moderate  
  if (db < 70) return '#ff9800'; // Orange - Loud
  return '#f44336'; // Red - Very loud
};
```

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Web Server
Copy the `build/` folder contents to your web server.

### Deploy with Docker
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
```

## 📊 Data Format

ESP32 sensors should send JSON data in this format:

```json
{
  "device_id": "esp32-001",
  "lat": 12.912,
  "lon": 77.675,
  "db": 65.3,
  "timestamp": 1721670783000
}
```

## 🔒 Security Considerations

- Use authentication for production MQTT brokers
- Enable TLS/WSS encryption for MQTT connections  
- Implement rate limiting for sensor data
- Validate all incoming sensor data
- Use environment variables for sensitive configuration

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused Error**:
   - Check if MQTT broker is running
   - Verify IP address and port in `.env.local`
   - Ensure firewall allows WebSocket connections on port 9001

2. **No Sensor Data**:
   - Verify ESP32s are connected to WiFi
   - Check MQTT topic names match between ESP32 and UI
   - Use MQTT client to test broker connectivity

3. **Build Errors**:
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` to reinstall dependencies
   - Check Node.js version compatibility

## 📈 Performance Tips

- Limit sensor update frequency to avoid overwhelming the UI
- Use QoS 0 for MQTT messages to reduce overhead
- Implement sensor data retention policies
- Consider using MQTT retained messages for latest sensor states

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)  
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Leaflet](https://leafletjs.com/) for the interactive maps
- [MQTT.js](https://github.com/mqttjs/MQTT.js) for WebSocket MQTT client
- [React](https://reactjs.org/) for the UI framework
- [Framer Motion](https://www.framer.com/motion/) for smooth animations

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the MQTT broker logs for connection issues

---

Made with 💙 for environmental monitoring