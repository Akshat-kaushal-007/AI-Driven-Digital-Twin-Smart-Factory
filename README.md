# AI-Driven Digital Twin for Smart Factory Operations

## 📌 Project Overview

This project implements an AI-driven Digital Twin prototype for smart factory machine monitoring, anomaly detection, recovery system and real-time visualization.

The system creates a virtual representation of an industrial machine by continuously generating machine operating data, analyzing it using an AI model, storing the data in InfluxDB Cloud, and visualizing the machine condition through Grafana Cloud.

## Machine Monitoring Flow
Machine Parameters
        ↓
      ESP32
        ↓
   MQTT / EMQX
        ↓
 Cloud Receiver
        ↓
   InfluxDB Cloud
        ↓
    AI Analysis
        ↓
 NORMAL / WARNING / FAULT
        ↓
   Grafana Dashboard

## ⚙️ Machine Parameters

The digital twin monitors:

- Temperature
- Pressure
- Motor Speed
- Vibration
- Current
- Voltage
- Power
- Humidity

## 🤖 AI-Based Fault Detection

A PyTorch neural network analyzes seven machine parameters and estimates the probability of a machine fault.

The AI output includes:

- Fault Probability.

The classification threshold is treated as a project/model parameter and is intended to be validated using test data rather than presented as an industrial standard.

## 📊 Real-Time Monitoring

InfluxDB Cloud is used for time-series data storage.

Grafana Cloud provides real-time visualization of:

- Temperature
- Pressure
- Motor Speed
- Vibration
- Current
- Voltage
- Power
- Humidity
- AI Fault Probability
- AI Machine Status

## 🛠️ Technologies Used

- Python
- PyTorch
- InfluxDB Cloud
- Grafana Cloud
- MQTT / Mosquitto
- ESP32 *(planned hardware integration)*
- Arduino *(planned hardware integration)*

## Learning Outcomes

Through this project, I gained practical experience in:

Embedded Systems
ESP32 programming
MQTT communication
Industrial IoT
Cloud computing
Time-series databases
Python backend development
PyTorch
AI-based anomaly detection
Grafana visualization
Cloud deployment
Git and GitHub

## Future Improvements
-Integration with physical industrial sensors
-Monitoring of multiple machines
-Larger and more diverse training datasets
-Predictive maintenance
-Automated alerts
-Historical fault analysis
-Advanced digital-twin visualization

## Author

Akshat Kaushal

B.Tech – Electronics & Communication Engineering
3rd Year | ECE-A
ABES Engineering College

## 📁 Project Structure

```text
AI-Driven-Digital-Twin-Smart-Factory/
│
|---Cloud Receiver
|    |---ai_worker.py
|    |---app.py
|    |---requriments.txt
├── src/
│   ├── esp_ai.py
│
├── docs/
│   └── SRS.pdf
│
├── grafana/
│   └── queries.md
│
├── README.md
├── requirements.txt
└── .gitignore

## 🔗 Only one thing to change

Find:

```markdown
[View Live Grafana Dashboard](https://happyjelly2598.grafana.net/public-dashboards/7ec087dd4c2148a284a327328854be12)
