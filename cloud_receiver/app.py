from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# InfluxDB Cloud settings from Render Environment Variables
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")


@app.route("/", methods=["GET"])
def home():
    return "Smart Factory Cloud Receiver is running"


@app.route("/mqtt", methods=["POST"])
def mqtt():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    topic = data.get("topic", "")
    payload = data.get("payload", "")

    print("Received from EMQX:", topic, "payload", payload)

    field_map = {
        "temperature": "temperature",
        "pressure": "pressure",
        "motor_speed": "motor_speed",
        "vibration": "vibration",
        "current": "current",
        "voltage": "voltage",
        "humidity": "humidity"
    }

    for key, field in field_map.items():

        if key in topic:

            try:
                # Remove single or double quotes from MQTT payload
                value = float(str(payload).strip("'\""))

                # InfluxDB Line Protocol
                line = (
                    f"factory_esp32,machine=machine1,source=ESP32 "
                    f"{field}={value}"
                )

                response = requests.post(
                    f"{INFLUX_URL}/api/v2/write",
                    params={
                        "org": INFLUX_ORG,
                        "bucket": INFLUX_BUCKET,
                        "precision": "s"
                    },
                    headers={
                        "Authorization": f"Token {INFLUX_TOKEN}",
                        "Content-Type": "text/plain; charset=utf-8"
                    },
                    data=line
                )

                print("InfluxDB:", response.status_code)

                if response.status_code != 204:
                    print("InfluxDB error:", response.text)

            except ValueError:
                print("Invalid numeric payload:", payload)

            break

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
