#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:5000/actuator-command"; // Replace with your laptop IP

#define PUMP_PIN 22
#define UV_LED_PIN 21
#define ELECTRODE_PIN 19
#define RELAY_MAIN_PIN 23

String currentAction = "system_off";

void turnOffAll() {
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(UV_LED_PIN, LOW);
  digitalWrite(ELECTRODE_PIN, LOW);
  digitalWrite(RELAY_MAIN_PIN, LOW);
}

void setup() {
  Serial.begin(115200);
  
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(UV_LED_PIN, OUTPUT);
  pinMode(ELECTRODE_PIN, OUTPUT);
  pinMode(RELAY_MAIN_PIN, OUTPUT);
  
  turnOffAll();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\nActuator Node Connected!");
}

void processCommand(String command) {
  if (command == currentAction) return;
  
  Serial.print("Executing new command: ");
  Serial.println(command);
  
  currentAction = command;
  turnOffAll();
  
  if (command == "pump_on") {
    digitalWrite(PUMP_PIN, HIGH);
  } else if (command == "uv_led_on") {
    digitalWrite(UV_LED_PIN, HIGH);
  } else if (command == "electrolysis_on") {
    digitalWrite(ELECTRODE_PIN, HIGH);
  } else if (command == "pump_and_pretreat") {
    digitalWrite(PUMP_PIN, HIGH);
    digitalWrite(RELAY_MAIN_PIN, HIGH);
  } else if (command == "system_off") {
    // All turned off
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
        Serial.print("JSON Parse Error: ");
        Serial.println(error.c_str());
      }
    }
    http.end();
  }
  delay(3000); // Poll every 3 seconds
}
