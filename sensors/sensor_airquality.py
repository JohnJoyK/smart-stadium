import json
import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "stadium/sensors/air_quality"
FREQUENCY = 4

ZONES = ["North Concourse", "South Concourse", "East Stand", "West Stand"]

def generate_air_quality_data():
    co2_ppm = round(random.uniform(400, 2000), 2)
    pm25 = round(random.uniform(0, 150), 2)
    humidity = round(random.uniform(30, 90), 2)

    return {
        "sensor_type": "air_quality",
        "location": random.choice(ZONES),
        "co2_ppm": co2_ppm,
        "pm2_5": pm25,
        "humidity_percent": humidity,
        "air_quality_index": calculate_aqi(co2_ppm, pm25),
        "alert": False,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def calculate_aqi(co2, pm25):
    if co2 < 800 and pm25 < 35:
        return "good"
    elif co2 < 1200 and pm25 < 75:
        return "moderate"
    elif co2 < 1600 and pm25 < 115:
        return "poor"
    else:
        return "hazardous"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Air quality sensor connected to broker")
    else:
        print(f"Connection failed with code {rc}")

client = mqtt.Client(client_id="air-quality-sensor")
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

print(f"Publishing air quality data every {FREQUENCY}s...")
try:
    while True:
        data = generate_air_quality_data()
        if data["air_quality_index"] in ["poor", "hazardous"]:
            data["alert"] = True
        payload = json.dumps(data)
        client.publish(TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(FREQUENCY)
except KeyboardInterrupt:
    print("Sensor stopped")
    client.loop_stop()
    client.disconnect()