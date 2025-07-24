#!/bin/bash
# Installation script for Raspberry Pi backend

set -e

echo "Installing Noise Mapping Backend..."

# Update system
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y mosquitto mosquitto-clients python3-pip python3-venv

# Create project directory
mkdir -p /home/pi/noise-backend
cd /home/pi/noise-backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip3 install -r requirements.txt

# Configure Mosquitto
sudo cp mosquitto.conf /etc/mosquitto/mosquitto.conf

# Install and enable system service
sudo cp noise-processor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable noise-processor.service
sudo systemctl enable mosquitto.service

# Start services
sudo systemctl start mosquitto.service
sudo systemctl start noise-processor.service

echo "Installation complete!"
echo "Check service status with: sudo systemctl status noise-processor"
echo "View logs with: sudo journalctl -u noise-processor -f"
