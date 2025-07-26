/*
 * ESP32 Noise Sensor for Noise Mapping System
 * Configurable for both local development and Raspberry Pi connection
 * 
 * Instructions:
 * 1. Update WiFi credentials below
 * 2. Choose connection mode:
 *    - LOCAL_MODE: Connect to local development setup
 *    - PI_MODE: Connect to Raspberry Pi at 192.168.1.11
 *    - CUSTOM_MODE: Use custom IP address
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ============== CONFIGURATION ==============

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Connection Mode Selection
#define LOCAL_MODE    1
#define PI_MODE       2
#define CUSTOM_MODE   3

// Choose your mode here:
#define CONNECTION_MODE PI_MODE

// MQTT Server Configuration based on mode
#if CONNECTION_MODE == LOCAL_MODE
  const char* mqtt_server = "192.168.1.100";  // Replace with your local PC IP
  const char* mode_name = "LOCAL";
#elif CONNECTION_MODE == PI_MODE
  const char* mqtt_server = "192.168.1.11";   // Raspberry Pi IP
  const char* mode_name = "RASPBERRY_PI";
#elif CONNECTION_MODE == CUSTOM_MODE
  const char* mqtt_server = "192.168.1.XXX";  // Replace with your custom IP
  const char* mode_name = "CUSTOM";
#endif

const int mqtt_port = 1883;

// Device Configuration
const char* device_id = "esp32-001";          // Unique device ID
const char* location_name = "Office Desk";     // Human readable location
const float device_lat = 20.5937;             // Device latitude
const float device_lon = 78.9629;             // Device longitude

// MQTT Topics
const char* data_topic = "noise/data";
const char* status_topic = "noise/status";

// Timing Configuration
const unsigned long publish_interval = 5000;  // 5 seconds
const unsigned long wifi_timeout = 10000;     // 10 seconds
const unsigned long mqtt_timeout = 5000;      // 5 seconds

// ============== GLOBAL VARIABLES ==============

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastPublish = 0;
int noise_readings[10];  // For averaging
int reading_index = 0;
bool wifi_connected = false;
bool mqtt_connected = false;

// ============== SETUP ==============

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("========================================");
  Serial.println("   ESP32 Noise Sensor Starting Up");
  Serial.println("========================================");
  Serial.printf("Device ID: %s\n", device_id);
  Serial.printf("Location: %s\n", location_name);
  Serial.printf("Mode: %s\n", mode_name);
  Serial.printf("MQTT Server: %s:%d\n", mqtt_server, mqtt_port);
  Serial.println("========================================");
  
  // Initialize noise sensor (using ADC pin)
  pinMode(A0, INPUT);  // Noise sensor connected to A0
  
  // Initialize readings array
  for(int i = 0; i < 10; i++) {
    noise_readings[i] = 0;
  }
  
  // Connect to WiFi
  connectWiFi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  Serial.println("✅ Setup complete!");
}

// ============== MAIN LOOP ==============

void loop() {
  // Check WiFi connection
  if (!wifi_connected && WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  
  // Check MQTT connection
  if (wifi_connected && !client.connected()) {
    connectMQTT();
  }
  
  // Process MQTT messages
  if (mqtt_connected) {
    client.loop();
  }
  
  // Publish sensor data
  if (mqtt_connected && millis() - lastPublish > publish_interval) {
    publishSensorData();
    lastPublish = millis();
  }
  
  delay(100);
}

// ============== WIFI FUNCTIONS ==============

void connectWiFi() {
  Serial.printf("🔌 Connecting to WiFi: %s", ssid);
  WiFi.begin(ssid, password);
  
  unsigned long start_time = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start_time < wifi_timeout) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifi_connected = true;
    Serial.println();
    Serial.printf("✅ WiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("📶 Signal strength: %d dBm\n", WiFi.RSSI());
  } else {
    wifi_connected = false;
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
  }
}

// ============== MQTT FUNCTIONS ==============

void connectMQTT() {
  Serial.printf("🔗 Connecting to MQTT broker: %s:%d", mqtt_server, mqtt_port);
  
  String client_id = String(device_id) + "-" + String(random(0xffff), HEX);
  
  unsigned long start_time = millis();
  while (!client.connected() && millis() - start_time < mqtt_timeout) {
    if (client.connect(client_id.c_str())) {
      mqtt_connected = true;
      Serial.println();
      Serial.printf("✅ MQTT connected! Client ID: %s\n", client_id.c_str());
      
      // Publish device status
      publishDeviceStatus("online");
      
    } else {
      Serial.print(".");
      delay(500);
    }
  }
  
  if (!mqtt_connected) {
    Serial.println();
    Serial.printf("❌ MQTT connection failed! State: %d\n", client.state());
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages if needed
  Serial.printf("📨 Message received on topic: %s\n", topic);
}

// ============== SENSOR FUNCTIONS ==============

float readNoiseSensor() {
  // Read analog value from noise sensor
  int analog_value = analogRead(A0);
  
  // Convert to decibel approximation (this is sensor-specific)
  // You'll need to calibrate this based on your actual noise sensor
  float voltage = (analog_value / 4095.0) * 3.3;  // ESP32 ADC
  float decibels = 50.0 + (voltage * 20.0);       // Simple approximation
  
  // Add some realistic variation
  decibels += random(-5, 5);
  
  // Store in readings array for averaging
  noise_readings[reading_index] = (int)decibels;
  reading_index = (reading_index + 1) % 10;
  
  return decibels;
}

float getAverageNoise() {
  float total = 0;
  for(int i = 0; i < 10; i++) {
    total += noise_readings[i];
  }
  return total / 10.0;
}

// ============== PUBLISHING FUNCTIONS ==============

void publishSensorData() {
  // Read current noise level
  float current_noise = readNoiseSensor();
  float average_noise = getAverageNoise();
  
  // Create JSON payload
  DynamicJsonDocument doc(512);
  doc["device_id"] = device_id;
  doc["location"] = location_name;
  doc["latitude"] = device_lat;
  doc["longitude"] = device_lon;
  doc["noise_level"] = current_noise;
  doc["noise_average"] = average_noise;
  doc["timestamp"] = millis();
  doc["battery_level"] = random(70, 100);  // Simulated battery level
  doc["signal_strength"] = WiFi.RSSI();
  doc["mode"] = mode_name;
  
  // Convert to string
  String payload;
  serializeJson(doc, payload);
  
  // Publish to MQTT
  if (client.publish(data_topic, payload.c_str())) {
    Serial.printf("📊 Published: %.1f dB (avg: %.1f dB)\n", current_noise, average_noise);
  } else {
    Serial.println("❌ Failed to publish sensor data");
    mqtt_connected = false;
  }
}

void publishDeviceStatus(const char* status) {
  DynamicJsonDocument doc(256);
  doc["device_id"] = device_id;
  doc["status"] = status;
  doc["location"] = location_name;
  doc["mode"] = mode_name;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["timestamp"] = millis();
  
  String payload;
  serializeJson(doc, payload);
  
  if (client.publish(status_topic, payload.c_str())) {
    Serial.printf("📡 Status published: %s\n", status);
  }
}

// ============== UTILITY FUNCTIONS ==============

void printDeviceInfo() {
  Serial.println("========================================");
  Serial.println("           DEVICE INFORMATION");
  Serial.println("========================================");
  Serial.printf("Device ID: %s\n", device_id);
  Serial.printf("Location: %s\n", location_name);
  Serial.printf("Coordinates: %.4f, %.4f\n", device_lat, device_lon);
  Serial.printf("Mode: %s\n", mode_name);
  Serial.printf("MQTT Server: %s:%d\n", mqtt_server, mqtt_port);
  Serial.printf("WiFi SSID: %s\n", ssid);
  Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());
  Serial.println("========================================");
}
