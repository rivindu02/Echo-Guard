#!/usr/bin/env python3
"""
Local WebSocket server for development
Uses localhost MQTT broker and configuration from config.ini
"""

import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import logging
import threading
from queue import Queue
import sys
import os

# Add current directory to path for config_loader
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
connected_clients = set()
message_queue = Queue()
config = None

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to local MQTT broker")
        client.subscribe("noise/#")
    else:
        logger.error(f"❌ MQTT connection failed: {rc}")

def on_mqtt_message(client, userdata, msg):
    try:
        # Put message in queue instead of directly sending
        message = {
            "topic": msg.topic,
            "payload": json.loads(msg.payload.decode())
        }
        message_queue.put(message)
        logger.info(f"📨 Queued message: {msg.topic}")
        
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

async def message_forwarder():
    """Forwards messages from queue to WebSocket clients"""
    while True:
        try:
            # Check if there are messages to send
            if not message_queue.empty() and connected_clients:
                message = message_queue.get_nowait()
                message_json = json.dumps(message)
                
                # Send to all connected clients
                disconnected_clients = []
                for client in connected_clients.copy():
                    try:
                        await client.send(message_json)
                        logger.info(f"📤 Sent to client: {message['topic']}")
                    except Exception as e:
                        logger.error(f"Failed to send to client: {e}")
                        disconnected_clients.append(client)
                
                # Remove disconnected clients
                for client in disconnected_clients:
                    connected_clients.discard(client)
                    
        except Exception as e:
            logger.error(f"Error in message forwarder: {e}")
        
        await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

async def handle_client(websocket):
    logger.info(f"🌐 New client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "Connected to local noise monitoring system"
        }))
        
        # Keep connection alive
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"📨 Received from client: {data}")
                
                # Echo back for now
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
    global config
    
    # Load configuration
    config = get_config()
    local_ip = config.get_local_ip()
    mqtt_port = config.get_mqtt_port()
    websocket_port = config.get_websocket_port()
    
    logger.info(f"📋 Local configuration loaded:")
    logger.info(f"   MQTT broker: {local_ip}:{mqtt_port}")
    logger.info(f"   WebSocket server: 0.0.0.0:{websocket_port}")
    
    # Setup MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    try:
        mqtt_client.connect(local_ip, mqtt_port, 60)
        mqtt_client.loop_start()
        logger.info("🦟 Local MQTT client started")
    except Exception as e:
        logger.error(f"❌ Failed to connect to local MQTT: {e}")
        logger.info("💡 Make sure Mosquitto is running locally on port 1883")
        logger.info("   You can install it with: choco install mosquitto")
        logger.info("   Or run it manually with: mosquitto -v")
    
    # Start message forwarder
    asyncio.create_task(message_forwarder())
    
    # Start WebSocket server
    logger.info(f"🚀 Starting local WebSocket server on port {websocket_port}...")
    
    async with websockets.serve(handle_client, "0.0.0.0", websocket_port, 
                               ping_interval=20, ping_timeout=10):
        logger.info("✅ Local WebSocket server running!")
        logger.info("🌐 React UI should connect to: ws://localhost:9001")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Local server stopped by user")
