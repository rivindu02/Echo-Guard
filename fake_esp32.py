#!/usr/bin/env python3
"""
Fake ESP32 Noise Sensor Simulator
Simulates multiple ESP32 devices publishing noise sensor data to MQTT
Compatible with both the React UI and the mqtt_processor.py
"""

import json
import time
import random
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FakeESP32Device:
    def __init__(self, device_id, lat, lon, location_name, mqtt_client):
        self.device_id = device_id
        self.lat = lat
        self.lon = lon
        self.location_name = location_name
        self.mqtt_client = mqtt_client
        self.is_running = False
        self.thread = None
        
        # Simulation parameters
        self.base_noise = random.uniform(40, 60)  # Base noise level
        self.noise_pattern = random.choice(['quiet', 'moderate', 'busy', 'industrial'])
        self.battery_level = random.randint(70, 100)
        self.signal_strength = random.randint(-70, -30)
        
        # Set noise patterns
        if self.noise_pattern == 'quiet':
            self.base_noise = random.uniform(35, 50)
        elif self.noise_pattern == 'moderate':
            self.base_noise = random.uniform(45, 65)
        elif self.noise_pattern == 'busy':
            self.base_noise = random.uniform(60, 75)
        elif self.noise_pattern == 'industrial':
            self.base_noise = random.uniform(70, 85)
    
    def generate_noise_reading(self):
        """Generate realistic noise reading"""
        # Add some random variation
        variation = random.uniform(-10, 15)
        
        # Add time-based patterns (higher during day)
        hour = datetime.now().hour
        if 6 <= hour <= 22:  # Daytime
            time_factor = 5
        elif 22 <= hour <= 24 or 0 <= hour <= 6:  # Nighttime
            time_factor = -8
        else:
            time_factor = 0
        
        # Calculate final noise level
        noise_level = self.base_noise + variation + time_factor
        
        # Add occasional spikes
        if random.random() < 0.1:  # 10% chance of spike
            noise_level += random.uniform(10, 25)
        
        # Ensure realistic bounds
        noise_level = max(25, min(120, noise_level))
        
        return round(noise_level, 1)
    
    def simulate_battery_drain(self):
        """Simulate battery draining"""
        if random.random() < 0.02:  # 2% chance to drain battery
            self.battery_level = max(0, self.battery_level - 1)
    
    def create_data_payload(self):
        """Create data payload compatible with React UI"""
        noise_level = self.generate_noise_reading()
        self.simulate_battery_drain()
        
        # Exact format expected by React UI (minimal fields only)
        payload = {
            "device_id": self.device_id,
            "lat": self.lat,
            "lon": self.lon,
            "db": noise_level,
            "timestamp": int(time.time() * 1000)  # Unix timestamp in milliseconds
        }
        
        return payload
    
    def publish_data(self):
        """Publish sensor data to MQTT"""
        try:
            payload = self.create_data_payload()
            payload_json = json.dumps(payload)
            
            # Publish to multiple topic formats for compatibility
            topics = [
                f"noise/{self.device_id}",           # Legacy format
                f"noise/{self.device_id}/data",      # Standard format
                f"noise/sensor/{self.device_id}",    # Sensor format
                f"noise/device/{self.device_id}",    # Device format
                "test/message"                       # Simple test topic
            ]
            
            for topic in topics:
                result = self.mqtt_client.publish(topic, payload_json, qos=0)
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    logger.error(f"Failed to publish to {topic}")
                else:
                    logger.debug(f"✅ Published to {topic}: {payload_json}")
            
            logger.info(f"📡 {self.device_id}: {payload['db']} dB at ({self.lat:.4f}, {self.lon:.4f})")
            logger.info(f"🔍 Payload: {payload_json}")
            
        except Exception as e:
            logger.error(f"Error publishing data for {self.device_id}: {e}")
    
    def run_simulation(self, interval=5):
        """Run continuous simulation"""
        logger.info(f"🚀 Starting {self.device_id} simulation ({self.noise_pattern} pattern)")
        
        while self.is_running:
            self.publish_data()
            time.sleep(interval + random.uniform(-1, 1))  # Add some jitter
    
    def start(self, interval=5):
        """Start the device simulation in a separate thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self.run_simulation, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the device simulation"""
        self.is_running = False
        if self.thread:
            self.thread.join()

class ESP32Simulator:
    def __init__(self, broker_host="localhost", broker_port=1884):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.devices = []
        
        # MQTT setup
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        logger.warning(f"🔌 Disconnected from MQTT broker: {rc}")
    
    def add_device(self, device_id, lat, lon, location_name):
        """Add a simulated ESP32 device"""
        device = FakeESP32Device(device_id, lat, lon, location_name, self.client)
        self.devices.append(device)
        logger.info(f"➕ Added device: {device_id} at {location_name}")
    
    def create_sample_devices(self):
        """Create a single ESP32 device (like Pi server setup)"""
        # Single device to simulate one ESP32 sending data directly to UI
        device_data = ("esp32-001", 20.5937, 78.9629, "ESP32 Sensor")
        
        device_id, lat, lon, location = device_data
        self.add_device(device_id, lat, lon, location)
    
    def start_all_devices(self, interval=5):
        """Start all devices"""
        logger.info(f"🚀 Starting {len(self.devices)} ESP32 devices...")
        
        for i, device in enumerate(self.devices):
            # Stagger device starts to avoid simultaneous publishing
            time.sleep(i * 0.5)
            device.start(interval)
        
        logger.info("✅ All devices started")
    
    def stop_all_devices(self):
        """Stop all devices"""
        logger.info("🛑 Stopping all devices...")
        
        for device in self.devices:
            device.stop()
        
        logger.info("✅ All devices stopped")
    
    def run(self, interval=5):
        """Run the simulator"""
        try:
            # Connect to MQTT broker
            logger.info(f"🔌 Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Create sample devices if none exist
            if not self.devices:
                self.create_sample_devices()
            
            # Start all devices
            self.start_all_devices(interval)
            
            # Keep running
            logger.info("📡 ESP32 Simulator running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping ESP32 Simulator...")
            self.stop_all_devices()
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("👋 ESP32 Simulator stopped")
        
        except Exception as e:
            logger.error(f"❌ Simulator error: {e}")
            self.stop_all_devices()
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fake ESP32 Noise Sensor Simulator')
    parser.add_argument('--broker', default='localhost', help='MQTT broker hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=1884, help='MQTT broker port (default: 1884)')
    parser.add_argument('--interval', type=int, default=5, help='Publishing interval in seconds (default: 5)')
    parser.add_argument('--devices', type=int, default=1, help='Number of devices to simulate (default: 1)')
    
    args = parser.parse_args()
    
    # Create simulator
    simulator = ESP32Simulator(args.broker, args.port)
    
    # Add custom devices or use samples
    if args.devices != 1:
        # Generate random devices around a central point
        center_lat, center_lon = 20.5937, 78.9629
        for i in range(args.devices):
            device_id = f"esp32-{i+1:03d}"
            lat = center_lat + random.uniform(-0.05, 0.05)
            lon = center_lon + random.uniform(-0.05, 0.05)
            location = f"Location {i+1}"
            simulator.add_device(device_id, lat, lon, location)
    
    # Run simulator
    simulator.run(args.interval)
