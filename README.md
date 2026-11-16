# Smart Vest — Gilet connecté (Profil B : sport collectif) · Wearable Technology 2026/2027

Mini-projet individuel — ESPRIM, 5ᵉ année Génie Électronique Embarqué & Télécoms (Enseignant : A. Kammoun).

## Contenu
| Dossier | Rôle |
|---|---|
| `report/` | Rapport SDD (PDF, 10–12 p.) |
| `simulation/wokwi/` | Projet Wokwi : ESP32 + DHT22 + potentiomètre (BPM) + MPU6050 + buzzer/LED + MQTT |
| `python/axis2_denoise.py` | Axe 2 : NLMS (référence IMU) vs auto-encodeur débruiteur (données synthétiques) |
| `python/budget_rf.py` | Bilan de puissance, autonomie, dimensionnement du patch textile 2,45 GHz |
| `python/mqtt_subscriber.py` | Client MQTT qui archive la télémétrie en CSV |
| `docs/` | Figures et résultats JSON générés par les scripts |

## Lancer la simulation Wokwi
1. Sur https://wokwi.com créer un projet **ESP32**, puis copier `sketch.ino`, `diagram.json` et `libraries.txt`.
2. **Changer `CHANGE_ME_AZIZ`** dans les deux topics MQTT (broker public : le topic doit être unique).
3. Lancer ▶. Le potentiomètre fait varier le pouls (50–200 bpm) ; le DHT22 et le MPU6050 sont réglables en cours de simulation.
4. Alertes : buzzer + LED si BPM > 140, température < 34 °C ou > 38,5 °C, ou choc > 4 g.
5. Réception : `pip install paho-mqtt && python3 python/mqtt_subscriber.py` (ou MQTT Explorer sur `broker.hivemq.com`).

## Reproduire les résultats Python
```bash
pip install numpy scipy scikit-learn matplotlib
cd python && python3 axis2_denoise.py && python3 budget_rf.py
```

## Limites connues
- Données de l'axe 2 **synthétiques** : l'avantage de l'auto-encodeur est surestimé (morphologie ECG fixe), à confirmer sur MIT-BIH + enregistrements bruités.
- Courants des composants : ordres de grandeur de datasheets, non mesurés.
- Le projet Wokwi doit être exécuté et capturé (screenshots) par l'étudiant pour le rendu.
