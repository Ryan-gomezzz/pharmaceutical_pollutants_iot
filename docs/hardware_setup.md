# Hardware Setup Guide (Dual-Node Architecture)

## 1. Sensor Node (ESP32 #1)
Monitors water quality and transmits data to the server. The ESP32 is a 3.3V logic device. **Do not apply 5V directly to the GPIO pins without voltage division or logic level conversion, or the ESP32 will permanently fail.**

### Power Requirements
- **Microcontroller**: The ESP32 requires a 5V input either via the Micro-USB port or specifically pin `VIN`. 
- **Mobile Power**: If deployed on the actual "Jellyfish", you should use `2x 18650 Li-ion` cells (in series for 7.4V or parallel for 3.7V). Provide a **buck converter (e.g., LM2596)** to strictly step the voltage down to 5.0V before entering the ESP32 `VIN` pin. 
- **Sensor Power**: Most commercial analog water sensors (pH, TDS, Turbidity) operate at 3.3V - 5.0V. It's recommended to pull their `VCC` from the stepped-down 5V line rather than relying on the ESP32's onboard 3.3V regulator, which may overheat if current draw exceeds ~200mA.

### Circuit Protective Measures
The pH, TDS, and Turbidity sensor probes output analog voltages. **If your sensor boards transmit a 5V peak analog signal**, you MUST use a voltage divider (e.g., a simple resistor network using `R1=2kΩ` and `R2=3.3kΩ`) between the sensor's `A0` output and the ESP32 `GPIO` to safely step the 5V max signal down to approximately 3.1V max.

### Wiring
| Sensor        | ESP32 Pin | Power | Ground |
|---------------|-----------|-------|--------|
| pH            | GPIO 34   | `5V OUT` (Stepped Down)  | `GND`    |
| TDS           | GPIO 35   | `5V OUT` (Stepped Down)  | `GND`    |
| Turbidity     | GPIO 32   | `5V OUT` (Stepped Down)  | `GND`    |
| DHT11 (Temp)  | GPIO 4    | 3.3V  | `GND`    |

*Critical Note: If using a bare `DHT11` sensor (not a pre-mounted module board), it strictly requires a `4.7kΩ` to `10kΩ` pull-up resistor bridging its `Data` (GPIO 4) and `VCC` (3.3V) lines.*

---

## 2. Actuator Node (ESP32 #2)
Receives commands from the Decision Engine and activates massive industrial relays to control physical treatment systems.

### Relay Electrical Safety (CRITICAL)
**DO NOT run the water pumps or UV lights directly from the ESP32 GPIOs or Power lines.** Microcontrollers output minimal logic current (~20mA). You **MUST** use a **4-Channel Opto-Isolated Relay Module**. The ESP32 simply switches the relay's low-voltage trigger, allowing the relay to safely open/close the high-voltage (12V-120V) circuits powering the pumps.

### Wiring
| Treatment System      | Optocoupler IN / ESP32 | Relay Load (Example) |
|-----------------------|-------------------|----------------------|
| Water Pump            | GPIO 22           | 12V 5A High-Torque |
| UV LED Module         | GPIO 21           | 12V 2A Panel       |
| Electrolysis Electrode| GPIO 19           | 5V 10A Lead Array  |
| Main Pipeline Relay   | GPIO 23           | Solenoid Valve Load|

---

## 3. Circuit Schematic (Sensor Node)

The following diagram illustrates the proper power and data mapping for the floating Jellyfish edge sensor.

```mermaid
graph TD
    classDef hardware fill:#1a1a1a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef power fill:#ef4444,stroke:#7f1d1d,stroke-width:2px,color:#fff;
    classDef sensor fill:#10b981,stroke:#064e3b,stroke-width:2px,color:#000;
    classDef resistor fill:#f59e0b,stroke:#78350f,stroke-width:2px,color:#000;

    subgraph Power Source
        BAT[Dual 18650 Battery Pack]:::power
        BUCK[LM2596 Buck Converter]:::hardware
    end

    subgraph MCU Core
        ESP[ESP32 Development Board]:::hardware
        GND((Common Ground)):::power
    end

    subgraph Probes
        S_PH[pH Sensor Module]:::sensor
        S_TDS[TDS Module]:::sensor
        S_TURB[Turbidity Module]:::sensor
        S_TEMP[DHT11 Temp Probe]:::sensor
    end

    subgraph Safety & Division
        R_PULLUP[4.7kΩ Pull-Up Resistor]:::resistor
        DIVIDER[Voltage Dividers if Sensors are 5V]:::resistor
    end

    %% Power Routing
    BAT -- "7.4V RAW" --> BUCK
    BUCK -. "Regulated 5.0V" .-> ESP_VIN[ESP32 VIN Pin]
    BUCK -. "Regulated 5.0V" .-> S_PH_VCC[pH VCC]
    BUCK -. "Regulated 5.0V" .-> S_TDS_VCC[TDS VCC]
    BUCK -. "Regulated 5.0V" .-> S_TURB_VCC[Turbidity VCC]
    
    ESP -- "3.3V Out" --> S_TEMP_VCC[Temp VCC]
    
    %% Ground Commonization
    BUCK -- "GND" --> GND
    ESP -- "GND" --> GND
    S_PH -- "GND" --> GND
    S_TDS -- "GND" --> GND
    S_TURB -- "GND" --> GND
    S_TEMP -- "GND" --> GND

    %% Data Routing
    S_PH -- "Analog Out (3.1v peak)" --> DIVIDER
    S_TDS -- "Analog Out (3.1v peak)" --> DIVIDER
    S_TURB -- "Analog Out (3.1v peak)" --> DIVIDER
    
    DIVIDER == "Safe Data" ==> ESP_G34[GPIO 34]
    DIVIDER == "Safe Data" ==> ESP_G35[GPIO 35]
    DIVIDER == "Safe Data" ==> ESP_G32[GPIO 32]

    %% Temp Specifics
    S_TEMP_VCC -- "Bridged via" --> R_PULLUP
    S_TEMP -- "1-Wire Digital" --> R_PULLUP
    R_PULLUP == "Data" ==> a4[GPIO 4]
```
