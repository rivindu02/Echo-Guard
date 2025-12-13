# Echo-Guard Docker Deployment Guide

## 🐳 Docker Setup - React UI Only

This guide covers dockerizing only the React UI. The **Server and MQTT Broker run on the Raspberry Pi**.

### Prerequisites
- Docker (v20.10+)
- Docker Compose (v1.29+)
- Raspberry Pi with running `fixed_websocket_server.py` and Mosquitto

### Install Docker

**Ubuntu/Debian/Raspberry Pi OS:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS (using Homebrew):**
```bash
brew install docker docker-compose
```

## 🚀 Quick Start

### Option 1: Using the Setup Script (Recommended)

```bash
chmod +x docker-entrypoint.sh
./docker-entrypoint.sh
```

Then:
1. Select option **8** to set Pi IP address (e.g., `192.168.208.242`)
2. Select option **1** to build React UI
3. Select option **2** to start React UI

### Option 2: Manual Docker Compose Commands

```bash
# Build React UI
docker-compose build noise-map-ui

# Start React UI (replace PI_IP with your Raspberry Pi IP)
PI_IP=192.168.208.242 docker-compose up -d noise-map-ui

# View logs
docker-compose logs -f noise-map-ui

# Stop React UI
docker-compose down
```

### Option 3: Using .env file

Create `.env` file in project root:
```bash
PI_IP=192.168.208.242
```

Then:
```bash
docker-compose up -d
```

## 📍 Architecture

```
Your Machine (Docker)          Raspberry Pi (Physical)
┌─────────────────────┐        ┌──────────────────────┐
│  React UI (3000)    │        │ WebSocket (9001)     │
└──────────┬──────────┘        └────────┬─────────────┘
           │ ws://192.168.x.x:9001       │
           └────────────────────────────►│
                                         │
                                  ┌──────▼──────┐
                                  │  Mosquitto  │
                                  │   (1883)    │
                                  └─────────────┘
```

## 🏗️ Container Details

### React UI Container
- **Image:** Built from `mqtt-noise-map-ui/Dockerfile`
- **Port:** 3000 (accessible at http://localhost:3000)
- **Environment:** 
  - `REACT_APP_WEBSOCKET_URL=ws://PI_IP:9001`
  - `NODE_ENV=production`
- **Health Check:** Every 30s
- **Auto-restart:** Yes

## 📊 Configuration

### Set Raspberry Pi IP

Three ways to set the Pi IP:

**Method 1: Interactive Script**
```bash
./docker-entrypoint.sh
# Select option 8 and enter your Pi IP
```

**Method 2: Environment Variable**
```bash
PI_IP=192.168.208.242 docker-compose up -d
```

**Method 3: .env File**
```bash
echo "PI_IP=192.168.208.242" > .env
docker-compose up -d
```

## 📦 Common Commands

```bash
# Build React UI image
docker-compose build noise-map-ui

# Start in background
docker-compose up -d

# View logs (last 50 lines, follow new output)
docker-compose logs -f --tail=50 noise-map-ui

# Stop container
docker-compose stop

# Remove container
docker-compose down

# Remove container and rebuild
docker-compose down && docker-compose build --no-cache noise-map-ui

# Enter container shell
docker-compose exec noise-map-ui /bin/sh

# Check container status
docker-compose ps
```

## 🐛 Troubleshooting

### React UI container won't start

```bash
# Check logs
docker-compose logs noise-map-ui

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache noise-map-ui
docker-compose up -d
```

### React UI shows blank page

1. Open browser console (F12)
2. Check for WebSocket connection errors
3. Verify Pi IP is correct in environment variables
4. Ensure Pi's WebSocket server is running:
   ```bash
   ssh pi@192.168.208.242
   ps aux | grep fixed_websocket_server.py
   ```

### WebSocket connection refused

```bash
# From your machine, test connectivity to Pi
ping 192.168.208.242
curl http://192.168.208.242:9001

# From Pi, verify server is running
ssh pi@192.168.208.242
python3 /path/to/Server/fixed_websocket_server.py
```

### Port 3000 already in use

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use a different port in docker-compose.yml:
# ports:
#   - "3001:3000"
```

### Wrong Pi IP address

```bash
# Update and restart
PI_IP=your-new-pi-ip docker-compose up -d --force-recreate
```

## 📈 Monitoring

### Check container health
```bash
docker-compose ps
```

Should show:
```
NAME                STATUS           PORTS
echo-guard-ui       Up (healthy)     0.0.0.0:3000->3000/tcp
```

### View real-time resource usage
```bash
docker stats echo-guard-ui
```

### Monitor specific logs
```bash
# Last 100 lines
docker-compose logs --tail=100 noise-map-ui

# Follow new logs (Ctrl+C to exit)
docker-compose logs -f noise-map-ui
```

## 🚀 Deployment Checklist

Before deploying:

- [ ] Docker installed on machine
- [ ] Docker Compose installed
- [ ] Raspberry Pi IP address known
- [ ] Pi running Mosquitto: `mosquitto -d`
- [ ] Pi running WebSocket server: `python3 fixed_websocket_server.py`
- [ ] Firewall allows ports 9001 (WebSocket) and 1883 (MQTT)
- [ ] Same WiFi network for Pi and Docker host (or direct IP routing)

## 🔐 Security Notes

- Docker uses host network - firewall protects the container
- WebSocket server on Pi should only accept local connections
- For production, restrict MQTT broker access
- Use strong WiFi password if using wireless network

## 📚 Additional Resources

- Docker Docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- React Docker Best Practices: https://nodejs.org/en/docs/guides/nodejs-docker-webapp/
- Nginx for reverse proxy: https://nginx.org/
