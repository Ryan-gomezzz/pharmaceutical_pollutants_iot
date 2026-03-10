# SensiFluid Dashboard - UI/UX Documentation

The SensiFluid Dashboard has been upgraded into a modern, responsive Single Page Application (SPA). This document outlines the purpose and functionality of each navigational tab within the interface.

## 1. 📊 Dashboard (Real-time Analytics)
**Purpose:** The primary command center. Provides an instant, high-level overview of the entire system's current status based on the latest telemetry stream.
- **Top Row (AI Intelligence):** Displays the current Random Forest classification (Normal/Packaging/Antibiotic), the Decision Engine's active counter-measure, and the LSTM's live prediction of an impending spike.
- **Middle Row (Telemetry):** Raw hardware numerical outputs from the ESP32 (pH, TDS, Turbidity, Temperature).
- **Bottom Row (Trends):** Two dynamic Chart.js canvas elements plotting the last 30 inferences of Turbidity and TDS over a rolling time window to visualize temporal trends.

## 2. 🖧 Nodes (Hardware Fleet Topology)
**Purpose:** Network monitoring for the physical edge devices.
- Displays a data table of all connected microcontrollers.
- **Node ID & Type:** Differentiates between Sensor nodes ("Jellyfish") and the downstream Actuator nodes.
- **Status & Uptime:** Visual badges indicate if a node is actively broadcasting telemetry or if it has dropped offline.
- **IP Address:** Lists the routing address for each specific piece of hardware.

## 3. ⚡ Actuation (Actuator Control Panel & Ruleset)
**Purpose:** Maps the AI outputs directly to physical world machinery.
- **Control Panel:** Displays visual toggle switches representing the physical relays wired to the Actuator ESP32. As the AI backend changes treatments (e.g. from "Standard Pump" to "Electrolysis"), these switches automatically toggle in the UI to reflect the live hardware state.
- **Ruleset Legend:** A quick-reference guide explaining the programmed logic of the Python Decision Engine (e.g. why a specific contamination triggers a specific UV or Electrolysis relay).

## 4. 🧠 AI Models (Inference Profiling)
**Purpose:** Profiles the underlying mathematical models currently hot-loaded by the Python Flask backend.
- Displays three cards detailing the architecture of the AI pipeline.
- Explains the role and algorithm type of the Isolation Forest (Anomaly Detection), Random Forest (Classification), and LSTM Neural Net (Prediction).
- Lists the exact `.pkl` and `.h5` file names the server is currently executing against.

## 5. ⚙️ Settings (System Configuration)
**Purpose:** Environment configuration and variable management.
- Currently displays read-only backend parameters essential to the system's operation, such as the REST API fetch URL, polling interval rates, and the critical probability threshold integer that triggers heavy pre-treatment.

## 💾 Export Report Functionality
- The "Export Report" button in the top right header is globally accessible across all tabs.
- The Javascript layer quietly banks up to the last 500 telemetry reads and AI decisions into memory.
- Clicking the button instantly renders this array into a formatted `.csv` file and triggers a local browser download, allowing for immediate post-incident analysis in Excel or Pandas.
