#!/usr/bin/env python3
"""
Simple MQTT Connection Tester
Tests if an MQTT broker is reachable and responsive
"""

import socket
import time
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_port_connectivity(host, port, timeout=5):
    """Test if a port is open and reachable"""
    try:
        logger.info(f"🔌 Testing TCP connection to {host}:{port}")
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Try to connect
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            logger.info(f"✅ Port {port} is OPEN on {host}")
            return True
        else:
            logger.error(f"❌ Port {port} is CLOSED on {host}")
            return False
            
    except socket.gaierror as e:
        logger.error(f"❌ DNS resolution failed for {host}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

def test_mqtt_broker(host, port=1883):
    """Test MQTT broker connectivity using basic socket connection"""
    try:
        import paho.mqtt.client as mqtt
        
        logger.info(f"🦟 Testing MQTT broker at {host}:{port}")
        
        # Create MQTT client
        client = mqtt.Client()
        client.on_connect = lambda client, userdata, flags, rc: logger.info(f"MQTT Connect result: {rc}")
        client.on_disconnect = lambda client, userdata, rc: logger.info(f"MQTT Disconnected: {rc}")
        
        # Set timeout
        client.connect_async(host, port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(3)
        
        if client.is_connected():
            logger.info("✅ MQTT broker is responding")
            client.disconnect()
            client.loop_stop()
            return True
        else:
            logger.error("❌ MQTT broker is not responding")
            client.loop_stop()
            return False
            
    except ImportError:
        logger.warning("⚠️ paho-mqtt not available, skipping MQTT test")
        return False
    except Exception as e:
        logger.error(f"❌ MQTT test failed: {e}")
        return False

def ping_host(host):
    """Test basic ping connectivity"""
    import subprocess
    import sys
    
    try:
        logger.info(f"🏓 Pinging {host}")
        
        # Choose ping command based on OS
        if sys.platform.startswith('win'):
            cmd = ['ping', '-n', '3', host]
        else:
            cmd = ['ping', '-c', '3', host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info(f"✅ {host} is reachable via ping")
            return True
        else:
            logger.error(f"❌ {host} is not reachable via ping")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Ping to {host} timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Ping test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='MQTT Connection Tester')
    parser.add_argument('host', help='MQTT broker hostname or IP')
    parser.add_argument('--port', type=int, default=1883, help='MQTT port (default: 1883)')
    parser.add_argument('--websocket-port', type=int, default=9001, help='WebSocket port (default: 9001)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("    MQTT Connection Diagnostics")
    print("=" * 50)
    print()
    
    # Test 1: Basic ping
    ping_ok = ping_host(args.host)
    print()
    
    # Test 2: MQTT port connectivity
    mqtt_port_ok = test_port_connectivity(args.host, args.port)
    print()
    
    # Test 3: WebSocket port connectivity
    ws_port_ok = test_port_connectivity(args.host, args.websocket_port)
    print()
    
    # Test 4: MQTT broker response
    if mqtt_port_ok:
        mqtt_ok = test_mqtt_broker(args.host, args.port)
    else:
        mqtt_ok = False
        logger.warning("⚠️ Skipping MQTT broker test (port not open)")
    
    print()
    print("=" * 50)
    print("           SUMMARY")
    print("=" * 50)
    print(f"🏓 Ping:           {'✅ OK' if ping_ok else '❌ FAIL'}")
    print(f"🔌 MQTT Port:      {'✅ OK' if mqtt_port_ok else '❌ FAIL'}")
    print(f"🌐 WebSocket Port: {'✅ OK' if ws_port_ok else '❌ FAIL'}")
    print(f"🦟 MQTT Broker:    {'✅ OK' if mqtt_ok else '❌ FAIL'}")
    print()
    
    if all([ping_ok, mqtt_port_ok, mqtt_ok]):
        print("🎉 All tests passed! MQTT broker is ready.")
        print(f"You can now run: python fake_esp32.py --broker {args.host}")
    else:
        print("❌ Some tests failed. Check the following:")
        print()
        if not ping_ok:
            print(f"   • Host {args.host} is not reachable")
            print("     - Check IP address")
            print("     - Check network connectivity")
        if not mqtt_port_ok:
            print(f"   • MQTT port {args.port} is not open")
            print("     - Start MQTT broker on target machine")
            print("     - Check firewall settings")
        if not ws_port_ok:
            print(f"   • WebSocket port {args.websocket_port} is not open")
            print("     - Start WebSocket server on target machine")
        if mqtt_port_ok and not mqtt_ok:
            print("   • MQTT broker is not responding properly")
            print("     - Check MQTT broker configuration")
            print("     - Check MQTT broker logs")
    
    print()

if __name__ == "__main__":
    main()
