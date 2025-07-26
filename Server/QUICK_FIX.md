# 🎯 FINAL SOLUTION: How to Fix Your Raspberry Pi

## The Problem
Your Raspberry Pi has a broken Python environment due to scipy installation failure.

## The Solution (Copy-Paste This)

**Step 1: Open terminal on your Raspberry Pi and navigate to the Server directory:**
```bash
cd ~/Noise-mapping/Server
```

**Step 2: Run the cleanup script:**
```bash
chmod +x cleanup_and_install.sh
./cleanup_and_install.sh
```

**Step 3: Test the installation:**
```bash
python3 test_installation.py
```

**Step 4: Start the system:**
```bash
./start_system.sh
```

## What This Does

1. **🧹 Fixes the broken dpkg**: `sudo dpkg --configure -a`
2. **🗑️ Removes broken environment**: Deletes the problematic `venv/`
3. **📦 Installs dependencies**: System packages + Python packages (NO scipy!)
4. **✅ Verifies everything**: Tests all components
5. **🚀 Ready to run**: Creates startup scripts

## Expected Result

You should see:
```
🚀 Starting Noise Mapping System...
📡 Starting Mosquitto MQTT broker...
🌐 Starting WebSocket server on ws://localhost:9001
🔄 Starting noise data processor...
✅ All systems operational!
```

## If It Still Doesn't Work

**Quick debug commands:**
```bash
# Check if you're in the right directory
pwd  # Should show: /home/rivindu02/Noise-mapping/Server

# Check if files exist
ls -la *.py

# Check virtual environment
source venv/bin/activate
which python3
python3 -c "import paho.mqtt.client; print('MQTT OK')"
```

**Last resort - manual commands:**
```bash
# Clean everything
rm -rf venv
sudo dpkg --configure -a

# Install manually
sudo apt install -y python3-venv mosquitto
python3 -m venv venv
source venv/bin/activate
pip install paho-mqtt numpy websockets

# Test
python3 -c "import paho.mqtt.client, numpy, websockets; print('All imports OK')"
```

## Files Created

After running the cleanup script, you'll have:
- ✅ `venv/` - Clean Python environment (no scipy!)
- ✅ `cleanup_and_install.sh` - The cleanup script
- ✅ `test_installation.py` - Test script
- ✅ `start_system.sh` - Easy startup
- ✅ `CLEANUP_GUIDE.md` - This guide
- ✅ Updated `requirements.txt` - Without problematic scipy

Your noise mapping system will work without scipy because it uses a custom interpolation algorithm with numpy only!

## Quick Commands Summary

```bash
cd ~/Noise-mapping/Server
./cleanup_and_install.sh
./start_system.sh
```

That's it! 🎉
