@echo off
echo ========================================
echo   LOCAL TESTING - Noise Mapping System
echo ========================================
echo.
echo 🏠 LOCAL TESTING MODE (No Hardware Required)
echo.
echo This starts a complete local development environment:
echo ✅ MQTT broker server (localhost:1883 + WebSocket :9001)
echo ✅ Simulated ESP32 sensors (fake_esp32.py)  
echo ✅ React UI (localhost:3000)
echo ✅ Real-time data visualization
echo.
echo 📋 Perfect for: Development, testing, demos, learning
echo 🔗 See LOCAL_TESTING_GUIDE.md for detailed information
echo.

REM Configure for local setup
cd mqtt-noise-map-ui
echo # Local testing configuration - No central device required> .env.local
echo # WebSocket connection for Python backend>> .env.local
echo REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env.local
echo REACT_APP_MQTT_BROKER_URL=ws://localhost:9001>> .env.local
echo REACT_APP_MQTT_TOPIC_PREFIX=noise>> .env.local
echo.>> .env.local
echo # Map configuration for test data>> .env.local
echo REACT_APP_DEFAULT_MAP_CENTER_LAT=6.7964>> .env.local
echo REACT_APP_DEFAULT_MAP_CENTER_LON=79.9012>> .env.local
echo REACT_APP_DEFAULT_MAP_ZOOM=15>> .env.local
echo.>> .env.local
echo # Development features>> .env.local
echo REACT_APP_ENABLE_NOTIFICATIONS=true>> .env.local
echo REACT_APP_AUTO_REFRESH_INTERVAL=3000>> .env.local
echo REACT_APP_DEBUG_MODE=true>> .env.local
cd ..

echo ✅ Configured for local testing (see mqtt-noise-map-ui/.env.local)
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
echo   🚀 LOCAL TESTING SYSTEM READY!
echo ========================================
echo.
echo The following services are starting:
echo 1. 🔌 MQTT Broker Server (Python backend)
echo 2. 📡 ESP32 Simulator (5 virtual sensors)
echo 3. 🌐 React UI (web interface)
echo.
echo 🌍 Access your system at: http://localhost:3000
echo.
echo 📊 Expected behavior:
echo ✅ Map shows sensor markers  
echo ✅ Connection status: "Connected"
echo ✅ Noise levels update every 3-5 seconds
echo ✅ No error messages in browser console
echo.
echo 🛑 To stop: Close all terminal windows or press Ctrl+C
echo 📖 Troubleshooting: See LOCAL_TESTING_GUIDE.md
echo.
pause
echo 2. ESP32 Simulator (fake sensor data)
echo 3. React UI (web interface at http://localhost:3000)
echo.
echo To stop everything, close all the opened windows.
echo.
pause
