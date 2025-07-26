#!/bin/bash

echo "🔧 Installing Missing Python Packages via APT"
echo "=============================================="

echo "1. Updating package list..."
sudo apt update

echo "2. Installing python3-websockets..."
sudo apt install -y python3-websockets

echo "3. Installing python3-paho-mqtt..."
sudo apt install -y python3-paho-mqtt

echo "4. Installing other useful packages..."
sudo apt install -y python3-numpy python3-scipy python3-matplotlib

echo "5. Testing imports..."
python3 -c "import websockets; print('✅ websockets imported successfully')"
python3 -c "import paho.mqtt.client; print('✅ paho-mqtt imported successfully')"
python3 -c "import numpy; print('✅ numpy imported successfully')"

echo
echo "✅ Python packages installed via APT!"
echo "Now try running the services again."
