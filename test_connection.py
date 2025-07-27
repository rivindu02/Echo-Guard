#!/usr/bin/env python3
"""
Test script to send fake sensor data to the MQTT broker
This will help verify the connection between Python MQTT server and React UI
Now supports connecting to Raspberry Pi
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import sys

# Configuration - change PI_IP to your Raspberry Pi's IP
PI_IP = "192.168.1.12"  # Change this to your Pi's IP
MQTT_PORT = 1883
USE_PI = True  # Set to True to connect to Pi, False for localhost

def get_broker_config():
    """Get broker configuration"""
    if USE_PI:
        print(f"🥧 Connecting to Raspberry Pi: {PI_IP}:{MQTT_PORT}")
        return PI_IP, MQTT_PORT
    else:
        print(f"🖥️ Connecting to localhost: localhost:{MQTT_PORT}")
        return "localhost", MQTT_PORT

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker successfully")
    else:
        print(f"❌ Failed to connect: {rc}")

def send_test_data():
    """Send fake sensor data to test the connection"""
    client = mqtt.Client(client_id="test_sender")
    client.on_connect = on_connect
    
    try:
        # Get broker configuration
        broker_host, broker_port = get_broker_config()
        
        # Connect to the MQTT broker
        client.connect(broker_host, broker_port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(1)
        
        # Send some test sensor data
        test_sensors = [
            {"device_id": "ESP32-001", "lat": 20.5937, "lon": 78.9629, "db": 45.2},
            {"device_id": "ESP32-002", "lat": 20.5940, "lon": 78.9635, "db": 52.8},
            {"device_id": "ESP32-003", "lat": 20.5945, "lon": 78.9642, "db": 38.5},
        ]
        
        for i in range(10):  # Send 10 rounds of data
            for sensor in test_sensors:
                # Add some randomness to the data
                sensor_data = {
                    "device_id": sensor["device_id"],
                    "lat": sensor["lat"] + random.uniform(-0.001, 0.001),
                    "lon": sensor["lon"] + random.uniform(-0.001, 0.001),
                    "db": sensor["db"] + random.uniform(-5, 5),
                    "timestamp": int(time.time() * 1000)
                }
                
                # Send to noise topic
                topic = f"noise/{sensor['device_id']}"
                payload = json.dumps(sensor_data)
                
                client.publish(topic, payload)
                print(f"📤 Sent: {topic} -> {payload}")
                
                time.sleep(0.5)  # Small delay between sensors
            
            print(f"📊 Round {i+1} completed")
            time.sleep(2)  # Wait 2 seconds between rounds
        
        client.loop_stop()
        client.disconnect()
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Starting connection test...")
    send_test_data()
