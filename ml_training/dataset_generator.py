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

    label = random.choice([0,1,2])

    if label == 0:  # Normal water
        ph = np.random.uniform(6.5,7.5)
        tds = np.random.uniform(200,400)
        turbidity = np.random.uniform(0,50)
        orp = np.random.uniform(300,400)
        temp = np.random.uniform(25,30)

    elif label == 1:  # Packaging pollution
        ph = np.random.uniform(6.0,7.0)
        tds = np.random.uniform(500,900)
        turbidity = np.random.uniform(100,300)
        orp = np.random.uniform(250,350)
        temp = np.random.uniform(25,32)

    else:  # Antibiotic contamination
        ph = np.random.uniform(5.5,6.5)
        tds = np.random.uniform(350,600)
        turbidity = np.random.uniform(50,120)
        orp = np.random.uniform(150,300)
        temp = np.random.uniform(25,30)

    data.append([ph,tds,turbidity,orp,temp,label])

df = pd.DataFrame(data, columns=[
    "ph",
    "tds",
    "turbidity",
    "orp",
    "temperature",
    "label"
])

csv_path = os.path.join(dataset_dir, "pollution_data.csv")
df.to_csv(csv_path, index=False)

print("Dataset created with 10,000 samples")
