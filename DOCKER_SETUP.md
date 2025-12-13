# 🐳 Docker Setup Summary

## What's Dockerized?

✅ **React UI** - Containerized and ready to deploy  
❌ **Server** - Runs on Raspberry Pi (not dockerized)  
❌ **Mosquitto** - Runs on Raspberry Pi (not dockerized)  

## Files Created

```
Echo-Guard/
├── docker-compose.yml          # Single-service compose file (React UI only)
├── docker-entrypoint.sh        # Interactive setup script
├── .env.example               # Configuration template
└── mqtt-noise-map-ui/
    ├── Dockerfile             # Multi-stage build for React
    └── .dockerignore          # Exclude unnecessary files
```

## Quick Start

### 1. Copy .env template
```bash
cp .env.example .env
```

### 2. Update .env with your Pi IP
```bash
echo "PI_IP=192.168.208.242" >> .env
```

### 3. Build and run
```bash
# Option A: Interactive script
chmod +x docker-entrypoint.sh
./docker-entrypoint.sh
# Select: 1 (Build), then 2 (Start)

# Option B: Direct commands
docker-compose build
docker-compose up -d
```

### 4. Access React UI
Open browser to: **http://localhost:3000**

## Prerequisites on Raspberry Pi

Make sure these are running:

```bash
# 1. Start Mosquitto
sudo systemctl start mosquitto

# 2. Start WebSocket Server
cd /home/rivindu02/Documents/Echo-Guard
python3 Server/fixed_websocket_server.py
```

## Docker Commands Reference

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Shell access
docker-compose exec noise-map-ui /bin/sh
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Blank React page | Check WebSocket connection in browser DevTools (F12) |
| WebSocket error | Verify Pi IP in .env and server running on Pi |
| Port 3000 in use | Change port in docker-compose.yml or kill process |
| Container won't start | Run `docker-compose logs` to see errors |

## Architecture

```
Client Machine          Raspberry Pi
   Docker              Physical/VM
   
┌─────────────────┐   ┌──────────────────┐
│  React UI       │   │ WebSocket (9001) │
│  Port 3000      │   │ Mosquitto (1883) │
└────────┬────────┘   └────────┬─────────┘
         │◄──ws://192.168.x.x:9001──┤
         │
    Browser
   (display)
```

## For More Details

See `DOCKER_GUIDE.md` for comprehensive documentation.

---

**Ready to containerize?** Run `./docker-entrypoint.sh` 🚀
