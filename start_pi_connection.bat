@echo off
echo ========================================
echo   Connecting to Raspberry Pi System
echo ========================================
echo.
echo This will configure the system to connect to your Raspberry Pi at 192.168.1.11
echo.
echo Prerequisites:
echo - Raspberry Pi should be running: python3 start_noise_system.py
echo - Pi should be accessible at 192.168.1.11:9001
echo.

REM Configure for Pi setup
cd mqtt-noise-map-ui
echo # WebSocket connection for Python backend> .env
echo # For local development (using localhost)>> .env
echo #REACT_APP_WEBSOCKET_URL=ws://localhost:9001>> .env
echo.>> .env
echo # For connecting to Raspberry Pi (uncomment the line below and comment the localhost line above)>> .env
echo REACT_APP_WEBSOCKET_URL=ws://192.168.1.11:9001>> .env
cd ..

echo ✅ Configured for Raspberry Pi setup!
echo.
echo Starting components...
echo.

REM Start fake ESP32 simulator connecting to Pi
echo 📡 Starting ESP32 simulator (connecting to Pi)...
start "ESP32 Simulator -> Pi" cmd /k "python fake_esp32.py --broker 192.168.1.11 --devices 3 --interval 5"
timeout /t 2 /nobreak > nul

REM Start React UI
echo 🌐 Starting React UI...
echo (This will connect to Pi and open in your browser)
cd mqtt-noise-map-ui
start "React UI -> Pi" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo   🚀 System Connecting to Pi!
echo ========================================
echo.
echo The following windows should open:
echo 1. ESP32 Simulator (sending data to Pi at 192.168.1.11)
echo 2. React UI (connecting to Pi WebSocket at ws://192.168.1.11:9001)
echo.
echo Make sure your Raspberry Pi is running the noise system!
echo On Pi run: python3 start_noise_system.py
echo.
pause
