#!/usr/bin/env python3
"""
Safe logging configuration for Windows that handles Unicode emoji characters
"""

import logging
import sys
import os


class SafeFormatter(logging.Formatter):
    """Custom formatter that safely handles Unicode characters on Windows"""
    
    def format(self, record):
        try:
            # Try normal formatting first
            return super().format(record)
        except UnicodeEncodeError:
            # Fallback: remove emojis and special Unicode characters
            msg = super().format(record)
            # Replace common emojis with text equivalents
            emoji_replacements = {
                '✅': '[OK]',
                '❌': '[ERROR]',
                '⚠️': '[WARNING]',
                '🚀': '[START]',
                '🔌': '[MQTT]',
                '🌐': '[WS]',
                '📊': '[DATA]',
                '📤': '[MSG]',
                '📡': '[SENSOR]',
                '🔄': '[PROCESS]',
                '📈': '[INTERP]',
                '🗑️': '[CLEANUP]',
                '🧹': '[CLEAN]',
                '🛑': '[STOP]',
                '🎉': '[SUCCESS]',
                '💡': '[INFO]',
                '🔍': '[DEBUG]',
                '🗺️': '[MAP]',
                '🦟': '[MOSQUITTO]'
            }
            
            for emoji, replacement in emoji_replacements.items():
                msg = msg.replace(emoji, replacement)
            
            # Remove any remaining non-ASCII characters
            msg = msg.encode('ascii', 'replace').decode('ascii')
            return msg


def setup_safe_logging(log_file='system.log', level=logging.INFO):
    """Setup logging that works on Windows with Unicode emoji fallback"""
    
    # Create custom formatter
    formatter = SafeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with safe encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Try to set UTF-8 encoding for console if possible
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass  # Fallback will handle it
    
    logger.addHandler(console_handler)
    
    # File handler with UTF-8 encoding
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
    
    return logger


def get_safe_logger(name=None):
    """Get a logger with safe Unicode handling"""
    return logging.getLogger(name)


# Test the safe logging
if __name__ == "__main__":
    logger = setup_safe_logging('test.log')
    logger.info("✅ Testing emoji logging")
    logger.warning("⚠️ This should work on Windows")
    logger.error("❌ Error with emoji")
    logger.info("🚀 Starting system with emojis")
    print("Safe logging test completed!")
