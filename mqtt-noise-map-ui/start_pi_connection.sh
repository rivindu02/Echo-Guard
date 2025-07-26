#!/bin/bash

# React UI Startup Script for Pi Connection
# Sets the correct WebSocket URL for connecting to Raspberry Pi

# Configuration
PI_IP="192.168.1.11"
WEBSOCKET_PORT="9001"

echo "🚀 Starting React UI with Pi connection..."
echo "📡 Connecting to WebSocket: ws://${PI_IP}:${WEBSOCKET_PORT}"
echo

# Check if we're in the React UI directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Not in React UI directory"
    echo "Please run this script from: mqtt-noise-map-ui/"
    exit 1
fi

# Set environment variable and start React app
export REACT_APP_WEBSOCKET_URL="ws://${PI_IP}:${WEBSOCKET_PORT}"

echo "🌐 Environment configured:"
echo "   REACT_APP_WEBSOCKET_URL=${REACT_APP_WEBSOCKET_URL}"
echo

echo "▶️ Starting React development server..."
npm start
