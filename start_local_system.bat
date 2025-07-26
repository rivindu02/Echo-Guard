@echo off
echo ========================================
echo   Starting LOCAL Noise Mapping System
echo ========================================
echo.
echo This will start the system for local testing with:
echo - fake_esp32.py (simulated ESP32 devices)
echo - mqtt_broker_server.py (MQTT broker + WebSocket server)
echo - React UI (connecting to localhost)
echo.

REM Configure for local setup
cd mqtt-noise-map-ui
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://192.168.1.11:9001>> .env
cd ..

echo ✅ Configured for local setup!
echo.
echo Starting components...
echo.

REM Start MQTT broker server in background
echo 🔌 Starting MQTT broker server...
start "MQTT Broker Server" cmd /k "python Server\mqtt_broker_server.py"
timeout /t 3 /nobreak > nul

REM Start fake ESP32 simulator
echo 📡 Starting ESP32 simulator...
start "ESP32 Simulator" cmd /k "python fake_esp32.py --devices 3 --interval 5"
timeout /t 2 /nobreak > nul

REM Start React UI
echo 🌐 Starting React UI...
echo (This will open in your default browser)
cd mqtt-noise-map-ui
start "React UI" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo   🚀 System Starting!
echo ========================================
echo.
echo The following windows should open:
echo 1. MQTT Broker Server (background service)
echo 2. ESP32 Simulator (fake sensor data)
echo 3. React UI (web interface at http://localhost:3000)
echo.
echo To stop everything, close all the opened windows.
echo.
pause
