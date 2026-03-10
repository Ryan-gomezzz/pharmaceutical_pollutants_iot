import numpy as np
import pandas as pd
import random
import os

samples = 10000

data = []

# Ensure directories exist
base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(base_dir, "..", "dataset")
models_dir = os.path.join(base_dir, "..", "models")
os.makedirs(dataset_dir, exist_ok=True)
os.makedirs(models_dir, exist_ok=True)

for i in range(samples):
    
    # Class distribution: 
    # Normal Water -> 60% (0)
    # Packaging Pollution -> 25% (1)
    # Antibiotic Contamination -> 15% (2)
    # (Minus ~5% for anomalies which will override these based on a random roll)
    
    rand_val = random.random()
    if rand_val < 0.05:
        label = 3 # Anomaly
    else:
        label_rand = random.random()
        # Remaining 95%: divide into 60/25/15 ratio
        # normalized ratios: 0.60/0.95 = 0.631, 0.25/0.95 = 0.263, 0.15/0.95 = 0.158
        if label_rand < 0.631:
            label = 0
        elif label_rand < 0.894: # 0.631 + 0.263
            label = 1
        else:
            label = 2

    # Simulate slow sensor drift (small offset on top of base values)
    ph_drift = np.random.normal(0, 0.05)
    tds_drift = np.random.normal(0, 5)
    turbidity_drift = np.random.normal(0, 2)
    temp_drift = np.random.normal(0, 0.2)

    if label == 0:  # Normal water
        ph = np.random.uniform(6.5,7.5) + np.random.normal(0,0.1) + ph_drift
        tds = np.random.uniform(200,400) + np.random.normal(0,10) + tds_drift
        turbidity = np.random.uniform(0,50) + np.random.normal(0,5) + turbidity_drift
        temp = np.random.uniform(25,30) + np.random.normal(0,0.5) + temp_drift

    elif label == 1:  # Packaging pollution
        ph = np.random.uniform(6.0,7.0) + np.random.normal(0,0.1) + ph_drift
        tds = np.random.uniform(450,900) + np.random.normal(0,10) + tds_drift
        turbidity = np.random.uniform(80,300) + np.random.normal(0,5) + turbidity_drift
        temp = np.random.uniform(25,32) + np.random.normal(0,0.5) + temp_drift

    elif label == 2:  # Antibiotic contamination
        ph = np.random.uniform(5.5,6.5) + np.random.normal(0,0.1) + ph_drift
        tds = np.random.uniform(350,600) + np.random.normal(0,10) + tds_drift
        turbidity = np.random.uniform(40,120) + np.random.normal(0,5) + turbidity_drift
        temp = np.random.uniform(25,30) + np.random.normal(0,0.5) + temp_drift
        
    else: # Anomaly
        ph = np.random.uniform(4,9) + np.random.normal(0,0.1) + ph_drift
        tds = np.random.uniform(100,1200) + np.random.normal(0,10) + tds_drift
        turbidity = np.random.uniform(0,500) + np.random.normal(0,5) + turbidity_drift
        temp = np.random.uniform(20,35) + np.random.normal(0,0.5) + temp_drift

    data.append([ph,tds,turbidity,temp,label])

df = pd.DataFrame(data, columns=[
    "ph",
    "tds",
    "turbidity",
    "temperature",
    "label"
])

csv_path = os.path.join(dataset_dir, "pollution_data.csv")
df.to_csv(csv_path, index=False)

print("Dataset created with 10,000 samples")
