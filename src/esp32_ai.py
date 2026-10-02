import os
import time
from pathlib import Path

import torch
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_ORG = "Smart Factory Project"
INFLUX_BUCKET = "Smart_factory"

INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

if not INFLUX_TOKEN:
    raise RuntimeError("INFLUX_TOKEN not found in .env")


# =====================================================
# AI TRAINING DATA
# =====================================================

# Feature order:
# Temperature
# Pressure
# Motor Speed
# Vibration
# Current
# Voltage
# Humidity

normal_data = [
    [-5, 100, 1470, 0.5, 8.0, 400, 45],
    [10, 101, 1465, 0.7, 8.5, 398, 50],
    [20, 99, 1480, 0.6, 9.0, 402, 55],
    [30, 102, 1455, 1.0, 9.5, 395, 60],
    [38, 100, 1475, 1.2, 10.0, 405, 65],
]

fault_data = [
    [48, 120, 1200, 4.0, 13.0, 350, 85],
    [50, 125, 1150, 4.5, 14.0, 450, 90],
    [46, 118, 1250, 3.5, 12.5, 340, 82],
]


# =====================================================
# PREPARE TRAINING DATA
# =====================================================

X = torch.tensor(
    normal_data + fault_data,
    dtype=torch.float32
)

y = torch.tensor(
    [0] * len(normal_data) +
    [1] * len(fault_data),
    dtype=torch.float32
).reshape(-1, 1)


# =====================================================
# CREATE AI MODEL
# =====================================================

model = torch.nn.Sequential(
    torch.nn.Linear(7, 16),
    torch.nn.ReLU(),
    torch.nn.Linear(16, 8),
    torch.nn.ReLU(),
    torch.nn.Linear(8, 1)
)


# =====================================================
# TRAIN AI MODEL
# =====================================================

loss_function = torch.nn.BCEWithLogitsLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)

print("Training AI model...")

for epoch in range(2000):

    prediction = model(X)

    loss = loss_function(
        prediction,
        y
    )

    optimizer.zero_grad()

    loss.backward()

    optimizer.step()


print("AI model training complete!")
print()


# =====================================================
# INFLUXDB CONNECTION
# =====================================================

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

query_api = influx_client.query_api()

write_api = influx_client.write_api()


# =====================================================
# GET LATEST VALUE
# =====================================================

def get_latest_value(field_name):

    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) =>
          r._measurement == "factory_esp32"
      )
      |> filter(fn: (r) =>
          r._field == "{field_name}"
      )
      |> last()
    '''

    tables = query_api.query(
        org=INFLUX_ORG,
        query=query
    )

    for table in tables:

        for record in table.records:

            return float(record.get_value())

    return None


# =====================================================
# GET ALL ESP32 PARAMETERS
# =====================================================

def get_machine_data():

    temperature = get_latest_value("temperature")
    pressure = get_latest_value("pressure")
    motor_speed = get_latest_value("motor_speed")
    vibration = get_latest_value("vibration")
    current = get_latest_value("current")
    voltage = get_latest_value("voltage")
    humidity = get_latest_value("humidity")

    values = [
        temperature,
        pressure,
        motor_speed,
        vibration,
        current,
        voltage,
        humidity
    ]

    if any(value is None for value in values):

        return None

    return values


# =====================================================
# REAL-TIME AI MONITORING
# =====================================================

print("==============================================")
print("       ESP32 → AI MONITORING SYSTEM")
print("==============================================")
print()

print("Waiting for ESP32 machine data...")
print()


while True:

    try:

        machine_data = get_machine_data()

        if machine_data is None:

            print(
                "Waiting for all 7 ESP32 parameters..."
            )

            time.sleep(3)

            continue


        # =================================================
        # AI PREDICTION
        # =================================================

        input_data = torch.tensor(
            [machine_data],
            dtype=torch.float32
        )


        with torch.no_grad():

            output = model(input_data)

            fault_probability = torch.sigmoid(
                output
            ).item()


        # =================================================
        # AI STATUS
        # =================================================

        if fault_probability >= 0.80:

            ai_status = "FAULT"

        elif fault_probability >= 0.50:

            ai_status = "WARNING"

        else:

            ai_status = "NORMAL"


        # =================================================
        # WRITE AI RESULT TO INFLUXDB
        # =================================================

        ai_point = (
            Point("factory_ai")
            .tag("machine", "machine1")
            .tag("source", "ESP32_AI")
            .field(
                "fault_probability",
                fault_probability
            )
            .field(
                "temperature",
                machine_data[0]
            )
            .field(
                "pressure",
                machine_data[1]
            )
            .field(
                "motor_speed",
                machine_data[2]
            )
            .field(
                "vibration",
                machine_data[3]
            )
            .field(
                "current",
                machine_data[4]
            )
            .field(
                "voltage",
                machine_data[5]
            )
            .field(
                "humidity",
                machine_data[6]
            )
            .field(
                "ai_status",
                ai_status
            )
        )


        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=ai_point
        )


        # =================================================
        # DISPLAY
        # =================================================

        print("----------------------------------------------")

        print(
            f"Temperature : {machine_data[0]:.2f} °C"
        )

        print(
            f"Pressure    : {machine_data[1]:.2f}"
        )

        print(
            f"Motor Speed : {machine_data[2]:.2f} RPM"
        )

        print(
            f"Vibration   : {machine_data[3]:.2f} mm/s"
        )

        print(
            f"Current     : {machine_data[4]:.2f} A"
        )

        print(
            f"Voltage     : {machine_data[5]:.2f} V"
        )

        print(
            f"Humidity    : {machine_data[6]:.2f} %"
        )

        print("----------------------------------------------")

        print(
            f"AI Fault Probability: "
            f"{fault_probability * 100:.2f}%"
        )

        print(
            f"AI Status: {ai_status}"
        )

        print(
            "✓ AI result written to InfluxDB"
        )

        print("----------------------------------------------")
        print()


        time.sleep(3)


    except KeyboardInterrupt:

        print()
        print("AI monitoring stopped.")

        break


    except Exception as error:

        print(
            "AI monitoring error:",
            error
        )

        time.sleep(3)


# =====================================================
# CLOSE INFLUXDB
# =====================================================

influx_client.close()