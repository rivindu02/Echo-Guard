"""
Configuration settings for the Raspberry Pi noise mapping system
"""

import os

class Config:
    # MQTT Settings
    MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
    MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', '60'))
    
    # WebSocket Settings
    WEBSOCKET_HOST = os.getenv('WEBSOCKET_HOST', 'localhost')
    WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', '9001'))
    
    # Topics
    SENSOR_TOPIC_PREFIX = os.getenv('SENSOR_TOPIC_PREFIX', 'noise')
    PROCESSED_TOPIC = os.getenv('PROCESSED_TOPIC', 'noise/processed')
    PROCESS_REQUEST_TOPIC = os.getenv('PROCESS_REQUEST_TOPIC', 'noise/process_request')
    
    # Processing Settings
    GRID_SIZE = (60, 60)  # Higher resolution for better visualization
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '2'))  # seconds
    MAX_SENSOR_AGE = int(os.getenv('MAX_SENSOR_AGE', '300'))  # seconds
    
    # Interpolation Settings
    IDW_POWER = float(os.getenv('IDW_POWER', '2.0'))
    GRID_PADDING = float(os.getenv('GRID_PADDING', '0.001'))  # degrees
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'noise_system.log')
    
    # System Settings
    ENABLE_FAKE_SENSORS = os.getenv('ENABLE_FAKE_SENSORS', 'true').lower() == 'true'
    AUTO_RESTART = os.getenv('AUTO_RESTART', 'true').lower() == 'true'
