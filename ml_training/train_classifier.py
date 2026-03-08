import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "..", "dataset", "pollution_data.csv")
data = pd.read_csv(csv_path)

X = data[['ph','tds','turbidity','orp','temperature']]
y = data['label']

X_train, X_test, y_train, y_test = train_test_split(
    X,y,test_size=0.2,random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train,y_train)

pred = model.predict(X_test)

print(classification_report(y_test,pred))

models_dir = os.path.join(base_dir, "..", "models")
os.makedirs(models_dir, exist_ok=True)
model_path = os.path.join(models_dir, "pollution_classifier.pkl")
joblib.dump(model, model_path)

print("Model saved to models folder")
