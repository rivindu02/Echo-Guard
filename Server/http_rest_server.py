#!/usr/bin/env python3
"""
HTTP REST API Server for Noise Mapping System
Alternative to WebSocket when WebSocket connection fails
Provides HTTP endpoints for React UI to fetch noise data
"""

import json
import logging
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse
import threading
import paho.mqtt.client as mqtt
from collections import defaultdict
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NoiseDataHTTPServer:
    def __init__(
        self,
        mqtt_broker_host="localhost",
        mqtt_port=1883,
        http_port=8080
    ):
        self.mqtt_broker_host = mqtt_broker_host
        self.mqtt_port = mqtt_port
        self.http_port = http_port
        
        # Data storage
        self.current_data = {}
        self.data_history = defaultdict(list)
        self.last_update = {}
        
        # MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # HTTP server
        self.http_server = None
        
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ Connected to MQTT broker")
            # Subscribe to all noise topics
            client.subscribe("noise/+/data")
            client.subscribe("noise/device/+")
            client.subscribe("noise/sensor/+")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Extract device ID from topic
            if "/data" in topic:
                device_id = topic.split("/")[1]
            elif "/device/" in topic or "/sensor/" in topic:
                device_id = topic.split("/")[-1]
            else:
                device_id = payload.get('device_id', 'unknown')
            
            # Store current data
            self.current_data[device_id] = {
                **payload,
                'device_id': device_id,
                'timestamp': time.time() * 1000,  # JavaScript timestamp
                'last_seen': datetime.now().isoformat()
            }
            
            # Store in history (keep last 100 readings per device)
            self.data_history[device_id].append(self.current_data[device_id])
            if len(self.data_history[device_id]) > 100:
                self.data_history[device_id].pop(0)
            
            self.last_update[device_id] = time.time()
            
            db_level = payload.get('db', 'N/A')
            logger.info(f"📊 Updated data for {device_id}: {db_level} dB")
            
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
    
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, server_instance, *args, **kwargs):
            self.server_instance = server_instance
            super().__init__(*args, **kwargs)
        
        def do_OPTIONS(self):
            """Handle CORS preflight requests"""
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
        
        def send_cors_headers(self):
            """Send CORS headers"""
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        def do_GET(self):
            """Handle GET requests"""
            try:
                parsed_path = urllib.parse.urlparse(self.path)
                path = parsed_path.path
                query_params = urllib.parse.parse_qs(parsed_path.query)
                
                if path == '/api/current':
                    # Get current data for all devices
                    response_data = {
                        'status': 'success',
                        'data': list(self.server_instance.current_data.values()),
                        'timestamp': time.time() * 1000,
                        'device_count': len(self.server_instance.current_data)
                    }
                    
                elif path == '/api/health':
                    # Health check endpoint
                    response_data = {
                        'status': 'healthy',
                        'mqtt_connected': self.server_instance.mqtt_client.is_connected(),
                        'device_count': len(self.server_instance.current_data),
                        'last_updates': self.server_instance.last_update,
                        'timestamp': time.time() * 1000
                    }
                    
                elif path.startswith('/api/device/'):
                    # Get data for specific device
                    device_id = path.split('/')[-1]
                    if device_id in self.server_instance.current_data:
                        response_data = {
                            'status': 'success',
                            'device_id': device_id,
                            'data': self.server_instance.current_data[device_id],
                            'history': self.server_instance.data_history[device_id][-10:]  # Last 10 readings
                        }
                    else:
                        response_data = {
                            'status': 'error',
                            'message': f'Device {device_id} not found'
                        }
                        
                elif path == '/api/status':
                    # System status
                    response_data = {
                        'status': 'running',
                        'method': 'http_rest',
                        'endpoints': {
                            'current_data': '/api/current',
                            'health': '/api/health',
                            'device_data': '/api/device/{device_id}',
                            'status': '/api/status'
                        },
                        'mqtt': {
                            'connected': self.server_instance.mqtt_client.is_connected(),
                            'broker': f"{self.server_instance.mqtt_broker_host}:{self.server_instance.mqtt_port}"
                        },
                        'devices': list(self.server_instance.current_data.keys())
                    }
                    
                else:
                    # 404 Not Found
                    response_data = {
                        'status': 'error',
                        'message': 'Endpoint not found',
                        'available_endpoints': ['/api/current', '/api/health', '/api/device/{id}', '/api/status']
                    }
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                response_json = json.dumps(response_data, indent=2)
                self.wfile.write(response_json.encode())
                
            except Exception as e:
                logger.error(f"❌ Error handling GET request: {e}")
                self.send_error(500, f"Internal server error: {e}")
        
        def log_message(self, format, *args):
            """Override to use our logger"""
            logger.info(f"🌐 HTTP {format % args}")
    
    def create_request_handler(self):
        """Create request handler with server instance"""
        def handler(*args, **kwargs):
            self.RequestHandler(self, *args, **kwargs)
        return handler
    
    class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        """Handle requests in separate threads"""
        allow_reuse_address = True
    
    def start_mqtt_client(self):
        """Start MQTT client in separate thread"""
        def mqtt_loop():
            try:
                logger.info(f"🔌 Connecting to MQTT broker at {self.mqtt_broker_host}:{self.mqtt_port}")
                self.mqtt_client.connect(self.mqtt_broker_host, self.mqtt_port, 60)
                self.mqtt_client.loop_forever()
            except Exception as e:
                logger.error(f"❌ MQTT client error: {e}")
        
        mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
        mqtt_thread.start()
        return mqtt_thread
    
    def start_http_server(self):
        """Start HTTP server"""
        try:
            handler = self.create_request_handler()
            self.http_server = self.ThreadedHTTPServer(("0.0.0.0", self.http_port), handler)
            
            logger.info(f"🌐 HTTP REST API server starting on port {self.http_port}")
            logger.info(f"📡 Available endpoints:")
            logger.info(f"   GET /api/current - Get all current device data")
            logger.info(f"   GET /api/health - Health check")
            logger.info(f"   GET /api/device/{{id}} - Get specific device data")
            logger.info(f"   GET /api/status - Server status")
            
            self.http_server.serve_forever()
            
        except Exception as e:
            logger.error(f"❌ HTTP server error: {e}")
    
    def start(self):
        """Start both MQTT client and HTTP server"""
        logger.info("🚀 Starting HTTP REST API server for noise mapping")
        
        # Start MQTT client
        mqtt_thread = self.start_mqtt_client()
        
        # Wait a moment for MQTT to connect
        time.sleep(2)
        
        # Start HTTP server (blocking)
        self.start_http_server()

def main():
    # Configuration
    mqtt_broker = os.getenv('MQTT_BROKER_HOST', '192.168.1.12')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    http_port = int(os.getenv('HTTP_PORT', '8080'))
    
    logger.info(f"🔧 Configuration:")
    logger.info(f"   MQTT Broker: {mqtt_broker}:{mqtt_port}")
    logger.info(f"   HTTP Port: {http_port}")
    
    # Create and start server
    server = NoiseDataHTTPServer(
        mqtt_broker_host=mqtt_broker,
        mqtt_port=mqtt_port,
        http_port=http_port
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down HTTP REST API server")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
