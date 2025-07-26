# 🛠️ Raspberry Pi Cleanup and Installation Guide

## Current Situation
You have a broken Python environment with scipy installation issues. Let's clean this up completely and start fresh.

## Quick Fix (Copy-Paste Commands)

Run these commands **one by one** on your Raspberry Pi:

### 1. Navigate to the Server directory
```bash
cd ~/Noise-mapping/Server
```

### 2. Download and run the cleanup script
```bash
# Make the cleanup script executable
chmod +x cleanup_and_install.sh

# Run the cleanup and installation
./cleanup_and_install.sh
```

## Manual Step-by-Step (if script fails)

If the automated script doesn't work, follow these manual steps:

### Step 1: Fix the dpkg issue
```bash
sudo dpkg --configure -a
```

### Step 2: Clean up the broken environment
```bash
# Deactivate virtual environment if active
deactivate

# Remove the broken virtual environment
rm -rf venv

# Clear pip cache
rm -rf ~/.cache/pip
```

### Step 3: Install system dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential mosquitto mosquitto-clients
```

### Step 4: Create fresh virtual environment
```bash
# Create new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 5: Install Python packages (one by one)
```bash
# Install MQTT client
pip install paho-mqtt==1.6.1

# Install numpy (this will take 5-10 minutes on Pi)
pip install numpy

# Install websockets
pip install websockets
```

### Step 6: Test the installation
```bash
# Test Python imports
python3 -c "import paho.mqtt.client; print('MQTT OK')"
python3 -c "import numpy; print('NumPy OK')"
python3 -c "import websockets; print('WebSockets OK')"
```

### Step 7: Start the system
```bash
# Start the noise mapping system
python3 start_noise_system.py
```

## What This Fixes

1. **🧹 Cleans up broken scipy installation**
2. **🔧 Removes problematic virtual environment**
3. **📦 Installs only required packages (no scipy)**
4. **🔌 Configures Mosquitto MQTT broker**
5. **✅ Verifies everything works**

## Expected Output

When successful, you should see:
```
🚀 Starting Noise Mapping System...
📡 Starting Mosquitto MQTT broker...
🌐 Starting WebSocket server on ws://localhost:9001
🔄 Starting noise data processor...
✅ All systems operational!
```

## Troubleshooting

### If numpy installation takes forever:
```bash
# Cancel with Ctrl+C and try with pre-compiled wheel
pip install numpy --only-binary=numpy
```

### If you get permission errors:
```bash
# Make sure you're not running as root
whoami  # should NOT show 'root'

# Fix permissions if needed
sudo chown -R $USER:$USER ~/Noise-mapping
```

### If Mosquitto won't start:
```bash
# Check if it's already running
sudo systemctl status mosquitto

# Stop system mosquitto if needed
sudo systemctl stop mosquitto
```

## After Installation

1. **Test with fake sensors:**
   ```bash
   cd ~/Noise-mapping
   python3 fake_esp32.py
   ```

2. **Connect React UI:**
   - Update WebSocket URL to: `ws://your-pi-ip:9001`
   - Or use: `ws://localhost:9001` if running locally

3. **Monitor logs:**
   ```bash
   tail -f ~/Noise-mapping/Server/*.log
   ```

## File Summary

The cleanup creates these files:
- ✅ `venv/` - Clean Python virtual environment
- ✅ `mosquitto.conf` - MQTT broker configuration
- ✅ `start_system.sh` - Easy startup script
- ✅ Updated `requirements.txt` - Without scipy

Your system should now work without any scipy-related issues!
