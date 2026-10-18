"""Estrategia RR 1:0,1 (SL 140 / TP 14, datos_v5/): 09:45, 11:00 y 12:00 en un mismo archivo de TradingView.
3 micros (piso(1.000 / 280)): ganada +81 USD, perdida −844,5 USD. TradingView mantiene una sola posición: si el trade
de una franja sigue abierto, la franja siguiente no se toma (esos días tienen menos trades). Se ignora dic 2024."""
import csv, glob, os, random, statistics as st, collections, datetime as dt
import fase1 as F, rr02 as R, combo3 as C
AQUI = os.path.dirname(os.path.abspath(__file__)); HORAS = ("09:45", "11:00", "12:00")

def cargar5():
    ops = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "datos_v5", "*.csv"))):
        filas = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}
        for r in filas:
            if not r["Tipo"].startswith("Entrada"): continue
            t = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M"); h = t.strftime("%H:%M")
            if t.year < 2025 or h not in HORAS: continue
            s = dt.datetime.strptime(sal[r["Número de operación"]]["Fecha y hora"], "%Y-%m-%d %H:%M"); pnl = float(r["PyG netas USD"])
            ops.setdefault((h, t.date()), dict(hora=h, sl=140, tp=14, ent=t, sal=s, ses=t.date(), pnl=pnl, gana=pnl > 0, anio=t.year,
                                               cat=F.categoria(t.date(), C.CAL), dia=t.weekday(), lado="largo" if "largo" in r["Tipo"] else "corto"))
    return list(ops.values())

OPS = cargar5(); C.OPS = OPS
K = F.contratos(140)

def franja(h, filtro=lambda o: True):
    x = sorted([o for o in OPS if o["hora"] == h and filtro(o)], key=lambda o: o["ent"]); wr = lambda v: 100 * sum(o["gana"] for o in v) / len(v) if v else 0
    a = {y: [o for o in x if o["anio"] == y] for y in (2025, 2026)}
    E = sum(o["pnl"] for o in x) / len(x) * K; dur = st.median((o["sal"] - o["ent"]).total_seconds() / 60 for o in x)
    return f"{h}: n {len(x)} WR {wr(x):.1f}% (2025 {wr(a[2025]):.1f} / 2026 {wr(a[2026]):.1f}) eq {R.eq(x):.1f} racha {R.racha(x)} esperanza {E:+.1f} USD/trade duración med {dur:.0f} min"

if __name__ == "__main__":
    random.seed(9)
    print("micros", K, "| pérdidas parciales/otras:", sorted((o["ses"].strftime("%d/%m/%Y"), o["hora"], o["pnl"]) for o in OPS if o["pnl"] not in (27, -281.5)))
    tr = collections.Counter(sum(1 for o in OPS if o["ses"] == d) for d in {o["ses"] for o in OPS}); print("trades por día:", dict(tr))
    for h in HORAS:
        print(franja(h)); print("   con regla:", franja(h, C.regla))
        x = [o for o in OPS if o["hora"] == h]
        print("   día:", " ".join(f"{d} {100*sum(o['gana'] for o in x if o['dia']==i)/sum(1 for o in x if o['dia']==i):.0f}%" for i, d in enumerate(["lun", "mar", "mié", "jue", "vie"])),
              "| cat:", "; ".join(f"{c[:16]} {100*sum(o['gana'] for o in x if o['cat']==c)/sum(1 for o in x if o['cat']==c):.0f}%({sum(1 for o in x if o['cat']==c)})" for c in sorted({o['cat'] for o in x})))
    COMB = [("09:45", ("09:45",)), ("11:00", ("11:00",)), ("09:45 + 11:00", ("09:45", "11:00")), ("09:45 + 12:00", ("09:45", "12:00")),
            ("11:00 + 12:00", ("11:00", "12:00")), ("las tres", HORAS)]
    for nom, hs in COMB:
        print(f"\n{nom}")
        C.resumen("todos los días", C.dias(hs)); C.resumen("regla recomendada", C.dias(hs, C.regla))
        print("  sin ventaja (regla): pasa %.1f%% (p95 %.1f%%)" % C.nulo(C.dias(hs, C.regla), reps=100))
