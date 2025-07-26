#!/usr/bin/env python3
"""
Easy IP Configuration Script
Run this to update all configuration files with your Raspberry Pi's IP
"""

import os
import re
import sys

def update_network_config(new_ip):
    """Update network.conf with new IP"""
    config_file = "Server/network.conf"
    
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update PI_IP line
        content = re.sub(r'PI_IP=.*', f'PI_IP={new_ip}', content)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {config_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {config_file}: {e}")
        return False

def update_react_env(new_ip):
    """Update React .env.local with new IP"""
    env_file = "mqtt-noise-map-ui/.env.local"
    
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update WebSocket URLs
        content = re.sub(r'REACT_APP_WEBSOCKET_URL=ws://[^:]+:', 
                        f'REACT_APP_WEBSOCKET_URL=ws://{new_ip}:', content)
        content = re.sub(r'REACT_APP_MQTT_BROKER_URL=ws://[^:]+:', 
                        f'REACT_APP_MQTT_BROKER_URL=ws://{new_ip}:', content)
        
        # Update PI_IP variable
        content = re.sub(r'PI_IP=.*', f'PI_IP={new_ip}', content)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {env_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {env_file}: {e}")
        return False

def update_test_connection(new_ip):
    """Update test_connection.py with new IP"""
    test_file = "test_connection.py"
    
    if not os.path.exists(test_file):
        print(f"❌ {test_file} not found")
        return False
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update PI_IP variable
        content = re.sub(r'PI_IP = "[^"]*"', f'PI_IP = "{new_ip}"', content)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {test_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {test_file}: {e}")
        return False

def validate_ip(ip):
    """Validate IP address format"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False

def main():
    """Main function"""
    print("🔧 Raspberry Pi IP Configuration Tool")
    print("=" * 40)
    
    # Get current IP from user or command line
    if len(sys.argv) > 1:
        new_ip = sys.argv[1]
    else:
        current_ip = "192.168.1.12"  # Default
        print(f"Current IP: {current_ip}")
        new_ip = input("Enter new Raspberry Pi IP (or press Enter to keep current): ").strip()
        if not new_ip:
            new_ip = current_ip
    
    # Validate IP
    if not validate_ip(new_ip):
        print(f"❌ Invalid IP address: {new_ip}")
        return
    
    print(f"🔧 Updating all configuration files with IP: {new_ip}")
    print("-" * 40)
    
    # Update all configuration files
    success = True
    success &= update_network_config(new_ip)
    success &= update_react_env(new_ip)
    success &= update_test_connection(new_ip)
    
    if success:
        print()
        print("✅ All configuration files updated successfully!")
        print()
        print("📋 Next steps:")
        print("1. Copy Server/ folder to your Raspberry Pi")
        print("2. On Pi, run: cd Server && chmod +x start_pi_broker.sh && ./start_pi_broker.sh")
        print("3. On PC, run: cd mqtt-noise-map-ui && npm start")
        print("4. Test with: python test_connection.py")
        print("5. Simulate ESP32: python fake_esp32.py --broker " + new_ip)
        print()
        print("🌐 Connection URLs:")
        print(f"   MQTT: {new_ip}:1883")
        print(f"   WebSocket: ws://{new_ip}:9001")
        print(f"   React UI: http://localhost:3000")
        print()
        print("🔧 Quick Commands:")
        print(f"   Test connection: python test_connection.py")
        print(f"   Fake ESP32: python fake_esp32.py --broker {new_ip}")
        print(f"   React UI: cd mqtt-noise-map-ui && npm start")
    else:
        print("❌ Some updates failed. Please check the errors above.")

if __name__ == "__main__":
    main()
