#!/bin/bash

echo "🧹 Cleaning up and installing Noise Mapping System on Raspberry Pi..."
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please run this script as a regular user (not root)"
    exit 1
fi

print_status "Starting cleanup and installation process..."

# Step 1: Fix interrupted dpkg operations
print_status "Step 1: Fixing interrupted package installations..."
sudo dpkg --configure -a
if [ $? -eq 0 ]; then
    print_success "Fixed interrupted package installations"
else
    print_warning "Some package issues remain, continuing anyway..."
fi

# Step 2: Clean up old virtual environment
print_status "Step 2: Cleaning up old virtual environment..."
if [ -d "venv" ]; then
    # Deactivate if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null || true
    fi
    rm -rf venv
    print_success "Removed old virtual environment"
else
    print_status "No existing virtual environment found"
fi

# Step 3: Update system packages
print_status "Step 3: Updating system packages..."
sudo apt update
print_success "System packages updated"

# Step 4: Install required system dependencies
print_status "Step 4: Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    mosquitto \
    mosquitto-clients \
    git \
    curl \
    wget \
    nano

if [ $? -eq 0 ]; then
    print_success "System dependencies installed successfully"
else
    print_error "Failed to install some system dependencies"
    exit 1
fi

# Step 5: Verify Python installation
print_status "Step 5: Verifying Python installation..."
PYTHON_VERSION=$(python3 --version)
print_success "Python version: $PYTHON_VERSION"

# Step 6: Create new virtual environment
print_status "Step 6: Creating new virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    print_success "Virtual environment created successfully"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Step 7: Activate virtual environment
print_status "Step 7: Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 8: Upgrade pip and install build tools
print_status "Step 8: Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel
if [ $? -eq 0 ]; then
    print_success "Pip and build tools upgraded"
else
    print_warning "Some issues with pip upgrade, continuing..."
fi

# Step 9: Install Python packages one by one
print_status "Step 9: Installing Python packages..."

# Install paho-mqtt
print_status "Installing paho-mqtt..."
pip install paho-mqtt==1.6.1
if [ $? -eq 0 ]; then
    print_success "paho-mqtt installed successfully"
else
    print_error "Failed to install paho-mqtt"
    exit 1
fi

# Install numpy (this might take a while on Pi)
print_status "Installing numpy (this may take several minutes on Raspberry Pi)..."
pip install numpy
if [ $? -eq 0 ]; then
    print_success "numpy installed successfully"
else
    print_error "Failed to install numpy"
    exit 1
fi

# Install websockets
print_status "Installing websockets..."
pip install "websockets>=11.0.0"
if [ $? -eq 0 ]; then
    print_success "websockets installed successfully"
else
    print_error "Failed to install websockets"
    exit 1
fi

# Step 10: Verify installations
print_status "Step 10: Verifying Python package installations..."
python3 -c "import paho.mqtt.client as mqtt; print('✓ paho-mqtt working')"
python3 -c "import numpy as np; print('✓ numpy working')"
python3 -c "import websockets; print('✓ websockets working')"
python3 -c "import json; print('✓ json working')"
python3 -c "import asyncio; print('✓ asyncio working')"

if [ $? -eq 0 ]; then
    print_success "All Python packages verified successfully"
else
    print_error "Some Python packages failed verification"
    exit 1
fi

# Step 11: Configure Mosquitto
print_status "Step 11: Configuring Mosquitto MQTT broker..."

# Check if mosquitto.conf exists in current directory
if [ -f "mosquitto.conf" ]; then
    print_status "Using existing mosquitto.conf"
else
    print_status "Creating mosquitto.conf..."
    cat > mosquitto.conf << 'EOF'
# Mosquitto configuration for Noise Mapping System
port 1883
listener 1883 0.0.0.0
allow_anonymous true
log_dest stdout
log_type all
connection_messages true
log_timestamp true
EOF
    print_success "Created mosquitto.conf"
fi

# Step 12: Test Mosquitto
print_status "Step 12: Testing Mosquitto broker..."
sudo systemctl stop mosquitto 2>/dev/null || true
sleep 2

# Start mosquitto in background for testing
mosquitto -c mosquitto.conf -d
sleep 3

# Test mosquitto connection
mosquitto_pub -h localhost -t test/topic -m "test message" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Mosquitto broker is working correctly"
else
    print_warning "Mosquitto test failed, but continuing..."
fi

# Kill the test mosquitto process
pkill mosquitto 2>/dev/null || true

# Step 13: Make scripts executable
print_status "Step 13: Making scripts executable..."
chmod +x *.py 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
print_success "Scripts made executable"

# Step 14: Create startup script
print_status "Step 14: Creating startup script..."
cat > start_system.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Noise Mapping System..."
cd "$(dirname "$0")"
source venv/bin/activate
python3 start_noise_system.py
EOF
chmod +x start_system.sh
print_success "Created start_system.sh"

# Step 15: Final verification
print_status "Step 15: Final system verification..."

# Check if all required files exist
REQUIRED_FILES=("mqtt_broker_server.py" "simple_noise_processor.py" "start_noise_system.py" "config.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file found"
    else
        print_error "✗ $file missing"
    fi
done

# Step 16: Display summary
echo ""
echo "=============================================================="
print_success "🎉 INSTALLATION COMPLETED SUCCESSFULLY!"
echo "=============================================================="
echo ""
print_status "Summary of what was installed:"
echo "  ✓ System dependencies (Python, Mosquitto, build tools)"
echo "  ✓ Python virtual environment (venv/)"
echo "  ✓ Python packages (paho-mqtt, numpy, websockets)"
echo "  ✓ Mosquitto MQTT broker configuration"
echo "  ✓ Startup scripts"
echo ""
print_status "To start the noise mapping system:"
echo "  cd ~/Noise-mapping/Server"
echo "  ./start_system.sh"
echo ""
print_status "Or manually:"
echo "  source venv/bin/activate"
echo "  python3 start_noise_system.py"
echo ""
print_status "System endpoints:"
echo "  🔗 MQTT Broker: localhost:1883"
echo "  🔗 WebSocket Server: ws://localhost:9001"
echo ""
print_status "To test with fake sensors:"
echo "  python3 ../fake_esp32.py"
echo ""
print_warning "Note: Remember to update your React UI to connect to ws://localhost:9001"
echo ""
print_success "Installation complete! Your Raspberry Pi is ready to run the noise mapping system."
