from flask import Flask, request, jsonify
from flask_cors import CORS
import ml_model
import dl_model
from data_buffer import DataBuffer
from decision_engine import get_action
import time
import math
import os

app = Flask(__name__)
CORS(app)

sensor_buffer = DataBuffer(size=10)

latest_state = {
    "ph": 0.0,
    "tds": 0.0,
    "turbidity": 0.0,
    "temperature": 0.0,
    "classification": "Waiting for data...",
    "anomaly": False,
    "spike_probability": 0.0,
    "treatment_action": "system_off",
    "timestamp": 0
}

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    global latest_state
    
    data = request.json
    if not data or "node" not in data or data["node"] != "sensor_node":
        return jsonify({"error": "Invalid request"}), 400

    required = ["ph", "tds", "turbidity", "temperature"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing data"}), 400

    # 1. Run Machine Learning models (Anomaly + Classification)
    ml_result = ml_model.predict(
        data["ph"], data["tds"], data["turbidity"], 
        data["temperature"]
    )
    
    # 2. Update buffer and run Deep Learning model
    reading = [data["ph"], data["tds"], data["turbidity"], data["temperature"]]
    sensor_buffer.append(reading)
    
    spike_prob = 0.0
    if sensor_buffer.is_full():
        spike_prob = dl_model.predict_spike(sensor_buffer.get_buffer())
        
    # 3. Decision Engine determines the action
    action = get_action(ml_result, spike_prob)
    
    # Filter NaNs for strict JSON compliance
    s_ph = float(data["ph"])
    s_tds = float(data["tds"])
    s_turb = float(data["turbidity"])
    s_temp = float(data["temperature"])
    s_prob = float(round(spike_prob, 4))
    
    latest_state.update({
        "ph": 0.0 if math.isnan(s_ph) else s_ph,
        "tds": 0.0 if math.isnan(s_tds) else s_tds,
        "turbidity": 0.0 if math.isnan(s_turb) else s_turb,
        "temperature": 0.0 if math.isnan(s_temp) else s_temp,
        "classification": str(ml_result["status"]),
        "anomaly": bool(ml_result["anomaly"]),
        "spike_probability": 0.0 if math.isnan(s_prob) else s_prob,
        "treatment_action": str(action),
        "timestamp": float(time.time())
    })

    return jsonify({"message": "Data processed"}), 200

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_state), 200

@app.route('/actuator-command', methods=['GET'])
def actuator_command():
    return jsonify({"command": latest_state["treatment_action"]}), 200

@app.route('/feedback', methods=['POST'])
def receive_feedback():
    data = request.json
    if not data or "label" not in data:
        return jsonify({"error": "Invalid request"}), 400
    
    required = ["ph", "tds", "turbidity", "temperature", "label"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing data"}), 400
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "dataset", "verified_data.csv")
    exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a') as f:
        if not exists:
            f.write("ph,tds,turbidity,temperature,label\n")
        f.write(f"{data['ph']},{data['tds']},{data['turbidity']},{data['temperature']},{data['label']}\n")
    
    return jsonify({"message": "Feedback saved successfully"}), 200

@app.route('/retrain', methods=['POST'])
def retrain_models():
    ml_success = ml_model.retrain_classifier()
    dl_success = dl_model.retrain_lstm()
    
    if ml_success and dl_success:
        return jsonify({"message": "Models successfully retrained and hot-reloaded"}), 200
    else:
        return jsonify({"error": "Retraining failed"}), 500

if __name__ == '__main__':
    ml_model.load_models()
    dl_model.load_model()
    print("Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
