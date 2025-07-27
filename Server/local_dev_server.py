#!/usr/bin/env python3
"""
ESP32 simulation client that connects to Pi server
Simulates ESP32 devices sending data to the Pi's MQTT broker
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
import sys
import os
import paho.mqtt.client as mqtt

# Add current directory to path for config_loader
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
connected_clients = set()
devices = []
config = None

# Predefined device locations (same as fake_esp32.py)
DEVICE_LOCATIONS = [
    {"id": "esp32-001", "name": "Entc", "lat": 6.7964368148947765, "lon": 79.90115269520993},
    {"id": "esp32-002", "name": "Landscape", "lat": 6.795970586191689, "lon": 79.90096694791089},
    {"id": "esp32-003", "name": "Sentra-court", "lat": 6.796370339052377, "lon": 79.90072317233378},
    {"id": "esp32-004", "name": "CITec", "lat": 6.796500450067444, "lon": 79.90172181262183},
    {"id": "esp32-005", "name": "Sumanadasa", "lat": 6.79677330410568, "lon": 79.90057941901183},
]

class VirtualESP32Device:
    def __init__(self, device_info):
        self.device_id = device_info["id"]
        self.name = device_info["name"]
        self.lat = device_info["lat"]
        self.lon = device_info["lon"]
        self.pattern = random.choice(['quiet', 'moderate', 'busy', 'industrial'])
        
    def generate_noise_level(self):
        """Generate realistic noise levels based on pattern"""
        base_levels = {
            'quiet': (30, 50),
            'moderate': (45, 70),
            'busy': (55, 80),
            'industrial': (65, 110)
        }
        
        min_db, max_db = base_levels[self.pattern]
        # Add some randomness and time-based variation
        variation = random.uniform(-5, 5)
        time_factor = abs(random.gauss(0, 3))
        
        db_level = random.uniform(min_db, max_db) + variation + time_factor
        return round(max(30, min(120, db_level)), 1)
    
    def get_sensor_data(self):
        """Generate sensor data packet"""
        return {
            "device_id": self.device_id,
            "lat": self.lat,
            "lon": self.lon,
            "db": self.generate_noise_level(),
            "timestamp": int(time.time() * 1000),
            "location_name": self.name
        }

async def simulate_devices():
    """Continuously generate sensor data"""
    while True:
        try:
            if connected_clients:
                # Generate data for all devices
                for device in devices:
                    sensor_data = device.get_sensor_data()
                    
                    # Create message in same format as MQTT version
                    message = {
                        "type": "sensor_data",
                        "topic": f"noise/{device.device_id}",
                        "payload": sensor_data,
                        "timestamp": int(time.time() * 1000)
                    }
                    
                    # Send to all connected clients
                    disconnected_clients = []
                    for client in connected_clients.copy():
                        try:
                            await client.send(json.dumps(message))
                            logger.info(f"📤 Sent {device.device_id}: {sensor_data['db']} dB")
                        except Exception as e:
                            logger.error(f"Failed to send to client: {e}")
                            disconnected_clients.append(client)
                    
                    # Remove disconnected clients
                    for client in disconnected_clients:
                        connected_clients.discard(client)
                
                # Wait before next data generation
                await asyncio.sleep(3)  # Send data every 3 seconds
            else:
                await asyncio.sleep(1)  # Wait for clients
                
        except Exception as e:
            logger.error(f"Error in device simulation: {e}")
            await asyncio.sleep(1)

async def handle_client(websocket):
    logger.info(f"🌐 New client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "Connected to local noise monitoring system (direct simulation)",
            "devices": len(devices)
        }))
        
        # Keep connection alive and handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"📨 Received from client: {data}")
                
                # Handle different message types
                if data.get('type') == 'get_devices':
                    device_list = [
                        {
                            "device_id": dev.device_id,
                            "name": dev.name,
                            "lat": dev.lat,
                            "lon": dev.lon,
                            "pattern": dev.pattern
                        }
                        for dev in devices
                    ]
                    await websocket.send(json.dumps({
                        "type": "device_list",
                        "devices": device_list
                    }))
                else:
                    # Echo back
                    await websocket.send(json.dumps({
                        "type": "echo",
                        "data": data
                    }))
                    
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("🔌 Client disconnected")
    finally:
        connected_clients.discard(websocket)

async def main():
    global config, devices
    
    # Load configuration
    config = get_config()
    websocket_port = config.get_websocket_port()
    
    # Initialize virtual devices
    devices = [VirtualESP32Device(device_info) for device_info in DEVICE_LOCATIONS[:5]]
    
    logger.info("🚀 Starting Local Development Server")
    logger.info(f"📱 Initialized {len(devices)} virtual ESP32 devices")
    for device in devices:
        logger.info(f"   {device.device_id} ({device.name}) - {device.pattern} pattern")
    
    # Start device simulation
    asyncio.create_task(simulate_devices())
    
    # Start WebSocket server
    logger.info(f"🌐 Starting WebSocket server on port {websocket_port}...")
    
    async with websockets.serve(handle_client, "0.0.0.0", websocket_port,
                               ping_interval=20, ping_timeout=10):
        logger.info("✅ Local development server running!")
        logger.info("🌐 React UI should connect to: ws://localhost:9001")
        logger.info("📊 Sensor data will be generated automatically")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Local development server stopped by user")
