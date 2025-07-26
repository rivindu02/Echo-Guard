@echo off
echo ========================================
echo   Noise Mapping - Pi Connection Setup
echo ========================================
echo.
echo This script connects to Raspberry Pi as MQTT broker
echo Pi IP: 192.168.1.12 (edit config.ini to change)
echo.
echo What this does:
echo 1. Starts fake_esp32.py to send data to Pi
echo 2. Configures React UI to connect to Pi WebSocket
echo 3. Starts React UI locally
echo.
echo Make sure your Pi is running:
echo   python3 start_noise_system.py
echo.
pause

echo.
echo 📡 Step 1: Starting fake ESP32 sensors (connecting to Pi)...
echo.
start /b cmd /c "python fake_esp32.py --pi && pause"

echo.
echo 🔧 Step 2: Configuring React UI for Pi connection...
cd mqtt-noise-map-ui

REM Create backup of current .env
if exist .env (
    copy .env .env.backup > nul
    echo ✅ Backed up current .env to .env.backup
)

REM Update .env for Pi connection
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi>> .env
echo REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001>> .env

echo ✅ Configured React UI to connect to Pi (192.168.1.12:9001)

echo.
echo 🌐 Step 3: Starting React UI...
echo Access at: http://localhost:3000
echo.

npm start
