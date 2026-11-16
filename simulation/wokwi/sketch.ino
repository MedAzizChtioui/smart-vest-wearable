// Smart Vest (Profil B : sport collectif) - ESP32 + Wokwi
// Capteurs simules : DHT22 (temperature cutanee/ambiante), potentiometre (rythme cardiaque),
// MPU6050 (impacts / accelerations brutales). Alertes : buzzer + LED. Telemetrie : MQTT (JSON).
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ---------- Broches ----------
#define PIN_DHT   15
#define PIN_POT   34   // ADC1_CH6 (entree seule, compatible avec le Wi-Fi actif)
#define PIN_BUZZ  18
#define PIN_LED   2

// ---------- Seuils d'alerte ----------
const int   BPM_MAX     = 140;    // consigne de l'enonce
const float TEMP_MAX_C  = 38.5;   // hyperthermie
const float TEMP_MIN_C  = 34.0;   // valeur anormale basse
const float IMPACT_G    = 1.5;    // choc brutal (profil B)

// ---------- Reseau (Wokwi-GUEST = Wi-Fi simule) ----------
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* MQTT_HOST = "broker.hivemq.com";   // broker public : topic unique ci-dessous
const int   MQTT_PORT = 1883;
const char* TOPIC_TELE  = "esprim/wearable/smartvest/aziz_vest_1102/telemetry";
const char* TOPIC_ALERT = "esprim/wearable/smartvest/aziz_vest_1102/alert";

DHT dht(PIN_DHT, DHT22);
Adafruit_MPU6050 mpu;
WiFiClient net;
PubSubClient mqtt(net);
bool mpuOk = false;
unsigned long tLast = 0;

void wifiConnect() {
  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  while (WiFi.status() != WL_CONNECTED) { delay(250); Serial.print("."); }
  Serial.println("\nWi-Fi OK");
}
void mqttConnect() {
  while (!mqtt.connected()) {
    String id = "smartvest-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (!mqtt.connect(id.c_str())) { delay(1000); }
  }
}
// bip court (n fois) - alerte sonore
void beep(int n, int ms) {
  for (int i = 0; i < n; i++) { tone(PIN_BUZZ, 2000, ms); digitalWrite(PIN_LED, HIGH); delay(ms + 40); digitalWrite(PIN_LED, LOW); }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BUZZ, OUTPUT); pinMode(PIN_LED, OUTPUT);
  dht.begin();
  Wire.begin(21, 22);
  mpuOk = mpu.begin();
  if (mpuOk) { mpu.setAccelerometerRange(MPU6050_RANGE_16_G); mpu.setFilterBandwidth(MPU6050_BAND_44_HZ); }
  else Serial.println("MPU6050 absent");
  wifiConnect();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) wifiConnect();
  if (!mqtt.connected()) mqttConnect();
  mqtt.loop();

  // Impact : echantillonne a ~100 Hz entre deux envois (le choc dure quelques ms)
  static float gMax = 0;
  if (mpuOk) {
    sensors_event_t a, g, t; mpu.getEvent(&a, &g, &t);
    float gn = sqrt(a.acceleration.x*a.acceleration.x + a.acceleration.y*a.acceleration.y + a.acceleration.z*a.acceleration.z) / 9.81f;
    if (gn > gMax) gMax = gn;
  }

  if (millis() - tLast >= 2000) {            // telemetrie toutes les 2 s
    tLast = millis();
    int raw = analogRead(PIN_POT);                         // 0..4095
    int bpm = map(raw, 0, 4095, 50, 200);                  // pouls simule 50..200 bpm
    float temp = dht.readTemperature();
    float hum  = dht.readHumidity();
    if (isnan(temp)) temp = -99;

    bool aBpm  = bpm > BPM_MAX;
    bool aTemp = (temp > TEMP_MAX_C) || (temp < TEMP_MIN_C && temp > -90);
    bool aImp  = gMax > IMPACT_G;

    char msg[200];
    snprintf(msg, sizeof(msg),
      "{\"bpm\":%d,\"temp_c\":%.1f,\"hum_pct\":%.0f,\"g_max\":%.2f,\"alert\":%d}",
      bpm, temp, hum, gMax, (aBpm || aTemp || aImp) ? 1 : 0);
    mqtt.publish(TOPIC_TELE, msg);
    Serial.println(msg);

    if (aBpm || aTemp || aImp) {
      char al[120];
      snprintf(al, sizeof(al), "{\"bpm\":%s,\"temp\":%s,\"impact\":%s}",
               aBpm ? "true" : "false", aTemp ? "true" : "false", aImp ? "true" : "false");
      mqtt.publish(TOPIC_ALERT, al);
      beep(aImp ? 3 : 2, 120);
    }
    gMax = 0;
  }
  delay(10);
}