print("AI_WORKER FILE LOADED")

import os
import time
import threading
from datetime import datetime, timezone

import torch
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# =========================
# InfluxDB configuration
# =========================

INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")


# =========================
# AI training data
# =========================

X_train = torch.tensor([
    # NORMAL
    [-5, 100, 1470, 0.5, 8, 400, 45],
    [10, 101, 1465, 0.7, 8.5, 398, 50],
    [20, 99, 1480, 0.6, 9, 402, 55],
    [30, 102, 1455, 1.0, 9.5, 395, 60],
    [38, 100, 1475, 1.2, 10, 405, 65],

    # FAULT
    [48, 120, 1200, 4.0, 13, 350, 85],
    [50, 125, 1150, 4.5, 14, 450, 90],
    [46, 118, 1250, 3.5, 12.5, 340, 82]
], dtype=torch.float32)


y_train = torch.tensor([
    0, 0, 0, 0, 0,
    1, 1, 1
], dtype=torch.float32).reshape(-1, 1)


# =========================
# AI model
# =========================

model = torch.nn.Sequential(
    torch.nn.Linear(7, 16),
    torch.nn.ReLU(),
    torch.nn.Linear(16, 8),
    torch.nn.ReLU(),
    torch.nn.Linear(8, 1)
)


loss_function = torch.nn.BCEWithLogitsLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)


# =========================
# Train model
# =========================

for epoch in range(2000):

    optimizer.zero_grad()

    output = model(X_train)

    loss = loss_function(output, y_train)

    loss.backward()

    optimizer.step()


model.eval()


# =========================
# InfluxDB connection
# =========================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

query_api = client.query_api()

write_api = client.write_api(
    write_options=SYNCHRONOUS
)


# =========================
# Get latest ESP32 values
# =========================

def get_latest_sensor_data():

    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -2m)
      |> filter(fn: (r) => r._measurement == "factory_esp32")
      |> filter(fn: (r) => r.machine == "machine1")
      |> filter(fn: (r) => contains(
          value: r._field,
          set: [
            "temperature",
            "pressure",
            "motor_speed",
            "vibration",
            "current",
            "voltage",
            "humidity"
          ]
      ))
      |> last()
    '''

    tables = query_api.query(
        query=flux,
        org=INFLUX_ORG
    )

    values = {}
    latest_time = None

    for table in tables:

        for record in table.records:

            field = record.get_field()
            value = record.get_value()

            values[field] = float(value)

            record_time = record.get_time()

            if latest_time is None or record_time > latest_time:
                latest_time = record_time

    required_fields = [
        "temperature",
        "pressure",
        "motor_speed",
        "vibration",
        "current",
        "voltage",
        "humidity"
    ]

    for field in required_fields:

        if field not in values:
            return None, None

    return values, latest_time


# =========================
# Run AI prediction
# =========================

def run_ai_prediction(values):

    features = torch.tensor([
        [
            values["temperature"],
            values["pressure"],
            values["motor_speed"],
            values["vibration"],
            values["current"],
            values["voltage"],
            values["humidity"]
        ]
    ], dtype=torch.float32)

    with torch.no_grad():

        output = model(features)

        probability = torch.sigmoid(output).item()

    # Dashboard thresholds
    if probability >= 0.80:
        status = "FAULT"

    elif probability >= 0.50:
        status = "WARNING"

    else:
        status = "NORMAL"

    return probability, status


# =========================
# Write AI result
# =========================

def write_ai_result(values, probability, status):

    point = (
        Point("factory_ai")
        .tag("machine", "machine1")
        .tag("source", "ESP32_AI")

        .field("fault_probability", probability)

        .field("temperature", values["temperature"])
        .field("pressure", values["pressure"])
        .field("motor_speed", values["motor_speed"])
        .field("vibration", values["vibration"])
        .field("current", values["current"])
        .field("voltage", values["voltage"])
        .field("humidity", values["humidity"])

        .field("ai_status", status)
    )

    write_api.write(
        bucket=INFLUX_BUCKET,
        org=INFLUX_ORG,
        record=point
    )


# =========================
# AI background worker
# =========================

def ai_loop():

    print("AI WORKER STARTED")

    while True:

        try:

            values, latest_time = get_latest_sensor_data()

            if values is None:

                print("AI: Waiting for complete ESP32 data...")
                time.sleep(3)
                continue

            # Make sure we are using fresh ESP32 data
            now = datetime.now(timezone.utc)

            if latest_time is not None:

                age = (
                    now - latest_time
                ).total_seconds()

                if age > 15:

                    print(
                        f"AI: Sensor data is {age:.1f}s old. Waiting..."
                    )

                    time.sleep(3)
                    continue

            probability, status = run_ai_prediction(values)

            write_ai_result(
                values,
                probability,
                status
            )

            print(
                f"AI RESULT | "
                f"Probability={probability:.3f} | "
                f"Status={status}"
            )

        except Exception as error:

            print(
                "AI WORKER ERROR:",
                str(error)
            )

        time.sleep(3)


# =========================
# Start worker
# =========================

print("STARTING AI WORKER FROM APP")
def start_ai_worker():

    print("STARTING AI WORKER NOW")

    worker_thread = threading.Thread(
        target=ai_loop,
        daemon=True
    )

    worker_thread.start()
