#!/usr/bin/env python3
"""
Test Pi Connection Script
Tests connectivity to Raspberry Pi MQTT broker and WebSocket server
"""

import socket
import time
import configparser
import os

def load_config():
    """Load Pi IP from config.ini"""
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        try:
            pi_ip = config.get('pi_connection', 'pi_ip', fallback='192.168.1.12')
            return pi_ip
        except:
            pass
    return '192.168.1.12'

def test_ping(host):
    """Test basic network connectivity"""
    print(f"🌐 Testing network connectivity to {host}...")
    
    import subprocess
    import platform
    
    # Use appropriate ping command for Windows/Linux
    if platform.system().lower() == 'windows':
        cmd = ['ping', '-n', '3', host]
    else:
        cmd = ['ping', '-c', '3', host]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"✅ Network connectivity to {host} successful")
            return True
        else:
            print(f"❌ Network connectivity to {host} failed")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Ping to {host} timed out")
        return False
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False

def test_port(host, port, service_name):
    """Test if a specific port is open"""
    print(f"🔌 Testing {service_name} connection to {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {service_name} port {port} is accessible")
            return True
        else:
            print(f"❌ {service_name} port {port} is not accessible")
            return False
    except Exception as e:
        print(f"❌ Error testing {service_name}: {e}")
        return False

def test_mqtt_basic(host, port=1883):
    """Test basic MQTT connection"""
    print(f"📡 Testing MQTT broker at {host}:{port}...")
    
    try:
        import paho.mqtt.client as mqtt
        
        connection_result = {'success': False}
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                connection_result['success'] = True
                print("✅ MQTT broker connection successful")
            else:
                print(f"❌ MQTT broker connection failed with code {rc}")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.connect(host, port, 10)
        
        # Wait for connection
        start_time = time.time()
        while time.time() - start_time < 10:
            client.loop()
            if connection_result['success']:
                break
            time.sleep(0.1)
        
        client.disconnect()
        return connection_result['success']
        
    except ImportError:
        print("⚠️ paho-mqtt not installed, skipping MQTT test")
        return None
    except Exception as e:
        print(f"❌ MQTT test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("   Raspberry Pi Connection Test")
    print("=" * 50)
    print()
    
    # Load Pi IP
    pi_ip = load_config()
    print(f"🎯 Testing connection to Pi: {pi_ip}")
    print(f"   (Edit config.ini to change IP)")
    print()
    
    # Test network connectivity
    network_ok = test_ping(pi_ip)
    print()
    
    if not network_ok:
        print("❌ Network connectivity failed. Check:")
        print("   1. Pi is powered on and connected to WiFi")
        print("   2. Pi IP address is correct in config.ini")
        print("   3. Both devices are on same WiFi network")
        return
    
    # Test MQTT port
    mqtt_ok = test_port(pi_ip, 1883, "MQTT Broker")
    print()
    
    # Test WebSocket port
    websocket_ok = test_port(pi_ip, 9001, "WebSocket Server")
    print()
    
    # Test MQTT connection if basic port test passed
    if mqtt_ok:
        mqtt_connect_ok = test_mqtt_basic(pi_ip)
        print()
    else:
        mqtt_connect_ok = False
    
    # Summary
    print("=" * 50)
    print("   CONNECTION TEST SUMMARY")
    print("=" * 50)
    
    status = "✅" if network_ok else "❌"
    print(f"{status} Network connectivity to {pi_ip}")
    
    status = "✅" if mqtt_ok else "❌"
    print(f"{status} MQTT broker port (1883)")
    
    status = "✅" if websocket_ok else "❌"
    print(f"{status} WebSocket server port (9001)")
    
    if mqtt_connect_ok is not None:
        status = "✅" if mqtt_connect_ok else "❌"
        print(f"{status} MQTT broker connection")
    
    print()
    
    if all([network_ok, mqtt_ok, websocket_ok]):
        print("🎉 All tests passed! Pi connection is ready.")
        print()
        print("🚀 Next steps:")
        print("   1. Run: python fake_esp32.py --pi")
        print("   2. Run: connect_to_pi.bat")
    else:
        print("⚠️ Some tests failed. Troubleshooting:")
        print()
        if not network_ok:
            print("📡 Network issues:")
            print("   - Check Pi is on and connected to WiFi")
            print("   - Verify IP address in config.ini")
            print("   - Ensure same WiFi network")
        
        if not mqtt_ok:
            print("🔌 MQTT broker issues:")
            print("   - Run on Pi: python3 start_noise_system.py")
            print("   - Check Pi firewall: sudo ufw status")
        
        if not websocket_ok:
            print("🌐 WebSocket server issues:")
            print("   - Ensure Python backend is running on Pi")
            print("   - Check port 9001 is not blocked")

if __name__ == "__main__":
    main()
