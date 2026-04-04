import json
import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "stadium/sensors/queue_wait"
FREQUENCY = 5

STANDS = ["North Stand", "South Stand", "East Kiosk", "West Kiosk"]

def generate_queue_data():
    stand = random.choice(STANDS)
    wait = round(random.uniform(0, 20), 1)
    return {
        "sensor_type": "queue_wait",
        "location": stand,
        "wait_minutes": wait,
        "queue_length": random.randint(0, 50),
        "recommendation": "go_now" if wait < 5 else "wait",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Queue sensor connected to broker")
    else:
        print(f"Connection failed with code {rc}")

client = mqtt.Client(client_id="queue-sensor")
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

print(f"Publishing queue wait data every {FREQUENCY}s...")
try:
    while True:
        data = generate_queue_data()
        payload = json.dumps(data)
        client.publish(TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(FREQUENCY)
except KeyboardInterrupt:
    print("Sensor stopped")
    client.loop_stop()
    client.disconnect()