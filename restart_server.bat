@echo off
echo Stopping existing Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak > nul

echo Starting server...
start "Noise Mapping Server" python Server/mqtt_broker_server.py

echo Server restarted! Check mqtt_broker.log for status.
