# Server Configuration Update Summary

## What was fixed

The server side has been updated to load configuration from `config.ini` instead of using hardcoded IP addresses. The following files were modified:

### 1. New Configuration System

**Created:** `Server/config_loader.py`
- Centralized configuration loading from `config.ini`
- Automatic fallback to sensible defaults
- Logging of current configuration for debugging

### 2. Updated Server Files

**Modified:** `Server/mqtt_broker_server.py`
- Now loads Pi IP and ports from `config.ini`
- Uses configuration for MQTT broker connection
- Respects command-line overrides

**Modified:** `Server/start_noise_system.py`
- Loads Pi IP from configuration
- Shows correct IP addresses in startup messages
- Displays configuration file location for easy editing

**Modified:** `fake_esp32.py`
- Uses Pi IP from configuration as default broker
- Loads device count and publish interval from config
- Falls back gracefully if config is not available

## How to use

### 1. Edit Configuration
Edit `config.ini` in the root directory:
```ini
[pi_connection]
pi_ip = 172.20.10.2    # Change this to your Pi's actual IP
mqtt_port = 1883
websocket_port = 9001
```

### 2. Start the System
On the Raspberry Pi:
```bash
cd Server
python3 start_noise_system.py
```

### 3. Connect from Windows
The system will now show the correct connection information:
```
📍 System Endpoints:
   🦟 MQTT Broker (TCP): 172.20.10.2:1883
   🌐 WebSocket Server: ws://172.20.10.2:9001

📱 To connect from Windows:
   ESP32: python fake_esp32.py --broker 172.20.10.2
   React UI: REACT_APP_WEBSOCKET_URL=ws://172.20.10.2:9001
```

### 4. Test with Fake Sensors
From Windows (automatically uses config):
```bash
python fake_esp32.py
```

Or override the configuration:
```bash
python fake_esp32.py --broker 172.20.10.2 --devices 3
```

## Benefits

1. **No more hardcoded IPs** - Everything reads from `config.ini`
2. **Easy configuration** - Change IP once in config file
3. **Clear documentation** - System shows exact connection details
4. **Backward compatibility** - Command-line arguments still work
5. **Graceful fallbacks** - Works even if config file is missing

## Configuration File Location

The system automatically finds `config.ini` in:
1. Parent directory (typical setup)
2. Current directory
3. Falls back to defaults if not found

When the system starts, it will show:
```
⚙️ Configuration loaded from: /path/to/config.ini
```

## Testing

All components have been tested and confirmed to:
- Load configuration correctly
- Show proper help messages with config defaults
- Connect using the configured Pi IP address
- Fall back gracefully to defaults if needed
