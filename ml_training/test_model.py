import joblib
import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "..", "models", "pollution_classifier.pkl")
model = joblib.load(model_path)

sample = np.array([[6.2,700,200,260,28]])

prediction = model.predict(sample)

print("Predicted class:",prediction)
