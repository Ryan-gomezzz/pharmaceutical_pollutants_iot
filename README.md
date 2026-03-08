# Smart Wastewater Monitoring System 🌊🌍

An end-to-end IoT and Machine Learning platform for monitoring and mitigating pharmaceutical pollutants in water streams in real-time.

---

## 🏗️ System Architecture

This project uses a dual-node edge architecture with a centralized AI backend.
1. **Sensor Node (ESP32 #1):** Collects `pH`, `TDS`, `Turbidity`, `ORP`, and `Temperature`.
2. **AI Processing Layer (Flask Server):** 
   - Uses **Isolation Forest** to detect sensor anomalies.
   - Uses **Random Forest** to classify pollution type.
   - Uses **LSTM Deep Learning** to predict future pollution spikes based on recent time-series data.
3. **Decision Engine:** Automatically maps AI outputs to physical treatments (e.g., triggering chemical or UV intervention).
4. **Actuator Node (ESP32 #2):** Receives actuation commands from the Decision Engine and activates relays (Pumps, UV Modules, Electrolysis).
5. **Dashboard:** A dynamic web interface to monitor all real-time stats and active treatments.

## 📂 Project Structure

- `esp32/` - Firmware for the Sensor Node and Actuator Node.
- `server/` - The Python Flask API backend, ML inference logic, and the Decision Engine.
- `ml_training/` - Python scripts to generate synthetic datasets, train the Random Forest, and train the LSTM.
- `dataset/` - Directory where the synthetic `pollution_data.csv` is generated.
- `models/` - Directory where `.pkl` and `.h5` model artifacts are saved and read by the server.
- `dashboard/` - HTML/JS/CSS files for the local web dashboard interface.
- `docs/` - Comprehensive markdown guides for hardware wiring and deployment setup.

## 🚀 Quick Start Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Generate Data and Train AI Models
You can run this locally or export the data to Google Colab.
```bash
python setup_ml_pipeline.py
```
*Follow the printed instructions to train models on Colab, or run the `train_classifier.py` and `train_lstm.py` scripts natively.*

### Step 3: Start the Backend Server
```bash
cd server
python app.py
```
Your backend will start listening on port `5000`.

### Step 4: Access Dashboard
Open `dashboard/index.html` in your web browser.

### Step 5: Flash ESP32s
Upload the `.ino` firmware to both microcontrollers. Ensure you update `WIFI_SSID`, `WIFI_PASSWORD`, and `SERVER_URL` to match your local network setup.

## 🧠 ML Details

- **Classes:** 
  - `0`: Normal Water 
  - `1`: Packaging Residue 
  - `2`: Antibiotic Contamination
- **Deep Learning Sequence:** The LSTM consumes a tumbling window of `10` sequences across all `5` sensor features.
