#!/usr/bin/env python3
"""
Simplified MQTT Noise Data Processor for Raspberry Pi
Works with mqtt_broker_server.py to process ESP32 sensor data and create interpolated noise maps
"""

import json
import time
import logging
import paho.mqtt.client as mqtt
import numpy as np
import threading
import sys

# Set console encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging with UTF-8 encoding for emoji support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('noise_processor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimpleNoiseProcessor:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id="simple_noise_processor")
        self.sensor_data = {}
        
        # MQTT setup
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Processing parameters
        self.update_interval = 2  # seconds
        self.max_sensor_age = 300  # 5 minutes
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info("✅ Connected to MQTT broker successfully")
            # Subscribe to processing requests
            client.subscribe("noise/process_request")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        logger.warning(f"❌ Disconnected from MQTT broker: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Process incoming processing requests"""
        try:
            payload = json.loads(msg.payload.decode())
            
            if msg.topic == "noise/process_request":
                self.handle_processing_request(payload)
                
        except json.JSONDecodeError:
            logger.error(f"⚠️ Invalid JSON in message: {msg.payload}")
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    def handle_processing_request(self, payload):
        """Handle interpolation processing requests"""
        try:
            sensors = payload.get('sensors', [])
            if len(sensors) < 2:
                logger.warning("⚠️ Not enough sensors for interpolation")
                return
            
            logger.info(f"🔄 Processing interpolation for {len(sensors)} sensors")
            
            # Create interpolated grid
            interpolated_data = self.create_interpolated_grid(sensors)
            
            if interpolated_data:
                # Publish processed data
                self.client.publish("noise/processed", json.dumps(interpolated_data))
                logger.info("📈 Published interpolated data")
            
        except Exception as e:
            logger.error(f"❌ Error in processing request: {e}")
    
    def create_interpolated_grid(self, sensors):
        """Create interpolated noise grid using Inverse Distance Weighting (IDW)"""
        try:
            if len(sensors) < 2:
                return None
            
            logger.info(f"🗺️ Creating interpolated grid for {len(sensors)} sensors")
            
            # Extract sensor positions and values
            lats = [s['lat'] for s in sensors]
            lons = [s['lon'] for s in sensors]
            dbs = [s['db'] for s in sensors]
            
            # Define grid bounds with padding
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            
            # Add padding (2% of the range or minimum padding)
            lat_range = max_lat - min_lat
            lon_range = max_lon - min_lon
            max_range = max(lat_range, lon_range)
            padding = max(max_range * 0.02, 0.001)  # 2% padding or minimum 0.001 degrees
            
            min_lat -= padding
            max_lat += padding
            min_lon -= padding
            max_lon += padding
            
            # Adaptive grid resolution based on area
            if max_range < 1:
                grid_res = 60  # High resolution for local areas
            elif max_range < 5:
                grid_res = 40  # Medium resolution
            else:
                grid_res = 30  # Lower resolution for large areas
            
            grid_size = [grid_res, grid_res]
            
            # Create coordinate grids
            lat_step = (max_lat - min_lat) / (grid_size[1] - 1)
            lon_step = (max_lon - min_lon) / (grid_size[0] - 1)
            
            # Generate interpolated values using IDW
            values = []
            min_db = float('inf')
            max_db = float('-inf')
            
            for i in range(grid_size[1]):
                for j in range(grid_size[0]):
                    # Current grid point coordinates
                    lat = max_lat - (i * lat_step)  # North to south
                    lon = min_lon + (j * lon_step)  # West to east
                    
                    # Calculate weighted average using IDW
                    weighted_sum = 0
                    weight_sum = 0
                    
                    for k, sensor in enumerate(sensors):
                        # Calculate distance
                        delta_lat = lat - sensor['lat']
                        delta_lon = lon - sensor['lon']
                        # Use approximate distance (good enough for IDW)
                        distance_sq = delta_lat**2 + (delta_lon * np.cos(np.radians(lat)))**2
                        
                        # IDW weight calculation (power = 2)
                        if distance_sq == 0:
                            # Exact match - use sensor value directly
                            weighted_sum = sensor['db']
                            weight_sum = 1
                            break
                        else:
                            weight = 1 / (distance_sq + 1e-10)  # Add small epsilon to prevent division by zero
                            weighted_sum += sensor['db'] * weight
                            weight_sum += weight
                    
                    if weight_sum > 0:
                        interpolated_value = weighted_sum / weight_sum
                        values.append(interpolated_value)
                        min_db = min(min_db, interpolated_value)
                        max_db = max(max_db, interpolated_value)
                    else:
                        values.append(0)
            
            # Create result structure compatible with React frontend
            result = {
                'type': 'interpolated_grid',
                'interpolated_grid': {
                    'bounds': [[min_lat, min_lon], [max_lat, max_lon]],
                    'grid_size': grid_size,
                    'values': values,
                    'min_db': min_db,
                    'max_db': max_db
                },
                'sensor_count': len(sensors),
                'timestamp': int(time.time() * 1000),
                'processing_time': time.time()
            }
            
            logger.info(f"📊 Grid created: {grid_size[0]}x{grid_size[1]}, dB range: {min_db:.1f}-{max_db:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creating interpolated grid: {e}")
            return None
    
    def start(self):
        """Start the processor"""
        try:
            logger.info("🚀 Starting Simple Noise Processor...")
            
            # Connect to MQTT broker
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Start the MQTT loop
            self.client.loop_forever()
            
        except KeyboardInterrupt:
            logger.info("🛑 Processor stopped by user")
            self.client.disconnect()
        except Exception as e:
            logger.error(f"❌ Processor error: {e}")
            self.client.disconnect()


def main():
    """Main entry point"""
    processor = SimpleNoiseProcessor()
    processor.start()


if __name__ == "__main__":
    main()
