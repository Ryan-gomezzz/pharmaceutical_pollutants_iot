import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "..", "dataset", "pollution_data.csv")
data = pd.read_csv(csv_path)

features = data[['ph','tds','turbidity','temperature']].values

scaler = MinMaxScaler()
features = scaler.fit_transform(features)

# Save the scaler so the inference engine can use it
models_dir = os.path.join(base_dir, "..", "models")
os.makedirs(models_dir, exist_ok=True)
scaler_path = os.path.join(models_dir, "scaler.pkl")
joblib.dump(scaler, scaler_path)

sequence_length = 10

X = []
y = []

for i in range(len(features)-sequence_length):
    X.append(features[i:i+sequence_length])
    y.append(features[i+sequence_length][2])  # predict turbidity

X = np.array(X)
y = np.array(y)

model = Sequential()

model.add(LSTM(64,input_shape=(sequence_length,4)))
model.add(Dense(32,activation='relu'))
model.add(Dense(1))

model.compile(
    optimizer='adam',
    loss='mse'
)

model.fit(
    X,y,
    epochs=10,
    batch_size=32
)

model_path = os.path.join(models_dir, "lstm_model.keras")
model.save(model_path)

print("LSTM model saved")
