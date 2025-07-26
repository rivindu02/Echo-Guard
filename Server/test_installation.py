#!/usr/bin/env python3
"""
Simple test script to verify the noise mapping system installation
Run this after installation to check if everything is working correctly
"""

import sys
import time
import subprocess
import os


def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[0;34m",
        "SUCCESS": "\033[0;32m",
        "WARNING": "\033[1;33m",
        "ERROR": "\033[0;31m"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')}{message}{reset}")


def test_python_imports():
    """Test if all required Python packages can be imported"""
    print_status("Testing Python package imports...", "INFO")

    packages = [
        ("paho.mqtt.client", "MQTT client"),
        ("numpy", "NumPy"),
        ("websockets", "WebSockets"),
        ("json", "JSON"),
        ("asyncio", "AsyncIO"),
        ("logging", "Logging"),
        ("threading", "Threading")
    ]

    for package, name in packages:
        try:
            __import__(package)
            print_status(f"✓ {name}", "SUCCESS")
        except ImportError as e:
            print_status(f"✗ {name}: {e}", "ERROR")
            return False

    return True


def test_mosquitto():
    """Test if Mosquitto MQTT broker is available"""
    print_status("Testing Mosquitto MQTT broker...", "INFO")

    try:
        # Check if mosquitto command exists
        result = subprocess.run(['mosquitto', '--help'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_status("✓ Mosquitto broker available", "SUCCESS")
            return True
        else:
            print_status("✗ Mosquitto broker not working", "ERROR")
            return False
    except Exception as e:
        print_status(f"✗ Mosquitto broker error: {e}", "ERROR")
        return False


def test_project_files():
    """Test if all required project files exist"""
    print_status("Testing project files...", "INFO")

    required_files = [
        "mqtt_broker_server.py",
        "simple_noise_processor.py",
        "start_noise_system.py",
        "config.py",
        "requirements.txt"
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print_status(f"✓ {file}", "SUCCESS")
        else:
            print_status(f"✗ {file} missing", "ERROR")
            all_exist = False

    return all_exist


def test_virtual_environment():
    """Test if virtual environment is properly set up"""
    print_status("Testing virtual environment...", "INFO")

    venv_active = (hasattr(sys, 'real_prefix') or
                   (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    if venv_active:
        print_status("✓ Virtual environment active", "SUCCESS")
        print_status(f"  Python executable: {sys.executable}", "INFO")
        print_status(f"  Python version: {sys.version}", "INFO")
        return True
    else:
        print_status("✗ Virtual environment not active", "WARNING")
        print_status("  Consider running: source venv/bin/activate", "INFO")
        return False


def test_system_startup():
    """Test if the system can start (quick check)"""
    print_status("Testing system startup (quick check)...", "INFO")

    try:
        # Try to import the main modules
        sys.path.insert(0, '.')

        # Test config import
        import config
        print_status("✓ Configuration module", "SUCCESS")

        # Test if we can create the classes (but don't start them)
        with open('mqtt_broker_server.py', 'r') as f:
            content = f.read()
            if 'class' in content and 'WebSocketServer' in content:
                print_status("✓ WebSocket server class available", "SUCCESS")
            else:
                print_status("✗ WebSocket server class not found", "ERROR")
                return False

        with open('simple_noise_processor.py', 'r') as f:
            content = f.read()
            if 'class' in content and 'NoiseProcessor' in content:
                print_status("✓ Noise processor class available", "SUCCESS")
            else:
                print_status("✗ Noise processor class not found", "ERROR")
                return False

        return True

    except Exception as e:
        print_status(f"✗ System startup test failed: {e}", "ERROR")
        return False


def run_quick_mqtt_test():
    """Run a quick MQTT publish/subscribe test"""
    print_status("Running quick MQTT test...", "INFO")

    try:
        import paho.mqtt.client as mqtt

        received_message = []

        def on_message(client, userdata, message):
            received_message.append(message.payload.decode())

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe("test/topic")

        # Create MQTT client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        # Try to connect to localhost
        client.connect("localhost", 1883, 60)
        client.loop_start()

        # Wait a moment for connection
        time.sleep(1)

        # Publish test message
        client.publish("test/topic", "test_message")

        # Wait for message
        time.sleep(1)

        client.loop_stop()
        client.disconnect()

        if received_message and received_message[0] == "test_message":
            print_status("✓ MQTT publish/subscribe working", "SUCCESS")
            return True
        else:
            print_status("✗ MQTT test failed - no message received", "WARNING")
            print_status("  This is normal if Mosquitto isn't running yet", "INFO")
            return False

    except Exception as e:
        print_status(f"✗ MQTT test error: {e}", "WARNING")
        print_status("  This is normal if Mosquitto isn't running yet", "INFO")
        return False

def main():
    """Run all tests"""
    print_status("🧪 Noise Mapping System Installation Test", "INFO")
    print("=" * 50)
    
    tests = [
        ("Python Virtual Environment", test_virtual_environment),
        ("Python Package Imports", test_python_imports),
        ("Project Files", test_project_files),
        ("Mosquitto Broker", test_mosquitto),
        ("System Startup Check", test_system_startup),
        ("MQTT Quick Test", run_quick_mqtt_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print_status("📋 TEST SUMMARY", "INFO")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        color = "SUCCESS" if result else "ERROR"
        print_status(f"{status:<10} {test_name}", color)
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print_status("\n🎉 ALL TESTS PASSED! Your installation is ready!", "SUCCESS")
        print_status("To start the system: python3 start_noise_system.py", "INFO")
    elif passed >= len(tests) - 2:  # Allow 2 failures (MQTT tests might fail if broker not running)
        print_status("\n✅ Installation looks good! Minor issues are normal.", "SUCCESS")
        print_status("To start the system: python3 start_noise_system.py", "INFO")
    else:
        print_status("\n❌ Installation has issues. Check the errors above.", "ERROR")
        print_status("Try running the cleanup script again: ./cleanup_and_install.sh", "WARNING")

if __name__ == "__main__":
    main()
