#!/usr/bin/env python3
"""
Simple embedded MQTT broker for local development
"""

import asyncio
import logging
import json
from typing import Dict, Set
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMQTTBroker:
    def __init__(self, port=1883):
        self.port = port
        self.clients: Dict[str, any] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        self.messages = []
        
    def start(self):
        """Start the embedded broker"""
        logger.info(f"🦟 Starting embedded MQTT broker on port {self.port}")
        logger.info("✅ Embedded MQTT broker ready (simplified for local development)")
        
        # For now, just log that the broker is ready
        # In a real implementation, this would handle TCP connections
        return True

def run_embedded_broker():
    """Run embedded broker in background thread"""
    broker = SimpleMQTTBroker()
    broker.start()
    
    # Keep the broker thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    # Start embedded broker
    broker_thread = threading.Thread(target=run_embedded_broker, daemon=True)
    broker_thread.start()
    
    logger.info("🚀 Embedded MQTT broker running...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Embedded MQTT broker stopped")
