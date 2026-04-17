import json
import time
import threading
import paho.mqtt.client as mqtt
from awscrt import mqtt as aws_mqtt
from awsiot import mqtt_connection_builder

LOCAL_BROKER = "localhost"
LOCAL_PORT = 1883
TOPICS = [
    "stadium/sensors/air_quality",
    "stadium/sensors/noise_level",
    "stadium/sensors/queue_wait",
]

AWS_ENDPOINT = "a1ahac2046m3dz-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "stadium-fog-node"
KEY_PATH = "certs/private.key"
CA_PATH = "certs/AmazonRootCA1.pem"
AWS_TOPIC = "stadium/fog/processed"
CERT_PATH = "certs/cert.pem"

buffer = []
buffer_lock = threading.Lock()

aws_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=AWS_ENDPOINT,
    pri_key_filepath=KEY_PATH,
    ca_filepath=CA_PATH,
    client_id=CLIENT_ID,
    cert_filepath=CERT_PATH,
    clean_session=False,
    keep_alive_secs=30,
)

print("Connecting to AWS IoT Core...")
connect_future = aws_connection.connect()
connect_future.result()
print("Connected to AWS IoT Core")


def process_buffer(readings):
    if not readings:
        return None

    processed = {
        "fog_node_id": "fog-node-01",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reading_count": len(readings),
        "sensors": {},
    }

    for reading in readings:
        sensor_type = reading.get("sensor_type")

        if sensor_type == "air_quality":
            processed["sensors"]["air_quality"] = {
                "avg_co2_ppm": round(
                    sum(
                        r["co2_ppm"]
                        for r in readings
                        if r.get("sensor_type") == "air_quality"
                    )
                    / max(
                        1,
                        sum(
                            1 for r in readings if r.get("sensor_type") == "air_quality"
                        ),
                    ),
                    2,
                ),
                "avg_pm2_5": round(
                    sum(
                        r["pm2_5"]
                        for r in readings
                        if r.get("sensor_type") == "air_quality"
                    )
                    / max(
                        1,
                        sum(
                            1 for r in readings if r.get("sensor_type") == "air_quality"
                        ),
                    ),
                    2,
                ),
                "alert": any(
                    r.get("alert")
                    for r in readings
                    if r.get("sensor_type") == "air_quality"
                ),
                "latest_aqi": reading.get("air_quality_index"),
            }

        elif sensor_type == "noise_level":
            noise_readings = [
                r["decibels"] for r in readings if r.get("sensor_type") == "noise_level"
            ]
            if noise_readings:
                processed["sensors"]["noise_level"] = {
                    "avg_decibels": round(sum(noise_readings) / len(noise_readings), 2),
                    "max_decibels": round(max(noise_readings), 2),
                    "category": reading.get("category"),
                }

        elif sensor_type == "queue_wait":
            queue_readings = [
                r for r in readings if r.get("sensor_type") == "queue_wait"
            ]
            if queue_readings:
                best = min(queue_readings, key=lambda x: x["wait_minutes"])
                processed["sensors"]["queue_wait"] = {
                    "avg_wait_minutes": round(
                        sum(r["wait_minutes"] for r in queue_readings)
                        / len(queue_readings),
                        2,
                    ),
                    "best_stand": best["location"],
                    "best_wait_minutes": best["wait_minutes"],
                    "recommendation": "go_now" if best["wait_minutes"] < 5 else "wait",
                }

    return processed


def dispatch_loop():
    while True:
        time.sleep(10)
        with buffer_lock:
            if not buffer:
                print("Buffer empty, nothing to dispatch")
                continue
            snapshot = buffer.copy()
            buffer.clear()

        payload = process_buffer(snapshot)
        if payload:
            message = json.dumps(payload)
            aws_connection.publish(
                topic=AWS_TOPIC, payload=message, qos=aws_mqtt.QoS.AT_LEAST_ONCE
            )
            print(f"Dispatched to AWS: {message}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Fog node connected to local broker")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"Subscribed to {topic}")
    else:
        print(f"Connection failed: {rc}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        with buffer_lock:
            buffer.append(data)
        print(f"Buffered reading from {msg.topic}")
    except Exception as e:
        print(f"Error parsing message: {e}")


dispatch_thread = threading.Thread(target=dispatch_loop, daemon=True)
dispatch_thread.start()

local_client = mqtt.Client(client_id="fog-node-local")
local_client.on_connect = on_connect
local_client.on_message = on_message
local_client.connect(LOCAL_BROKER, LOCAL_PORT, 60)

print("Fog node running...")
try:
    local_client.loop_forever()
except KeyboardInterrupt:
    print("Fog node stopped")
    aws_connection.disconnect()
