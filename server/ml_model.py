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

def retrain_classifier():
    global rf_model
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    
    base_dir = os.path.dirname(__file__)
    main_csv = os.path.join(base_dir, "..", "dataset", "pollution_data.csv")
    verified_csv = os.path.join(base_dir, "..", "dataset", "verified_data.csv")
    
    try:
        data = pd.read_csv(main_csv)
        if os.path.exists(verified_csv):
            new_data = pd.read_csv(verified_csv)
            data = pd.concat([data, new_data], ignore_index=True)
            
        X = data[['ph','tds','turbidity','temperature']]
        y = data['label']
        
        # Retrain online
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        rf_path = os.path.join(base_dir, "..", "models", "pollution_classifier.pkl")
        joblib.dump(model, rf_path)
        
        rf_model = model
        print("ML Model retrained and hot-swapped successfully.")
        return True
    except Exception as e:
        print(f"Error retraining ML model: {e}")
        return False
