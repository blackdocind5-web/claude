import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_xau as X, gestion as G
Dd = X.Dd; B = Dd.B
sys.path.insert(0, os.path.join(X.RAIZ, "mec_diario")); import costos as Co
S = Co.stops(); PIP = 0.0001
MB = dict(XAUUSD=0.05, EURUSD=0.4 * PIP, GBPUSD=0.8 * PIP, BTC_spread=50, fee_btc=0)
T = B.cargar()
real = sorted(Co.aplicar([t for a in ("XAUUSD", "EURUSD", "GBPUSD") for t in T[a]], MB, S), key=lambda t: t["ent"])
V = G.V
out = []
for nom, ts, kw in (("Cartera real (Pre NY, 3 activos)", real, dict(base=1.0, freno=2.7)),
                    ("Cartera real + XAUUSD NY", sorted(real + V, key=lambda t: t["ent"]), dict(base=1.0, freno=2.7)),
                    ("Cartera real + XAUUSD NY, objetivo semanal +1,8%", sorted(real + V, key=lambda t: t["ent"]), dict(base=1.0, freno=2.7, obj_sem=1.8)),
                    ("Cartera real, objetivo semanal +1,8%", real, dict(base=1.0, freno=2.7, obj_sem=1.8))):
    r = Dd.simular(ts, **kw); m = Dd.montecarlo(ts, sims=1000, **kw)
    out.append(dict(nombre=nom, r={k: v for k, v in r.items() if k != "niveles"}, mc=m))
    print(f"{nom:48} | {r['n']} ops cagr {r['cagr']} dd {r['mdd']} {r['anios']} sem+ {r['sem_pos']} >=1% {r['sem_mas1']} peor_sem {r['peor_sem']} sem_med {r['sem_med']} mes+ {r['mes_pos']} | MC cagr {m['cagr_med']} p5 {m['cagr_p5']} dd95 {m['dd_p95']} añoneg {m['p_anio_neg']} sem+ {m['sem_pos_med']} >=1% {m['sem_mas1_med']}")
json.dump(out, open("con_cartera.json", "w"), ensure_ascii=False)
