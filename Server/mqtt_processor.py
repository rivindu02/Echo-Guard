#!/usr/bin/env python3
"""
MQTT Noise Data Processor for Raspberry Pi
Handles incoming ESP32 sensor data and processes it for real-time visualization
"""

import json
import time
import logging
import paho.mqtt.client as mqtt
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import threading
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/noise_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NoiseDataProcessor:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.sensor_data = {}
        self.processed_grid = None
        self.last_update = 0
        
        # MQTT setup
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Processing parameters
        self.grid_size = (50, 50)
        self.update_interval = 5  # seconds
        self.max_sensor_age = 300  # 5 minutes
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            # Subscribe to raw sensor data
            client.subscribe("noise/+")
            client.subscribe("noise/esp32/+")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        logger.warning(f"Disconnected from MQTT broker: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Process incoming sensor messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Validate required fields
            required_fields = ['device_id', 'lat', 'lon', 'db', 'timestamp']
            if not all(field in payload for field in required_fields):
                logger.warning(f"Invalid payload format: {payload}")
                return
            
            # Store sensor data
            device_id = payload['device_id']
            self.sensor_data[device_id] = {
                'lat': float(payload['lat']),
                'lon': float(payload['lon']),
                'db': float(payload['db']),
                'timestamp': int(payload['timestamp']),
                'received_at': int(time.time() * 1000)
            }
            
            logger.info(f"Received data from {device_id}: {payload['db']} dB")
            
            # Trigger processing if enough time has passed
            current_time = time.time()
            if current_time - self.last_update > self.update_interval:
                self.process_and_publish()
                self.last_update = current_time
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in message: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def cleanup_old_data(self):
        """Remove sensor data older than max_sensor_age"""
        current_time = int(time.time() * 1000)
        expired_sensors = []
        
        for device_id, data in self.sensor_data.items():
            age = (current_time - data['received_at']) / 1000
            if age > self.max_sensor_age:
                expired_sensors.append(device_id)
        
        for device_id in expired_sensors:
            del self.sensor_data[device_id]
            logger.info(f"Removed expired data for {device_id}")
    
    def process_and_publish(self):
        """Process sensor data and publish results"""
        self.cleanup_old_data()
        
        if len(self.sensor_data) < 2:
            logger.warning("Not enough sensor data for processing")
            return
        
        try:
            # Create processed data structure
            processed_data = {
                'sensor_data': list(self.sensor_data.values()),
                'processed_grid': self.generate_interpolated_grid(),
                'timestamp': int(time.time() * 1000),
                'active_sensors': len(self.sensor_data)
            }
            
            # Publish processed data
            self.client.publish(
                "noise/processed",
                json.dumps(processed_data),
                qos=1
            )
            
            logger.info(f"Published processed data with {len(self.sensor_data)} sensors")
            
        except Exception as e:
            logger.error(f"Error in processing: {e}")
    
    def generate_interpolated_grid(self):
        """Generate interpolated noise grid using IDW"""
        if len(self.sensor_data) < 2:
            return None
        
        # Extract sensor positions and values
        positions = []
        values = []
        
        for data in self.sensor_data.values():
            positions.append([data['lat'], data['lon']])
            values.append(data['db'])
        
        positions = np.array(positions)
        values = np.array(values)
        
        # Define grid bounds with padding
        lat_min, lat_max = positions[:, 0].min(), positions[:, 0].max()
        lon_min, lon_max = positions[:, 1].min(), positions[:, 1].max()
        
        # Add padding (0.001 degrees ≈ 100m)
        padding = 0.001
        lat_min -= padding
        lat_max += padding
        lon_min -= padding
        lon_max += padding
        
        # Create grid
        lat_grid = np.linspace(lat_min, lat_max, self.grid_size[0])
        lon_grid = np.linspace(lon_min, lon_max, self.grid_size[1])
        
        # Perform IDW interpolation
        grid_values = np.zeros(self.grid_size)
        
        for i, lat in enumerate(lat_grid):
            for j, lon in enumerate(lon_grid):
                # Calculate distances to all sensors
                distances = np.sqrt((positions[:, 0] - lat)**2 + (positions[:, 1] - lon)**2)
                
                # Avoid division by zero
                distances = np.maximum(distances, 1e-10)
                
                # IDW with power=2
                weights = 1.0 / (distances ** 2)
                grid_values[i, j] = np.sum(weights * values) / np.sum(weights)
        
        return {
            'bounds': {
                'lat_min': lat_min,
                'lat_max': lat_max,
                'lon_min': lon_min,
                'lon_max': lon_max
            },
            'grid_size': self.grid_size,
            'values': grid_values.flatten().tolist(),
            'min_db': float(grid_values.min()),
            'max_db': float(grid_values.max())
        }
    
    def start(self):
        """Start the MQTT processor"""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"Failed to start processor: {e}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MQTT Noise Data Processor')
    parser.add_argument('--broker', default='localhost', help='MQTT broker hostname')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    
    args = parser.parse_args()
    
    processor = NoiseDataProcessor(args.broker, args.port)
    
    try:
        processor.start()
    except KeyboardInterrupt:
        logger.info("Processor stopped by user")
    except Exception as e:
        logger.error(f"Processor failed: {e}")
