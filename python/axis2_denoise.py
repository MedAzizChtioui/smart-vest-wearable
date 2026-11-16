"""Axe 2 - Filtrage & TinyML frugal : NLMS (reference IMU) vs auto-encodeur debruiteur.
Donnees 100 % synthetiques (ECG gaussien + artefact de mouvement derive de l'accelerometre).
Execution : python3 axis2_denoise.py  -> figures dans ../docs/figures, metriques dans ../docs/results.json
"""
import json, time, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, sosfiltfilt, lfilter
from sklearn.neural_network import MLPRegressor

FS = 250
rng = np.random.default_rng(7)
OUT = "../docs/figures/"

def ecg(T, hr=150, rng=rng):
    """ECG synthetique : somme de gaussiennes P,Q,R,S,T par battement (HR avec variabilite)."""
    n = int(T*FS); x = np.zeros(n); t = np.arange(n)/FS
    beat_t, tt = [], 0.3
    while tt < T:
        beat_t.append(tt); tt += 60/hr*(1+0.03*rng.standard_normal())
    for b in beat_t:
        for a, mu, s in [(0.12,-0.20,0.025),(-0.10,-0.04,0.010),(1.0,0.0,0.010),(-0.20,0.03,0.010),(0.30,0.22,0.040)]:
            x += a*np.exp(-0.5*((t-b-mu)/s)**2)
    return x, np.array(beat_t)

def imu(T, mode, rng=rng):
    """Accelerometre 3 axes (g) : course (~3 Hz) + impacts (rugby) selon l'intensite."""
    n = int(T*FS); t = np.arange(n)/FS
    amp = {"low":0.5, "high":2.0}[mode]
    a = np.stack([amp*np.sin(2*np.pi*3.0*t+p)+0.2*amp*rng.standard_normal(n) for p in (0,1.1,2.3)])
    for _ in range(int(T/3)):                      # impacts (plaquages) : pics amortis
        k = rng.integers(0, n-60); d = np.exp(-np.arange(60)/10)*np.sin(2*np.pi*np.arange(60)/12)
        a[:, k:k+60] += (amp*4*rng.standard_normal((3,1)))*d
    return a

def artefact(a, rng=rng):
    """Chemin electrode-peau inconnu : FIR par axe + non-linearite douce (tanh) -> non parfaitement lineaire."""
    h = [rng.standard_normal(12)*np.exp(-np.arange(12)/4) for _ in range(3)]
    y = sum(lfilter(h[i], 1, a[i]) for i in range(3))
    y = 0.35*np.tanh(0.8*y)+0.08*y
    return y

def make(T, mode, seed):
    r = np.random.default_rng(seed)
    clean, beats = ecg(T, 150, r)
    a = imu(T, mode, r)
    noisy = clean + artefact(a, r) + 0.03*r.standard_normal(len(clean))
    return clean, noisy, a, beats

def snr(ref, x): return 10*np.log10(np.sum(ref**2)/np.sum((ref-x)**2))

def nlms(d, a, L=16, mu=0.3, eps=1e-3):
    """NLMS multi-reference : d = ECG bruite, a = IMU (3, n). Sortie = erreur e = ECG estime."""
    n = len(d); w = np.zeros(3*L); e = np.zeros(n)
    for k in range(L, n):
        u = np.concatenate([a[i, k-L+1:k+1][::-1] for i in range(3)])
        y = w@u; e[k] = d[k]-y
        w += mu*e[k]*u/(u@u+eps)
    return e

W, H = 128, 64
def windows(noisy, a, clean=None):
    idx = range(0, len(noisy)-W, H)
    X = np.array([np.concatenate([noisy[i:i+W], a[0,i:i+W]/3, a[1,i:i+W]/3, a[2,i:i+W]/3]) for i in idx])
    Y = None if clean is None else np.array([clean[i:i+W] for i in idx])
    return X, Y, list(idx)

def ae_reconstruct(model, noisy, a):
    X, _, idx = windows(noisy, a); P = model.predict(X)
    win = np.hanning(W)+1e-6; out = np.zeros(len(noisy)); nrm = np.zeros(len(noisy))
    for p, i in zip(P, idx): out[i:i+W] += p*win; nrm[i:i+W] += win
    return out/np.maximum(nrm, 1e-6)

def f1_peaks(sig, beats, tol=0.05):
    sig = sosfiltfilt(butter(2, [5, 30], 'bp', fs=FS, output='sos'), sig)
    pk, _ = find_peaks(sig, distance=int(0.25*FS), height=0.35*np.max(np.abs(sig[FS:])))
    pk = pk/FS
    tp = sum(np.any(np.abs(pk-b) < tol) for b in beats)
    fp = len(pk)-tp; fn = len(beats)-tp
    return 2*tp/(2*tp+fp+fn)

# ---------- entrainement de l'AE (enregistrements distincts du test) ----------
Xs, Ys = [], []
for s, mode in enumerate(["low","high"]*6):
    c, n_, a, _ = make(60, mode, 100+s); X, Y, _ = windows(n_, a, c); Xs.append(X); Ys.append(Y)
Xtr, Ytr = np.vstack(Xs), np.vstack(Ys)
t0 = time.time()
ae = MLPRegressor(hidden_layer_sizes=(64, 16, 64), activation="tanh", max_iter=150, early_stopping=True, random_state=0)
ae.fit(Xtr, Ytr); train_s = time.time()-t0

# ---------- test ----------
res = {}
fig, axs = plt.subplots(2, 1, figsize=(9, 5.2), sharex=True)
for row, mode in enumerate(["low", "high"]):
    c, n_, a, beats = make(30, mode, 900+row)
    e_nlms = nlms(n_, a); e_ae = ae_reconstruct(ae, n_, a)
    sl = slice(FS, None)                              # on ignore la convergence initiale (1 s)
    res[mode] = {
        "SNR_in_dB": snr(c[sl], n_[sl]),
        "SNR_NLMS_dB": snr(c[sl], e_nlms[sl]),
        "SNR_AE_dB": snr(c[sl], e_ae[sl]),
        "F1_R_in": f1_peaks(n_, beats), "F1_R_NLMS": f1_peaks(e_nlms, beats), "F1_R_AE": f1_peaks(e_ae, beats)}
    if row == 0 or row == 1:
        t = np.arange(len(c))/FS; s0, s1 = 8*FS, 12*FS
        ax = axs[row]; ax.plot(t[s0:s1], n_[s0:s1], color="#bbbbbb", lw=.8, label="ECG bruité")
        ax.plot(t[s0:s1], c[s0:s1], color="k", lw=1.0, label="référence")
        ax.plot(t[s0:s1], e_nlms[s0:s1], color="#d95f02", lw=.9, label="NLMS")
        ax.plot(t[s0:s1], e_ae[s0:s1], color="#1b9e77", lw=.9, label="Auto-encodeur")
        ax.set_ylabel("amplitude (u.a.)"); ax.set_title(f"Mouvement {'faible (course)' if mode=='low' else 'fort (course + impacts)'}", fontsize=9)
        if row == 0: ax.legend(ncol=4, fontsize=7, loc="upper right")
axs[1].set_xlabel("temps (s)"); plt.tight_layout(); plt.savefig(OUT+"axe2_signaux.png", dpi=170); plt.close()

# ---------- cout calcul ----------
L = 16; macs_nlms = 3*L*2 + 3*L + 10            # filtre + normalisation + mise a jour w, par echantillon
sizes = [4*W, 64, 16, 64, W]; params = sum(sizes[i]*sizes[i+1]+sizes[i+1] for i in range(len(sizes)-1))
macs_ae = sum(sizes[i]*sizes[i+1] for i in range(len(sizes)-1))  # par fenetre (hop 64 -> par 64 echantillons)
cost = {"NLMS_MAC_par_echantillon": macs_nlms, "NLMS_MAC_par_s": macs_nlms*FS,
        "AE_params": params, "AE_octets_INT8": params, "AE_MAC_par_fenetre": macs_ae,
        "AE_MAC_par_s": macs_ae*FS/H, "train_s": train_s}
res["cout"] = cost
json.dump(res, open("../docs/results.json", "w"), indent=2)

# figure comparaison SNR
fig, ax = plt.subplots(figsize=(6, 3.2)); xs = np.arange(2); w = .26
for j, (k, col, lab) in enumerate([("SNR_in_dB", "#bbbbbb", "Entrée"), ("SNR_NLMS_dB", "#d95f02", "NLMS"), ("SNR_AE_dB", "#1b9e77", "Auto-encodeur")]):
    v = [res["low"][k], res["high"][k]]; b = ax.bar(xs+(j-1)*w, v, w, color=col, label=lab)
    for xx, vv in zip(xs+(j-1)*w, v): ax.text(xx, vv+.2, f"{vv:.1f}", ha="center", fontsize=7)
ax.set_xticks(xs); ax.set_xticklabels(["Mouvement faible", "Mouvement fort"]); ax.set_ylabel("SNR (dB)"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(OUT+"axe2_snr.png", dpi=170)
print(json.dumps(res, indent=1))
