#!/bin/bash

echo "=========================================="
echo "   Pi MQTT Broker Troubleshooting & Fix"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_info "Checking and fixing MQTT broker setup on Raspberry Pi..."
echo

# 1. Check if mosquitto is installed
print_info "1. Checking if Mosquitto is installed..."
if command -v mosquitto &> /dev/null; then
    print_success "Mosquitto is installed"
    mosquitto -h | head -1
else
    print_error "Mosquitto not found! Installing..."
    sudo apt update
    sudo apt install -y mosquitto mosquitto-clients
fi
echo

# 2. Stop any running mosquitto services
print_info "2. Stopping existing Mosquitto services..."
sudo systemctl stop mosquitto 2>/dev/null || print_warning "Systemd mosquitto not running"
sudo pkill mosquitto 2>/dev/null || print_warning "No mosquitto processes to kill"
print_success "Cleared existing mosquitto processes"
echo

# 3. Copy and apply our configuration
print_info "3. Setting up Mosquitto configuration..."
if [ -f "etc/mosquitto/mosquitto.conf" ]; then
    sudo cp etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf
    print_success "Copied mosquitto configuration"
else
    print_warning "Local config not found, creating one..."
    sudo tee /etc/mosquitto/mosquitto.conf > /dev/null << 'EOF'
# /etc/mosquitto/mosquitto.conf

# Basic configuration
pid_file /run/mosquitto/mosquitto.pid
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# MQTT over TCP - LISTEN ON ALL INTERFACES
listener 1883 0.0.0.0
protocol mqtt

# WebSocket support for React UI - LISTEN ON ALL INTERFACES
listener 9001 0.0.0.0
protocol websockets

# Allow anonymous connections (configure authentication as needed)
allow_anonymous true

# Maximum message size (for large interpolated grids)
message_size_limit 1048576
EOF
    print_success "Created mosquitto configuration"
fi
echo

# 4. Set proper permissions
print_info "4. Setting up permissions..."
sudo mkdir -p /var/lib/mosquitto
sudo mkdir -p /var/log/mosquitto
sudo mkdir -p /run/mosquitto
sudo chown -R mosquitto:mosquitto /var/lib/mosquitto /var/log/mosquitto /run/mosquitto 2>/dev/null || print_warning "mosquitto user not found (continuing anyway)"
print_success "Set up directories and permissions"
echo

# 5. Test mosquitto configuration
print_info "5. Testing Mosquitto configuration..."
if mosquitto -c /etc/mosquitto/mosquitto.conf -t 2>&1 | grep -q "Error"; then
    print_error "Configuration test failed!"
    mosquitto -c /etc/mosquitto/mosquitto.conf -t
    exit 1
else
    print_success "Configuration test passed"
fi
echo

# 6. Start mosquitto manually (not as service)
print_info "6. Starting Mosquitto broker..."
print_info "Starting in background..."

# Start mosquitto in background and capture PID
nohup mosquitto -c /etc/mosquitto/mosquitto.conf > /tmp/mosquitto_manual.log 2>&1 &
MOSQUITTO_PID=$!
sleep 2

# Check if it's running
if kill -0 $MOSQUITTO_PID 2>/dev/null; then
    print_success "Mosquitto started successfully (PID: $MOSQUITTO_PID)"
    echo $MOSQUITTO_PID > /tmp/mosquitto.pid
else
    print_error "Failed to start Mosquitto"
    cat /tmp/mosquitto_manual.log
    exit 1
fi
echo

# 7. Test the broker
print_info "7. Testing MQTT broker connectivity..."

# Test MQTT port
print_info "Testing MQTT port 1883..."
timeout 5 mosquitto_pub -h localhost -p 1883 -t test/topic -m "test message" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "MQTT port 1883 is working"
else
    print_warning "MQTT port 1883 test failed"
fi

# Test WebSocket port
print_info "Testing WebSocket port 9001..."
if netstat -tlnp 2>/dev/null | grep -q ":9001"; then
    print_success "WebSocket port 9001 is listening"
else
    print_warning "WebSocket port 9001 may not be ready yet"
fi
echo

# 8. Show status
print_info "8. Current status:"
echo "Mosquitto PID: $MOSQUITTO_PID"
echo "Log file: /tmp/mosquitto_manual.log"
echo "Config file: /etc/mosquitto/mosquitto.conf"
echo
print_info "Listening ports:"
netstat -tlnp 2>/dev/null | grep -E "(1883|9001)" || print_warning "Ports not yet visible in netstat"
echo

# 9. Show next steps
echo "=========================================="
echo "           NEXT STEPS"
echo "=========================================="
echo
print_success "Mosquitto broker is now running!"
echo
echo "Now run the noise system:"
echo "  python3 start_noise_system.py"
echo
echo "To test from your Windows machine:"
echo "  python fake_esp32.py --broker 192.168.1.11"
echo
echo "To stop Mosquitto later:"
echo "  kill $MOSQUITTO_PID"
echo "  # or"
echo "  sudo pkill mosquitto"
echo
echo "To check logs:"
echo "  tail -f /tmp/mosquitto_manual.log"
echo
echo "=========================================="
