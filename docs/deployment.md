# 🚀 Deployment Guide

## Production Deployment

### Raspberry Pi Setup

#### 1. System Requirements
- Raspberry Pi 4 (2GB+ RAM recommended)
- SD Card (16GB+ Class 10)
- Stable network connection
- Python 3.7+

#### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install MQTT broker
sudo apt install mosquitto mosquitto-clients -y

# Install Python packages
sudo apt install python3-pip -y
pip3 install websockets paho-mqtt

# Enable MQTT broker
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

#### 3. Configure Mosquitto
```bash
# Edit mosquitto config
sudo nano /etc/mosquitto/mosquitto.conf

# Add these lines:
listener 1883
allow_anonymous true
persistence true
log_dest /var/log/mosquitto/mosquitto.log
```

#### 4. Deploy Server Code
```bash
# Clone repository
git clone https://github.com/rivindu02/Noise-mapping.git
cd Noise-mapping

# Start WebSocket server
cd Server
python3 fixed_websocket_server.py
```

#### 5. Auto-start Service (Optional)
```bash
# Create systemd service
sudo nano /etc/systemd/system/noise-websocket.service

[Unit]
Description=Noise Monitoring WebSocket Server
After=network.target mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Noise-mapping/Server
ExecStart=/usr/bin/python3 fixed_websocket_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable service
sudo systemctl enable noise-websocket
sudo systemctl start noise-websocket
```

### React UI Deployment

#### 1. Build for Production
```bash
cd mqtt-noise-map-ui
npm install
npm run build
```

#### 2. Serve with Nginx
```bash
# Install nginx
sudo apt install nginx -y

# Copy build files
sudo cp -r build/* /var/www/html/

# Configure nginx
sudo nano /etc/nginx/sites-available/default

# Add WebSocket proxy:
location /ws {
    proxy_pass http://localhost:9001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Security Hardening

### 1. Firewall Configuration
```bash
# Install ufw
sudo apt install ufw -y

# Allow SSH
sudo ufw allow ssh

# Allow MQTT and WebSocket
sudo ufw allow 1883
sudo ufw allow 9001

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

### 2. MQTT Authentication
```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd username

# Update mosquitto.conf
password_file /etc/mosquitto/passwd
allow_anonymous false
```

### 3. SSL/TLS Setup
```bash
# Generate certificates
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/mosquitto.key \
  -out /etc/ssl/certs/mosquitto.crt

# Update mosquitto.conf
listener 8883
protocol mqtt
cafile /etc/ssl/certs/ca-certificates.crt
certfile /etc/ssl/certs/mosquitto.crt
keyfile /etc/ssl/private/mosquitto.key
```

## Monitoring & Maintenance

### 1. Log Monitoring
```bash
# Check MQTT logs
sudo tail -f /var/log/mosquitto/mosquitto.log

# Check WebSocket server logs
journalctl -u noise-websocket -f

# Check system logs
sudo tail -f /var/log/syslog
```

### 2. Performance Monitoring
```bash
# Monitor system resources
htop

# Monitor network connections
netstat -tuln | grep -E "(1883|9001)"

# Monitor MQTT topics
mosquitto_sub -h localhost -t "noise/#"
```

### 3. Backup Strategy
```bash
# Backup configuration
tar -czf backup_$(date +%Y%m%d).tar.gz \
  /etc/mosquitto/ \
  /home/pi/Noise-mapping/

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/noise_system_$DATE.tar.gz \
  /etc/mosquitto/ \
  /home/pi/Noise-mapping/
```

## Troubleshooting

### Common Issues

#### WebSocket Connection Failed
```bash
# Check if server is running
ps aux | grep websocket

# Check port availability
netstat -tuln | grep 9001

# Test connection
python3 -c "
import websocket
ws = websocket.WebSocket()
ws.connect('ws://localhost:9001')
print('Connection successful')
"
```

#### MQTT Broker Issues
```bash
# Check broker status
sudo systemctl status mosquitto

# Test MQTT connection
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# Check broker logs
sudo journalctl -u mosquitto
```

#### High CPU/Memory Usage
```bash
# Monitor resources
top -p $(pgrep -f websocket)

# Check memory usage
free -h

# Monitor network
iftop
```

### Performance Tuning

#### Mosquitto Optimization
```bash
# Edit /etc/mosquitto/mosquitto.conf
max_connections 1000
max_keepalive 60
message_size_limit 1024
```

#### System Optimization
```bash
# Increase file limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize network
echo "net.core.rmem_max = 16777216" >> /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" >> /etc/sysctl.conf
```
