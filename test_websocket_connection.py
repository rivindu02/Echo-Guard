#!/usr/bin/env python3
"""
Test script to verify WebSocket connection from React UI to Pi broker
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection(url):
    """Test WebSocket connection to the broker"""
    try:
        print(f"🔗 Attempting to connect to: {url}")
        
        async with websockets.connect(url) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "type": "get_current_data"
            }
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message: get_current_data")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📨 Received response: {data.get('type', 'unknown')}")
                return True
            except asyncio.TimeoutError:
                print("⚠️ No response received within 5 seconds")
                return False
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    """Main test function"""
    # Test URLs
    test_urls = [
        "ws://localhost:9001",
        "ws://192.168.1.11:9001"
    ]
    
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    print("🧪 Testing WebSocket connections...")
    print()
    
    for url in test_urls:
        success = await test_websocket_connection(url)
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {url}")
        print()
    
    print("🧪 WebSocket connection test completed")

if __name__ == "__main__":
    asyncio.run(main())
