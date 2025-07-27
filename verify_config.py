#!/usr/bin/env python3
"""
Verification script for the updated Noise Mapping System
Tests that all components can load configuration correctly
"""

import sys
import os

# Add Server directory to path
server_dir = os.path.join(os.path.dirname(__file__), 'Server')
sys.path.insert(0, server_dir)

def test_config_loader():
    """Test the configuration loader"""
    print("🧪 Testing configuration loader...")
    try:
        from config_loader import get_config
        config = get_config()
        
        pi_ip = config.get_pi_ip()
        mqtt_port = config.get_mqtt_port()
        websocket_port = config.get_websocket_port()
        
        print(f"   ✅ Pi IP: {pi_ip}")
        print(f"   ✅ MQTT Port: {mqtt_port}")
        print(f"   ✅ WebSocket Port: {websocket_port}")
        print(f"   ✅ Config file: {config.config_file_path}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_mqtt_broker_server():
    """Test that mqtt_broker_server can import and initialize"""
    print("\n🧪 Testing MQTT broker server...")
    try:
        # Suppress logging for clean output
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)
        
        from mqtt_broker_server import MQTTBrokerServer
        server = MQTTBrokerServer()
        
        print(f"   ✅ Broker host: {server.broker_host}")
        print(f"   ✅ WebSocket host: {server.websocket_host}")
        print(f"   ✅ MQTT port: {server.mqtt_port}")
        print(f"   ✅ WebSocket port: {server.websocket_port}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_start_noise_system():
    """Test that start_noise_system can import and initialize"""
    print("\n🧪 Testing noise system startup...")
    try:
        # Suppress logging for clean output
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)
        
        from start_noise_system import NoiseMapSystem
        system = NoiseMapSystem()
        
        print(f"   ✅ Pi IP from config: {system.config.get_pi_ip()}")
        print(f"   ✅ MQTT port: {system.config.get_mqtt_port()}")
        print(f"   ✅ WebSocket port: {system.config.get_websocket_port()}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_fake_esp32():
    """Test that fake_esp32 can import and get config"""
    print("\n🧪 Testing fake ESP32 simulator...")
    try:
        # Change to parent directory for fake_esp32.py
        import sys
        parent_dir = os.path.dirname(__file__)
        sys.path.insert(0, parent_dir)
        
        # Import ESP32Simulator
        from fake_esp32 import ESP32Simulator
        
        # Test with default config
        simulator = ESP32Simulator()
        
        print(f"   ✅ Broker host: {simulator.broker_host}")
        print(f"   ✅ Broker port: {simulator.broker_port}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Noise Mapping System Configuration Verification")
    print("=" * 55)
    
    tests = [
        test_config_loader,
        test_mqtt_broker_server,
        test_start_noise_system,
        test_fake_esp32
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Configuration system is working correctly.")
        print("\n📋 Next steps:")
        print("   1. Edit config.ini to set your Pi's IP address")
        print("   2. Run: python Server/start_noise_system.py (on Pi)")
        print("   3. Run: python fake_esp32.py (on Windows)")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
