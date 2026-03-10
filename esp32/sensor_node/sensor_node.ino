#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:5000/sensor-data"; // Replace with your laptop IP

#define PH_PIN 34
#define TDS_PIN 35
#define TURBIDITY_PIN 32
#define TEMP_PIN 4

#define DHTTYPE DHT11
DHT dht(TEMP_PIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\nSensor Node Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  
  dht.begin();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    float ph = analogRead(PH_PIN) * (3.3 / 4095.0) * 3.5; 
    float tds = analogRead(TDS_PIN) * 0.5;
    float turbidity = analogRead(TURBIDITY_PIN) * 0.1;
    
    float temperature = dht.readTemperature();
    if (isnan(temperature)) {
      Serial.println("Failed to read from DHT sensor!");
      temperature = 0.0; // Fallback
    }

    String payload = "{";
    payload += "\"node\": \"sensor_node\",";
    payload += "\"ph\":" + String(ph) + ",";
    payload += "\"tds\":" + String(tds) + ",";
    payload += "\"turbidity\":" + String(turbidity) + ",";
    payload += "\"temperature\":" + String(temperature);
    payload += "}";

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(payload);
    Serial.print("Data sent: ");
    Serial.println(payload);
    Serial.println(httpResponseCode);
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected!");
  }
  
  delay(5000); 
}
