# 🎯 Quick Reference - Pi MQTT Broker Setup

## 📋 Summary

You now have a flexible system where:
- **Raspberry Pi (192.168.1.12)** = MQTT Broker + Data Processing
- **Your Laptop** = Fake ESP32 sensors + React UI
- **Easy IP configuration** via `config.ini` and scripts

## 🚀 Quick Commands

### First Time Setup
```cmd
configure_ip.bat          # Set your Pi IP address
test_pi_connection.py      # Test Pi connectivity
```

### Daily Usage - Pi as Broker
```cmd
# On Raspberry Pi (192.168.1.12)
python3 start_noise_system.py

# On your laptop
connect_to_pi.bat          # Starts fake sensors + React UI
```

### Daily Usage - Localhost Only
```cmd
connect_to_localhost.bat   # Configure for localhost
start_local_system.bat     # Start everything locally
```

## 🔧 Configuration Files

### `config.ini` (Edit Pi IP here)
```ini
[pi_connection]
pi_ip = 192.168.1.12        # ← Change this to your Pi's IP
```

### `fake_esp32.py` Options
```cmd
python fake_esp32.py --pi               # Use Pi from config.ini
python fake_esp32.py --broker 192.168.1.12   # Specify Pi IP
python fake_esp32.py --config           # Use all config.ini settings
python fake_esp32.py --devices 10       # More sensors
```

## 📱 Access Points

- **React UI:** http://localhost:3000 (always on your laptop)
- **Pi WebSocket:** ws://192.168.1.12:9001
- **Pi MQTT:** 192.168.1.12:1883

## 🔄 Easy Switching

| Script | Description |
|--------|-------------|
| `configure_ip.bat` | Set/change Pi IP address |
| `connect_to_pi.bat` | Connect to Pi, start UI |
| `connect_to_localhost.bat` | Switch back to localhost |
| `start_local_system.bat` | Full localhost setup |
| `test_pi_connection.py` | Test Pi connectivity |

## 🐛 Troubleshooting

### Pi Connection Issues
```cmd
test_pi_connection.py      # Diagnose connection problems
ping 192.168.1.12          # Check network connectivity
```

### React UI Not Updating
Check `mqtt-noise-map-ui/.env`:
```properties
REACT_APP_WEBSOCKET_URL=ws://192.168.1.12:9001
```

### Change Pi IP
1. Edit `config.ini`: Change `pi_ip = NEW_IP`
2. Run: `configure_ip.bat`
3. Or manually edit `mqtt-noise-map-ui/.env`

## 📊 Data Flow

```
fake_esp32.py → Pi MQTT (1883) → Pi WebSocket (9001) → React UI (3000)
     💻              🥧               🥧                💻
  Your Laptop        Pi              Pi            Your Laptop
```

## ✅ What You've Achieved

✅ **Flexible IP Configuration** - Easy to change Pi address  
✅ **Pi as MQTT Broker** - Centralized data processing  
✅ **Localhost Fallback** - Can still test without Pi  
✅ **One-Command Setup** - Simple batch scripts  
✅ **Real-time Data Flow** - fake_esp32.py → Pi → React UI  
✅ **No Blocking** - Localhost connections still work  

## 🎉 Ready to Use!

Your system is now configured for easy switching between:
- **Pi-based setup** (recommended for testing with "real" architecture)
- **Localhost setup** (for quick development)

Just run `connect_to_pi.bat` and enjoy your noise mapping system! 🔊📊
