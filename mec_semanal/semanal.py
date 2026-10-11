"""Pre NY, cartera real (XAUUSD E, EURUSD ES, GBPUSD S; costos Multibank; sin enero; lunes a jueves):
¿se puede cerrar cada semana entre +0,9% y +1,8% con escalera y freno al alcanzar el objetivo semanal?"""
import itertools, json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(AQUI, "..", "mec_diario"))
import diario as Dd, costos as Co
B = Dd.B; S = Co.stops(); PIP = 0.0001
MB = dict(XAUUSD=0.05, EURUSD=0.4 * PIP, GBPUSD=0.8 * PIP, BTC_spread=50, fee_btc=0)
T = B.cargar()
REAL = sorted(Co.aplicar([t for a in ("XAUUSD", "EURUSD", "GBPUSD") for t in T[a]], MB, S), key=lambda t: (t["ent"], B.H.ACTIVOS.index(t["a"])))
if __name__ == "__main__":
    rows = []
    for base, tope, obj, es, fr in itertools.product((0.25, 0.5, 0.75, 1.0, 1.25), (0, 1, 2, 3, 4), (None, 0.9, 1.8), (True, False), (None, "3R")):
        if tope == 0 and not es: continue
        freno = 2.7 * base if fr else None
        r = Dd.simular(REAL, base=base, tope=tope, obj_sem=obj, escalera_sem=es, freno=freno)
        rows.append(dict(base=base, tope=tope, obj_sem=obj, esc_sem=es, freno=fr, **{k: v for k, v in r.items() if k != "niveles"}))
    json.dump(rows, open(os.path.join(AQUI, "grilla.json"), "w"))
    print("semanas con operaciones", rows[0]["sem_n"])
    hdr = "base tope obj escSem freno | cagr mdd 25 26 | sem+ sem>=0,9 obj% neg% peor_sem p10 | maxr abierto"
    f = lambda r: f"{r['base']} {r['tope']} {r['obj_sem']} {int(r['esc_sem'])} {r['freno']} | {r['cagr']:6} {r['mdd']:5} {r['anios'].get('2025')} {r['anios'].get('2026')} | {r['sem_pos']} {r['sem_09']} {r['sem_obj']} {r['sem_neg']} {r['peor_sem']} {r['peor_sem_p10']} | {r['max_riesgo']} {r['max_abierto']}"
    for obj in (0.9, 1.8):
        print(f"== objetivo {obj}% · escalera vuelve a la base cada lunes · sin freno de pérdida"); print(hdr)
        for r in rows:
            if r["obj_sem"] == obj and r["esc_sem"] and r["freno"] is None and r["base"] in (0.25, 0.5, 0.75, 1.0): print(f(r))
    print("== referencia sin objetivo, fijo"); print(hdr)
    for r in rows:
        if r["obj_sem"] is None and r["tope"] == 0: print(f(r))
