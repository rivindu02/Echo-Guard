#!/usr/bin/env python3
"""
Main startup script for the Raspberry Pi Noise Mapping System
This replaces the Node.js functionality with Python components
"""

import subprocess
import threading
import time
import signal
import sys
import logging
import os

# Set console encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging with UTF-8 encoding for emoji support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system_startup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class NoiseMapSystem:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_mosquitto_broker(self):
        """Start Mosquitto MQTT broker"""
        try:
            logger.info("🦟 Starting Mosquitto MQTT broker...")
            
            # Check if Mosquitto is installed
            result = subprocess.run(['which', 'mosquitto'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Mosquitto not found. Please install it:")
                logger.error("   sudo apt update")
                logger.error("   sudo apt install mosquitto mosquitto-clients")
                return False
            
            # Start Mosquitto with custom config
            config_file = "/etc/mosquitto/mosquitto.conf"
            if os.path.exists("mosquitto.conf"):
                config_file = "mosquitto.conf"
            
            process = subprocess.Popen([
                'mosquitto', '-c', config_file, '-v'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('mosquitto', process))
            logger.info("✅ Mosquitto MQTT broker started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Mosquitto: {e}")
            return False
    
    def start_broker_server(self):
        """Start the Python MQTT broker server"""
        try:
            logger.info("🌐 Starting Python MQTT broker server...")
            
            process = subprocess.Popen([
                'python3', 'mqtt_broker_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('broker_server', process))
            logger.info("✅ MQTT broker server started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start broker server: {e}")
            return False
    
    def start_noise_processor(self):
        """Start the noise data processor"""
        try:
            logger.info("📊 Starting noise data processor...")
            
            process = subprocess.Popen([
                'python3', 'simple_noise_processor.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('noise_processor', process))
            logger.info("✅ Noise data processor started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start noise processor: {e}")
            return False
    
    def start_fake_sensors(self):
        """Start fake ESP32 sensors for testing"""
        try:
            logger.info("🔧 Starting fake ESP32 sensors for testing...")
            
            # Check if fake_esp32.py exists in parent directory
            fake_sensor_path = "../fake_esp32.py"
            if os.path.exists(fake_sensor_path):
                process = subprocess.Popen([
                    'python3', fake_sensor_path
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.processes.append(('fake_sensors', process))
                logger.info("✅ Fake ESP32 sensors started")
                return True
            else:
                logger.warning("⚠️ fake_esp32.py not found, skipping fake sensors")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start fake sensors: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed"""
        while self.running:
            try:
                for name, process in self.processes[:]:  # Copy list to iterate
                    if process.poll() is not None:  # Process has terminated
                        logger.warning(f"⚠️ Process {name} has stopped unexpectedly")
                        
                        # Remove from list
                        self.processes.remove((name, process))
                        
                        # Restart the process
                        if name == 'mosquitto':
                            self.start_mosquitto_broker()
                        elif name == 'broker_server':
                            self.start_broker_server()
                        elif name == 'noise_processor':
                            self.start_noise_processor()
                        elif name == 'fake_sensors':
                            self.start_fake_sensors()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in process monitoring: {e}")
                time.sleep(10)
    
    def start_system(self):
        """Start the complete noise mapping system"""
        logger.info("🚀 Starting Raspberry Pi Noise Mapping System...")
        
        # Give some time between starts
        services = [
            ("Mosquitto MQTT Broker", self.start_mosquitto_broker),
            ("Python MQTT Broker Server", self.start_broker_server),
            ("Noise Data Processor", self.start_noise_processor),
            ("Fake Sensors (Testing)", self.start_fake_sensors)
        ]
        
        for service_name, start_func in services:
            logger.info(f"Starting {service_name}...")
            if start_func():
                time.sleep(2)  # Wait 2 seconds between services
            else:
                logger.warning(f"⚠️ Failed to start {service_name}")
        
        # Start process monitoring
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        logger.info("🎉 Noise Mapping System started successfully!")
        logger.info("")
        logger.info("📍 System Endpoints:")
        logger.info("   🦟 MQTT Broker (TCP): localhost:1883")
        logger.info("   🌐 WebSocket Server: ws://localhost:9001")
        logger.info("   📊 Data Processing: Active")
        logger.info("")
        logger.info("📱 React UI Configuration:")
        logger.info("   Update mqttService.js to use: ws://localhost:9001")
        logger.info("")
        logger.info("🛑 Press Ctrl+C to stop the system")
        
        return True
    
    def stop_system(self):
        """Stop all system processes"""
        logger.info("🛑 Stopping Noise Mapping System...")
        self.running = False
        
        for name, process in self.processes:
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
        
        logger.info("🛑 Noise Mapping System stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal")
    if 'system' in globals():
        system.stop_system()
    sys.exit(0)

def main():
    """Main entry point"""
    global system
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start system
    system = NoiseMapSystem()
    
    if system.start_system():
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 System stopped by user")
            system.stop_system()
    else:
        logger.error("❌ Failed to start system")
        sys.exit(1)

if __name__ == "__main__":
    main()
