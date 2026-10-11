import itertools, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_xau as X
Dd = X.Dd
def variante(p, hora9=True, sin_fomc=True, viernes=True):
    ts, _ = X.cargar(p)
    ts = [dict(t, a="XAUUSD_NY") for t in ts if t["ent"].month != 1 and (not hora9 or t["ent"].hour == 9)
          and (not sin_fomc or not any(g.startswith("FOMC") for g in t["tags"])) and (viernes or t["ent"].weekday() != 4)]
    return sorted(ts, key=lambda t: t["ent"])
V = variante("ES")
rows = []
for base, tope, obj, fr, es in itertools.product((0.5, 0.75, 1.0, 1.5), (0, 1, 2, 3), (None, 1.8), (None, 0.9, 1.8, 2.7, 3.6), (False, True)):
    if tope == 0 and es: continue
    r = Dd.simular(V, base=base, tope=tope, obj=None, freno=fr, obj_sem=obj, escalera_sem=es)
    rows.append(dict(base=base, tope=tope, obj_sem=obj, freno=fr, esc_sem=es, **{k: v for k, v in r.items() if k != "niveles"}))
json.dump(rows, open("grilla.json", "w"))
print("operaciones", len(V), "semanas con operaciones", rows[0]["sem_n"])
def show(f, t):
    print("==", t); print("base tope obj freno escSem | cagr mdd 25 26 | sem+ sem>=1% obj% peor_sem sem_med sem_neg_prom | maxr")
    for r in f: print(f"{r['base']} {r['tope']} {r['obj_sem']} {r['freno']} {int(r['esc_sem'])} | {r['cagr']:6} {r['mdd']:5} {r['anios'].get('2025')} {r['anios'].get('2026')} | {r['sem_pos']} {r['sem_mas1']} {r['sem_obj']} {r['peor_sem']} {r['sem_med']} {r['sem_neg_prom']} | {r['max_riesgo']}")
sel = lambda **kw: [r for r in rows if all(r[k] == v for k, v in kw.items())]
show(sel(base=1.0, esc_sem=False, obj_sem=None, freno=None) + sel(base=1.0, esc_sem=False, obj_sem=1.8, freno=None), "1%: escalera, sin y con objetivo +1,8%, sin freno")
show(sel(base=0.5, esc_sem=False, obj_sem=1.8, freno=None) + sel(base=0.5, esc_sem=True, obj_sem=1.8, freno=None), "0,5%: objetivo 1,8%, escalera continua vs reinicio semanal")
show(sel(base=1.0, tope=2, obj_sem=1.8, esc_sem=False) + sel(base=0.5, tope=3, obj_sem=1.8, esc_sem=False), "freno semanal (límite de pérdida)")
top = sorted([r for r in rows if r["anios"].get("2025", -1) > 0 and r["anios"].get("2026", -1) > 0], key=lambda r: (-r["sem_pos"], r["mdd"]))[:12]
show(top, "más semanas positivas (gana los dos años)")
