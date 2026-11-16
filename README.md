# Smart Vest — Gilet connecté (Profil B : sport collectif) · Wearable Technology 2026/2027

Mini-projet individuel — ESPRIM, 5ᵉ année Génie Électronique Embarqué & Télécoms (Enseignant : A. Kammoun).
Auteur : Med.Aziz Chtioui.

## Contenu
| Dossier | Rôle |
|---|---|
| `report/` | Rapport SDD (PDF, 8 p.) |
| `simulation/wokwi/` | Projet Wokwi : ESP32 + DHT22 + potentiomètre (BPM) + MPU6050 + buzzer/LED + MQTT |
| `python/axis2_denoise.py` | Axe 2 : NLMS (référence IMU) vs auto-encodeur débruiteur (données synthétiques) |
| `python/budget_rf.py` | Bilan de puissance, autonomie, dimensionnement du patch textile 2,45 GHz |
| `python/mqtt_subscriber.py` | Client MQTT qui archive la télémétrie en CSV |
| `docs/` | Figures du rapport (`figures/`) et captures des tests Wokwi (`screenshots/`) |

## Lancer la simulation Wokwi
1. Sur https://wokwi.com créer un projet **ESP32**, puis copier `sketch.ino`, `diagram.json` et `libraries.txt`.
2. Les topics MQTT utilisent l'identifiant `aziz_vest_1102` (broker public : le topic doit être unique). Pour refaire le test, remplacer cet identifiant par un mot personnel, **identique** dans `sketch.ino` et dans `python/mqtt_subscriber.py`.
3. Lancer ▶. Le potentiomètre fait varier le pouls (50–200 bpm) ; le DHT22 et le MPU6050 sont réglables en cours de simulation.
4. Alertes : buzzer + LED si BPM > 140, température < 34 °C ou > 38,5 °C, ou choc > 1,5 g.
   (Seuil abaissé pour la démonstration car les curseurs du MPU6050 simulé sont limités à ≈ ±2 g par axe ; dans le gilet réel le seuil est de 4 g avec l'ADXL375.)
5. Réception (Windows) : `pip install paho-mqtt`, puis `cd python` et `python mqtt_subscriber.py` (ou MQTT Explorer sur `broker.hivemq.com`).

## Résultats des tests (captures dans `docs/screenshots/`)
| Scénario | Action | Résultat |
|---|---|---|
| `Normal.png` | 36,7 °C, pouls 112 bpm | `alert = 0` |
| `high_bpm.png` | pouls 149 bpm (> 140) | `alert = 1`, topic alert : `bpm: true` |
| `Fever.png` | température 39,2 °C | `alert = 1`, topic alert : `temp: true` |
| `Shock.png` | accélération 3,46 g | `alert = 1`, topic alert : `impact: true` |

Les messages JSON apparaissent à la fois dans le moniteur série de Wokwi et dans le récepteur Python.

## Reproduire les résultats Python
```bash
pip install numpy scipy scikit-learn matplotlib
cd python
python axis2_denoise.py
python budget_rf.py
```
(Les scripts créent les fichiers de résultats dans `docs/`.)

## Limites connues
- Données de l'axe 2 **synthétiques** : l'avantage de l'auto-encodeur est surestimé (morphologie ECG fixe), à confirmer sur MIT-BIH + enregistrements bruités.
- Courants des composants : ordres de grandeur de datasheets, non mesurés.
- Antenne dimensionnée analytiquement, sans simulation électromagnétique ; quantification INT8 non simulée.
- La simulation Wokwi valide les seuils, le format des messages et la transmission MQTT, pas le bruit des capteurs.
