"""Bilan de puissance (profil B) et dimensionnement du patch textile 2.45 GHz. -> ../docs/budget.json"""
import json, numpy as np
V=3.0; eta=0.90; Vbat=3.7
# courants (mA) sous 3.0 V : ordres de grandeur issus des datasheets, a valider sur banc reel
parts={"AFE ECG/resp ADS1292R":0.25,"IMU ICM-42688-P (LN, 6 axes)":0.90,"Accelero haut-g ADXL375":0.14,
       "Temp. peau MAX30208":0.07,"MCU nRF5340 (acq.+inference, moyen)":1.20}
I_acq=sum(parts.values())
I_tx_peak, t_tx, f_tx = 8.0, 3e-3, 10        # rafale BLE 0 dBm, 3 ms, 10 Hz (alertes + resume)
I_rx, duty_rx = 4.6, 0.05                    # ecoute maillage 5 %
I_radio=I_tx_peak*t_tx*f_tx + I_rx*duty_rx
I_sleep=0.020
I_rail=I_acq+I_radio+0.010                   # + Iq PMIC
I_bat=I_rail*V/(Vbat*eta)
out={"I_acq_mA":I_acq,"I_radio_moy_mA":I_radio,"I_rail_mA":I_rail,"I_bat_mA":I_bat,"I_sleep_mA":I_sleep}
for C in (150,200,250):
    use=C*0.85*0.9                           # 85 % utilisable x 0.9 (froid/vieillissement)
    out[f"autonomie_h_{C}mAh_nominal"]=use/I_bat
    out[f"autonomie_h_{C}mAh_pire_cas"]=use/(I_bat*1.5)   # +50 % courant
out["jours_4h_par_jour_200mAh"]=(200*0.85*0.9-0)/ (I_bat*4+I_sleep*Vbat/Vbat*20) / 1   # mAh/jour -> jours
out["conso_jour_mAh"]=I_bat*4+I_sleep*20
out["jours_200mAh"]=200*0.85*0.9/out["conso_jour_mAh"]
# patch micro-ruban (modele ligne de transmission)
c=3e8; f=2.45e9; er=1.3; h=3e-3
W=c/(2*f)*np.sqrt(2/(er+1))
def eeff(er): return (er+1)/2+(er-1)/2*(1+12*h/W)**-0.5
def dL(e): return 0.412*h*(e+0.3)*(W/h+0.264)/((e-0.258)*(W/h+0.8))
e0=eeff(er); L=c/(2*f*np.sqrt(e0))-2*dL(e0)
out["patch"]={"W_mm":W*1e3,"L_mm":L*1e3,"eps_eff_sec":e0}
f_of=lambda er_: c/(2*(L+2*dL(eeff(er_)))*np.sqrt(eeff(er_)))
out["patch"]["f_sec_GHz"]=f_of(er)/1e9
for erw in (1.5,1.8,2.2): out["patch"][f"f_humide_er{erw}_GHz"]=f_of(erw)/1e9
# SAR : borne superieure pessimiste, 1 mW (0 dBm) entierement absorbes dans 10 g
out["SAR_borne_Wkg"]=1e-3/0.010
print(json.dumps(out,indent=1)); json.dump(out,open('../docs/budget.json','w'),indent=1)
