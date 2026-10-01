from flask import Flask, request, jsonify
import os
import requests

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

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    print("Received from EMQX:", data)

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
