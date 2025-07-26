#!/bin/bash
echo "🔄 Restarting Noise Mapping System..."

# Stop any existing processes
echo "🛑 Stopping existing processes..."
sudo pkill -f "python3 start_noise_system.py"
sudo pkill -f "mqtt_broker_server.py"
sudo pkill -f "simple_noise_processor.py"
sudo pkill mosquitto

# Wait a moment
sleep 2

echo "🚀 Starting system..."
python3 start_noise_system.py
