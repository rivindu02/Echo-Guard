#!/usr/bin/env python3
"""
Configuration loader for the Noise Mapping System
Loads settings from config.ini file
"""

import configparser
import os
import logging

logger = logging.getLogger(__name__)


class NoiseMapConfig:
    def __init__(self, config_file_path=None):
        """Initialize configuration loader
        
        Args:
            config_file_path: Path to config.ini file. If None, searches in parent directory.
        """
        self.config = configparser.ConfigParser()
        
        # Find config file
        if config_file_path is None:
            # Look in parent directory first (typical setup)
            parent_config = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
            local_config = os.path.join(os.path.dirname(__file__), 'config.ini')
            
            if os.path.exists(parent_config):
                config_file_path = parent_config
            elif os.path.exists(local_config):
                config_file_path = local_config
            else:
                raise FileNotFoundError("config.ini not found in current or parent directory")
        
        # Load configuration
        self.config_file_path = os.path.abspath(config_file_path)
        logger.info(f"Loading configuration from: {self.config_file_path}")
        
        if not os.path.exists(self.config_file_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file_path}")
        
        self.config.read(self.config_file_path)
        logger.info("✅ Configuration loaded successfully")
    
    def get_pi_ip(self):
        """Get the Pi IP address from configuration"""
        try:
            return self.config.get('pi_connection', 'pi_ip')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.warning("Pi IP not found in config, using default: localhost")
            return "localhost"
    
    def get_local_ip(self):
        """Get the local IP address from configuration"""
        try:
            return self.config.get('local_connection', 'local_ip')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.warning("Local IP not found in config, using default: localhost")
            return "localhost"
    
    def get_mqtt_port(self):
        """Get MQTT port from configuration"""
        try:
            return self.config.getint('pi_connection', 'mqtt_port')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.warning("MQTT port not found in config, using default: 1883")
            return 1883
    
    def get_websocket_port(self):
        """Get WebSocket port from configuration"""
        try:
            return self.config.getint('pi_connection', 'websocket_port')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.warning("WebSocket port not found in config, using default: 9001")
            return 9001
    
    def get_fake_esp32_device_count(self):
        """Get fake ESP32 device count from configuration"""
        try:
            return self.config.getint('fake_esp32', 'device_count')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.warning("Device count not found in config, using default: 5")
            return 5
    
    def get_fake_esp32_publish_interval(self):
        """Get fake ESP32 publish interval from configuration"""
        try:
            return self.config.getint('fake_esp32', 'publish_interval')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.warning("Publish interval not found in config, using default: 3")
            return 3
    
    def is_local_mode(self):
        """Check if running in local mode (localhost)"""
        pi_ip = self.get_pi_ip()
        return pi_ip in ['localhost', '127.0.0.1', '0.0.0.0']
    
    def get_connection_info(self):
        """Get complete connection information"""
        return {
            'pi_ip': self.get_pi_ip(),
            'local_ip': self.get_local_ip(),
            'mqtt_port': self.get_mqtt_port(),
            'websocket_port': self.get_websocket_port(),
            'is_local': self.is_local_mode()
        }
    
    def log_configuration(self):
        """Log current configuration for debugging"""
        conn_info = self.get_connection_info()
        logger.info("📋 Current Configuration:")
        logger.info(f"   Pi IP: {conn_info['pi_ip']}")
        logger.info(f"   Local IP: {conn_info['local_ip']}")
        logger.info(f"   MQTT Port: {conn_info['mqtt_port']}")
        logger.info(f"   WebSocket Port: {conn_info['websocket_port']}")
        logger.info(f"   Local Mode: {conn_info['is_local']}")
        logger.info(f"   Fake ESP32 Devices: {self.get_fake_esp32_device_count()}")
        logger.info(f"   Publish Interval: {self.get_fake_esp32_publish_interval()}s")

# Global config instance
_config_instance = None

def get_config():
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = NoiseMapConfig()
    return _config_instance

def reload_config():
    """Reload configuration from file"""
    global _config_instance
    _config_instance = NoiseMapConfig()
    return _config_instance


if __name__ == "__main__":
    # Test the configuration loader
    try:
        config = get_config()
        config.log_configuration()
        print("\n✅ Configuration loader test successful!")
    except Exception as e:
        print(f"❌ Configuration loader test failed: {e}")
