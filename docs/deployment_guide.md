# Deployment Guide

## 1. Environment Setup
1. Ensure Python 3.9+ is installed.
2. Install dependencies mapping the AI pipeline:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Machine Learning Training
The server relies on trained models to function.
1. Generate synthetic time-series data:
   ```bash
   python ml_training/dataset_generator.py
   ```
2. Train Isolation Forest and Random Forest:
   ```bash
   python ml_training/train_classifier.py
   ```
3. Train LSTM Sequence Predictor:
   ```bash
   python ml_training/train_lstm.py
   ```
   *Models are saved directly to the `server/` directory.*

## 3. Run the Backend API
```bash
cd server
python app.py
```
*Note the local IP address of your machine for the ESP32 configurations.*

## 4. Flash ESP32 Nodes
1. In `esp32/sensor_node/sensor_node.ino`, update your `WIFI_SSID`, `WIFI_PASSWORD`, and the `SERVER_URL`. Upload to ESP32 #1.
2. In `esp32/actuator_node/actuator_node.ino`, perform the same configuration. Upload to ESP32 #2.

## 5. Dashboard
Open `dashboard/index.html` in your browser. Monitoring and remote commands will begin automatically as soon as the ESP32s connect.
