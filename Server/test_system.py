#!/usr/bin/env python3
"""
Test script to verify the Python noise mapping system is working correctly
"""

import asyncio
import websockets
import json
import time
import logging
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
        logging.StreamHandler(),
        logging.FileHandler('test_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection to the broker server"""
    
    try:
        logger.info("🧪 Testing WebSocket connection to ws://localhost:9001")
        
        async with websockets.connect("ws://localhost:9001") as websocket:
            logger.info("✅ Connected to WebSocket server")
            
            # Send a test message
            test_message = {
                "type": "get_current_data"
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info("📤 Sent test message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                logger.info(f"📨 Received response: {data.get('type', 'unknown')}")
                
                if data.get('type') == 'sensor_data':
                    sensor_count = len(data.get('payload', []))
                    logger.info(f"📊 Current sensors: {sensor_count}")
                    return True
                
            except asyncio.TimeoutError:
                logger.warning("⏰ Timeout waiting for response")
                return False
                
    except ConnectionRefusedError:
        logger.error("❌ Connection refused - is the server running?")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing WebSocket: {e}")
        return False

def test_system_components():
    """Test if system components are accessible"""
    
    import os
    import subprocess
    
    logger.info("🧪 Testing system components...")
    
    # Check if required files exist
    required_files = [
        "mqtt_broker_server.py",
        "simple_noise_processor.py",
        "start_noise_system.py",
        "config.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
        return False
    else:
        logger.info("✅ All required files present")
    
    # Check Python dependencies
    try:
        import paho.mqtt.client as mqtt
        import numpy as np
        import websockets
        logger.info("✅ Python dependencies installed")
    except ImportError as e:
        logger.error(f"❌ Missing Python dependency: {e}")
        return False
    
    # Check if Mosquitto is available
    try:
        result = subprocess.run(['mosquitto', '--help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("✅ Mosquitto MQTT broker available")
        else:
            logger.warning("⚠️ Mosquitto might not be properly installed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("⚠️ Mosquitto not found - install with: sudo apt install mosquitto")
    
    return True

async def test_full_system():
    """Run full system test"""
    
    logger.info("🚀 Starting full system test...")
    
    # Test components
    if not test_system_components():
        logger.error("❌ System component test failed")
        return False
    
    # Test WebSocket connection
    if not await test_websocket_connection():
        logger.error("❌ WebSocket connection test failed")
        logger.info("💡 Make sure to start the system first:")
        logger.info("   python start_noise_system.py")
        return False
    
    logger.info("🎉 All tests passed!")
    logger.info("")
    logger.info("📋 System Status:")
    logger.info("   ✅ Python components: Ready")
    logger.info("   ✅ Dependencies: Installed")
    logger.info("   ✅ WebSocket server: Running")
    logger.info("   ✅ System: Operational")
    logger.info("")
    logger.info("🔗 Next steps:")
    logger.info("   1. Start React UI: cd ../mqtt-noise-map-ui && npm start")
    logger.info("   2. Connect ESP32 sensors to MQTT broker")
    logger.info("   3. View real-time noise map at http://localhost:3000")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_full_system())
        if not success:
            exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        exit(1)
