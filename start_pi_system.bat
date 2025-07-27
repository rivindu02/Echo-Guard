@echo off
echo ========================================
echo   Starting Noise Mapping System
echo   Pi IP: 172.20.10.2
echo ========================================
echo.

echo Starting fake ESP32 sensors connecting to Pi...
start cmd /k "title Fake ESP32 Sensors && python fake_esp32.py --broker 172.20.10.2"

echo.
echo Waiting 3 seconds for sensors to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting React UI...
cd mqtt-noise-map-ui
start cmd /k "title React UI && npx react-scripts start"
cd ..

echo.
echo ========================================
echo   System Starting!
echo ========================================
echo.
echo Make sure your Raspberry Pi (172.20.10.2) is running:
echo   python3 start_noise_system.py
echo.
echo Access the web interface at:
echo   http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul
