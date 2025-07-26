@echo off
echo ========================================
echo   Pi Central Setup (192.168.1.12)
echo ========================================
echo.
echo 🥧 Starting system with Raspberry Pi as central MQTT broker
echo.
echo System architecture:
echo   PC (fake ESP32s) → Pi (MQTT broker) → PC (React UI)
echo.

REM Configure React UI for Pi
echo 🔧 Configuring React UI...
cd mqtt-noise-map-ui
echo REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001> .env.local
echo REACT_APP_MQTT_BROKER_URL=ws://192.168.1.12:9001>> .env.local
echo REACT_APP_MQTT_TOPIC_PREFIX=noise>> .env.local
echo REACT_APP_DEFAULT_MAP_CENTER_LAT=6.7964>> .env.local
echo REACT_APP_DEFAULT_MAP_CENTER_LON=79.9012>> .env.local
echo REACT_APP_DEFAULT_MAP_ZOOM=15>> .env.local
cd ..

echo ✅ React UI configured for Pi connection
echo.

echo 🚀 Starting services...
echo.

REM Start ESP32 simulator sending to Pi
echo 📡 Starting ESP32 simulators (sending to Pi)...
start "ESP32 to Pi" cmd /k "python fake_esp32.py --broker 192.168.1.12 --devices 5 --interval 3"
timeout /t 3 /nobreak > nul

REM Start React UI
echo 🌐 Starting React UI (connecting to Pi)...
cd mqtt-noise-map-ui
start "React UI" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo   🎯 System Started!
echo ========================================
echo.
echo Services running:
echo ✅ ESP32 simulators → sending data to Pi (192.168.1.12:1883)
echo ✅ React UI → connecting to Pi WebSocket (192.168.1.12:9001)
echo.
echo 🥧 ENSURE YOUR RASPBERRY PI IS RUNNING:
echo    ssh pi@192.168.1.12
echo    cd ~/Noise-mapping
echo    python3 Server/start_noise_system.py
echo.
echo 🌍 Access your system at: http://localhost:3000
echo.
echo Expected behavior:
echo ✅ ESP32 simulators show "Connected to MQTT broker at 192.168.1.12:1883"
echo ✅ React UI shows "Connected" status
echo ✅ Map displays sensor data from Pi
echo.
echo 🛑 To stop: Close both terminal windows or press Ctrl+C
echo.
pause
