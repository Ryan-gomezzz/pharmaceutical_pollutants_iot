# Hardware Setup Guide (Dual-Node Architecture)

## 1. Sensor Node (ESP32 #1)
Monitors water quality and transmits data to the server.

### Wiring
| Sensor        | ESP32 Pin | Power | Ground |
|---------------|-----------|-------|--------|
| pH            | GPIO 34   | 3.3V  | GND    |
| TDS           | GPIO 35   | 3.3V  | GND    |
| Turbidity     | GPIO 32   | 3.3V  | GND    |
| ORP           | GPIO 33   | 3.3V  | GND    |
| DS18B20 (Temp)| GPIO 4    | 3.3V  | GND    |

*Note: Ensure DS18B20 has a 4.7k pull-up resistor between Data and VCC.*

## 2. Actuator Node (ESP32 #2)
Receives commands from the Decision Engine and activates physical treatment systems.

### Wiring
| Treatment System      | Relay / ESP32 Pin |
|-----------------------|-------------------|
| Water Pump            | GPIO 22           |
| UV LED Module         | GPIO 21           |
| Electrolysis Electrode| GPIO 19           |
| Main Pipeline Relay   | GPIO 23           |
