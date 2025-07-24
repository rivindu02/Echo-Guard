#!/usr/bin/env python3
"""
fake_esp32.py

Simulates one or more ESP32 noise sensors by publishing JSON payloads
to an MQTT broker at regular intervals.
"""

import json
import time
import random
import argparse

import paho.mqtt.client as mqtt

def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulate ESP32 noise sensor data over MQTT"
    )
    parser.add_argument(
        "--broker", "-b", default="localhost", help="MQTT broker host or IP"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=1883, help="MQTT broker port"
    )
    parser.add_argument(
        "--topic", "-t", default="noise/esp32-sim1",
        help="MQTT topic to publish to (e.g. noise/esp32-001)"
    )
    parser.add_argument(
        "--lat", type=float, default=12.912, help="Sensor latitude"
    )
    parser.add_argument(
        "--lon", type=float, default=77.675, help="Sensor longitude"
    )
    parser.add_argument(
        "--interval", "-i", type=float, default=3.0,
        help="Publish interval in seconds"
    )
    return parser.parse_args()

def random_db(min_db=40.0, max_db=80.0):
    """Generate a random dB(A) value within the given range."""
    return round(random.uniform(min_db, max_db), 1)

def main():
    args = parse_args()

    client = mqtt.Client()
    client.connect(args.broker, args.port, keepalive=60)

    print(f"Publishing to mqtt://{args.broker}:{args.port}/{args.topic}")
    try:
        while True:
            payload = {
                "device_id": args.topic.split('/')[-1],
                "lat": args.lat,
                "lon": args.lon,
                "db": random_db(),
                "timestamp": int(time.time() * 1000)
            }
            message = json.dumps(payload)
            client.publish(args.topic, message)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Published: {message}")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
