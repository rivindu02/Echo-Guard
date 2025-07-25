#!/usr/bin/env python3
"""
Python MQTT Broker and WebSocket Server for Noise Mapping System
Replaces the Node.js mqtt-broker.js functionality

This script creates:
1. An embedded MQTT broker using paho-mqtt
2. A WebSocket server for browser connections
3. Data processing and forwarding between ESP32 sensors and React UI
"""

import asyncio
import websockets
import json
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Set, Any
import paho.mqtt.client as mqtt
import threading
import time
from collections import defaultdict
import os

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
        logging.StreamHandler(),
        logging.FileHandler('mqtt_broker.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class MQTTBrokerServer:
    def __init__(self):
        # Configuration
        self.mqtt_port = 1884
        self.websocket_port = 9001
        self.broker_host = "localhost"
        
        # Data storage
        self.sensor_data: Dict[str, Any] = {}
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_subscriptions: Dict[websockets.WebSocketServerProtocol, Set[str]] = defaultdict(set)
        
        # MQTT client setup (acts as both broker relay and client)
        self.mqtt_client = mqtt.Client(client_id="broker_server")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        
        # Processing parameters
        self.last_interpolation = 0
        self.interpolation_interval = 2  # seconds
        
        # Shutdown flag
        self.shutdown_flag = threading.Event()
        
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback for MQTT client connection"""
        if rc == 0:
            logger.info("✅ Connected to MQTT broker successfully")
            # Subscribe to all noise-related topics
            client.subscribe("noise/+")
            client.subscribe("noise/esp32/+")
            client.subscribe("noise/processed")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """Callback for MQTT client disconnection"""
        logger.warning(f"❌ Disconnected from MQTT broker: {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """Process incoming MQTT messages and forward to WebSocket clients"""
        try:
            topic = msg.topic
            payload_str = msg.payload.decode()
            
            logger.info(f"📤 MQTT message on topic {topic}: {payload_str}")
            
            # Parse the payload
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Invalid JSON payload: {payload_str}")
                return
            
            # Handle sensor data
            if topic.startswith("noise/esp32/") or topic.startswith("noise/"):
                self.handle_sensor_data(topic, payload)
            
            # Handle processed interpolation data
            elif topic == "noise/processed":
                self.handle_processed_data(payload)
            
            # Forward to WebSocket clients
            asyncio.run_coroutine_threadsafe(
                self.broadcast_to_websocket_clients(topic, payload),
                self.websocket_loop
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
    
    def handle_sensor_data(self, topic, payload):
        """Process and store sensor data"""
        try:
            # Validate required fields
            required_fields = ['device_id', 'lat', 'lon', 'db', 'timestamp']
            if not all(field in payload for field in required_fields):
                logger.warning(f"⚠️ Invalid sensor payload format: {payload}")
                return
            
            device_id = payload['device_id']
            
            # Store sensor data with additional metadata
            self.sensor_data[device_id] = {
                'device_id': device_id,
                'lat': float(payload['lat']),
                'lon': float(payload['lon']),
                'db': float(payload['db']),
                'timestamp': int(payload['timestamp']),
                'received_at': int(time.time() * 1000),
                'topic': topic
            }
            
            logger.info(f"📊 Stored data from {device_id}: {payload['db']} dB at ({payload['lat']}, {payload['lon']})")
            
            # Trigger interpolation if enough time has passed
            current_time = time.time()
            if current_time - self.last_interpolation > self.interpolation_interval:
                self.trigger_interpolation()
                self.last_interpolation = current_time
                
        except Exception as e:
            logger.error(f"❌ Error handling sensor data: {e}")
    
    def handle_processed_data(self, payload):
        """Handle processed interpolation data"""
        logger.info("📈 Received processed interpolation data")
        # This data will be automatically forwarded to WebSocket clients
    
    def trigger_interpolation(self):
        """Trigger data interpolation and processing"""
        if len(self.sensor_data) >= 2:
            # Create a simple interpolation trigger message
            processed_data = {
                'type': 'interpolation_request',
                'sensor_count': len(self.sensor_data),
                'sensors': list(self.sensor_data.values()),
                'timestamp': int(time.time() * 1000)
            }
            
            # Publish to processing topic (could be handled by external processor)
            self.mqtt_client.publish("noise/process_request", json.dumps(processed_data))
            logger.info(f"🔄 Triggered interpolation for {len(self.sensor_data)} sensors")
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections from React UI"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🌐 WebSocket client connected: {client_id}")
        
        # Add client to the set
        self.websocket_clients.add(websocket)
        
        try:
            # Send current sensor data to new client
            await self.send_current_data_to_client(websocket)
            
            # Handle incoming messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_websocket_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Invalid JSON from WebSocket client: {message}")
                except Exception as e:
                    logger.error(f"❌ Error handling WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🌐 WebSocket client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"❌ WebSocket error for client {client_id}: {e}")
        finally:
            # Remove client from sets
            self.websocket_clients.discard(websocket)
            if websocket in self.client_subscriptions:
                del self.client_subscriptions[websocket]
    
    async def handle_websocket_message(self, websocket, data):
        """Handle messages from WebSocket clients"""
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            # Handle subscription requests
            topic = data.get('topic', '')
            self.client_subscriptions[websocket].add(topic)
            logger.info(f"📡 WebSocket client subscribed to: {topic}")
            
        elif msg_type == 'publish':
            # Handle publish requests from client
            topic = data.get('topic', '')
            payload = data.get('payload', {})
            
            # Publish to MQTT broker
            self.mqtt_client.publish(topic, json.dumps(payload))
            logger.info(f"📤 Published from WebSocket to MQTT: {topic}")
            
        elif msg_type == 'get_current_data':
            # Send current sensor data
            await self.send_current_data_to_client(websocket)
    
    async def send_current_data_to_client(self, websocket):
        """Send current sensor data to a specific WebSocket client"""
        try:
            if self.sensor_data:
                sensor_list = list(self.sensor_data.values())
                message = {
                    'type': 'sensor_data',
                    'topic': 'noise/current',
                    'payload': sensor_list,
                    'timestamp': int(time.time() * 1000)
                }
                await websocket.send(json.dumps(message))
                logger.info(f"📊 Sent current data to client: {len(sensor_list)} sensors")
        except Exception as e:
            logger.error(f"❌ Error sending current data: {e}")
    
    async def broadcast_to_websocket_clients(self, topic, payload):
        """Broadcast MQTT messages to WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = {
            'type': 'mqtt_message',
            'topic': topic,
            'payload': payload,
            'timestamp': int(time.time() * 1000)
        }
        
        # Send to all connected WebSocket clients
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"❌ Error sending to WebSocket client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.discard(client)
            if client in self.client_subscriptions:
                del self.client_subscriptions[client]
    
    def start_mqtt_client(self):
        """Start the MQTT client in a separate thread"""
        def mqtt_loop():
            try:
                # Connect to external MQTT broker (could be Mosquitto)
                self.mqtt_client.connect(self.broker_host, 1883, 60)
                self.mqtt_client.loop_start()
                
                # Keep the thread alive
                while not self.shutdown_flag.is_set():
                    time.sleep(1)
                    
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                
            except Exception as e:
                logger.error(f"❌ MQTT client error: {e}")
        
        mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
        mqtt_thread.start()
        logger.info(f"🔌 MQTT client connecting to {self.broker_host}:1883")
    
    async def start_websocket_server(self):
        """Start the WebSocket server"""
        server = await websockets.serve(
            self.websocket_handler,
            "localhost",
            self.websocket_port,
            ping_interval=20,
            ping_timeout=10
        )
        logger.info(f"🌐 WebSocket server listening on ws://localhost:{self.websocket_port}")
        return server
    
    def cleanup_old_data(self):
        """Clean up old sensor data periodically"""
        def cleanup_loop():
            while not self.shutdown_flag.is_set():
                try:
                    current_time = int(time.time() * 1000)
                    max_age = 300000  # 5 minutes in milliseconds
                    
                    expired_sensors = []
                    for device_id, data in self.sensor_data.items():
                        if current_time - data['received_at'] > max_age:
                            expired_sensors.append(device_id)
                    
                    for device_id in expired_sensors:
                        del self.sensor_data[device_id]
                        logger.info(f"🗑️ Removed expired sensor data: {device_id}")
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"❌ Error in cleanup loop: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("🧹 Started data cleanup service")
    
    async def run(self):
        """Main run method"""
        logger.info("🚀 Starting MQTT Broker Server with WebSocket support...")
        
        # Store event loop for cross-thread communication
        self.websocket_loop = asyncio.get_event_loop()
        
        # Start MQTT client
        self.start_mqtt_client()
        
        # Start cleanup service
        self.cleanup_old_data()
        
        # Start WebSocket server
        websocket_server = await self.start_websocket_server()
        
        logger.info("🚀 MQTT Broker Server started successfully!")
        logger.info(f"📡 WebSocket URL: ws://localhost:{self.websocket_port}")
        logger.info(f"🔌 MQTT connection: {self.broker_host}:1883")
        logger.info("📍 Ready to receive ESP32 sensor data and serve React UI")
        
        # Keep the server running
        try:
            await websocket_server.wait_closed()
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down server...")
            self.shutdown_flag.set()
            websocket_server.close()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal")
    sys.exit(0)

async def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run server
    server = MQTTBrokerServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
