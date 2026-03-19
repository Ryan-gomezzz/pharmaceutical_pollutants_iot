# Changelog

All notable changes to AquaIntel are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2025

### Added

**Core System**
- Dual ESP32 node architecture: Jellyfish Sensor Node + downstream Actuator Node
- Flask REST API backend (`server/app.py`) with full CORS support
- Exponential Moving Average (EMA) filter for real-time sensor smoothing
- 20-reading baseline calibration system for anomaly deviation detection
- Node registry tracking connection status, IP addresses, and read counts

**Machine Learning**
- Random Forest classifier (100 trees, 4-class pharmaceutical pollution taxonomy)
- LSTM deep learning model (64 units, 10-step sliding window) for spike prediction
- MinMax scaler pipeline for LSTM feature normalization
- Continuous learning endpoint: human ground truth labels expand training set
- Hot-reload model endpoint: models retrain and reload without server restart
- Synthetic 10,000-sample dataset generator with Gaussian noise and sensor drift

**Decision Engine**
- AI-to-action mapping: 5 treatment states (pump, UV, electrolysis, pretreat, system_off)
- Spike probability threshold triggering (default: 80%)
- Manual override system for human operator takeover

**Dashboard (AquaIntel)**
- Single-page application with 6 views: Dashboard, Nodes, Actuation, Gov Coordination, AI Models, Settings
- Real-time Chart.js visualizations: turbidity, TDS, pH, temperature, spike probability, class pie chart
- Leaflet map with 25 simulated regional monitoring hubs (Bengaluru default)
- Pollution source triangulation from hub cluster centroids
- Indian regulatory framework workflow (NWMP, SPCB, CPCB) with severity-tiered escalation
- Dark/light theme system with localStorage persistence
- CSV telemetry export with full session data
- Contamination alert banner with blinking indicator
- Baseline calibration progress UI
- Mobile-responsive layout (bottom nav bar on small screens)

**Documentation**
- System architecture overview
- ML pipeline training guide
- Hardware setup with wiring diagrams and power calculations
- Deployment guide
- Dashboard user guide
- Results analysis (clean and noisy conditions)
- ML model flowchart

**Open Source**
- MIT License
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- CITATION.cff for academic use
- .gitignore (excludes model artifacts and dataset — regenerate locally)
- GitHub issue templates (bug report, feature request)
- GitHub pull request template

---

## [Unreleased]

### Planned
- MQTT transport layer (replacing HTTP polling for lower latency)
- Docker Compose deployment for Flask server
- Support for additional sensors: nitrates, heavy metals, dissolved oxygen
- EU Water Framework Directive (WFD) governance module
- US EPA regulatory integration
- Mobile companion app for field operators
