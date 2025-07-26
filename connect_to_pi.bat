@echo off
echo ========================================
echo   Connect to Raspberry Pi (192.168.1.12)
echo ========================================
echo.
echo 🥧 RASPBERRY PI SETUP - Using Pi as Central MQTT Broker
echo.
echo This will configure the system to use your Raspberry Pi at 192.168.1.12 as:
echo ✅ Central MQTT broker (port 1883)
echo ✅ WebSocket server (port 9001)  
echo ✅ Data processing hub
echo.
echo 📡 Your PC will run:
echo ✅ Simulated ESP32 sensors (fake_esp32.py)
echo ✅ React UI (connects to Pi)
echo.

echo 🧪 Step 1: Testing Pi connection...
echo Testing if Pi is reachable...
ping -n 2 192.168.1.12 > nul
if %errorlevel% == 0 (
    echo ✅ Pi is reachable at 192.168.1.12
) else (
    echo ❌ Cannot reach Pi at 192.168.1.12
    echo.
    echo 🔧 TROUBLESHOOTING:
    echo 1. Check Pi is powered on and connected to WiFi
    echo 2. Verify Pi IP: ssh pi@192.168.1.12
    echo 3. Make sure both devices are on same network
    echo.
    pause
    exit /b 1
)

echo.
echo � Step 2: Configuring React UI for Pi connection...
cd mqtt-noise-map-ui
echo # Raspberry Pi connection configuration> .env.local
echo # React UI connects to Pi WebSocket server>> .env.local
echo REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001>> .env.local
echo REACT_APP_MQTT_BROKER_URL=ws://192.168.1.12:9001>> .env.local
echo REACT_APP_MQTT_TOPIC_PREFIX=noise>> .env.local
echo.>> .env.local
echo # Map configuration>> .env.local
echo REACT_APP_DEFAULT_MAP_CENTER_LAT=6.7964>> .env.local
echo REACT_APP_DEFAULT_MAP_CENTER_LON=79.9012>> .env.local
echo REACT_APP_DEFAULT_MAP_ZOOM=15>> .env.local
echo.>> .env.local
echo # Development features>> .env.local
echo REACT_APP_ENABLE_NOTIFICATIONS=true>> .env.local
echo REACT_APP_AUTO_REFRESH_INTERVAL=3000>> .env.local
echo REACT_APP_DEBUG_MODE=true>> .env.local
cd ..

echo ✅ React UI configured to connect to Pi (192.168.1.12:9001)
echo.

echo � Next Steps:
echo.
echo 🥧 ON RASPBERRY PI (192.168.1.12):
echo    1. SSH to Pi: ssh pi@192.168.1.12
echo    2. Navigate to project: cd ~/Noise-mapping
echo    3. Start services: python3 Server/start_noise_system.py
echo.
echo 💻 ON THIS PC:
echo    1. Start ESP32 simulators: python fake_esp32.py --broker 192.168.1.12
echo    2. Start React UI: cd mqtt-noise-map-ui ^&^& npm start
echo    3. Access UI: http://localhost:3000
echo.
echo 🎯 Expected Data Flow:
echo    PC (fake ESP32s) → Pi (MQTT broker) → PC (React UI)
echo.

set /p start="Do you want to start the ESP32 simulators now? (y/n): "
if /i "%start%"=="y" goto start_esp32
if /i "%start%"=="yes" goto start_esp32
goto manual

:start_esp32
echo.
echo 🚀 Starting ESP32 simulators (sending data to Pi)...
echo Press Ctrl+C to stop the simulators
echo.
python fake_esp32.py --broker 192.168.1.12 --devices 5 --interval 3
goto end

:manual
echo.
echo ✅ Configuration complete! 
echo.
echo Manual startup commands:
echo 1. python fake_esp32.py --broker 192.168.1.12
echo 2. cd mqtt-noise-map-ui ^&^& npm start
echo.

:end
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
