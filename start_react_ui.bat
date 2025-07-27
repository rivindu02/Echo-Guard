@echo off
REM Smart Noise Monitoring System - Windows React UI Startup Script

echo 🔊 Starting Smart Noise Monitoring React UI...

cd /d "%~dp0mqtt-noise-map-ui"

if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
)

echo 🌐 Starting React development server...
echo 📋 The UI will open automatically in your browser
echo 🔗 URL: http://localhost:3000
echo.
echo ⚠️  Make sure the Pi server is running first!
echo.

npm start
