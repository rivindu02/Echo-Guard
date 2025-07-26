#!/bin/bash

echo "🔧 Installing Missing Python Packages"
echo "====================================="

echo "1. Installing websockets..."
pip3 install websockets

echo "2. Installing paho-mqtt..."
pip3 install paho-mqtt

echo "3. Installing other required packages..."
pip3 install numpy scipy matplotlib

echo "4. Testing imports..."
python3 -c "import websockets; print('✅ websockets imported successfully')"
python3 -c "import paho.mqtt.client; print('✅ paho-mqtt imported successfully')"

echo
echo "✅ Python packages installed!"
echo "Now try running the services again."
