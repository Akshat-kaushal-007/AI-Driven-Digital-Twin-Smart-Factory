# AI-Driven Digital Twin for Smart Factory Operations

## 📌 Project Overview

This project implements an AI-driven Digital Twin prototype for smart factory machine monitoring, anomaly detection, recovery system and real-time visualization.

The system creates a virtual representation of an industrial machine by continuously generating machine operating data, analyzing it using an AI model, storing the data in InfluxDB Cloud, and visualizing the machine condition through Grafana Cloud.

## 🏭 System Architecture

Python Machine Simulator
        ↓
Machine Parameters
        ↓
PyTorch AI Model
        ↓
Fault Probability
        ↓
InfluxDB Cloud
        ↓
Grafana Cloud Dashboard

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

- Fault Probability
- AI Machine Status
- NORMAL / FAULT classification

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

## 📁 Project Structure

```text
AI-Driven-Digital-Twin-Smart-Factory/
│
├── src/
│   ├── realtime_factory_v2.py
│   └── ai_to_influx.py
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