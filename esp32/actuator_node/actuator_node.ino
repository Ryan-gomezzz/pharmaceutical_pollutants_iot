/*
 * ============================================================
 *  ACTUATOR NODE — 4-LED Pollution Cluster Indicator
 * ============================================================
 *  This ESP32 polls the Flask server for the latest actuation
 *  command and lights up the corresponding LED to show which
 *  pollution treatment cluster is currently active.
 *
 *  LED Mapping (matches Decision Engine output):
 *  ┌─────────────────────┬───────┬────────┬──────┐
 *  │ Server Command      │ LED # │ Color  │ GPIO │
 *  ├─────────────────────┼───────┼────────┼──────┤
 *  │ pump_on             │  1    │ GREEN  │  22  │  → Normal Water
 *  │ uv_led_on           │  2    │ BLUE   │  21  │  → Packaging Residue
 *  │ electrolysis_on     │  3    │ YELLOW │  19  │  → Antibiotic Contamination
 *  │ pump_and_pretreat   │  4    │ RED    │  23  │  → High Spike Risk
 *  │ system_off          │ ALL   │  OFF   │  --  │  → Anomaly / Idle
 *  └─────────────────────┴───────┴────────┴──────┘
 *
 *  Hardware: Connect each LED's anode to the GPIO pin through
 *  a 220Ω resistor, cathode to GND.
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ─── WiFi Credentials ───────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ─── Server Endpoint ────────────────────────────────────────
const char* SERVER_URL = "http://192.168.1.100:5000/actuator-command"; // Replace with your laptop IP

// ─── LED GPIO Pin Definitions ───────────────────────────────
#define LED_GREEN   22   // Normal Water          → pump_on
#define LED_BLUE    21   // Packaging Residue      → uv_led_on
#define LED_YELLOW  19   // Antibiotic Contamination → electrolysis_on
#define LED_RED     23   // High Spike Risk        → pump_and_pretreat

String currentAction = "system_off";

// ─── Turn all LEDs OFF ──────────────────────────────────────
void turnOffAll() {
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
}

// ─── Boot-up LED test: flash all LEDs in sequence ───────────
void startupFlash() {
  int leds[] = { LED_GREEN, LED_BLUE, LED_YELLOW, LED_RED };
  for (int i = 0; i < 4; i++) {
    digitalWrite(leds[i], HIGH);
    delay(200);
    digitalWrite(leds[i], LOW);
  }
  // Quick all-on flash
  for (int i = 0; i < 4; i++) digitalWrite(leds[i], HIGH);
  delay(300);
  turnOffAll();
}

void setup() {
  Serial.begin(115200);

  // Configure all LED pins as outputs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  turnOffAll();

  // Visual startup self-test
  startupFlash();

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[Actuator] Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("[Actuator] Connected! IP: " + WiFi.localIP().toString());
  Serial.println("[Actuator] 4-LED Cluster Indicator Ready.");
  Serial.println("  GPIO 22 = GREEN  (Normal Water)");
  Serial.println("  GPIO 21 = BLUE   (Packaging Residue)");
  Serial.println("  GPIO 19 = YELLOW (Antibiotic Contamination)");
  Serial.println("  GPIO 23 = RED    (High Spike Risk)");
}

// ─── Process server command and activate the right LED ──────
void processCommand(String command) {
  if (command == currentAction) return; // No change

  Serial.print("[Actuator] New cluster command: ");
  Serial.println(command);

  currentAction = command;
  turnOffAll();

  if (command == "pump_on") {
    // Cluster: Normal Water → GREEN LED
    digitalWrite(LED_GREEN, HIGH);
    Serial.println("  >> GREEN LED ON  — Normal Water (Standard Pump)");

  } else if (command == "uv_led_on") {
    // Cluster: Packaging Residue → BLUE LED
    digitalWrite(LED_BLUE, HIGH);
    Serial.println("  >> BLUE LED ON   — Packaging Residue (UV Treatment)");

  } else if (command == "electrolysis_on") {
    // Cluster: Antibiotic Contamination → YELLOW LED
    digitalWrite(LED_YELLOW, HIGH);
    Serial.println("  >> YELLOW LED ON — Antibiotic Contamination (Electrolysis)");

  } else if (command == "pump_and_pretreat") {
    // Cluster: High Spike Risk → RED LED
    digitalWrite(LED_RED, HIGH);
    Serial.println("  >> RED LED ON    — High Spike Risk (Heavy Pre-treatment)");

  } else if (command == "system_off") {
    // All LEDs already turned off above
    Serial.println("  >> ALL LEDs OFF  — System Idle / Anomaly Lock");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();

      StaticJsonDocument<256> doc;
      DeserializationError error = deserializeJson(doc, response);

      if (!error) {
        const char* cmd = doc["command"];
        if (cmd) {
          processCommand(String(cmd));
        }
      } else {
        Serial.print("[Actuator] JSON Parse Error: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("[Actuator] HTTP Error: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("[Actuator] WiFi Disconnected! Reconnecting...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(3000);
  }

  delay(3000); // Poll every 3 seconds
}
