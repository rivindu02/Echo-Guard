#!/bin/bash

echo "========================================"
echo "   Noise Mapping System Configuration"
echo "========================================"
echo
echo "Choose your setup:"
echo "1. Local setup (localhost)"
echo "2. Raspberry Pi setup (192.168.1.11)"
echo "3. Custom IP address"
echo
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo
        echo "Configuring for LOCAL setup..."
        cd mqtt-noise-map-ui
        cat > .env << 'EOF'
# WebSocket connection for Python backend
# For local development (using localhost)
REACT_APP_WEBSOCKET_URL=ws://localhost:9001

# For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)
#REACT_APP_WEBSOCKET_URL=ws://192.168.1.11:9001
EOF
        cd ..
        echo
        echo "✅ Configuration updated for LOCAL setup!"
        echo
        echo "To start the system locally:"
        echo "1. Run: python3 fake_esp32.py"
        echo "2. Run: python3 Server/mqtt_broker_server.py"
        echo "3. Run: cd mqtt-noise-map-ui && npm start"
        ;;
    2)
        echo
        echo "Configuring for RASPBERRY PI setup..."
        cd mqtt-noise-map-ui
        cat > .env << 'EOF'
# WebSocket connection for Python backend
# For local development (using localhost)
#REACT_APP_WEBSOCKET_URL=ws://localhost:9001

# For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)
REACT_APP_WEBSOCKET_URL=ws://192.168.1.11:9001
EOF
        cd ..
        echo
        echo "✅ Configuration updated for RASPBERRY PI setup!"
        echo
        echo "To start the system:"
        echo "1. Make sure Pi is running: python3 start_noise_system.py"
        echo "2. Run locally: python3 fake_esp32.py --broker 192.168.1.11"
        echo "3. Run: cd mqtt-noise-map-ui && npm start"
        ;;
    3)
        echo
        read -p "Enter the IP address: " custom_ip
        echo
        echo "Configuring for CUSTOM IP: $custom_ip"
        cd mqtt-noise-map-ui
        cat > .env << EOF
# WebSocket connection for Python backend
# For local development (using localhost)
#REACT_APP_WEBSOCKET_URL=ws://localhost:9001

# For connecting to custom IP
REACT_APP_WEBSOCKET_URL=ws://$custom_ip:9001
EOF
        cd ..
        echo
        echo "✅ Configuration updated for CUSTOM IP: $custom_ip!"
        echo
        echo "To start the system:"
        echo "1. Make sure target system is running the server"
        echo "2. Run locally: python3 fake_esp32.py --broker $custom_ip"
        echo "3. Run: cd mqtt-noise-map-ui && npm start"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo
read -p "Press Enter to continue..."
