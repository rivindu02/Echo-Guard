#!/usr/bin/env python3
"""
Super Simple WebSocket server that forwards MQTT messages
"""

import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
connected_clients = set()
mqtt_client = None

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")
        client.subscribe("noise/#")
    else:
        logger.error(f"❌ MQTT connection failed: {rc}")

def on_mqtt_message(client, userdata, msg):
    try:
        # Forward message to all connected WebSocket clients
        message = {
            "topic": msg.topic,
            "payload": json.loads(msg.payload.decode()),
            "timestamp": msg.timestamp if hasattr(msg, 'timestamp') else None
        }
        
        # Send to all connected clients
        if connected_clients:
            asyncio.create_task(broadcast_to_clients(json.dumps(message)))
            
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

async def broadcast_to_clients(message):
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )

async def handle_client(websocket, path):
    logger.info(f"🌐 New client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "Connected to noise monitoring system"
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
            except:
                pass  # Ignore parsing errors
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
    finally:
        connected_clients.discard(websocket)

async def main():
    global mqtt_client
    
    # Setup MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    try:
        mqtt_client.connect("172.20.10.2", 1883, 60)
        mqtt_client.loop_start()
        logger.info("🦟 MQTT client started")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MQTT: {e}")
    
    # Start WebSocket server
    logger.info("🚀 Starting WebSocket server on port 9001...")
    
    async with websockets.serve(handle_client, "0.0.0.0", 9001):
        logger.info("✅ WebSocket server running!")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
