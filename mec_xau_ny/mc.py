import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_xau as X, gestion as G
Dd = X.Dd; V = G.V
C = [("Fijo 1%", dict(base=1.0, tope=0)), ("Fijo 1% + objetivo +1,8%", dict(base=1.0, tope=0, obj_sem=1.8)),
     ("Escalera 1% tope 2 + objetivo +1,8% (continua)", dict(base=1.0, tope=2, obj_sem=1.8)),
     ("Escalera 0,5% tope 3, reinicio semanal", dict(base=0.5, tope=3, escalera_sem=True)),
     ("Escalera 0,75% tope 3, reinicio semanal", dict(base=0.75, tope=3, escalera_sem=True)),
     ("Escalera 1% tope 3, reinicio semanal + objetivo +1,8%", dict(base=1.0, tope=3, escalera_sem=True, obj_sem=1.8)),
     ("Escalera 1% tope 2, reinicio semanal + objetivo +1,8%", dict(base=1.0, tope=2, escalera_sem=True, obj_sem=1.8)),
     ("Escalera 1,5% tope 3, reinicio semanal + objetivo +1,8%", dict(base=1.5, tope=3, escalera_sem=True, obj_sem=1.8)),
     ("Fijo 1,5% + objetivo +1,8%", dict(base=1.5, tope=0, obj_sem=1.8))]
out = []
for nom, kw in C:
    r = Dd.simular(V, freno=None, **kw); m = Dd.montecarlo(V, sims=1500, freno=None, **kw)
    out.append(dict(nombre=nom, kw=kw, r={k: v for k, v in r.items() if k != "niveles"}, mc=m))
    print(f"{nom:58} | hist {r['cagr']:6} dd {r['mdd']:5} sem+ {r['sem_pos']} >=1% {r['sem_mas1']} peor_sem {r['peor_sem']} maxr {r['max_riesgo']} | MC cagr {m['cagr_med']} p5 {m['cagr_p5']} dd {m['dd_med']}/{m['dd_p95']} dd30 {m['p_dd30']} añoneg {m['p_anio_neg']} sem+ {m['sem_pos_med']} (p5 {m['sem_pos_p5']}) >=1% {m['sem_mas1_med']} peor_sem_p5 {m['peor_sem_p5']}")
json.dump(out, open("mc.json", "w"), ensure_ascii=False)
