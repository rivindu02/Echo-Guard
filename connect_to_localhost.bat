@echo off
echo ========================================
echo   Noise Mapping - Localhost Setup
echo ========================================
echo.
echo This script configures for local testing
echo.
echo What this does:
echo 1. Configures React UI for localhost connection
echo 2. You can then run: start_local_system.bat
echo.

echo 🔧 Configuring React UI for localhost connection...
cd mqtt-noise-map-ui

REM Create backup of current .env
if exist .env (
    copy .env .env.backup > nul
    echo ✅ Backed up current .env to .env.backup
)

REM Update .env for localhost connection
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001>> .env

echo ✅ Configured React UI for localhost connection
echo.
echo 🚀 Now you can run:
echo    start_local_system.bat
echo.
echo Or manually:
echo    python fake_esp32.py
echo    python Server\mqtt_broker_server.py
echo    cd mqtt-noise-map-ui ^&^& npm start
echo.
pause
