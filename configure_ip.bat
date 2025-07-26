@echo off
echo ========================================
echo   Noise Mapping - IP Configuration
echo ========================================
echo.
echo Current configuration (config.ini):

REM Display current Pi IP from config.ini if it exists
if exist config.ini (
    findstr "pi_ip" config.ini
) else (
    echo No config.ini found - will create one
)

echo.
echo Choose an option:
echo 1. Use default Pi IP (192.168.1.12)
echo 2. Enter custom Pi IP
echo 3. Use localhost only
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto default_pi
if "%choice%"=="2" goto custom_pi
if "%choice%"=="3" goto localhost_only
echo Invalid choice!
pause
exit /b 1

:default_pi
set PI_IP=192.168.1.12
goto update_config

:custom_pi
set /p PI_IP="Enter your Pi IP address: "
goto update_config

:localhost_only
echo.
echo 🔧 Configuring for localhost only...
cd mqtt-noise-map-ui
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://%PI_IP%:9001>> .env
cd ..
echo ✅ Configured for localhost
echo.
echo Run: start_local_system.bat
goto end

:update_config
echo.
echo 🔧 Updating configuration for Pi IP: %PI_IP%
echo.

REM Update config.ini
echo # Noise Mapping System Configuration> config.ini
echo # Edit this file to change IP addresses easily>> config.ini
echo.>> config.ini
echo [pi_connection]>> config.ini
echo # Raspberry Pi IP address (change this to your Pi's IP)>> config.ini
echo pi_ip = %PI_IP%>> config.ini
echo.>> config.ini
echo # Ports (usually don't need to change these)>> config.ini
echo mqtt_port = 1883>> config.ini
echo websocket_port = 9001>> config.ini
echo.>> config.ini
echo [local_connection]>> config.ini
echo # Local development settings>> config.ini
echo local_ip = localhost>> config.ini
echo mqtt_port = 1883>> config.ini
echo websocket_port = 9001>> config.ini
echo.>> config.ini
echo [fake_esp32]>> config.ini
echo # Default number of simulated devices>> config.ini
echo device_count = 5>> config.ini
echo # Publishing interval in seconds>> config.ini
echo publish_interval = 3>> config.ini

REM Update React UI .env file
cd mqtt-noise-map-ui
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi>> .env
echo REACT_APP_WEBSOCKET_URL=ws://%PI_IP%:9001>> .env
cd ..

echo ✅ Configuration updated!
echo.
echo 📋 Summary:
echo    Pi IP: %PI_IP%
echo    React UI will connect to: ws://%PI_IP%:9001
echo    fake_esp32.py will send data to: %PI_IP%:1883
echo.
echo 🚀 To start the system:
echo    1. On Pi (%PI_IP%): python3 start_noise_system.py
echo    2. On this PC: connect_to_pi.bat
echo.

:end
pause
