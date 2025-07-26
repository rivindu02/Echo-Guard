@echo off
REM React UI Startup Script for Pi Connection (Windows)
REM Sets the correct WebSocket URL for connecting to Raspberry Pi

REM Configuration
set PI_IP=192.168.1.11
set WEBSOCKET_PORT=9001

echo 🚀 Starting React UI with Pi connection...
echo 📡 Connecting to WebSocket: ws://%PI_IP%:%WEBSOCKET_PORT%
echo.

REM Check if we're in the React UI directory
if not exist "package.json" (
    echo ❌ Error: Not in React UI directory
    echo Please run this script from: mqtt-noise-map-ui\
    pause
    exit /b 1
)

REM Set environment variable and start React app
set REACT_APP_WEBSOCKET_URL=ws://%PI_IP%:%WEBSOCKET_PORT%

echo 🌐 Environment configured:
echo    REACT_APP_WEBSOCKET_URL=%REACT_APP_WEBSOCKET_URL%
echo.

echo ▶️ Starting React development server...
npm start
