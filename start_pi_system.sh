#!/bin/bash
# Smart Noise Monitoring System - Pi Server Startup Script

echo "🔊 Starting Smart Noise Monitoring System..."

# Check if MQTT broker is running
if ! pgrep -x "mosquitto" > /dev/null; then
    echo "📡 Starting MQTT broker..."
    sudo systemctl start mosquitto
    sleep 2
fi

# Check if WebSocket server is already running
if pgrep -f "fixed_websocket_server.py" > /dev/null; then
    echo "⚠️  WebSocket server already running"
    echo "🔄 Stopping existing server..."
    pkill -f "fixed_websocket_server.py"
    sleep 2
fi

echo "🌐 Starting WebSocket server..."
cd "$(dirname "$0")/Server"
python3 fixed_websocket_server.py &

echo "✅ System started successfully!"
echo "📋 Services:"
echo "   - MQTT Broker: port 1883"
echo "   - WebSocket Server: port 9001"
echo ""
echo "🔍 To test the system:"
echo "   python3 fake_esp32.py --broker $(hostname -I | awk '{print $1}')"
echo ""
echo "🌐 Web UI should connect to: ws://$(hostname -I | awk '{print $1}'):9001"
