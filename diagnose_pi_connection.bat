@echo off
echo ==========================================
echo   Diagnosing Pi Connection Issues
echo ==========================================
echo.

set PI_IP=192.168.1.11

echo Testing connection to Pi at %PI_IP%...
echo.

REM Test basic connectivity
echo 1. Testing basic connectivity...
ping -n 2 %PI_IP% >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Pi is reachable at %PI_IP%
) else (
    echo ❌ Cannot reach Pi at %PI_IP%
    echo Check: Pi is on, connected to network, correct IP
    pause
    exit /b 1
)

echo.
echo 2. Testing MQTT port 1883...
REM Try to connect to MQTT port
powershell -Command "try { $tcp = New-Object System.Net.Sockets.TcpClient; $tcp.ConnectAsync('%PI_IP%', 1883).Wait(3000); if($tcp.Connected) { Write-Host '✅ MQTT port 1883 is open'; $tcp.Close() } else { Write-Host '❌ MQTT port 1883 is not accessible' } } catch { Write-Host '❌ Cannot connect to MQTT port 1883' }"

echo.
echo 3. Testing WebSocket port 9001...
REM Try to connect to WebSocket port  
powershell -Command "try { $tcp = New-Object System.Net.Sockets.TcpClient; $tcp.ConnectAsync('%PI_IP%', 9001).Wait(3000); if($tcp.Connected) { Write-Host '✅ WebSocket port 9001 is open'; $tcp.Close() } else { Write-Host '❌ WebSocket port 9001 is not accessible' } } catch { Write-Host '❌ Cannot connect to WebSocket port 9001' }"

echo.
echo ==========================================
echo           TROUBLESHOOTING STEPS
echo ==========================================
echo.
echo If ports are not accessible, run this ON THE RASPBERRY PI:
echo.
echo   1. Check if services are running:
echo      ps aux ^| grep mosquitto
echo      ps aux ^| grep python3
echo.
echo   2. Fix and start Mosquitto:
echo      chmod +x Server/fix_mosquitto_pi.sh
echo      cd Server
echo      ./fix_mosquitto_pi.sh
echo.
echo   3. Start the noise system:
echo      python3 start_noise_system.py
echo.
echo   4. Check if ports are listening:
echo      sudo netstat -tlnp ^| grep :1883
echo      sudo netstat -tlnp ^| grep :9001
echo.
echo   5. Check firewall (if applicable):
echo      sudo ufw status
echo      sudo ufw allow 1883
echo      sudo ufw allow 9001
echo.
echo ==========================================
echo.
pause
