# Grafana Dashboard Queries

## Data Source

The dashboard uses InfluxDB Cloud as the time-series data source.

Bucket:

Smart_factory

## Machine Monitoring

### Temperature

```flux
from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "temperature")

### Pressure

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "pressure")

### Motor Speed

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "motor_speed")

### Vibration

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "vibration")

### Current

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "current")

### Voltage

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "voltage")

### Power

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "power")

### Humidity

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_machine")
  |> filter(fn: (r) => r._field == "humidity")

### AI Fault Probability

from(bucket: "Smart_factory")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "factory_ai")
  |> filter(fn: (r) => r._field == "fault_probability")

