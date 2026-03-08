# 🪼 Smart Wastewater Monitoring System: "The Jellyfish" 🌊

An end-to-end IoT, Machine Learning, and Edge Robotics platform for monitoring and mitigating pharmaceutical pollutants in water streams in real-time.

![Jellyfish Concept Form Factor](https://images.unsplash.com/photo-1544520786-89d2c499ea8d?q=80&w=1200&auto=format&fit=crop)

---

## 🦾 Robotics Form Factor: The Jellyfish Node
The physical hardware for the **Sensor Node (ESP32 #1)** is designed as an autonomous, floating bio-mimetic "Jellyfish" robot:
- **The Cranium (Head):** A buoyant, sealed, translucent waterproof dome housing the motherboard, the ESP32 microcontroller, dual 18650 Li-ion battery arrays, and wireless communication telemetry.
- **The Tentacles:** Flexible, weighted appendages dangling beneath the dome into the water stream. Each tentacle houses a specific environmental probe (pH, Turbidity, TDS, ORP, Temperature). This bio-inspired design prevents debris entanglement and ensures sensors capture readings at various optimal depths.

---

## 🏗️ System Architecture

This project uses a dual-node edge architecture with a centralized AI backend.
1. **The Jellyfish Node (ESP32 #1):** Collects the physical variables (`pH`, `TDS`, `Turbidity`, `ORP`, `Temp`) and broadcasts them to the remote server.
2. **AI Processing Layer (Flask Server):** 
   - Uses **Isolation Forest** to immediately filter catastrophic sensor anomalies (e.g. a severed tentacle).
   - Uses **Random Forest** to classify the exact pollutant signature.
   - Uses **LSTM Deep Learning** to ingest sliding 10-step windows of time-series data to predict *future* pollution spikes before they peak.
3. **Decision Engine:** Automatically maps the AI intelligence into physical action parameters.
4. **Treatment Actuator Node (ESP32 #2):** A stationary node located downstream. It receives actuation commands from the Decision Engine and activates massive industrial relays (Pumps, UV Modules, Electrolysis fields).
5. **Dashboard:** A dynamic web interface mapping real-time Jellyfish intelligence, AI confidence scores, and downstream Treatment activation constraints.

---

## 📂 Codebase Structure

- `esp32/` - C++ Firmware for the Jellyfish Sensor Node and downstream Actuator Node.
- `server/` - The Python Flask API backend, ML inference logic, `joblib` scalers, and the Decision Engine.
- `ml_training/` - Python scripts to synthesize constrained datasets, train the Random Forest, and train the Deep Learning LSTM natively.
- `dataset/` - Auto-generated `pollution_data.csv` mapping 10,000 algorithmic simulation states.
- `models/` - Directory where `.pkl` and `.h5` model artifacts are saved and hot-loaded by the server.
- `dashboard/` - Futuristic HTML/JS/CSS files for the command center UI.
- `docs/` - Comprehensive markdown guides for hardware wiring and deployment setup.

---

## 🚀 Deployment Guide & Setup

### Step 1: Install Dependencies
Ensure you have Python 3.9+ installed and run:
```bash
pip install -r requirements.txt
```

### Step 2: Generate Data and Train AI Models
You can run this locally or export the data to Google Colab.
```bash
python setup_ml_pipeline.py
```
*Follow the printed terminal instructions to train models using the Colab GPU Notebook, or run the `train_classifier.py` and `train_lstm.py` scripts natively.*

### Step 3: Start the Command Center Server
```bash
cd server
python app.py
```
Your backend will spool up and begin listening on `0.0.0.0:5000`.

### Step 4: Access Dashboard
Open `dashboard/index.html` in your web browser. The charts will wait for Jellyfish telemetry.

### Step 5: Flash ESP32s
Upload the `.ino` firmware to both microcontrollers. Ensure you update `WIFI_SSID`, `WIFI_PASSWORD`, and `SERVER_URL` inside the `.ino` loops to match your network infrastructure.

---

## 🧠 Machine Learning Taxonomy

- **Constrained Classes:** 
  - `0`: Normal Water 
  - `1`: Packaging Residue (Elevated TDS & Turbidity)
  - `2`: Antibiotic Contamination (Aggressive ORP & pH volatility)
- **Deep Learning Sequence:** The LSTM framework natively consumes a tumbling inference window of `10` sequence-steps across all `5` sensor features before outputting its catastrophic spike probability (`loss='mse'`).
