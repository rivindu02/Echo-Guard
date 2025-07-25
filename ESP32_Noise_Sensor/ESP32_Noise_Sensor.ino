/*
ESP32 Noise Sensor - Sends data to Raspberry Pi Hub
This sketch captures noise data and sends it via WebSocket to the Pi hub
*/

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Raspberry Pi Hub connection
const char* hub_host = "192.168.1.100";  // Replace with your Pi's IP
const int hub_port = 9999;               // ESP32 connection port

// Sensor configuration
const String DEVICE_ID = "esp32-sensor-001";  // Unique ID for this sensor
const float LATITUDE = 20.5937;               // Update with actual coordinates
const float LONGITUDE = 78.9629;
const String LOCATION = "ESP32 Sensor Location";

// Hardware pins
const int ANALOG_PIN = A0;    // Analog pin for noise sensor
const int LED_PIN = 2;        // Built-in LED

// Timing
unsigned long lastSensorRead = 0;
unsigned long lastHeartbeat = 0;
const unsigned long SENSOR_INTERVAL = 1000;    // Send data every 1 second
const unsigned long HEARTBEAT_INTERVAL = 30000; // Heartbeat every 30 seconds

WebSocketsClient webSocket;
bool connected = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(ANALOG_PIN, INPUT);
  
  Serial.println("🚀 ESP32 Noise Sensor Starting...");
  Serial.println("Device ID: " + DEVICE_ID);
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup WebSocket
  setupWebSocket();
}

void loop() {
  webSocket.loop();
  
  unsigned long currentTime = millis();
  
  // Send sensor data
  if (connected && (currentTime - lastSensorRead >= SENSOR_INTERVAL)) {
    sendSensorData();
    lastSensorRead = currentTime;
  }
  
  // Send heartbeat
  if (connected && (currentTime - lastHeartbeat >= HEARTBEAT_INTERVAL)) {
    sendHeartbeat();
    lastHeartbeat = currentTime;
  }
  
  delay(100);
}

void connectToWiFi() {
  Serial.print("🔌 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(1000);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Blink LED
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("📍 IP address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_PIN, HIGH); // LED on when connected
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    digitalWrite(LED_PIN, LOW);
  }
}

void setupWebSocket() {
  Serial.print("🌐 Connecting to Pi Hub: ");
  Serial.print(hub_host);
  Serial.print(":");
  Serial.println(hub_port);
  
  webSocket.begin(hub_host, hub_port, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("❌ WebSocket Disconnected");
      connected = false;
      digitalWrite(LED_PIN, LOW);
      break;
      
    case WStype_CONNECTED:
      Serial.printf("✅ WebSocket Connected to: %s\n", payload);
      connected = true;
      digitalWrite(LED_PIN, HIGH);
      sendDeviceInfo();
      break;
      
    case WStype_TEXT:
      Serial.printf("📨 Received: %s\n", payload);
      handleMessage((char*)payload);
      break;
      
    case WStype_ERROR:
      Serial.println("❌ WebSocket Error");
      connected = false;
      break;
      
    default:
      break;
  }
}

void handleMessage(String message) {
  // Parse incoming messages from Pi hub
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.println("⚠️ Failed to parse JSON message");
    return;
  }
  
  String messageType = doc["type"];
  
  if (messageType == "ping") {
    // Respond to ping
    sendPong();
  } else if (messageType == "config_update") {
    // Handle configuration updates
    Serial.println("🔧 Received config update");
  }
}

float readNoiseLevel() {
  // Read analog value from noise sensor
  int rawValue = analogRead(ANALOG_PIN);
  
  // Convert to noise level in dB
  // This is a simplified conversion - adjust based on your sensor
  float voltage = (rawValue / 4095.0) * 3.3; // ESP32 ADC reference
  float noiseLevel = 30 + (voltage / 3.3) * 60; // Scale to 30-90 dB range
  
  // Add some variation for testing
  noiseLevel += random(-5, 5);
  
  // Ensure reasonable range
  noiseLevel = constrain(noiseLevel, 30, 90);
  
  return noiseLevel;
}

int getBatteryLevel() {
  // If using battery, read battery voltage here
  // For now, return simulated value
  return random(70, 100);
}

int getSignalStrength() {
  // Get WiFi signal strength
  return WiFi.RSSI();
}

void sendSensorData() {
  if (!connected) return;
  
  float noiseLevel = readNoiseLevel();
  
  // Create JSON payload
  DynamicJsonDocument doc(1024);
  doc["type"] = "sensor_data";
  doc["device_id"] = DEVICE_ID;
  doc["latitude"] = LATITUDE;
  doc["longitude"] = LONGITUDE;
  doc["location"] = LOCATION;
  doc["noise_level"] = round(noiseLevel * 10) / 10.0; // Round to 1 decimal
  doc["timestamp"] = WiFi.getTime() * 1000; // Convert to milliseconds
  doc["battery_level"] = getBatteryLevel();
  doc["signal_strength"] = getSignalStrength();
  doc["status"] = "online";
  
  // Add sensor-specific info
  doc["sensor_type"] = "esp32";
  doc["firmware_version"] = "1.0.0";
  doc["free_heap"] = ESP.getFreeHeap();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
  
  Serial.print("📊 Sent noise level: ");
  Serial.print(noiseLevel);
  Serial.println(" dB");
}

void sendDeviceInfo() {
  if (!connected) return;
  
  // Send device information on connection
  DynamicJsonDocument doc(1024);
  doc["type"] = "device_info";
  doc["device_id"] = DEVICE_ID;
  doc["device_type"] = "esp32_noise_sensor";
  doc["firmware_version"] = "1.0.0";
  doc["mac_address"] = WiFi.macAddress();
  doc["ip_address"] = WiFi.localIP().toString();
  doc["chip_id"] = String((uint32_t)ESP.getEfuseMac(), HEX);
  doc["flash_size"] = ESP.getFlashChipSize();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["location"] = LOCATION;
  doc["latitude"] = LATITUDE;
  doc["longitude"] = LONGITUDE;
  doc["timestamp"] = WiFi.getTime() * 1000;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
  
  Serial.println("📋 Sent device info");
}

void sendHeartbeat() {
  if (!connected) return;
  
  DynamicJsonDocument doc(512);
  doc["type"] = "heartbeat";
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = WiFi.getTime() * 1000;
  doc["uptime"] = millis();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["signal_strength"] = WiFi.RSSI();
  doc["status"] = "online";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
  
  Serial.println("💓 Sent heartbeat");
}

void sendPong() {
  if (!connected) return;
  
  DynamicJsonDocument doc(256);
  doc["type"] = "pong";
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = WiFi.getTime() * 1000;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
}
