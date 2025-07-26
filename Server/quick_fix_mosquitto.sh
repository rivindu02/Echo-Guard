#!/bin/bash

echo "🔧 Quick Fix for Mosquitto MQTT Broker"
echo "======================================"

# Stop the current failing system
echo "1. Stopping current system..."
sudo pkill -f start_noise_system.py
sudo pkill mosquitto
sudo pkill -f mqtt_broker_server.py
sudo pkill -f simple_noise_processor.py

echo "2. Installing/updating Mosquitto..."
sudo apt update
sudo apt install mosquitto mosquitto-clients -y

echo "3. Creating simple working configuration..."
sudo tee /etc/mosquitto/mosquitto.conf > /dev/null << 'EOF'
# Basic Mosquitto Configuration
# Don't use PID file to avoid permission issues
persistence true
persistence_location /var/lib/mosquitto/
log_dest stdout
log_type all

# Allow anonymous connections
allow_anonymous true

# MQTT TCP port - listen on all interfaces
listener 1883 0.0.0.0
protocol mqtt

# WebSocket port - listen on all interfaces
listener 9001 0.0.0.0
protocol websockets
EOF

echo "4. Setting up directories and permissions..."
sudo mkdir -p /var/lib/mosquitto /var/log/mosquitto /run/mosquitto
sudo chown -R mosquitto:mosquitto /var/lib/mosquitto /var/log/mosquitto /run/mosquitto 2>/dev/null || echo "Note: mosquitto user may not exist, continuing..."

echo "5. Testing Mosquitto configuration..."
# Note: -t option doesn't exist in mosquitto 2.0.11, so we'll just try to start it briefly
mosquitto -c /etc/mosquitto/mosquitto.conf -v &
TEST_PID=$!
sleep 2

if kill -0 $TEST_PID 2>/dev/null; then
    echo "✅ Configuration appears to be working"
    kill $TEST_PID
    wait $TEST_PID 2>/dev/null
else
    echo "❌ Configuration test failed!"
    wait $TEST_PID 2>/dev/null
    exit 1
fi

echo "6. Starting Mosquitto manually..."
mosquitto -c /etc/mosquitto/mosquitto.conf -v &
MOSQUITTO_PID=$!

sleep 3

echo "7. Testing if Mosquitto is running..."
if kill -0 $MOSQUITTO_PID 2>/dev/null; then
    echo "✅ Mosquitto is running (PID: $MOSQUITTO_PID)"
else
    echo "❌ Mosquitto failed to start"
    exit 1
fi

echo "8. Checking ports..."
netstat -tln | grep -E "(1883|9001)"

echo "9. Testing MQTT connection..."
timeout 5 mosquitto_pub -h localhost -p 1883 -t test/topic -m "test message"
if [ $? -eq 0 ]; then
    echo "✅ MQTT is working!"
else
    echo "❌ MQTT test failed"
fi

echo
echo "==========================================="
echo "🎉 Mosquitto should now be working!"
echo "==========================================="
echo "MQTT Port 1883: $(netstat -tln | grep :1883 >/dev/null && echo 'OPEN' || echo 'CLOSED')"
echo "WebSocket Port 9001: $(netstat -tln | grep :9001 >/dev/null && echo 'OPEN' || echo 'CLOSED')"
echo
echo "Now you can:"
echo "1. Test from Windows: python test_mqtt_connection.py 192.168.1.11"
echo "2. Connect ESP32: python fake_esp32.py --broker 192.168.1.11"
echo
echo "To stop Mosquitto: kill $MOSQUITTO_PID"
echo "==========================================="
