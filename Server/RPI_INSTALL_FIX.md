# Raspberry Pi Installation Fix

## Current Issue
The scipy package is failing to install due to missing OpenBLAS dependency, but **good news**: your project doesn't actually need scipy!

## Quick Fix

1. **First, fix the interrupted dpkg operation:**
   ```bash
   sudo dpkg --configure -a
   ```

2. **Deactivate the current virtual environment and remove it:**
   ```bash
   deactivate
   rm -rf venv
   ```

3. **Install system dependencies (in case numpy needs compilation):**
   ```bash
   sudo apt install -y libopenblas-dev python3-dev build-essential
   ```

4. **Create a new virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install the updated requirements (without scipy):**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Alternative: Use the automated script
Run the Raspberry Pi setup script:
```bash
chmod +x install_rpi.sh
./install_rpi.sh
```

## What Changed
- Removed scipy from requirements.txt (not needed by your code)
- Your project uses a custom Inverse Distance Weighting (IDW) interpolation with numpy only
- Updated version constraints to be more flexible for ARM architecture

## If You Still Have Issues
Try installing packages individually:
```bash
pip install paho-mqtt==1.6.1
pip install numpy
pip install websockets
```

The numpy package on Raspberry Pi sometimes takes a while to compile, so be patient.
