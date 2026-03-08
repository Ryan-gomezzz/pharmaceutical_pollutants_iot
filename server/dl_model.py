import os
import numpy as np
import tensorflow as tf
import joblib

model = None
scaler = None

def load_model():
    global model, scaler
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "..", "models", "lstm_model.h5")
    scaler_path = os.path.join(base_dir, "..", "models", "scaler.pkl")
    
    if os.path.exists(model_path):
        tf.get_logger().setLevel('ERROR')
        model = tf.keras.models.load_model(model_path)
        print("DL Model (lstm_model.h5) loaded successfully.")
    else:
        print(f"Warning: DL model not found at {model_path}.")
        
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
    else:
        print(f"Warning: Scaler not found at {scaler_path}.")

def predict_spike(raw_buffer):
    """ raw_buffer has length 10, features list """
    if model is None or scaler is None:
        load_model()
        if model is None or scaler is None:
            return 0.0

    if len(raw_buffer) < 10:
        return 0.0
        
    # User's training mapped: 
    # data[['ph','tds','turbidity','orp','temperature']].values
    # features = scaler.fit_transform(features)
    # Then y.append(features[i+sequence_length][2]) # Predict turbidity
    
    scaled_features = scaler.transform(raw_buffer)
    input_data = np.array([scaled_features[-10:]])
    prediction = model.predict(input_data, verbose=0)
    
    # Reversing transformation for the predicted turbidity value (index 2)
    # Our prediction is outputted functionally from loss=mse, we can inverse scale it
    # But usually a spike probability is requested. We use MSE scalar output here
    turbidity_pred_scaled = prediction[0][0]
    
    # We create a dummy array to inverse transform just the turbidity
    dummy = np.zeros((1, 5))
    dummy[0][2] = turbidity_pred_scaled
    pred_real = scaler.inverse_transform(dummy)[0][2]
    
    # Spike probability translation: turbidity > 100 is typically a spike in synthetic data
    # (Sigmoid output can be pseudo-extrapolated. We map it out of 200 NTU for probabilty approx)
    prob = float(pred_real / 200.0) 
    if prob < 0: prob = 0.0
    if prob > 1: prob = 1.0
    
    return float(prob)
