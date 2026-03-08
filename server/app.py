from flask import Flask, request, jsonify
from flask_cors import CORS
import ml_model
import dl_model
from data_buffer import DataBuffer
from decision_engine import get_action
import time

app = Flask(__name__)
CORS(app)

sensor_buffer = DataBuffer(size=10)

latest_state = {
    "ph": 0.0,
    "tds": 0.0,
    "turbidity": 0.0,
    "orp": 0.0,
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

    required = ["ph", "tds", "turbidity", "orp", "temperature"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing data"}), 400

    # 1. Run Machine Learning models (Anomaly + Classification)
    ml_result = ml_model.predict(
        data["ph"], data["tds"], data["turbidity"], 
        data["orp"], data["temperature"]
    )
    
    # 2. Update buffer and run Deep Learning model
    reading = [data["ph"], data["tds"], data["turbidity"], data["orp"], data["temperature"]]
    sensor_buffer.append(reading)
    
    spike_prob = 0.0
    if sensor_buffer.is_full():
        spike_prob = dl_model.predict_spike(sensor_buffer.get_buffer())
        
    # 3. Decision Engine determines the action
    action = get_action(ml_result, spike_prob)
    
    # 4. Update the global state
    latest_state.update({
        "ph": data["ph"],
        "tds": data["tds"],
        "turbidity": data["turbidity"],
        "orp": data["orp"],
        "temperature": data["temperature"],
        "classification": ml_result["status"],
        "anomaly": ml_result["anomaly"],
        "spike_probability": round(spike_prob, 4),
        "treatment_action": action,
        "timestamp": time.time()
    })

    return jsonify({"message": "Data processed"}), 200

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_state), 200

@app.route('/actuator-command', methods=['GET'])
def actuator_command():
    return jsonify({"command": latest_state["treatment_action"]}), 200

if __name__ == '__main__':
    ml_model.load_models()
    dl_model.load_model()
    print("Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
