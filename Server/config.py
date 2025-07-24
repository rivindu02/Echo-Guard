"""
Configuration settings for the noise mapping backend
"""

import os

class Config:
    # MQTT Settings
    MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
    MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', '60'))
    
    # Topics
    SENSOR_TOPIC_PREFIX = os.getenv('SENSOR_TOPIC_PREFIX', 'noise')
    PROCESSED_TOPIC = os.getenv('PROCESSED_TOPIC', 'noise/processed')
    
    # Processing Settings
    GRID_SIZE = (50, 50)
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '5'))  # seconds
    MAX_SENSOR_AGE = int(os.getenv('MAX_SENSOR_AGE', '300'))  # seconds
    
    # Interpolation Settings
    IDW_POWER = float(os.getenv('IDW_POWER', '2.0'))
    GRID_PADDING = float(os.getenv('GRID_PADDING', '0.001'))  # degrees
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/noise_processor.log')
