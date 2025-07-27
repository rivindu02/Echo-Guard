#!/usr/bin/env python3
"""
WebSocket server for MQTT over WebSocket connections
"""

import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MQTT client for forwarding messages
mqtt_client = mqtt.Client()

# MQTT connection handling
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")
    else:
        logger.error(f"❌ Failed to connect to MQTT broker: {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning("⚠️ Unexpected MQTT disconnection, attempting to reconnect...")

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Try to connect to MQTT broker
try:
    mqtt_client.connect('172.20.10.2', 1883, 60)  # Connect to Pi's MQTT broker
    mqtt_client.loop_start()
except Exception as e:
    logger.error(f"❌ Failed to connect to MQTT broker: {e}")
    logger.info("🔄 Will retry connection when needed...")

async def handle_websocket(websocket, path):
    try:
        logger.info(f"🌐 New WebSocket connection from {websocket.remote_address}")
        
        # Set up MQTT message callback
        def on_mqtt_message(client, userdata, msg):
            asyncio.create_task(websocket.send(json.dumps({
                'type': 'mqtt_message',
                'topic': msg.topic,
                'payload': json.loads(msg.payload.decode())
            })))
        
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.subscribe('noise/#')
        
        # Handle incoming WebSocket messages
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get('type') == 'publish':
                    mqtt_client.publish(data['topic'], json.dumps(data['payload']))
                elif data.get('type') == 'subscribe':
                    mqtt_client.subscribe(data['topic'])
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    finally:
        mqtt_client.unsubscribe('noise/#')

async def main():
    logger.info("🚀 Starting WebSocket server on port 9001...")
    async with websockets.serve(handle_websocket, '0.0.0.0', 9001):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
