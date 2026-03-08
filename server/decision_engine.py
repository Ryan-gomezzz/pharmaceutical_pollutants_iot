def get_action(ml_result, spike_probability):
    action = "system_off"
    
    if ml_result["label"] == -1 and not ml_result["anomaly"]:
        return action
        
    # If anomaly detected, turn system off to avoid damage
    if ml_result["anomaly"]:
        return "system_off" 
        
    pollution_type = ml_result["label"]
    
    # Preemptive treatment if spike is highly probable
    if spike_probability > 0.8:
        action = "pump_and_pretreat"
    elif pollution_type == 2: # Antibiotic
        action = "electrolysis_on"
    elif pollution_type == 1: # Packaging
        action = "uv_led_on"
    elif pollution_type == 0: # Normal 
        action = "pump_on"
        
    return action
