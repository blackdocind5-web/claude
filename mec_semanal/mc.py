import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semanal as SM
Dd = SM.Dd; REAL = SM.REAL
C = [("Actual: fijo 1%, freno −3R", dict(base=1.0, tope=0, freno=2.7))]
for base in (0.5, 0.75, 1.0):
    for tope in (1, 2):
        for obj in (0.9, 1.8):
            for fr in (None, 2.7):
                C.append((f"{base}% tope {tope} · objetivo {obj}% · freno {'−3R' if fr else 'no'}", dict(base=base, tope=tope, obj_sem=obj, escalera_sem=True, freno=fr * base if fr else None)))
out = []
for nom, kw in C:
    r = Dd.simular(REAL, **kw); m = Dd.montecarlo(REAL, sims=1000, **kw)
    out.append(dict(nombre=nom, kw=kw, r={k: v for k, v in r.items() if k != "niveles"}, mc=m))
    print(f"{nom:44} | hist {r['cagr']:5} dd {r['mdd']:4} sem+ {r['sem_pos']} ≥0,9 {r['sem_09']} | MC cagr {m['cagr_med']:5} p5 {m['cagr_p5']:5} dd {m['dd_med']}/{m['dd_p95']} añoneg {m['p_anio_neg']:4} sem+ {m['sem_pos_med']} (p5 {m['sem_pos_p5']}) ≥0,9 {m['sem_09_med']} obj {m['sem_obj_med']} peor_sem_p5 {m['peor_sem_p5']} peor_mes_p5 {m['peor_mes_p5']}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mc.json"), "w"), ensure_ascii=False)
