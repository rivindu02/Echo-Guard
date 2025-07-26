#!/bin/bash

echo "Setting up Noise Mapping System on Raspberry Pi..."

# Check if we're running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null && ! grep -q "BCM" /proc/cpuinfo; then
    echo "Warning: This script is optimized for Raspberry Pi"
fi

# Fix any interrupted dpkg operations
echo "Fixing any interrupted package installations..."
sudo dpkg --configure -a

# Update system
echo "Updating system packages..."
sudo apt update

# Install system dependencies for scipy and numpy
echo "Installing system dependencies..."
sudo apt install -y \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    libatlas-base-dev \
    libblas-dev \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    mosquitto \
    mosquitto-clients \
    git

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install wheel
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip wheel setuptools

# Install numpy first (scipy depends on it)
echo "Installing numpy..."
pip install numpy

# Install scipy with specific flags for ARM
echo "Installing scipy..."
pip install scipy --no-use-pep517

# Install remaining requirements
echo "Installing remaining Python packages..."
pip install paho-mqtt websockets

echo "Installation complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "source venv/bin/activate"
echo ""
echo "To start the noise mapping system, run:"
echo "python start_noise_system.py"
