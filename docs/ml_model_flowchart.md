# Machine Learning AI Engine - Working Diagram & Explanation

This document provides a comprehensive overview of the intelligent monitoring system built into the Smart Pollution Dashboard. The pipeline merges deterministic rule engines, traditional Machine Learning (Random Forests), and Deep Learning (LSTM) to evaluate telemetry data in real-time.

## Data Processing Flowchart

```mermaid
flowchart TD
    %% Define Styles
    classDef input fill:#2563eb,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef baseline fill:#059669,stroke:#047857,stroke-width:2px,color:#fff
    classDef rule fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff
    classDef ml fill:#7c3aed,stroke:#5b21b6,stroke-width:2px,color:#fff
    classDef dl fill:#db2777,stroke:#be185d,stroke-width:2px,color:#fff
    classDef output fill:#475569,stroke:#334155,stroke-width:2px,color:#fff

    A[Incoming Raw IoT Data<br/>pH, TDS, Turb, Temp]:::input --> B{Baseline Calibration<br/>Active?}:::baseline
    
    B -- Yes --> C[Calculate Deviation Deltas<br/>ΔpH, ΔTDS, ΔTurb]:::baseline
    B -- No --> D[Use Absolute Values]:::baseline
    
    C --> E{Rule-Based Thresholds<br/>Turb > 100, TDS > 250, pH > 1.5}:::rule
    D --> E
    
    E -- Triggers --> F[Set System Contamination Alert = TRUE]:::output
    E -- Nominal --> G[Random Forest Classifier<br/>predict(pH, TDS, Turb, Temp)]:::ml
    F --> G
    
    G --> H{Is result Anomaly (Class 3)?}:::ml
    
    H -- No --> I{Cluster Deviation Check<br/>ΔTDS > 150 & ΔpH < -0.5?}:::ml
    
    I -- Yes --> J[Override: Pharma Contamination Vector]:::ml
    I -- No --> K[Assign Class:<br/>0: Normal, 1: Packaging, 2: Antibiotic]:::ml
    
    H -- Yes --> L[Flag as Hardware Fault / Severe Anomaly]:::ml
    J --> L
    
    G --> M[Append to Sliding Data Buffer<br/>n = 10]:::input
    
    M --> N[LSTM Deep Learning Net<br/>Time-Series Sequence]:::dl
    N --> O[Predict Future Turbidity]:::dl
    O --> P[Calculate Forecast Spike Prob %]:::dl
    
    K --> Q((Decision Engine<br/>Actuator Logic)):::output
    L --> Q
    P --> Q
    
    Q --> R[Trigger: System Offline,<br/>Electrolysis, UV, or Pumping]:::output
```

## Step-by-Step Explanation

### 1. Data Ingestion & Baseline Anchoring
When raw telemetry arrives from the ESP32 array, the system first checks if a "Baseline Calibration" exists. The baseline acts as the 'ground truth' for normal water. 
If calibrated, the system calculates the **deltas (Δ)**—the exact deviation from normal for every parameter.

### 2. Rule-Based Environmental Override
Before the complex AI evaluates the data, the calculated deltas hit a hardcoded rule engine. If the deviations breach extreme tolerances (e.g., Turbidity swinging more than 100 NTU, or TDS swinging by 250 ppm), the system forcibly throws a `Contamination Alert`. By using large error control margins, this layer filters out false positives caused by natural environmental noise (like ambient sunlight refracting off the turbidity sensor).

### 3. Machine Learning Classification (Random Forest)
The data array (pH, TDS, Turbidity, Temperature) is fed into the loaded `pollution_classifier.pkl` module. 
The **Random Forest** algorithm runs the telemetry through an ensemble of decision trees to predict the chemical signature.
- **Class 0:** Normal Water
- **Class 1:** Packaging Residue (Plastic/Micro-waste profiles)
- **Class 2:** Antibiotic Contamination
- **Class 3:** Anomaly (Out of known bounds)

**Vector Override (Cluster Analysis):**
If the baseline is active, a secondary cluster-check runs. It knows that a massive TDS shift coupled with a sharp drop in pH—while turbidity remains low—is the classic signature of pharmaceutical dumping. If this vector is detected, the AI overrides standard classification to tag it as a "Pharma Contamination Vector".

### 4. Deep Learning Spike Prediction (LSTM)
Simultaneously, the last 10 readings are flushed into a sliding window array and fed to the `lstm_model.keras` module.
The **Long Short-Term Memory (LSTM)** neural network analyzes the *time-series momentum* of the data rather than just the current frame. It is trying to predict where the turbidity and TDS will be 1 minute from now. The output translates into a **Spike Risk Percentage**.

### 5. Final Hardware Actuation (Decision Engine)
The results from the ML Classifier and DL Forecaster converge at the Decision Engine. It uses a strict precedence order to trigger the physical response nodes:
- If a future Spike > 80% is predicted -> Trigger **Heavy Pre-treatment**.
- If Antibiotic or Pharma Contaminants found -> Trigger **Electrolysis Electrodes**.
- If Packaging Residue found -> Trigger **UV LED Module**.
- If extreme Anomaly -> Trigger **System Offline Lockout** to prevent damage.
- Else -> Route water to standard clean pumping.
