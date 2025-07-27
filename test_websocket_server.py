#!/usr/bin/env python3
"""
Simple WebSocket test server to verify network connectivity
Run this on the Raspberry Pi to test if port 9001 is accessible
"""

import asyncio
import websockets
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(websocket, path):
    """Handle WebSocket client connections"""
    client_ip = websocket.remote_address[0]
    logger.info(f"✅ Client connected from {client_ip}")
    
    try:
        # Send welcome message
        welcome = {
            "type": "welcome",
            "message": "WebSocket test server connected!",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(welcome))
        
        # Echo any messages received
        async for message in websocket:
            logger.info(f"📥 Received from {client_ip}: {message}")
            
            # Echo back
            response = {
                "type": "echo",
                "original": message,
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(response))
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"❌ Client {client_ip} disconnected")
    except Exception as e:
        logger.error(f"❌ Error with client {client_ip}: {e}")

async def main():
    """Start the test WebSocket server"""
    host = "0.0.0.0"  # Listen on all interfaces
    port = 9001
    
    logger.info(f"🚀 Starting WebSocket test server on {host}:{port}")
    
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"✅ WebSocket server listening on ws://{host}:{port}")
    logger.info("📡 Waiting for connections...")
    
    # Keep server running
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
