import json
import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "stadium/sensors/noise_level"
FREQUENCY = 3

def generate_noise_data():
    return {
        "sensor_type": "noise_level",
        "location": "pitch_side",
        "decibels": round(random.uniform(40, 120), 2),
        "category": "normal",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def categorise(db):
    if db < 60:
        return "quiet"
    elif db < 85:
        return "normal"
    elif db < 100:
        return "loud"
    else:
        return "very_loud"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Noise sensor connected to broker")
    else:
        print(f"Connection failed with code {rc}")

client = mqtt.Client(client_id="noise-sensor")
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

print(f"Publishing noise level data every {FREQUENCY}s...")
try:
    while True:
        data = generate_noise_data()
        data["category"] = categorise(data["decibels"])
        payload = json.dumps(data)
        client.publish(TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(FREQUENCY)
except KeyboardInterrupt:
    print("Sensor stopped")
    client.loop_stop()
    client.disconnect()