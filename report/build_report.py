# -*- coding: utf-8 -*-
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (CondPageBreak, BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("F", D+"DejaVuSansCondensed.ttf")); pdfmetrics.registerFont(TTFont("FB", D+"DejaVuSansCondensed-Bold.ttf"))
pdfmetrics.registerFont(TTFont("FI", D+"DejaVuSansCondensed-Oblique.ttf")); pdfmetrics.registerFont(TTFont("FM", D+"DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("F", normal="F", bold="FB", italic="FI", boldItalic="FB")
R = json.load(open("../docs/results.json")); B = json.load(open("../docs/budget.json"))
NAVY = colors.HexColor("#1f3a5f"); GREY = colors.HexColor("#f0f3f7")
body = ParagraphStyle("b", fontName="F", fontSize=9.6, leading=13.4, alignment=TA_JUSTIFY, spaceAfter=4)
h1 = ParagraphStyle("h1", fontName="FB", fontSize=13, leading=16, textColor=NAVY, spaceBefore=8, spaceAfter=5, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="FB", fontSize=10, leading=13, textColor=NAVY, spaceBefore=5, spaceAfter=3)
small = ParagraphStyle("s", parent=body, fontSize=7.5, leading=10, textColor=colors.HexColor("#444444"), alignment=TA_CENTER)
cell = ParagraphStyle("c", fontName="F", fontSize=8.4, leading=11)
cellb = ParagraphStyle("cb", parent=cell, fontName="FB")
code = ParagraphStyle("code", fontName="FM", fontSize=7.2, leading=9, backColor=GREY, borderPadding=3, spaceAfter=5)
def P(t, s=body): return Paragraph(t, s)
def T(rows, widths, header=True, keep=True):
    data = [[Paragraph(str(c), cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w*mm for w in widths], repeatRows=1 if header else 0)
    st = [("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#b7c1d1")), ("VALIGN", (0,0), (-1,-1), "TOP"),
          ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2)]
    if header: st += [("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dbe4f0"))]
    t.setStyle(TableStyle(st)); return KeepTogether([t, Spacer(1, 5)]) if keep else t
def IMG(path, w_mm, cap):
    from PIL import Image as PI
    iw, ih = PI.open(path).size; w = w_mm*mm
    return KeepTogether([Image(path, w, w*ih/iw), P(cap, small), Spacer(1, 3)])

def footer(c, d):
    c.saveState(); c.setFont("F", 7.5); c.setFillColor(colors.HexColor("#555555"))
    c.drawString(18*mm, 10*mm, "Wearable Technology 2026/2027 — ESPRIM — SDD Smart Vest (Profil B / Axe 2)")
    c.drawRightString(192*mm, 10*mm, f"Page {d.page}"); c.setStrokeColor(NAVY); c.line(18*mm, 13*mm, 192*mm, 13*mm); c.restoreState()
doc = BaseDocTemplate("SDD_SmartVest_ProfilB_Axe2.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm,
                      title="SDD — Gilet connecté pour sport collectif", author="Med.Aziz Chtioui")
doc.addPageTemplates([PageTemplate("p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=footer)])
S = []
F = "../docs/figures/"
lo, hi, c = R["low"], R["high"], R["cout"]

# ---------------- En-tête + 1. Fiche synoptique ----------------
S += [P("<b>Smart Vest : gilet connecté pour sport collectif à haute intensité</b>", ParagraphStyle("t", fontName="FB", fontSize=17, leading=21, textColor=NAVY)),
      P("Dossier de conception d'architecture système préliminaire (SDD) — Profil B · Axe d'innovation 2 (filtrage &amp; TinyML frugal)", ParagraphStyle("st", parent=body, fontSize=10, textColor=colors.HexColor("#444444"))),
      P("Auteur : Med.Aziz Chtioui · Module Wearable Technology · 5ᵉ année Génie Électronique Embarqué &amp; Télécoms · ESPRIM · Enseignant : A. Kammoun · 2026/2027 S1<br/>Dépôt GitHub (code, simulation Wokwi, scripts) : <b>[URL à renseigner]</b>", small),
      Spacer(1, 4), P("1. Fiche synoptique &amp; cahier des charges", h1)]
S.append(P("<b>Profil retenu : B — football / rugby.</b> Le gilet est porté pendant l'entraînement et le match. La contrainte dominante n'est pas l'autonomie mais le <b>choc mécanique</b> (plaquages, chutes, contacts), l'<b>artefact de mouvement</b> qui en découle sur l'ECG, et la <b>transmission à faible latence</b> vers le staff médical et technique (plusieurs joueurs simultanés, d'où un maillage BLE). Le dispositif mesure la charge interne (ECG, fréquence respiratoire, température cutanée) et la charge externe (accélérations, impacts), traite localement les signaux (edge computing) et déclenche des alertes : surchauffe, pouls anormal, choc violent."))
S.append(T([["Réf.", "Exigence", "Cible", "Justification / vérification"],
 ["E1", "Latence d'alerte d'impact (choc → LED/vibreur + trame radio)", "&lt; 20 ms", "Chemin matériel : ADXL375 → INT → GPIO ; test par oscilloscope (non mesuré ici)"],
 ["E2", "Latence de l'estimation ECG débruitée", "&lt; 0,6 s", "Fenêtre de 128 éch. à 250 Hz = 0,51 s + calcul &lt; 1 ms"],
 ["E3", "Masse du pod électronique", "&lt; 40 g (limite énoncé : 60 g)", "Estimation : ≈ 28 g (détail section 6)"],
 ["E4", "Autonomie en session (entraînement + match)", "≥ 10 h", f"Calculée : {B['autonomie_h_200mAh_pire_cas']:.0f} h au pire cas (200 mAh)"],
 ["E5", "Étanchéité à la sueur / lavage", "IP67 pod ; textile lavable 30 cycles", "Pod amovible, connecteur magnétique étanche"],
 ["E6", "Tenue aux chocs", "200 g (ADXL375) ; pod encapsulé", "Pistes e-textile à serpentins, pod sur sangle thoracique"],
 ["E7", "Exposition RF", "SAR &lt; 2 W/kg", f"Borne pessimiste {B['SAR_borne_Wkg']:.1f} W/kg à 0 dBm (section 5)"],
 ["E8", "Gain de débruitage ECG en mouvement fort", "≥ +10 dB de SNR vs entrée", f"Obtenu en simulation : {hi['SNR_AE_dB']-hi['SNR_in_dB']:+.1f} dB (AE), {hi['SNR_NLMS_dB']-hi['SNR_in_dB']:+.1f} dB (NLMS)"]],
 [12, 60, 38, 64]))

# ---------------- 2. Architecture système ----------------
S += [P("2. Architecture système &amp; schéma bloc", h1),
      P("L'électronique est regroupée dans un <b>pod unique</b> fixé sur la sangle thoracique, relié aux électrodes et à la ceinture d'élongation par un connecteur magnétique étanche. Les capteurs inertiels sont dans le pod : le sternum est proche du centre de masse, donc représentatif de la charge externe et peu sujet aux vibrations parasites des membres. Le SoC <b>Nordic nRF5340</b> (cœur applicatif Cortex-M33 à 128 MHz, cœur réseau dédié à la radio) isole le traitement du signal du temps réel radio."),
      T([["Lien", "Type", "Débit / fréquence", "Remarque"],
         ["Électrodes → ADS1292R", "analogique différentiel", "—", "Entrées avec filtre RFI + résistances de protection 2 × 1 kΩ"],
         ["ADS1292R → nRF5340", "SPI + DRDY", "SPI 4 MHz ; 250 éch./s × 2 voies × 24 bits", "≈ 12 kbit/s, interruption à chaque échantillon"],
         ["ICM-42688-P → nRF5340", "SPI + INT", "SPI 8 MHz ; 400 Hz × 6 axes × 16 bits", "Référence du filtre NLMS (synchrone ECG)"],
         ["ADXL375 → nRF5340", "SPI + INT activité", "800 Hz ; seuil d'impact programmable", "Réveille le MCU en Deep Sleep, latence matérielle"],
         ["MAX30208 → nRF5340", "I²C", "400 kHz ; 1 mesure/s", "Température cutanée ±0,1 °C"],
         ["nRF5340 → patch", "RF 50 Ω", "2,45 GHz, 0 dBm", "Ligne microruban adaptée + cadre de masse continu"],
         ["nPM1300 → rails", "alimentation", "3,0 V (buck) ; LDO filtré pour l'AFE", "Rail analogique séparé : bruit &lt; 10 µVrms"]],
        [38, 32, 52, 52], keep=False),
      IMG(F+"schema_bloc.png", 132, "Fig. 1 — Schéma bloc fonctionnel : liaisons analogiques différentielles (vert), bus numériques (bleu), distribution de puissance (jaune).")]

# ---------------- 3. Instrumentation ----------------
S += [P("3. Instrumentation &amp; chaîne d'acquisition", h1),
      P("<b>Choix des capteurs.</b> Les électrodes sont des <b>électrodes sèches textiles</b> (fil d'argent ou tissu enduit, surface ≈ 4 cm²) positionnées sur la ceinture thoracique. Elles évitent le gel et la peau rasée, mais leur impédance de contact est élevée (typiquement 100 kΩ à 1 MΩ à 50 Hz) et varie avec la pression et la sueur : c'est la cause principale de l'artefact de mouvement. Le capteur respiratoire est la même ceinture, avec une jauge d'élongation en tissu conducteur ; l'ADS1292R fournit aussi la respiration par pneumographie d'impédance, utilisée en secours. L'IMU 6 axes (ICM-42688-P, ±16 g) caractérise la course ; <b>un accéléromètre haut-g séparé (ADXL375, ±200 g)</b> est indispensable en rugby, car un plaquage sature largement une plage de ±16 g."),
      T([["Capteur", "Grandeur", "Plage / résolution", "Fréq.", "Rôle"],
         ["Électrodes sèches + ADS1292R", "ECG 2 dérivations", "±400 mV ; 24 bits ; CMRR &gt; 105 dB", "250 Hz", "Charge interne, arythmies, FC"],
         ["Ceinture d'élongation", "Respiration", "5–60 resp/min", "25 Hz", "Fatigue, charge ventilatoire"],
         ["MAX30208", "Température cutanée", "±0,1 °C", "1 Hz", "Hyperthermie"],
         ["ICM-42688-P", "Accélération + gyro", "±16 g ; ±2000 °/s", "400 Hz", "Course, référence NLMS"],
         ["ADXL375", "Chocs", "±200 g ; 49 mg/LSB", "800 Hz", "Détection d'impact"]],
        [38, 30, 44, 18, 42]),
      P("<b>Conditionnement.</b> L'AFE intègre l'amplificateur d'instrumentation, un gain programmable (×6 retenu : 400 mV × 6 reste dans la plage du CAN 24 bits) et un CAN delta-sigma. Le <b>CMRR</b> compte moins ici que l'<b>impédance d'entrée</b> : avec des électrodes à 1 MΩ, un déséquilibre d'impédance de 100 kΩ entre les deux voies convertit le bruit secteur en mode commun (50 Hz, ≈ 1 V sur le corps) en tension différentielle ; l'impédance d'entrée de l'ADS1292R (&gt; 100 MΩ) maintient cette conversion sous le niveau du signal. Une jambe droite active (RLD) rebouclée sur une troisième électrode textile abaisse la tension de mode commun. Filtrage analogique : passe-bas RC du premier ordre (fc ≈ 150 Hz), anti-repliement complété par le filtre sinc du delta-sigma."),
      P("<b>Intégration textile.</b> Les pistes sont brodées au fil d'argent en <b>serpentins</b> (amplitude 3 mm, pas 6 mm) pour absorber l'allongement de 10–20 % de la ceinture sans rupture ; elles sont isolées par un film TPU thermocollé. Les électrodes sont maintenues par une mousse 2 mm qui assure une pression de contact stable. Ces points sont à valider par essais de traction et de lavage.")]

# ---------------- 4. Edge AI ----------------
S += [P("4. Architecture électronique &amp; pipeline Edge AI", h1),
      P("<b>Cible matérielle.</b> Le nRF5340 est retenu pour la séparation cœur applicatif (traitement) / cœur réseau (BLE), sa radio 2,4 GHz intégrée et son Cortex-M33 avec extensions DSP. Alternatives étudiées : STM32U5 (très bas courant mais pas de radio, donc deuxième puce) ; ESP32-S3 (accélération vectorielle, mais courant actif et radio plus élevés) ; Ambiq Apollo4 (très faible consommation mais BLE moins adapté à un maillage). Aucun NPU n'est nécessaire : le modèle (42 ko) tient largement sur le cœur applicatif."),
      P("<b>Pipeline embarqué</b> (deux chemins indépendants) :"),
      T([["Chemin", "Étapes", "Déclenchement / sortie"],
         ["Impact (temps réel dur)", "ADXL375 : comparaison au seuil matériel (8 g) → interruption → lecture 32 éch. du FIFO → |a| max et durée du pic", "Alerte si |a| &gt; 4 g sur ≥ 2 ms ; latence &lt; 20 ms (E1) ; trame BLE Mesh prioritaire"],
         ["Physiologique (temps réel souple)", "ECG 250 Hz + IMU rééchantillonnée → fenêtrage 128 éch. (50 % de recouvrement) → débruitage (section 7) → détection des pics R → FC, variabilité sur 30 s", "Alerte si FC &gt; 140 bpm soutenue 10 s ou température &lt; 34 ou &gt; 38,5 °C ; résumé BLE à 1 Hz"]],
        [32, 84, 56]),
      P(f"<b>Modèle et quantification.</b> Le débruiteur retenu est un perceptron à goulot d'étranglement 512→64→16→64→128 (entrée : 128 éch. d'ECG + 3 × 128 éch. d'accélération ; sortie : 128 éch. d'ECG propre) : <b>{c['AE_params']:,} paramètres</b>, soit {c['AE_octets_INT8']/1024:.0f} ko en INT8 (poids) et {c['AE_MAC_par_fenetre']:,} MAC par fenêtre. Avec un recouvrement de 50 % à 250 Hz, une fenêtre est traitée toutes les 256 ms, soit {c['AE_MAC_par_s']/1000:.0f} kMAC/s. <b>Budget temporel</b> : en supposant 2 cycles par MAC avec CMSIS-NN INT8 (hypothèse à vérifier sur cible), une inférence prend ≈ {c['AE_MAC_par_fenetre']*2/128e6*1e3:.2f} ms à 128 MHz, soit un taux d'occupation du cœur d'environ {c['AE_MAC_par_fenetre']*2/128e6/0.256*100:.2f} %. La latence de bout en bout (≈ 0,51 s) est dominée par le remplissage de la fenêtre, pas par le calcul. La quantification INT8 n'a pas été simulée ici (l'entraînement est en virgule flottante) ; l'écart attendu est faible pour un réseau de cette taille mais doit être mesuré avec une calibration sur données réelles.")]

# ---------------- 5. Télécoms ----------------
bt = B["patch"]
S += [P("5. Dossier télécoms &amp; antenne textile", h1),
      P("<b>Protocole.</b> Pour 20 à 30 joueurs sur un terrain, un lien cellulaire (NB-IoT) est inadapté (latence et consommation). On retient le <b>BLE (nRF5340, 2,4 GHz) en maillage</b> : les joueurs relaient les trames d'alerte vers une passerelle en bord de terrain, ce qui supprime le besoin d'un lien direct à chaque joueur. L'UWB est envisagé en option pour la localisation (non dimensionné ici). Les alertes (quelques dizaines d'octets) utilisent des annonces étendues à 1 Mbit/s ; le flux de résumé physiologique est de 1 Hz."),
      P(f"<b>Antenne.</b> Un <b>patch microruban</b> à 2,45 GHz sur feutre (ε<sub>r</sub> ≈ 1,3 ; épaisseur h = 3 mm) avec élément rayonnant et plan de masse en tissu argenté de type Shieldex. Par le modèle de ligne de transmission : largeur W = {bt['W_mm']:.1f} mm, ε<sub>eff</sub> = {bt['eps_eff_sec']:.3f}, longueur résonante L = {bt['L_mm']:.1f} mm (corrections de bord incluses). Le patch occupe donc environ 57 × 51 mm, compatible avec une sangle thoracique ; le plan de masse (≈ 70 × 65 mm) est placé côté peau."),
      P(f"<b>Couplage au corps.</b> Le muscle (ε<sub>r</sub> ≈ 52) est très proche de l'antenne. Un patch avec plan de masse confine l'essentiel du champ entre l'élément et la masse, ce qui <b>réduit fortement</b> l'influence du corps par rapport à un dipôle ou une IFA ; c'est la raison du choix. Le désaccord provient surtout de l'humidité du feutre : si ε<sub>r</sub> passe de 1,3 à 1,5 / 1,8 / 2,2 par imprégnation de sueur, la fréquence de résonance calculée tombe de 2,45 GHz à {bt['f_humide_er1.5_GHz']:.2f} / {bt['f_humide_er1.8_GHz']:.2f} / {bt['f_humide_er2.2_GHz']:.2f} GHz. Ces décalages (jusqu'à −500 MHz) sortent de la bande BLE (2,40–2,4835 GHz) : le substrat doit donc être <b>hydrophobe ou encapsulé</b> (laminage TPU des deux faces), ce qui est la mesure principale retenue, complétée par un réseau d'adaptation ajustable sur le pod. Ce modèle est analytique et non simulé en électromagnétique ; la courbure du torse et l'adaptation réelle (S11) restent à simuler (CST/HFSS) puis à mesurer."),
      IMG(F+"detuning.png", 105, "Fig. 4 — Dérive de la fréquence de résonance du patch lorsque le feutre s'imprègne de sueur (modèle analytique)."),
      P(f"<b>SAR.</b> La puissance de sortie est de 0 dBm (1 mW). Même en supposant, de façon très pessimiste, que toute la puissance soit absorbée dans 10 g de tissu, le débit d'absorption spécifique serait de 1 mW / 0,010 kg = <b>{B['SAR_borne_Wkg']:.1f} W/kg</b>, soit 20 fois moins que la limite de 2 W/kg (10 g). La conformité formelle repose néanmoins sur une mesure normalisée du produit final.")]

# ---------------- 6. Bilan énergétique ----------------
S += [P("6. Bilan énergétique &amp; dimensionnement de la batterie", h1),
      P("Les courants ci-dessous sont des <b>ordres de grandeur issus des datasheets</b> (sous 3,0 V), à confirmer par mesure sur prototype avec un analyseur de courant."),
      T([["Bloc", "Mode", "Courant moyen (mA)"],
         ["ADS1292R (2 voies, 250 SPS)", "Acquisition", "0,25"], ["ICM-42688-P (6 axes, mode bas bruit)", "Acquisition", "0,90"],
         ["ADXL375 (800 Hz)", "Acquisition", "0,14"], ["MAX30208", "Acquisition", "0,07"],
         ["nRF5340 cœur applicatif (acquisition + inférence, moyenne)", "Acquisition + inférence", "1,20"],
         ["<b>Sous-total acquisition + inférence</b>", "", f"<b>{B['I_acq_mA']:.2f}</b>"],
         ["Radio : émission 0 dBm, 3 ms à 10 Hz (8 mA crête) + écoute maillage 5 % (4,6 mA)", "Rafales", f"{B['I_radio_moy_mA']:.2f}"],
         ["PMIC (courant de repos)", "—", "0,01"],
         ["<b>Total sur le rail 3,0 V</b>", "", f"<b>{B['I_rail_mA']:.2f}</b>"],
         ["Courant côté batterie (3,7 V, rendement du buck 90 %)", "", f"<b>{B['I_bat_mA']:.2f}</b>"],
         ["Veille profonde (réveil par ADXL375)", "Deep Sleep", f"{B['I_sleep_mA']:.3f}"]], [102, 40, 30]),
      IMG(F+"courants.png", 115, "Fig. 3 — Répartition du courant moyen en mode acquisition + inférence + radio (total 3,04 mA sous 3,0 V)."),
      P(f"<b>Autonomie.</b> Pour une batterie Li-Po de <b>200 mAh</b>, on retient 85 % de capacité utilisable et un facteur 0,9 pour le froid et le vieillissement : capacité utile 153 mAh. Autonomie nominale : <b>{B['autonomie_h_200mAh_nominal']:.0f} h</b> ; en ajoutant 50 % de marge sur le courant (radio plus sollicitée par le maillage), <b>{B['autonomie_h_200mAh_pire_cas']:.0f} h</b>, soit largement au-delà de l'exigence E4 (10 h). Pour une utilisation de 4 h par jour (le reste en veille profonde), la consommation est d'environ {B['conso_jour_mAh']:.1f} mAh/jour, soit ≈ {B['jours_200mAh']:.0f} jours entre deux charges. Une capacité de 150 mAh suffirait ({B['autonomie_h_150mAh_pire_cas']:.0f} h au pire cas) et gagnerait ≈ 1 g ; 200 mAh est conservée pour la marge de vieillissement."),
      P("<b>Recharge et gestion de l'énergie.</b> Le PMIC <b>nPM1300</b> (Nordic) intègre un chargeur Li-Po linéaire (courant de charge programmable, 0,1 C ≈ 20 mA retenu), un buck 3,0 V et une jauge de batterie ; il réalise la charge CC/CV avec arrêt en température, tension de coupure basse (3,0 V) et protection contre l'inversion de polarité du connecteur. La charge s'effectue via les mêmes contacts magnétiques, pod retiré du gilet. <b>Masse estimée du pod</b> : batterie 4,5 g + carte (nRF5340, AFE, capteurs) 4 g + boîtier encapsulé 10 g + connecteur magnétique 6 g + vibreur 2 g + joints et visserie 1,5 g ≈ <b>28 g</b> (cible E3 : &lt; 40 g)."),
      P("<b>Gestion thermique.</b> La dissipation totale est d'environ 9 mW (3,04 mA × 3,0 V), négligeable ; l'échauffement du pod est inférieur à 1 °C et ne perturbe pas la mesure de température cutanée, qui est de plus lue sur un capteur déporté côté peau.")]

# ---------------- 7. Innovation ----------------
S += [P("7. Dossier d'innovation personnelle — Axe 2 : filtrage &amp; TinyML frugal", h1),
      P("<b>Problématique.</b> En rugby ou en football, l'ECG capté par des électrodes sèches est dominé par l'artefact de mouvement, dont le spectre (0,5–20 Hz) recouvre celui du QRS (5–30 Hz) : un filtre passe-bande fixe est donc inefficace. Deux approches sont comparées sur une même simulation, avec le même budget de calcul embarqué sur Cortex-M33 : un <b>filtre adaptatif NLMS</b> utilisant l'accélération comme référence de bruit, et un <b>auto-encodeur débruiteur</b> de très petite taille."),
      P("<b>Méthode (reproductible : scripts <font name='FM'>python/axis2_denoise.py</font>).</b> L'ECG est synthétisé (somme de gaussiennes P-Q-R-S-T, 150 bpm avec variabilité) ; l'accélération triaxiale contient la course (≈ 3 Hz) et des impacts amortis (un toutes les 3 s en moyenne) ; l'artefact est obtenu par filtrage de l'accélération à travers un chemin électrode-peau FIR inconnu suivi d'une non-linéarité (tanh), puis ajouté à l'ECG avec un bruit blanc. Deux régimes sont testés : mouvement faible (amplitude 0,5 g) et fort (2 g). Le NLMS (16 coefficients par axe, μ = 0,3) filtre l'ECG bruité en prenant les 3 axes comme référence. L'auto-encodeur (512→64→16→64→128, tanh) est entraîné sur 12 enregistrements de 60 s et testé sur des enregistrements distincts de 30 s ; les sorties de fenêtres sont recombinées par recouvrement-addition (fenêtre de Hann). Les 1ʳᵉˢ secondes (convergence du NLMS) sont exclues du calcul du SNR."),
      IMG(F+"axe2_signaux.png", 165, "Fig. 2 — ECG bruité, référence, sortie NLMS et sortie auto-encodeur (4 s) pour mouvement faible (haut) et fort (bas)."),
      T([["Régime", "SNR entrée (dB)", "SNR NLMS (dB)", "SNR AE (dB)", "F1 pics R : entrée / NLMS / AE"],
         ["Mouvement faible", f"{lo['SNR_in_dB']:.1f}", f"{lo['SNR_NLMS_dB']:.1f}", f"{lo['SNR_AE_dB']:.1f}", f"{lo['F1_R_in']:.2f} / {lo['F1_R_NLMS']:.2f} / {lo['F1_R_AE']:.2f}"],
         ["Mouvement fort", f"{hi['SNR_in_dB']:.1f}", f"{hi['SNR_NLMS_dB']:.1f}", f"{hi['SNR_AE_dB']:.1f}", f"{hi['F1_R_in']:.2f} / {hi['F1_R_NLMS']:.2f} / {hi['F1_R_AE']:.2f}"]],
        [32, 30, 30, 30, 50]),
      T([["Critère", "NLMS (16 coeff. × 3 axes)", "Auto-encodeur 512-64-16-64-128"],
         ["Calcul", f"{c['NLMS_MAC_par_echantillon']} MAC/éch. → {c['NLMS_MAC_par_s']/1000:.1f} kMAC/s", f"{c['AE_MAC_par_fenetre']:,} MAC/fenêtre → {c['AE_MAC_par_s']/1000:.0f} kMAC/s"],
         ["Mémoire", "96 coefficients + tampons (&lt; 1 ko)", f"{c['AE_octets_INT8']/1024:.0f} ko de poids INT8"],
         ["Latence algorithmique", "1 échantillon (4 ms)", "128 éch. (≈ 0,51 s)"],
         ["Dépendance à l'IMU", "obligatoire (référence de bruit)", "utilisée en entrée, mais peut apprendre la morphologie QRS"],
         ["Risque principal", "convergence lente, modèle linéaire face à une relation non linéaire", "généralisation aux vrais ECG (non vérifiée) ; biais de morphologie"]],
        [32, 62, 78]),
      P(f"<b>Analyse critique.</b> (1) L'auto-encodeur surpasse nettement le NLMS dans les deux régimes ({lo['SNR_AE_dB']-lo['SNR_in_dB']:+.1f} dB et {hi['SNR_AE_dB']-hi['SNR_in_dB']:+.1f} dB contre {lo['SNR_NLMS_dB']-lo['SNR_in_dB']:+.1f} et {hi['SNR_NLMS_dB']-hi['SNR_in_dB']:+.1f} dB), ce qui s'explique par la non-linéarité du chemin d'artefact simulé : un filtre linéaire ne peut supprimer que la part linéaire. (2) <b>Cet écart est très probablement surestimé</b> : les ECG synthétiques ont une morphologie identique d'un battement à l'autre, qu'un réseau mémorise facilement ; sur de vrais signaux (variabilité inter-individuelle, arythmies), l'avantage sera plus faible et le risque de « lisser » une anomalie réelle existe, ce qui serait dangereux pour une alerte d'arythmie. (3) Le F1 de détection de pics du NLMS en mouvement fort ({hi['F1_R_NLMS']:.2f}) est mauvais en partie à cause d'un détecteur à seuil relatif sensible aux résidus de pics d'impact ; ce chiffre reflète donc autant le détecteur que le filtre et ne doit pas être surinterprété. (4) Conclusion de conception : <b>architecture hybride</b> — NLMS en prétraitement (coût négligeable, convergence rapide, aucune hypothèse de morphologie), auto-encodeur uniquement en confirmation lorsque l'énergie de l'IMU dépasse un seuil, et <b>détection d'arythmie toujours basée sur le signal d'entrée brut validé</b> par un indice de qualité du signal. Prochaine étape : réentraînement et évaluation sur la base MIT-BIH avec le bruit réel « NSTDB » (motion artifact), quantification INT8 et mesure du cycle sur le nRF5340.")]

# ---------------- 8. Intégration mécanique + simulation ----------------
S += [P("8. Intégration mécanique, lavabilité &amp; simulation Wokwi", h1),
      P("<b>Pod amovible vs lavage intégral.</b> Le pod électronique (boîtier en polyuréthane surmoulé, IP67) se retire avant lavage ; il est tenu par aimants (6 contacts POGO magnétiques plaqués or) qui assurent à la fois l'alignement, la reprise de contrainte (détachement sous traction pour protéger la ceinture) et la charge. Le textile (électrodes, pistes, patch) est lavable à 30 °C sans essorage fort : pistes encapsulées sous TPU, coutures de connectique renforcées. Le choix « pod amovible » est préféré à une électronique lavable intégrée car il élimine le risque de corrosion et simplifie la charge ; en contrepartie, les contacts doivent résister à la sueur (placage or, joint torique) et au sable ou à la boue du terrain."),
      P("<b>Simulation Wokwi (volet 2 du sujet).</b> La simulation (<font name='FM'>simulation/wokwi</font>) reprend la chaîne d'alerte du gilet sur une ESP32 : un potentiomètre simule la fréquence cardiaque (50–200 bpm), un DHT22 la température, un MPU6050 les chocs (profil B), un buzzer et une LED les alertes. Les données sont publiées en JSON sur un broker MQTT public (<font name='FM'>broker.hivemq.com</font>) toutes les 2 s, et les alertes sur un topic dédié : seuils BPM &gt; 140, température &lt; 34 °C ou &gt; 38,5 °C, choc &gt; 4 g. Un client Python (<font name='FM'>mqtt_subscriber.py</font>) archive la télémétrie en CSV. Cette simulation ne modélise ni le bruit des capteurs ni l'inférence embarquée : elle valide la logique de seuils, le format des messages et la chaîne de transmission, tandis que le débruitage est étudié dans le volet Python."),
      P("<b>Limites du dossier.</b> Courants et masses sont des estimations de datasheet, non mesurés ; l'antenne est dimensionnée analytiquement sans simulation électromagnétique ; les résultats de l'axe 2 reposent sur des signaux synthétiques ; l'INT8 n'est pas simulé. Chacun de ces points est identifié comme prochaine étape de validation.")]

S += [CondPageBreak(70*mm), P("9. Risques &amp; plan de validation", h1),
      T([["Risque", "Impact", "Mitigation prévue", "Validation (prototype)"],
         ["Artefact de mouvement sur vrais ECG plus complexe que la simulation", "Fausses alertes ou arythmie masquée", "Architecture hybride NLMS + AE ; indice de qualité de signal ; alerte sur signal brut validé", "Évaluation MIT-BIH + bruit NSTDB, puis essais sur joueurs"],
         ["Rupture de piste textile ou perte de contact électrode", "Perte de signal ECG", "Serpentins, pression de contact par mousse, détection de dérive d'impédance (lead-off)", "Essais de traction cyclique, 30 lavages"],
         ["Saturation de l'IMU lors d'un plaquage", "Charge externe sous-estimée", "Accéléromètre haut-g ±200 g dédié", "Test de chute / banc d'impact"],
         ["Désaccord de l'antenne par la sueur", "Perte de liaison maillée", "Substrat laminé TPU, adaptation ajustable", "Mesure S11 sur mannequin humide (liquide équivalent)"],
         ["Consommation réelle supérieure aux datasheets", "Autonomie réduite", "Marge de 50 % déjà incluse ; capacité 200 mAh", "Mesure du courant par analyseur dédié"],
         ["Contacts magnétiques corrodés par la sueur", "Coupure intermittente", "Placage or, joint, rinçage après usage", "Essai brouillard salin 48 h"]],
        [46, 30, 52, 44])]
doc.build(S)
