"""Client MQTT de reception : affiche et archive la telemetrie du gilet (CSV).
Usage : pip install paho-mqtt ; python3 mqtt_subscriber.py
"""
import csv, json, time, paho.mqtt.client as mqtt
TOPIC = "esprim/wearable/smartvest/aziz_vest_1102/#"   # meme identifiant que dans sketch.ino
f = open("telemetry_log.csv", "a", newline=""); w = csv.writer(f)
def on_msg(c, u, m):
    p = m.payload.decode(); print(m.topic, p)
    if m.topic.endswith("telemetry"):
        d = json.loads(p); w.writerow([time.time(), d["bpm"], d["temp_c"], d["hum_pct"], d["g_max"], d["alert"]]); f.flush()
c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2); c.on_message = on_msg
c.connect("broker.hivemq.com", 1883); c.subscribe(TOPIC); c.loop_forever()
