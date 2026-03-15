import math
import random
import time

# Simulation Base Location (e.g., a central point in an Indian city context, like Bengaluru lakes)
BASE_LAT = 12.9716
BASE_LNG = 77.5946
RADIUS_KM = 5.0 # hubs spread within 5km

class HubNetworkSimulation:
    def __init__(self, num_hubs=15):
        self.hubs = []
        self.active_simulation = False
        self.sim_start_time = 0
        self.sim_duration = 120 # simulated event lasts 2 minutes
        
        # Generate random hubs around the base location
        for i in range(num_hubs):
            # Random distance and angle
            r = RADIUS_KM * math.sqrt(random.random()) / 111.32 # rough conversion to degrees
            theta = random.random() * 2 * math.pi
            
            lat = BASE_LAT + r * math.cos(theta)
            lng = BASE_LNG + r * math.sin(theta)
            
            self.hubs.append({
                "id": f"HUB-{100+i}",
                "lat": round(lat, 5),
                "lng": round(lng, 5),
                "status": "normal",
                "deviation_intensity": 0.0 # 0.0 to 1.0 (1.0 being extreme contamination)
            })

    def trigger_simulation(self):
        """Forces a cluster of hubs to detect contamination for demonstration."""
        self.active_simulation = True
        self.sim_start_time = time.time()
        
        # Pick a random epicenter from existing hubs to look realistic
        epicenter = random.choice(self.hubs)
        epi_lat, epi_lng = epicenter["lat"], epicenter["lng"]
        
        for hub in self.hubs:
            # Calculate distance to epicenter
            dist = math.sqrt((hub["lat"] - epi_lat)**2 + (hub["lng"] - epi_lng)**2) * 111.32 # rough km
            
            if dist < 2.0: # within 2km, high chance of contamination
                intensity = max(0.2, 1.0 - (dist / 2.0)) # closer = higher intensity
                intensity = round(intensity * random.uniform(0.8, 1.2), 2)
                if intensity > 1.0: intensity = 1.0
                
                hub["status"] = "alert"
                hub["deviation_intensity"] = intensity
            else:
                hub["status"] = "normal"
                hub["deviation_intensity"] = 0.0
                
        return {"message": "Simulation triggered", "epicenter_roughly": {"lat": epi_lat, "lng": epi_lng}}

    def update_simulation_state(self, current_latest_state):
        """
        Updates the simulated status based on time or real sensor input.
        If real sensor is alerting, ensure HUB-100 (which we pretend is the real one) matches.
        """
        if self.active_simulation and time.time() - self.sim_start_time > self.sim_duration:
            self.active_simulation = False
            for hub in self.hubs:
                hub["status"] = "normal"
                hub["deviation_intensity"] = 0.0
                
        # Link the real sensor's state to HUB-100 to bridge simulation and reality
        if current_latest_state.get("contamination_alert", False):
            self.hubs[0]["status"] = "alert"
            # Fake an intensity based on the spike probability
            self.hubs[0]["deviation_intensity"] = max(0.5, current_latest_state.get("spike_probability", 0.0))
        elif not self.active_simulation:
             self.hubs[0]["status"] = "normal"
             self.hubs[0]["deviation_intensity"] = 0.0

    def calculate_severity(self, active_alert=False, max_intensity=0.0):
        if not active_alert and max_intensity == 0:
            return "Normal"
            
        if max_intensity > 0.8: return "Severe"
        if max_intensity > 0.5: return "Moderate"
        return "Low"

    def get_indian_governance_actions(self, severity, pollutant_type):
        """Maps contamination severity to Indian regulatory frameworks."""
        if severity == "Normal":
            return []
            
        actions = []
        is_pharma = "Pharma" in pollutant_type or "Antibiotic" in pollutant_type
        
        if severity == "Low":
            actions = [
                "Log event in National Water Quality Monitoring Programme (NWMP) database",
                "Increase localized sensor polling frequency",
                "Notify Regional Monitoring Authority"
            ]
        elif severity == "Moderate":
            actions = [
                "Issue automated alert to State Pollution Control Board (SPCB)",
                "Deploy drone sampling near triangulated source",
                "Flag commercial/industrial zones within 2km radius"
            ]
            if is_pharma:
                actions.append("Cross-reference recent local pharmaceutical manufacturing discharges")
        elif severity == "Severe":
            actions = [
                "TRIGGER: Environmental Incident Level 1 Alert",
                "Notify Central Pollution Control Board (CPCB) Headquarters",
                "Dispatch SPCB field sampling units to estimated coordinates",
                "Initiate emergency containment protocols for downstream water intakes"
            ]
            if is_pharma:
                 actions.append("Mandate immediate compliance audit of nearby API (Active Pharmaceutical Ingredient) clusters")
                 
        return actions

    def estimate_source(self):
        """
        Triangulates (weighted average) the pollution source based on alerting hubs.
        Returns None if < 3 hubs are alerting.
        """
        alerting_hubs = [h for h in self.hubs if h["status"] == "alert"]
        
        if len(alerting_hubs) < 3:
            return None
            
        total_weight = sum([h["deviation_intensity"] for h in alerting_hubs])
        if total_weight == 0: return None
        
        est_lat = sum([h["lat"] * h["deviation_intensity"] for h in alerting_hubs]) / total_weight
        est_lng = sum([h["lng"] * h["deviation_intensity"] for h in alerting_hubs]) / total_weight
        
        return {
            "lat": round(est_lat, 5),
            "lng": round(est_lng, 5),
            "confidence": min(95.0, round((len(alerting_hubs) / 5) * 80 + (total_weight / len(alerting_hubs)) * 20, 1)),
            "radius_km": round(2.0 * (1.1 - (total_weight / len(alerting_hubs))), 2) # Higher average intensity = tighter radius estimation
        }

    def get_gov_status(self, current_latest_state):
        self.update_simulation_state(current_latest_state)
        
        alerting_hubs = [h for h in self.hubs if h["status"] == "alert"]
        max_intensity = max([h["deviation_intensity"] for h in alerting_hubs]) if alerting_hubs else 0.0
        
        # Override with real sensor if heavily anomalous
        real_alert = current_latest_state.get("contamination_alert", False)
        if real_alert and max_intensity < 0.5:
             max_intensity = 0.5
             
        severity = self.calculate_severity(real_alert or len(alerting_hubs) > 0, max_intensity)
        estimated_source = self.estimate_source()
        
        # Determine classification to pass to governance rules
        pollutant = current_latest_state.get("classification", "Unknown")
        actions = self.get_indian_governance_actions(severity, pollutant)
        
        return {
            "active_alert": real_alert or len(alerting_hubs) > 0,
            "severity": severity,
            "pollutant_category": pollutant,
            "recommended_actions": actions,
            "hubs": self.hubs,
            "estimated_source": estimated_source,
            "sim_active": self.active_simulation
        }
