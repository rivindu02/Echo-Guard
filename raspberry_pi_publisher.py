#!/usr/bin/env python3
"""
Raspberry Pi MQTT Noise Data Publisher
This script simulates noise sensor data and publishes it to MQTT
"""

import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuration
MQTT_BROKER = "localhost"  # Since this runs on the Pi
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "noise"
DEVICE_ID = "rpi-001"

# Sensor location (update with your actual coordinates)
SENSOR_LOCATION = {
    "latitude": 20.5937,
    "longitude": 78.9629,
    "location": "Raspberry Pi Sensor"
}

class NoiseSensorPublisher:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            # Publish online status
            self.publish_status("online")
        else:
            print(f"❌ Failed to connect to MQTT broker. Return code: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print("🔌 Disconnected from MQTT broker")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def publish_status(self, status):
        """Publish device status"""
        status_data = {
            "device_id": DEVICE_ID,
            "status": status,
            "timestamp": int(time.time() * 1000)
        }
        
        topic = f"{MQTT_TOPIC_PREFIX}/device/{DEVICE_ID}/status"
        self.client.publish(topic, json.dumps(status_data), retain=True)
        print(f"📡 Published status: {status}")
    
    def read_noise_level(self):
        """
        Replace this with actual noise sensor reading
        For now, we'll simulate noise levels
        """
        # Simulate realistic noise levels (30-90 dB)
        base_noise = 45  # Background noise
        variation = random.uniform(-10, 30)  # Random variation
        noise_level = max(30, min(90, base_noise + variation))
        
        return round(noise_level, 1)
    
    def get_system_info(self):
        """Get system information (battery, signal, etc.)"""
        try:
            # For actual implementation, you might read from:
            # - Battery level from UPS/battery monitor
            # - WiFi signal strength
            # - CPU temperature, etc.
            
            return {
                "battery_level": random.randint(70, 100),  # Simulate battery
                "signal_strength": random.randint(-70, -30),  # dBm
                "cpu_temp": random.randint(40, 70),  # Celsius
                "memory_usage": random.randint(20, 80)  # Percentage
            }
        except:
            return {
                "battery_level": None,
                "signal_strength": None,
                "cpu_temp": None,
                "memory_usage": None
            }
    
    def publish_noise_data(self):
        """Read and publish noise sensor data"""
        try:
            # Read noise level
            noise_level = self.read_noise_level()
            
            # Get system info
            system_info = self.get_system_info()
            
            # Prepare data payload
            data = {
                "device_id": DEVICE_ID,
                "latitude": SENSOR_LOCATION["latitude"],
                "longitude": SENSOR_LOCATION["longitude"],
                "location": SENSOR_LOCATION["location"],
                "noise_level": noise_level,
                "timestamp": int(time.time() * 1000),  # Unix timestamp in milliseconds
                "battery_level": system_info["battery_level"],
                "signal_strength": system_info["signal_strength"],
                "cpu_temp": system_info["cpu_temp"],
                "memory_usage": system_info["memory_usage"]
            }
            
            # Publish to multiple topic formats for compatibility
            topics = [
                f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/data",
                f"{MQTT_TOPIC_PREFIX}/sensor/{DEVICE_ID}",
                f"{MQTT_TOPIC_PREFIX}/device/{DEVICE_ID}"
            ]
            
            for topic in topics:
                result = self.client.publish(topic, json.dumps(data))
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"📨 Published to {topic}: {noise_level} dB")
                else:
                    print(f"❌ Failed to publish to {topic}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error publishing data: {e}")
            return False
    
    def run(self, interval=5):
        """Run the publisher continuously"""
        print(f"🚀 Starting Noise Sensor Publisher for device: {DEVICE_ID}")
        print(f"📍 Location: {SENSOR_LOCATION['location']}")
        print(f"🔄 Publishing interval: {interval} seconds")
        
        if not self.connect():
            return
        
        try:
            while True:
                self.publish_noise_data()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping publisher...")
            self.publish_status("offline")
            self.client.loop_stop()
            self.client.disconnect()
            print("👋 Goodbye!")

if __name__ == "__main__":
    publisher = NoiseSensorPublisher()
    publisher.run(interval=5)  # Publish every 5 seconds
