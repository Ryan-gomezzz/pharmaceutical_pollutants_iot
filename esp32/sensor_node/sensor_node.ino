/*
 * ============================================================
 *  SENSOR NODE — "The Jellyfish" IoT Probe
 * ============================================================
 *  Reads environmental sensors (pH, TDS, Turbidity, Temperature)
 *  and sends data to the Flask AI server via HTTP POST.
 *
 *  Sensors:
 *  ┌────────────────┬──────────┬───────────────────────────┐
 *  │ Sensor         │ GPIO Pin │ Read Method               │
 *  ├────────────────┼──────────┼───────────────────────────┤
 *  │ pH Probe       │ GPIO 34  │ Analog (ADC1)             │
 *  │ TDS Probe      │ GPIO 35  │ Analog (ADC1)             │
 *  │ Turbidity      │ GPIO 32  │ Analog (ADC1)             │
 *  │ DHT11 (Temp)   │ GPIO 4   │ Digital (DHT library)     │
 *  └────────────────┴──────────┴───────────────────────────┘
 *
 *  Required Libraries (install via Arduino Library Manager):
 *  - WiFi (built-in with ESP32 board package)
 *  - HTTPClient (built-in with ESP32 board package)
 *  - DHT sensor library by Adafruit
 *  - Adafruit Unified Sensor (dependency of DHT lib)
 *
 *  Board: ESP32 Dev Module (or your specific ESP32 board)
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// ─── WiFi Credentials ───────────────────────────────────────
// UPDATE THESE before uploading!
const char* WIFI_SSID     = "Ryan's iPhone";
const char* WIFI_PASSWORD = "12345678";

// ─── Server Endpoint ────────────────────────────────────────
// UPDATE THIS to your laptop/server IP address
const char* SERVER_URL = "http://172.20.10.4:5000/sensor-data";

// ─── Sensor Pin Definitions ─────────────────────────────────
// Note: Use ADC1 pins only (GPIO 32-39) since WiFi uses ADC2
#define PH_PIN        34   // Analog pH sensor
#define TDS_PIN       35   // Analog TDS sensor
#define TURBIDITY_PIN 32   // Analog turbidity sensor
#define DHT_PIN        4   // Digital DHT11 sensor

// ─── DHT Sensor Setup ───────────────────────────────────────
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

// ─── Calibration Constants ──────────────────────────────────
// Adjust these based on your specific sensor calibration
const float PH_OFFSET     = 0.0;   // pH calibration offset
const float PH_SLOPE      = 3.5;   // pH voltage-to-pH multiplier
const float TDS_FACTOR    = 0.5;   // TDS raw-to-ppm factor
const float TURB_FACTOR   = 0.1;   // Turbidity raw-to-NTU factor
const float VREF          = 3.3;   // ESP32 ADC reference voltage
const float ADC_MAX       = 4095.0; // 12-bit ADC resolution

// ─── Timing ─────────────────────────────────────────────────
const unsigned long SEND_INTERVAL = 5000; // Send data every 5 seconds
unsigned long lastSendTime = 0;

// ─── Read pH Sensor ─────────────────────────────────────────
float readPH() {
  // Take multiple readings and average for stability
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(PH_PIN);
    delay(10);
  }
  float avgRaw = sum / 10.0;
  float voltage = avgRaw * (VREF / ADC_MAX);
  float ph = voltage * PH_SLOPE + PH_OFFSET;
  return ph;
}

// ─── Read TDS Sensor ────────────────────────────────────────
float readTDS() {
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(TDS_PIN);
    delay(10);
  }
  float avgRaw = sum / 10.0;
  float tds = avgRaw * TDS_FACTOR;
  return tds;
}

// ─── Read Turbidity Sensor ──────────────────────────────────
float readTurbidity() {
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(TURBIDITY_PIN);
    delay(10);
  }
  float avgRaw = sum / 10.0;
  float turbidity = avgRaw * TURB_FACTOR;
  return turbidity;
}

// ─── Read Temperature (DHT11) ───────────────────────────────
float readTemperature() {
  float temp = dht.readTemperature(); // Celsius
  if (isnan(temp)) {
    Serial.println("[Sensor] WARNING: DHT11 read failed, using fallback 25.0°C");
    return 25.0; // Safe fallback
  }
  return temp;
}

// ─── Setup ──────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000); // Give serial monitor time to connect

  Serial.println();
  Serial.println("============================================");
  Serial.println("  Jellyfish Sensor Node — Initializing...");
  Serial.println("============================================");

  // Initialize DHT sensor
  dht.begin();
  Serial.println("[Sensor] DHT11 initialized on GPIO 4");

  // Connect to WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[Sensor] Connecting to WiFi");

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("[Sensor] Connected to WiFi!");
    Serial.print("[Sensor] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("[Sensor] ERROR: WiFi connection failed!");
    Serial.println("[Sensor] Will retry in loop...");
  }

  Serial.println("[Sensor] Server URL: " + String(SERVER_URL));
  Serial.println("[Sensor] Send interval: " + String(SEND_INTERVAL) + " ms");
  Serial.println("============================================");
  Serial.println("[Sensor] Ready! Sending telemetry...");
  Serial.println();
}

// ─── Main Loop ──────────────────────────────────────────────
void loop() {
  unsigned long currentTime = millis();

  // Non-blocking interval check
  if (currentTime - lastSendTime < SEND_INTERVAL) {
    return;
  }
  lastSendTime = currentTime;

  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[Sensor] WiFi disconnected! Reconnecting...");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(3000);
    return;
  }

  // ─── Read all sensors ───────────────────────────────────
  float ph          = readPH();
  float tds         = readTDS();
  float turbidity   = readTurbidity();
  float temperature = readTemperature();

  // ─── Build JSON payload ─────────────────────────────────
  String payload = "{";
  payload += "\"node\":\"sensor_node\",";
  payload += "\"ph\":" + String(ph, 2) + ",";
  payload += "\"tds\":" + String(tds, 2) + ",";
  payload += "\"turbidity\":" + String(turbidity, 2) + ",";
  payload += "\"temperature\":" + String(temperature, 2);
  payload += "}";

  // ─── Send HTTP POST ─────────────────────────────────────
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000); // 5 second timeout

  int httpResponseCode = http.POST(payload);

  // ─── Log results ────────────────────────────────────────
  Serial.print("[Sensor] pH=");
  Serial.print(ph, 2);
  Serial.print(" TDS=");
  Serial.print(tds, 2);
  Serial.print(" Turb=");
  Serial.print(turbidity, 2);
  Serial.print(" Temp=");
  Serial.print(temperature, 2);

  if (httpResponseCode > 0) {
    Serial.print(" → Server: HTTP ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print(" → ERROR: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
}
