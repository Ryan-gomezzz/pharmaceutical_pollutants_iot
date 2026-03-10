import joblib
import os
import numpy as np

rf_model = None

def load_models():
    global rf_model
    base_dir = os.path.dirname(__file__)
    
    # Updated to point to new models/ absolute folder schema 
    rf_path = os.path.join(base_dir, "..", "models", "pollution_classifier.pkl")
    
    if os.path.exists(rf_path):
        rf_model = joblib.load(rf_path)
        print("ML Model (pollution_classifier.pkl) loaded successfully.")
    else:
        print(f"Warning: ML model not found at {rf_path}. Run training scripts first.")

def predict(ph, tds, turbidity, temperature):
    if rf_model is None:
        load_models()
        if rf_model is None:
            return {"anomaly": False, "label": -1, "status": "Model not loaded"}
            
    features = np.array([[ph, tds, turbidity, temperature]])
        
    class_pred = rf_model.predict(features)[0]
    classes = {0: "Normal Water", 1: "Packaging Residue", 2: "Antibiotic Contamination", 3: "Anomaly"}
    
    return {"anomaly": class_pred == 3, "label": int(class_pred), "status": classes.get(int(class_pred), "Unknown")}
