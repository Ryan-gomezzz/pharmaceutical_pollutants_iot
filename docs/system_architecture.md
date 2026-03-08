# System Architecture

## Overview
This is a comprehensive Dual-Node IoT Smart Wastewater Monitoring system featuring a 3-stage AI pipeline.

## Data Flow
`Sensors -> ESP32 Sensor Node -> WiFi -> Python Flask Server -> ML/DL Models -> Decision Engine -> WiFi -> ESP32 Actuator Node`

## Component Layers

### 1. Edge Layer
- **Sensor Node:** Collects ph, tds, turbidity, orp, and temperature every 5 seconds.
- **Actuator Node:** Polls the server every 3 seconds for treatment commands.

### 2. AI Processing Layer (Python Backend)
- **Anomaly Detection:** `Isolation Forest` detects whether the incoming sensor data represents a fundamental system error or extreme anomaly.
- **Pollution Classification:** `RandomForestClassifier` categorizes the water into: Normal (0), Packaging Residue (1), or Antibiotic Contamination (2).
- **Time-Series Prediction:** `LSTM` predicts the probability of a pollution spike based on the last 10 readings.

### 3. Application & Decision Layer
- **Decision Engine:** Determines physical intervention. For example: Antibiotics trigger Electrolysis. Spikes trigger preemptive pre-treatment.
- **Dashboard:** HTML/JS web interface displaying real-time metrics, AI status, and active treatments automatically refreshing from the backend server.
