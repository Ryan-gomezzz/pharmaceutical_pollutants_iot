# AquaIntel: Smart Wastewater Monitoring System — "The Jellyfish"

> An end-to-end IoT, Machine Learning, and Edge Robotics platform for real-time detection and mitigation of pharmaceutical pollutants in water streams.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/backend-Flask-lightgrey)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/ML-TensorFlow%20%7C%20scikit--learn-orange)](https://www.tensorflow.org/)
[![Platform: ESP32](https://img.shields.io/badge/hardware-ESP32-green)](https://www.espressif.com/en/products/socs/esp32)
[![Status: Research](https://img.shields.io/badge/status-Research%20Prototype-yellow)]()

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Hardware Design: The Jellyfish Node](#hardware-design-the-jellyfish-node)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Codebase Structure](#codebase-structure)
- [Quickstart](#quickstart)
- [Dashboard](#dashboard)
- [Government Coordination Module](#government-coordination-module)
- [Results](#results)
- [Research & Citation](#research--citation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Pharmaceutical pollution in water bodies is an emerging global crisis. Residues from antibiotics, hormones, and plasticizers enter waterways through hospital effluent, agricultural runoff, and manufacturing discharge — often below the detection threshold of conventional monitoring infrastructure.

**AquaIntel** addresses this gap with a low-cost, deployable IoT platform that combines:

- **Real-time edge sensing** via a bio-mimetic floating robot ("The Jellyfish")
- **On-server AI inference** — Random Forest classification + LSTM time-series spike prediction
- **Automated treatment actuation** mapped from AI decisions to physical relay outputs
- **Continuous learning** via human-in-the-loop ground truth feedback
- **Regulatory coordination** simulating India's NWMP / SPCB / CPCB governance framework

The system is designed to be **deployed in rivers, lakes, and industrial effluent channels** with minimal infrastructure.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AQUAINTEL SYSTEM                             │
│                                                                     │
│  ┌──────────────┐    WiFi/HTTP    ┌───────────────────────────────┐ │
│  │ Jellyfish    │ ─────────────► │       Flask API Server        │ │
│  │ Sensor Node  │                │  ┌─────────────────────────┐  │ │
│  │  (ESP32 #1)  │                │  │  EMA Smoothing Filter   │  │ │
│  │              │                │  │  Baseline Calibration   │  │ │
│  │  pH  TDS     │                │  │  Anomaly Detection      │  │ │
│  │  Turb Temp   │                │  ├─────────────────────────┤  │ │
│  └──────────────┘                │  │  Random Forest (4-class)│  │ │
│                                  │  │  LSTM (10-step window)  │  │ │
│  ┌──────────────┐    WiFi/HTTP   │  ├─────────────────────────┤  │ │
│  │ Actuator     │ ◄──────────── │  │    Decision Engine      │  │ │
│  │ Node         │                │  └─────────────────────────┘  │ │
│  │  (ESP32 #2)  │                └───────────────────────────────┘ │
│  │              │                             │                     │
│  │  Pump UV     │                             │ REST API            │
│  │  Elec Valve  │                             ▼                     │
│  └──────────────┘                ┌───────────────────────────────┐ │
│                                  │   AquaIntel Dashboard (HTML)  │ │
│                                  │   Real-time charts, AI scores,│ │
│                                  │   Gov coordination, Controls  │ │
│                                  └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

**Data flow:** Jellyfish Sensor Node → WiFi → Flask Backend → ML/DL Inference → Decision Engine → Actuator Node → Physical Treatment

---

## Hardware Design: The Jellyfish Node

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

See [docs/hardware_setup.md](docs/hardware_setup.md) for full wiring diagrams and power calculations.

---

## Machine Learning Pipeline

### Dataset

10,000 synthetic samples generated with Gaussian noise and sensor drift to simulate real-world variability.

| Class | Label | pH | TDS (ppm) | Turbidity (NTU) | Prevalence |
|-------|-------|----|-----------|-----------------|-----------|
| 0 | Normal Water | 6.5–7.5 | 200–400 | 0–50 | 60% |
| 1 | Packaging Residue | 7.0–8.5 | 400–700 | 50–200 | 25% |
| 2 | Antibiotic Contamination | 5.0–6.5 | 350–600 | 20–80 | 15% |
| 3 | Systemic Anomaly | Random | Random | Random | ~5% |

### Model 1: Random Forest Classifier

- **Purpose:** Immediate pollution-type classification from 4 sensor features
- **Architecture:** 100-tree ensemble, Gini impurity criterion
- **Input:** `[pH, TDS, Turbidity, Temperature]`
- **Output:** 4-class label (0–3) + per-class confidence scores
- **Reported F1:** 0.96
- **Artifact:** `models/pollution_classifier.pkl`

### Model 2: LSTM Neural Network

- **Purpose:** Predict pollution spikes *before* they peak using historical windows
- **Architecture:** LSTM (64 units) → Dense (32, ReLU) → Dense (1, linear)
- **Input:** 10-step sliding window of normalized 4-feature time-series
- **Output:** Predicted next turbidity value (deviation → spike probability)
- **Artifact:** `models/lstm_model.keras` + `models/scaler.pkl`

### Decision Engine

```
Spike probability > 80%  →  pump_and_pretreat
Anomaly detected         →  system_off
Antibiotic (Class 2)     →  electrolysis_on
Packaging (Class 1)      →  uv_led_on
Normal (Class 0)         →  pump_on
```

See [docs/ml_pipeline.md](docs/ml_pipeline.md) for detailed training instructions and evaluation metrics.

---

## Codebase Structure

```
smart_pollution_system/
├── esp32/
│   ├── sensor_node/sensor_node.ino      # Jellyfish sensor firmware
│   └── actuator_node/actuator_node.ino  # Treatment actuator firmware
├── server/
│   ├── app.py                           # Flask REST API & data pipeline
│   ├── ml_model.py                      # Random Forest inference
│   ├── dl_model.py                      # LSTM inference & spike prediction
│   ├── decision_engine.py               # AI-to-action mapping
│   ├── data_buffer.py                   # Circular time-series buffer
│   └── hub_network.py                   # Gov coordination simulation
├── ml_training/
│   ├── dataset_generator.py             # Synthetic dataset (10k samples)
│   ├── train_classifier.py              # Random Forest training
│   ├── train_lstm.py                    # LSTM training
│   └── test_model.py                    # Evaluation & metrics
├── dashboard/
│   ├── index.html                       # SPA dashboard
│   ├── script.js                        # Frontend logic & Chart.js
│   └── style.css                        # Dark/light theme system
├── docs/                                # Architecture & deployment guides
├── dataset/                             # Generated training data (gitignored)
├── models/                              # Trained artifacts (gitignored)
├── results/                             # Analysis outputs
├── requirements.txt                     # Pinned Python dependencies
├── setup_ml_pipeline.py                 # One-shot setup automation
├── CITATION.cff                         # Academic citation metadata
├── CONTRIBUTING.md                      # Contribution guidelines
├── CODE_OF_CONDUCT.md                   # Community standards
├── CHANGELOG.md                         # Version history
└── LICENSE                              # MIT License
```

---

## Quickstart

### Prerequisites

- Python 3.9+
- Arduino IDE with ESP32 board support
- Two ESP32 development boards (for hardware deployment)

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Generate dataset and train models

```bash
# One-shot automated setup
python setup_ml_pipeline.py

# Or manually:
python ml_training/dataset_generator.py
python ml_training/train_classifier.py
python ml_training/train_lstm.py
```

> **Google Colab:** Upload the Jupyter notebook `pharmaceutical_pollution_detection.ipynb` to Colab for GPU-accelerated LSTM training. Download the artifact files to `models/`.

### Step 3 — Start the backend server

```bash
cd server
python app.py
# Listening on http://0.0.0.0:5000
```

### Step 4 — Open the dashboard

Open `dashboard/index.html` directly in your browser. It polls the Flask API every 2 seconds.

### Step 5 — Flash ESP32 firmware

Edit the following constants in both `.ino` files before uploading:

```cpp
const char* WIFI_SSID     = "YOUR_NETWORK";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* SERVER_URL    = "http://192.168.x.x:5000/sensor-data";
```

Upload via Arduino IDE to both sensor and actuator nodes.

### Demo mode (no hardware)

The backend includes a `/simulate-event` endpoint and the gov coordination view has a built-in simulation engine — the full system can be demonstrated without physical ESP32 nodes.

---

## Dashboard

The AquaIntel dashboard is a single-page application with six views:

| View | Description |
|------|-------------|
| **Dashboard** | Real-time sensor telemetry, AI classification, spike probability gauge, charts |
| **Nodes** | Hardware fleet table — connection status, IP, uptime per node |
| **Actuation** | Manual override toggles, Decision Engine ruleset display |
| **Gov Coordination** | Leaflet map, 25-hub network, triangulation, NWMP/SPCB/CPCB alerts |
| **AI Models** | Model status cards, continuous learning feedback, retrain trigger |
| **Settings** | API endpoint, polling interval, threshold configuration |

**Features:** Dark/light theme toggle · CSV telemetry export · Baseline calibration workflow · Blinking contamination alert banner · Mobile-responsive layout

---

## Government Coordination Module

The platform implements a simulated version of India's National Water Monitoring Protocol (NWMP):

- **25 monitoring hubs** distributed within a 5 km radius of the deployment site (default: Bengaluru, 12.9716°N, 77.5946°E)
- **Pollution triangulation** from alerting hub cluster centroids
- **Severity-tiered response:**
  - **Low:** NWMP data logging, frequency increase, local authority notification
  - **Moderate:** SPCB alert, drone sampling request, pharmaceutical facility flagging
  - **Severe:** CPCB emergency alert, field unit dispatch, pipeline containment

Applicable regulatory bodies: **MoEFCC · CPCB · SPCB · NWMP**

---

## Results

Pre-computed analysis results (classification reports, confusion matrices, LSTM training curves) are available in [`results/`](results/) and [`results_noisy/`](results_noisy/).

The executed Jupyter notebook with full outputs is at [`executed_notebook.ipynb`](executed_notebook.ipynb).

Key findings:
- Random Forest: **96% F1-score** on 4-class pollution classification
- LSTM: Successfully predicts turbidity spikes **2–4 readings in advance** under simulated pharmaceutical discharge conditions
- Baseline deviation detection reliably flags contamination events with **< 3% false-positive rate** under Gaussian noise conditions

See [docs/results_analysis.md](docs/results_analysis.md) and [docs/noisy_results_analysis.md](docs/noisy_results_analysis.md) for detailed breakdowns.

---

## Research & Citation

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

1. **Gap in affordable real-time pharmaceutical pollution sensing** — conventional lab analysis is slow and expensive
2. **Edge-cloud hybrid ML architecture** — inference runs on commodity hardware with no cloud subscription
3. **Human-in-the-loop continuous learning** — ground truth labels from field operators improve models over time
4. **Regulatory integration** — automated escalation workflows aligned to Indian environmental law

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

Areas particularly open for contribution:
- Additional sensor types (heavy metals, nitrates, phosphates)
- MQTT-based communication layer (replacing HTTP polling)
- Docker deployment for the Flask server
- Mobile app for field operators
- Additional regional regulatory frameworks (EU WFD, US EPA)

---

## Documentation

| Document | Description |
|----------|-------------|
| [System Architecture](docs/system_architecture.md) | Full design overview |
| [ML Pipeline](docs/ml_pipeline.md) | Training, evaluation, model hot-reload |
| [Hardware Setup](docs/hardware_setup.md) | Wiring, power, sensor calibration |
| [Deployment Guide](docs/deployment_guide.md) | Step-by-step deployment |
| [Dashboard Guide](docs/dashboard_guide.md) | UI walkthrough |
| [Results Analysis](docs/results_analysis.md) | Performance metrics |
| [Noisy Results](docs/noisy_results_analysis.md) | Robustness under sensor noise |
| [ML Flowchart](docs/ml_model_flowchart.md) | Visual model architecture |

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

You are free to use, modify, and distribute this software for any purpose, including commercial and academic use, provided attribution is maintained.
