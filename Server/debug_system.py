#!/usr/bin/env python3
"""
Debug script to see why services are failing
"""

import subprocess
import time
import os

def test_mosquitto_config():
    """Test if mosquitto config is valid"""
    print("🧪 Testing Mosquitto configuration...")
    
    config_file = "/etc/mosquitto/mosquitto.conf"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False
    
    # Test config by trying to start mosquitto briefly
    process = subprocess.Popen(['mosquitto', '-c', config_file, '-v'], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    time.sleep(2)
    
    if process.poll() is None:
        print("✅ Mosquitto configuration appears valid")
        process.terminate()
        process.wait()
        return True
    else:
        stdout, stderr = process.communicate()
        print("❌ Mosquitto configuration test failed:")
        print(f"Exit code: {process.returncode}")
        if stdout:
            print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        return False

def test_python_scripts():
    """Test if Python scripts can start"""
    scripts = ['mqtt_broker_server.py', 'simple_noise_processor.py']
    
    for script in scripts:
        print(f"🧪 Testing {script}...")
        
        if not os.path.exists(script):
            print(f"❌ Script not found: {script}")
            continue
        
        # Try to start the script
        try:
            process = subprocess.Popen(['python3', script], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     text=True)
            
            # Wait a moment
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {script} started successfully")
                process.terminate()
                process.wait()
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {script} failed to start:")
                print(f"Exit code: {process.returncode}")
                if stdout:
                    print(f"STDOUT: {stdout}")
                if stderr:
                    print(f"STDERR: {stderr}")
                    
        except Exception as e:
            print(f"❌ Error testing {script}: {e}")

def main():
    print("🔍 Debugging Noise Mapping System")
    print("=================================")
    
    # Check current directory
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📋 Files in directory: {os.listdir('.')}")
    print()
    
    # Test mosquitto config
    test_mosquitto_config()
    print()
    
    # Test Python scripts
    test_python_scripts()
    print()
    
    print("🔧 If you see errors above, run: chmod +x quick_fix_mosquitto.sh && ./quick_fix_mosquitto.sh")

if __name__ == "__main__":
    main()
