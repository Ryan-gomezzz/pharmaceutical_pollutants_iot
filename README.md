<p align="center">
  <img src="https://img.shields.io/badge/🪼_AquaIntel-The_Jellyfish-0D7C66?style=for-the-badge" alt="AquaIntel">
</p>

<h1 align="center">AquaIntel: Smart Wastewater Monitoring System</h1>

<p align="center">
  <em>An end-to-end IoT + Machine Learning platform for real-time detection<br>and mitigation of pharmaceutical pollutants in water streams.</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Backend-Flask-000000?style=flat-square&logo=flask" alt="Flask"></a>
  <a href="https://www.tensorflow.org/"><img src="https://img.shields.io/badge/ML-TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white" alt="TensorFlow"></a>
  <a href="https://scikit-learn.org/"><img src="https://img.shields.io/badge/ML-scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn"></a>
  <a href="https://www.espressif.com/en/products/socs/esp32"><img src="https://img.shields.io/badge/Hardware-ESP32-E7352C?style=flat-square&logo=espressif&logoColor=white" alt="ESP32"></a>
  <img src="https://img.shields.io/badge/Status-Research_Prototype-yellow?style=flat-square" alt="Status">
</p>

---

## 📑 Table of Contents

- [Why AquaIntel?](#-why-aquaintel)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Hardware — The Jellyfish Node](#-hardware--the-jellyfish-node)
- [Machine Learning Pipeline](#-machine-learning-pipeline)
- [Results & Performance](#-results--performance)
  - [Clean Data Results](#1-clean-controlled-data)
  - [Noisy Data Results](#2-noisy-uncontrolled-data)
  - [Robustness Comparison](#3-robustness-comparison--clean-vs-noisy)
  - [Key Findings](#-key-findings)
- [Dashboard](#-dashboard)
- [Government Coordination Module](#-government-coordination-module)
- [Codebase Structure](#-codebase-structure)
- [Quickstart](#-quickstart)
- [Documentation](#-documentation)
- [Research & Citation](#-research--citation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌊 Why AquaIntel?

Pharmaceutical pollution in water bodies is an emerging global crisis. Residues from antibiotics, hormones, and plasticizers enter waterways through hospital effluent, agricultural runoff, and manufacturing discharge — often below the detection threshold of conventional monitoring infrastructure.

**AquaIntel** addresses this gap with a low-cost, deployable IoT platform that uses **proxy sensing** — instead of expensive direct chemical analysis, we leverage correlated deviations in five low-cost environmental sensors (pH, Turbidity, TDS, Temperature, Humidity) to infer pharmaceutical contamination in real time.

The system is designed to be **deployed in rivers, lakes, and industrial effluent channels** with minimal infrastructure.

---

## ✨ Key Features

| Category | Capability |
|----------|-----------|
| **Edge Sensing** | Bio-mimetic floating robot ("The Jellyfish") with 4 sensor probes |
| **AI Classification** | Random Forest (4-class) + Neural Network (3-class) pollution classifiers |
| **Spike Prediction** | LSTM deep learning model predicts turbidity spikes 2–4 readings in advance |
| **Anomaly Detection** | Isolation Forest safety pre-filter with 99.75% recall |
| **Automated Treatment** | Decision Engine maps AI outputs to physical relay actuators (pump, UV, electrolysis) |
| **Continuous Learning** | Human-in-the-loop ground truth feedback expands training data |
| **Regulatory Compliance** | Simulates India's NWMP / SPCB / CPCB governance framework |
| **Real-time Dashboard** | 6-view SPA with Chart.js, Leaflet maps, dark/light themes, CSV export |

---

## 🏗 System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                          AQUAINTEL SYSTEM                             │
│                                                                       │
│  ┌──────────────┐    WiFi / HTTP    ┌───────────────────────────────┐ │
│  │  Jellyfish   │ ───────────────► │        Flask API Server       │ │
│  │  Sensor Node │                  │  ┌─────────────────────────┐  │ │
│  │  (ESP32 #1)  │                  │  │  EMA Smoothing Filter   │  │ │
│  │              │                  │  │  Baseline Calibration   │  │ │
│  │  pH  TDS     │                  │  │  Anomaly Detection      │  │ │
│  │  Turb Temp   │                  │  ├─────────────────────────┤  │ │
│  └──────────────┘                  │  │  Random Forest (4-class)│  │ │
│                                    │  │  Neural Network (3-class│  │ │
│  ┌──────────────┐    WiFi / HTTP   │  │  LSTM (10-step window)  │  │ │
│  │  Actuator    │ ◄─────────────  │  ├─────────────────────────┤  │ │
│  │  Node        │                  │  │    Decision Engine      │  │ │
│  │  (ESP32 #2)  │                  │  └─────────────────────────┘  │ │
│  │              │                  └───────────────────────────────┘ │
│  │  Pump  UV    │                               │                    │
│  │  Elec  Valve │                               │ REST API           │
│  └──────────────┘                               ▼                    │
│                                    ┌───────────────────────────────┐ │
│                                    │   AquaIntel Dashboard (SPA)  │ │
│                                    │   Charts · AI Scores · Maps  │ │
│                                    │   Gov Coord · Actuation Ctrl │ │
│                                    └───────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

**Data flow:** Jellyfish Sensor Node → WiFi → Flask Backend → ML/DL Inference → Decision Engine → Actuator Node → Physical Treatment

---

## 🪼 Hardware — The Jellyfish Node

The sensor node is designed as a bio-mimetic floating robot:

- **The Cranium:** A buoyant, sealed waterproof dome housing the ESP32, dual 18650 Li-ion batteries, and wireless telemetry.
- **The Tentacles:** Flexible weighted appendages dangling into the water. Each tentacle carries a dedicated probe — pH, TDS, Turbidity, and Temperature. The bio-inspired geometry prevents debris entanglement and positions sensors at optimal sampling depths.

### Sensor Node Pinout (ESP32 #1)

| Sensor | GPIO | Interface | Calibration |
|--------|------|-----------|-------------|
| pH Probe | 34 | ADC1 (12-bit) | Offset: 0.0, Slope: 3.5 |
| TDS Probe | 35 | ADC1 (12-bit) | Factor: 0.5 ppm/unit |
| Turbidity | 32 | ADC1 (12-bit) | Factor: 0.1 NTU/unit |
| DHT11 (Temp) | 4 | 1-Wire | Native |

**Power:** 5V via LM2596 buck converter from 7.4V Li-ion pack. All 5V sensor outputs pass through voltage dividers (2kΩ/3.3kΩ) to protect ESP32 GPIO.

### Actuator Node Pinout (ESP32 #2)

| Treatment System | GPIO | Relay Load |
|-----------------|------|-----------|
| Water Pump | 22 | 12V / 5A |
| UV LED Module | 21 | 12V / 2A |
| Electrolysis Electrode | 19 | 5V / 10A |
| Pipeline Solenoid Valve | 23 | 12V / 3A |

**Safety:** 4-channel opto-isolated relay module required for electrical isolation between logic and load circuits.

> See [docs/hardware_setup.md](docs/hardware_setup.md) for full wiring diagrams and power calculations.

---

## 🧠 Machine Learning Pipeline

### Dataset

**10,000 synthetic samples** generated with Gaussian noise and sensor drift to simulate real-world variability across 5 sensor features:

| Feature | Mean | Std | Min | Max |
|---------|------|-----|-----|-----|
| pH | 7.473 | 0.787 | 5.31 | 9.80 |
| Turbidity (NTU) | 10.461 | 11.917 | 0.00 | 51.75 |
| TDS (ppm) | 329.841 | 210.774 | 29.59 | 937.05 |
| Temperature (°C) | 27.460 | 4.367 | 18.24 | 36.28 |
| Humidity (%) | 62.762 | 13.598 | 28.47 | 100.00 |

**Class distribution:**

| Class | Label | Samples | Percentage |
|-------|-------|---------|-----------|
| 0 | Normal Water | 6,000 | 60% |
| 1 | Possible Contamination | 2,500 | 25% |
| 2 | Severe Contamination | 1,500 | 15% |

### Models

<table>
<tr>
<th>Model</th>
<th>Purpose</th>
<th>Architecture</th>
<th>Artifact</th>
</tr>
<tr>
<td><strong>Random Forest</strong></td>
<td>Immediate pollution-type classification</td>
<td>100-tree ensemble, Gini impurity, 4 features → 4-class label + confidence</td>
<td><code>models/pollution_classifier.pkl</code></td>
</tr>
<tr>
<td><strong>Neural Network</strong></td>
<td>Supervised 3-class pollution classification</td>
<td>Dense: 64→32→16→3 neurons, ReLU + BatchNorm + Dropout, Softmax output</td>
<td>Trained in analysis pipeline</td>
</tr>
<tr>
<td><strong>Isolation Forest</strong></td>
<td>Unsupervised anomaly detection (safety pre-filter)</td>
<td>200 estimators, trained on normal samples only, contamination=0.10</td>
<td>Trained in analysis pipeline</td>
</tr>
<tr>
<td><strong>K-Means</strong></td>
<td>Unsupervised pattern discovery / validation</td>
<td>k=3 clusters (Elbow + Silhouette optimized)</td>
<td>Trained in analysis pipeline</td>
</tr>
<tr>
<td><strong>LSTM</strong></td>
<td>Predict pollution spikes <em>before</em> they peak</td>
<td>LSTM (64 units) → Dense (32, ReLU) → Dense (1, linear), 10-step window</td>
<td><code>models/lstm_model.keras</code> + <code>models/scaler.pkl</code></td>
</tr>
</table>

### Decision Engine

```
Spike probability > 80%  →  pump_and_pretreat   (Heavy pre-treatment)
Anomaly detected         →  system_off           (Safety lockdown)
Antibiotic (Class 2)     →  electrolysis_on      (Electrolysis electrode)
Packaging (Class 1)      →  uv_led_on            (UV LED module)
Normal (Class 0)         →  pump_on              (Standard pump route)
```

> See [docs/ml_pipeline.md](docs/ml_pipeline.md) for detailed training instructions and evaluation metrics.
> See [docs/ml_model_flowchart.md](docs/ml_model_flowchart.md) for a visual architecture diagram.

---

## 📊 Results & Performance

All models were evaluated under two conditions:
- **Controlled (Clean):** Ideal sensor data with expected noise levels
- **Uncontrolled (Noisy):** Simulated field conditions with 6 types of injected noise — Gaussian measurement noise, random sensor spikes, slow sensor drift, day/night temperature cycles, cross-sensor electromagnetic interference, and ADC saturation clipping

### 1. Clean (Controlled) Data

#### Overall Model Comparison

| Model | Accuracy | F1 Score | Precision | Recall |
|-------|----------|----------|-----------|--------|
| 🥇 **Random Forest** | **95.50%** | **95.39%** | 95.72% | 95.50% |
| 🥈 **Neural Network** | **95.20%** | **95.01%** | 95.68% | 95.20% |
| 🥉 **Isolation Forest** | 93.95% | 92.95% | 87.02% | **99.75%** |
| K-Means | 78.45% | 72.62% | — | — |

#### Neural Network — Per-Class Breakdown

| Class | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|---------|
| Normal Water | 99.75% | 100.00% | **99.88%** | 1,200 |
| Possible Contamination | 84.95% | 98.20% | 91.09% | 500 |
| Severe Contamination | 97.26% | 71.00% | 82.08% | 300 |
| **Weighted Avg** | **95.68%** | **95.20%** | **95.01%** | **2,000** |

#### K-Means Cluster Centroids

| Cluster | pH | Turbidity (NTU) | TDS (ppm) | Temp (°C) | Humidity (%) | Interpretation |
|---------|-----|-----------------|-----------|-----------|-------------|----------------|
| 0 | 7.54 | 3.37 | 201.96 | 23.76 | 64.08 | Normal Water (cool) |
| 1 | 7.45 | 3.62 | 209.03 | 31.06 | 53.18 | Normal Water (warm) |
| 2 | 7.44 | **24.69** | **583.32** | 27.32 | 71.50 | **Contaminated Water** |

> K-Means correctly identifies contaminated water (high turbidity + high TDS) but splits normal water into temperature-based sub-clusters rather than separating possible from severe contamination — expected for unsupervised methods.

---

### 2. Noisy (Uncontrolled) Data

Six noise types were injected to simulate field conditions:

| Noise Type | Simulation | Magnitude |
|-----------|-----------|-----------|
| Gaussian Measurement | Uncalibrated/cheap sensors | pH ±0.4, TDS ±50, Turb ±4, Temp ±2°C, Hum ±6% |
| Random Sensor Spikes | Electrical interference | ~8% of readings, ±2 pH, ±300 TDS |
| Slow Sensor Drift | Probe fouling / aging | Linear drift ±0.3 pH, ±30 TDS |
| Day/Night Cycles | Ambient temperature swings | ±3°C sinusoidal + inverse humidity |
| Cross-Sensor Interference | Electromagnetic proximity | pH ↔ turbidity, TDS ↔ temperature |
| Sensor Saturation | ADC clipping | Clamped to valid physical ranges |

#### Neural Network — Per-Class (Noisy)

| Class | Precision | Recall | F1 Score |
|-------|-----------|--------|----------|
| Normal Water | 96.53% | 97.42% | **96.97%** |
| Possible Contamination | 77.03% | 85.20% | 80.91% |
| Severe Contamination | 85.59% | 67.33% | 75.37% |

---

### 3. Robustness Comparison — Clean vs Noisy

| Model | Clean Accuracy | Noisy Accuracy | Accuracy Drop | Clean F1 | Noisy F1 | F1 Drop |
|-------|---------------|----------------|---------------|----------|----------|---------|
| **Isolation Forest** | 93.95% | 89.35% | **−4.9%** | 92.95% | 86.99% | −6.4% |
| **K-Means** | 78.45% | 75.20% | **−4.1%** | 72.62% | 69.39% | −4.4% |
| **Neural Network** | 95.20% | 89.85% | **−5.6%** | 95.01% | 89.72% | −5.6% |
| **Random Forest** | 95.50% | 89.65% | **−6.1%** | 95.39% | 89.60% | −6.1% |

### 💡 Key Findings

1. **Proxy sensing works.** Correlated changes in pH, Turbidity, TDS, Temperature, and Humidity can reliably infer pharmaceutical contamination without direct chemical analysis.

2. **TDS and Turbidity are the strongest proxy indicators** — combined Random Forest feature importance exceeds 70%, directly reflecting dissolved pharmaceutical compounds and particulates.

3. **Random Forest achieves the best overall accuracy** at 95.50%, closely followed by the Neural Network at 95.20%.

4. **The Isolation Forest provides 99.75% recall** as a binary anomaly detector — it catches nearly every contamination event, making it ideal as a safety-first pre-filter.

5. **All models degrade by only 4–6% under noisy conditions** — none collapse catastrophically, confirming the fundamental robustness of the proxy sensing approach.

6. **Normal Water classification remains strong** even under noise (~97% F1), ensuring the system reliably identifies safe water.

7. **Severe Contamination is the hardest class** under noise (F1 drops from 82.08% → 75.37%), suggesting that additional training data or periodic sensor recalibration would improve field performance.

8. **LSTM successfully predicts turbidity spikes 2–4 readings in advance** under simulated pharmaceutical discharge conditions, enabling proactive treatment.

9. **Real-time simulation** with two injected contamination events (moderate at t=80–120, severe at t=180–220) showed accurate detection in near-real-time with smooth EMA-filtered transitions.

> 📂 Full analysis with 24+ visualizations: [`results/`](results/) (clean) and [`results_noisy/`](results_noisy/) (noisy)
>
> 📄 Detailed breakdowns: [results_analysis.md](docs/results_analysis.md) · [noisy_results_analysis.md](docs/noisy_results_analysis.md)
>
> 📓 Jupyter notebook with full outputs: [`executed_notebook.ipynb`](executed_notebook.ipynb)

---

## 📺 Dashboard

The AquaIntel dashboard is a single-page application with six views:

| View | Description |
|------|-------------|
| **Dashboard** | Real-time sensor telemetry, AI classification scores, spike probability gauge, live charts |
| **Nodes** | Hardware fleet table — connection status, IP address, uptime per node |
| **Actuation** | Manual override toggles, Decision Engine ruleset display, relay state indicators |
| **Gov Coordination** | Leaflet map with 25 monitoring hubs, triangulation overlays, NWMP/SPCB/CPCB alert workflow |
| **AI Models** | Model status cards, continuous learning feedback interface, retrain trigger |
| **Settings** | API endpoint configuration, polling interval, threshold parameters |

**Features:** Dark/light theme toggle · CSV telemetry export · Baseline calibration workflow · Blinking contamination alert banner · Mobile-responsive layout

---

## 🏛 Government Coordination Module

The platform implements a simulated version of India's National Water Monitoring Protocol (NWMP):

- **25 monitoring hubs** distributed within a 5 km radius of the deployment site (default: Bengaluru, 12.9716°N, 77.5946°E)
- **Pollution triangulation** from alerting hub cluster centroids
- **Severity-tiered response:**

| Severity | Regulatory Action |
|----------|------------------|
| 🟢 **Low** | NWMP data logging, frequency increase, local authority notification |
| 🟡 **Moderate** | SPCB alert, drone sampling request, pharmaceutical facility flagging |
| 🔴 **Severe** | CPCB emergency alert, field unit dispatch, pipeline containment |

**Applicable regulatory bodies:** MoEFCC · CPCB · SPCB · NWMP

---

## 📁 Codebase Structure

```
smart_pollution_system/
├── esp32/
│   ├── sensor_node/sensor_node.ino       # Jellyfish sensor firmware
│   └── actuator_node/actuator_node.ino   # Treatment actuator firmware
├── server/
│   ├── app.py                            # Flask REST API & data pipeline
│   ├── ml_model.py                       # Random Forest inference
│   ├── dl_model.py                       # LSTM inference & spike prediction
│   ├── decision_engine.py                # AI-to-action mapping
│   ├── data_buffer.py                    # Circular time-series buffer
│   └── hub_network.py                    # Gov coordination simulation
├── ml_training/
│   ├── dataset_generator.py              # Synthetic dataset (10k samples)
│   ├── train_classifier.py               # Random Forest training
│   ├── train_lstm.py                     # LSTM training
│   └── test_model.py                     # Evaluation & metrics
├── dashboard/
│   ├── index.html                        # SPA dashboard
│   ├── script.js                         # Frontend logic & Chart.js
│   └── style.css                         # Dark/light theme system
├── docs/                                 # Architecture & deployment guides
├── dataset/                              # Generated training data (gitignored)
├── models/                               # Trained artifacts (gitignored)
├── results/                              # Clean data analysis — 24 plots + CSVs
├── results_noisy/                        # Noisy data analysis — 20 plots + CSVs
├── run_all_analysis.py                   # Full analysis pipeline (clean)
├── run_noisy_analysis.py                 # Full analysis pipeline (noisy)
├── build_notebook.py                     # Jupyter notebook builder
├── setup_ml_pipeline.py                  # One-shot setup automation
├── pharmaceutical_pollution_detection.ipynb  # Colab-ready notebook
├── executed_notebook.ipynb               # Pre-executed notebook with outputs
├── requirements.txt                      # Pinned Python dependencies
├── CITATION.cff                          # Academic citation metadata
├── CONTRIBUTING.md                       # Contribution guidelines
├── CODE_OF_CONDUCT.md                    # Community standards
├── CHANGELOG.md                          # Version history
└── LICENSE                               # MIT License
```

---

## 🚀 Quickstart

### Prerequisites

- Python 3.9+
- Arduino IDE with ESP32 board support
- Two ESP32 development boards (for hardware deployment)

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Generate dataset & train models

```bash
# One-shot automated setup
python setup_ml_pipeline.py

# Or manually:
python ml_training/dataset_generator.py
python ml_training/train_classifier.py
python ml_training/train_lstm.py
```

> **Google Colab:** Upload `pharmaceutical_pollution_detection.ipynb` to Colab for GPU-accelerated LSTM training. Download the artifact files to `models/`.

### Step 3 — Run the full analysis pipeline (optional)

```bash
# Generates all plots and CSVs in results/
python run_all_analysis.py

# Generates noisy-condition analysis in results_noisy/
python run_noisy_analysis.py
```

### Step 4 — Start the backend server

```bash
cd server
python app.py
# Listening on http://0.0.0.0:5000
```

### Step 5 — Open the dashboard

Open `dashboard/index.html` directly in your browser. It polls the Flask API every 2 seconds.

### Step 6 — Flash ESP32 firmware

Edit the following constants in both `.ino` files before uploading:

```cpp
const char* WIFI_SSID     = "YOUR_NETWORK";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* SERVER_URL    = "http://192.168.x.x:5000/sensor-data";
```

Upload via Arduino IDE to both sensor and actuator nodes.

### 🎮 Demo Mode (No Hardware)

The backend includes a `/simulate-event` endpoint and the Gov Coordination view has a built-in simulation engine — the full system can be demonstrated without physical ESP32 nodes.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [System Architecture](docs/system_architecture.md) | Full design overview and data flow |
| [ML Pipeline](docs/ml_pipeline.md) | Training, evaluation, model hot-reload |
| [ML Flowchart](docs/ml_model_flowchart.md) | Visual model architecture diagram |
| [Hardware Setup](docs/hardware_setup.md) | Wiring diagrams, power calculations, calibration |
| [Deployment Guide](docs/deployment_guide.md) | Step-by-step deployment instructions |
| [Dashboard Guide](docs/dashboard_guide.md) | UI walkthrough and feature reference |
| [Results Analysis](docs/results_analysis.md) | Clean data — full performance metrics with 24 plots |
| [Noisy Results](docs/noisy_results_analysis.md) | Noisy data — robustness under 6 noise types |

---

## 📖 Research & Citation

If you use this work in your research, please cite:

```bibtex
@software{aquaintel2025,
  title     = {AquaIntel: Smart Wastewater Monitoring System — The Jellyfish},
  author    = {Gomez, Ryan and Gudi, Anusha and Khot, Sukanya and Mani, Shreyas},
  year      = {2025},
  url       = {https://github.com/[username]/aquaintel},
  license   = {MIT},
  version   = {1.0.0}
}
```

A formal `CITATION.cff` file is included in this repository for automated citation tooling.

### Research Context

This system was developed as part of research into low-cost, AI-augmented IoT platforms for pharmaceutical pollution monitoring in developing-world water infrastructure. The work addresses:

1. **Gap in affordable real-time pharmaceutical pollution sensing** — conventional lab analysis is slow, expensive, and non-continuous
2. **Edge-cloud hybrid ML architecture** — inference runs on commodity hardware with no cloud subscription required
3. **Human-in-the-loop continuous learning** — ground truth labels from field operators improve models over time
4. **Regulatory integration** — automated escalation workflows aligned to Indian environmental law (MoEFCC, CPCB, SPCB, NWMP)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

**Areas open for contribution:**
- Additional sensor types (heavy metals, nitrates, phosphates, dissolved oxygen)
- MQTT-based communication layer (replacing HTTP polling)
- Docker Compose deployment for the Flask server
- Mobile companion app for field operators
- Additional regional regulatory frameworks (EU WFD, US EPA)

---

## ⚖ License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

You are free to use, modify, and distribute this software for any purpose, including commercial and academic use, provided attribution is maintained.

---

<p align="center">
  <strong>🪼 AquaIntel — The Jellyfish</strong><br>
  <em>Built with ❤️ for cleaner water</em>
</p>
