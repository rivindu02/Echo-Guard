# Quick Pi IP Configuration Guide 🍓

## When to Update IP Address

Update the Pi IP address when:
- Moving to a different WiFi network
- Pi gets a new DHCP address
- Switching from hotspot to home WiFi
- Network configuration changes

## Step-by-Step IP Update Process

### 1. Find Pi's New IP Address
```bash
# SSH to Pi or use Pi directly:
hostname -I
# Example output: 192.168.1.100 172.17.0.1
# Use the first IP (192.168.1.100)
```

### 2. Update Configuration Files

#### File 1: `config.ini` (Root directory)
```ini
[pi_connection]
pi_ip = 192.168.1.100  # ← Update this line
mqtt_port = 1883
websocket_port = 9001
```

#### File 2: `mqtt-noise-map-ui/.env` (UI directory)
```env
# WebSocket Configuration
REACT_APP_WEBSOCKET_URL=ws://192.168.1.100:9001  # ← Update this line
```

### 3. Restart Services

```bash
# Stop running services (Ctrl+C):
# - fake_esp32.py
# - React UI (npm start)

# Restart with new configuration:
python fake_esp32.py          # Will read new IP from config.ini
cd mqtt-noise-map-ui && npm start  # Will read new IP from .env
```

## Common IP Address Ranges

| Network Type | IP Range | Example |
|--------------|----------|---------|
| Home WiFi Router | 192.168.1.x | 192.168.1.100 |
| Alternative Router | 192.168.0.x | 192.168.0.50 |
| Mobile Hotspot | 172.20.10.x | 172.20.10.2 |
| Office/School | 10.x.x.x | 10.0.1.50 |

## Testing Connectivity

```bash
# Test if Pi is reachable:
ping 192.168.1.100

# Test specific ports:
telnet 192.168.1.100 1883  # MQTT port
telnet 192.168.1.100 9001  # WebSocket port

# If telnet not available, use:
nc -zv 192.168.1.100 1883
nc -zv 192.168.1.100 9001
```

## Troubleshooting

### ❌ "Connection Refused"
- Check if Pi is powered on and connected to network
- Verify IP address is correct
- Check if services are running on Pi

### ❌ "No Route to Host" 
- Pi and PC must be on same network
- Check firewall settings on Pi
- Verify network connectivity

### ❌ WebSocket Connection Failed
- Ensure fixed_websocket_server.py is running on Pi
- Check port 9001 is not blocked by firewall
- Verify .env file has correct WebSocket URL

### ❌ MQTT Connection Failed
- Ensure Mosquitto broker is running on Pi: `sudo systemctl status mosquitto`
- Check port 1883 accessibility
- Verify config.ini has correct Pi IP

## Quick Commands

```bash
# Find files to edit:
nano config.ini
nano mqtt-noise-map-ui/.env

# Restart Pi services:
sudo systemctl restart mosquitto
python3 Server/fixed_websocket_server.py

# Restart PC services:
python fake_esp32.py
cd mqtt-noise-map-ui && npm start

# Check Pi network:
ip addr show
hostname -I
```

## Automation Script (Optional)

Create `update_pi_ip.sh` for quick updates:
```bash
#!/bin/bash
NEW_IP=$1
if [ -z "$NEW_IP" ]; then
    echo "Usage: $0 <new_pi_ip>"
    exit 1
fi

# Update config.ini
sed -i "s/pi_ip = .*/pi_ip = $NEW_IP/" config.ini

# Update .env
sed -i "s/REACT_APP_WEBSOCKET_URL=.*/REACT_APP_WEBSOCKET_URL=ws:\/\/$NEW_IP:9001/" mqtt-noise-map-ui/.env

echo "✅ Updated Pi IP to $NEW_IP"
echo "🔄 Restart services to apply changes"
```

Usage:
```bash
chmod +x update_pi_ip.sh
./update_pi_ip.sh 192.168.1.100
```
