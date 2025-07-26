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
import socket
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
    def __init__(self, broker_host="localhost", broker_port=1883):
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
        """Create sample ESP32 devices with hardcoded test locations
        
        Note: These are fixed coordinates for testing only.
        Real ESP32 devices use GPS modules to automatically determine
        and transmit their actual coordinates.
        """
        # Define 5 sensors at fixed test coordinates
        device_locations = [
            ("esp32-001", 6.7964368148947765, 79.90115269520993, "ENTC"),
            ("esp32-002", 6.795970586191689, 79.90096694791089, "Landscape"),
            ("esp32-003", 6.796370339052377, 79.90072317233378, "Sentra-court"),
            ("esp32-004", 6.796500450067444, 79.90172181262183, "CITec"),
            ("esp32-005", 6.79677330410568, 79.90057941901183, "Sumanadasa")
        ]
        
        for device_id, lat, lon, location in device_locations:
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
        """Run the simulator with retry logic"""
        max_retries = 5
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                # Connect to MQTT broker
                logger.info(f"🔌 Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
                if attempt > 0:
                    logger.info(f"   Attempt {attempt + 1}/{max_retries}")
                
                self.client.connect(self.broker_host, self.broker_port, 60)
                self.client.loop_start()
                
                logger.info("✅ Connected to MQTT broker successfully!")
                
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
                return
                
            except ConnectionRefusedError as e:
                logger.error(f"❌ Connection refused by {self.broker_host}:{self.broker_port}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    logger.info("💡 Make sure MQTT broker is running on the target machine:")
                    if self.broker_host == 'localhost' or self.broker_host == '127.0.0.1':
                        logger.info("   For localhost: python Server/mqtt_broker_server.py")
                    else:
                        logger.info(f"   For {self.broker_host}: python3 start_noise_system.py")
                        logger.info(f"   Or check: telnet {self.broker_host} {self.broker_port}")
                    time.sleep(retry_delay)
                    retry_delay += 2  # Increase delay for next attempt
                else:
                    logger.error("❌ Max retries reached. Cannot connect to MQTT broker.")
                    logger.error("")
                    logger.error("🔧 TROUBLESHOOTING STEPS:")
                    logger.error("========================")
                    if self.broker_host == 'localhost' or self.broker_host == '127.0.0.1':
                        logger.error("For LOCAL setup:")
                        logger.error("1. Start MQTT broker: python Server/mqtt_broker_server.py")
                        logger.error("2. Or use: ./start_local_system.bat")
                    else:
                        logger.error(f"For REMOTE setup ({self.broker_host}):")
                        logger.error(f"1. SSH to {self.broker_host}")
                        logger.error("2. Run: python3 start_noise_system.py")
                        logger.error("3. Check ports: sudo netstat -tlnp | grep :1883")
                        logger.error(f"4. Test connectivity: ping {self.broker_host}")
                        logger.error(f"5. Test port: telnet {self.broker_host} 1883")
                    logger.error("")
                    raise
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay += 2
                else:
                    logger.error("❌ Max retries reached due to unexpected errors.")
                    self.stop_all_devices()
                    raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fake ESP32 Noise Sensor Simulator')
    parser.add_argument('--broker', default='localhost', help='MQTT broker hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port (default: 1883)')
    parser.add_argument('--interval', type=int, default=5, help='Publishing interval in seconds (default: 5)')
    parser.add_argument('--devices', type=int, default=1, help='Number of devices to simulate (default: 1)')
    
    args = parser.parse_args()
    
    # Create simulator
    simulator = ESP32Simulator(args.broker, args.port)
    
    # Create devices based on --devices argument
    if args.devices <= 5:
        # Use predefined realistic locations (first N devices)
        simulator.create_sample_devices()
        # Keep only the requested number of devices
        simulator.devices = simulator.devices[:args.devices]
        logger.info(f"📋 Using first {args.devices} predefined device(s)")
    else:
        # Generate random devices around a central point for more than 5
        center_lat, center_lon = 20.5937, 78.9629
        for i in range(args.devices):
            device_id = f"esp32-{i+1:03d}"
            lat = center_lat + random.uniform(-0.05, 0.05)
            lon = center_lon + random.uniform(-0.05, 0.05)
            location = f"Location {i+1}"
            simulator.add_device(device_id, lat, lon, location)
        logger.info(f"📋 Generated {args.devices} random device(s)")
    
    # Run simulator
    simulator.run(args.interval)
