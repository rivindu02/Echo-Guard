@echo off
echo ========================================
echo   Testing Connection to Raspberry Pi
echo ========================================
echo.

set PI_IP=192.168.1.11

echo Testing connection to Pi at %PI_IP%...
echo.

echo 1. Testing basic connectivity...
ping -n 2 %PI_IP% > nul
if %errorlevel% equ 0 (
    echo ✅ Pi is reachable at %PI_IP%
) else (
    echo ❌ Cannot reach Pi at %PI_IP%
    echo    Please check:
    echo    - Pi is powered on
    echo    - Pi is connected to network
    echo    - IP address is correct
    pause
    exit /b 1
)

echo.
echo 2. Testing MQTT port (1883)...
timeout /t 1 /nobreak > nul
netstat -an | findstr "%PI_IP%:1883" > nul
echo    (MQTT broker should be running on Pi)

echo.
echo 3. Testing WebSocket port (9001)...
timeout /t 1 /nobreak > nul
echo    (WebSocket server should be running on Pi)

echo.
echo 4. Testing fake ESP32 connection...
echo    Starting a quick test connection...
timeout /t 2 /nobreak > nul
start /min "Test ESP32" cmd /c "python fake_esp32.py --broker %PI_IP% --devices 1 --interval 10 & timeout /t 10 & taskkill /f /im python.exe /fi \"WINDOWTITLE eq Test ESP32\""

echo.
echo ========================================
echo   Manual Verification Steps
echo ========================================
echo.
echo On your Raspberry Pi, verify these are running:
echo   1. Check if services are running:
echo      ps aux ^| grep python3
echo.
echo   2. Check if ports are listening:
echo      sudo netstat -tlnp ^| grep :1883  (MQTT)
echo      sudo netstat -tlnp ^| grep :9001  (WebSocket)
echo.
echo   3. Check system logs:
echo      tail -f system_startup.log
echo.
echo If everything looks good, you can now run:
echo   ./start_pi_connection.bat
echo.
pause
