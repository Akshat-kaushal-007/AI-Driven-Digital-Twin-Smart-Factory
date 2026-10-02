from flask import Flask, request, jsonify
import os
import requests

from ai_worker import start_ai_worker

app = Flask(__name__)

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

    print("STEP 1 - Request received")
    print("RAW DATA:", data)

    if not data:
        print("STEP 2 - No JSON data")
        return jsonify({"error": "No JSON data received"}), 400

    topic = str(data.get("topic", ""))
    payload = data.get("payload", "")

    print("STEP 2 - Topic:", topic)
    print("STEP 3 - Payload:", payload)

    field_map = {
        "temperature": "temperature",
        "pressure": "pressure",
        "motor_speed": "motor_speed",
        "vibration": "vibration",
        "current": "current",
        "voltage": "voltage",
        "humidity": "humidity"
    }

    matched_field = None

    for key, field in field_map.items():
        if key in topic:
            matched_field = field
            break

    print("STEP 4 - Matched field:", matched_field)

    if matched_field is None:
        print("ERROR - No matching topic field")
        return jsonify({"error": "Unknown topic"}), 400

    try:
        value = float(str(payload).strip("'\""))
        print("STEP 5 - Numeric value:", value)
    except ValueError:
        print("ERROR - Cannot convert payload to number:", payload)
        return jsonify({"error": "Invalid numeric payload"}), 400

    line = (
        f"factory_esp32,machine=machine1,source=ESP32 "
        f"{matched_field}={value}"
    )

    print("STEP 6 - InfluxDB line:", line)

    try:
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
            data=line,
            timeout=10
        )

        print("STEP 7 - InfluxDB status:", response.status_code)
        print("STEP 8 - InfluxDB response:", response.text)

    except Exception as e:
        print("ERROR - InfluxDB request failed:", str(e))
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "received"}), 200
print("STARTING AI WORKER FROM APP")
start_ai_worker()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
