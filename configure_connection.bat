@echo off
echo ========================================
echo   Noise Mapping System Configuration
echo ========================================
echo.
echo Choose your setup:
echo 1. Local setup (localhost)
echo 2. Raspberry Pi setup (192.168.1.12)
echo 3. Custom IP address
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto pi
if "%choice%"=="3" goto custom
echo Invalid choice!
pause
exit /b 1

:local
echo.
echo Configuring for LOCAL setup...
cd mqtt-noise-map-ui
copy /y nul .env.temp > nul
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001>> .env
cd ..
echo.
echo ✅ Configuration updated for LOCAL setup!
echo.
echo To start the system locally:
echo 1. Run: python fake_esp32.py
echo 2. Run: python Server\mqtt_broker_server.py  
echo 3. Run: cd mqtt-noise-map-ui ^&^& npm start
goto end

:pi
echo.
echo Configuring for RASPBERRY PI setup...
cd mqtt-noise-map-ui
copy /y nul .env.temp > nul
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)>> .env
echo REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001>> .env
cd ..
echo.
echo ✅ Configuration updated for RASPBERRY PI setup!
echo.
echo To start the system:
echo 1. Make sure Pi is running: python3 start_noise_system.py
echo 2. Run locally: python fake_esp32.py --broker 192.168.1.12
echo 3. Run: cd mqtt-noise-map-ui ^&^& npm start
goto end

:custom
echo.
set /p custom_ip="Enter the IP address: "
echo.
echo Configuring for CUSTOM IP: %custom_ip%
cd mqtt-noise-map-ui
copy /y nul .env.temp > nul
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to custom IP>> .env
echo REACT_APP_WEBSOCKET_URL=ws://%custom_ip%:9001>> .env
cd ..
echo.
echo ✅ Configuration updated for CUSTOM IP: %custom_ip%!
echo.
echo To start the system:
echo 1. Make sure target system is running the server
echo 2. Run locally: python fake_esp32.py --broker %custom_ip%
echo 3. Run: cd mqtt-noise-map-ui ^&^& npm start

:end
echo.
pause
