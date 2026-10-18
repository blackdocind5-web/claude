"""SL 50 / TP 14, 9 micros por trade (+243 / −913,5): 09:45 (datos_v7/) + 11:00 (datos_v8/). Dos pérdidas el mismo día queman."""
import csv, glob, os, random, collections, datetime as dt
import fase1 as F, rr02 as R, combo3 as C, rr04
AQUI = os.path.dirname(os.path.abspath(__file__))

def cargar8():
    ops = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "datos_v8", "*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if not r["Tipo"].startswith("Entrada"): continue
            t = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M")
            if t.year < 2025 or t.strftime("%H:%M") != "11:00": continue
            pnl = float(r["PyG netas USD"])
            ops.setdefault(t.date(), dict(hora="11:00", sl=50, tp=14, ent=t, ses=t.date(), pnl=pnl, gana=pnl > 0, anio=t.year,
                                          cat=F.categoria(t.date(), C.CAL), dia=t.weekday(), lado="largo" if "largo" in r["Tipo"] else "corto"))
    return list(ops.values())

O11 = cargar8(); OPS = rr04.OPS + O11; C.OPS = OPS
n10 = lambda o: o["cat"].startswith("Noticia 10:00")
base = lambda o: o["cat"] not in R.E.FUERA

if __name__ == "__main__":
    random.seed(8)
    d945 = {o["ses"] for o in rr04.OPS}; d11 = {o["ses"] for o in O11}
    print("09:45 sin 11:00:", sorted(d945 - d11), "| 11:00 sin 09:45:", sorted(d11 - d945), "| raros 11:00:", [(o["ses"], o["pnl"]) for o in O11 if o["pnl"] not in (27, -101.5)])
    wr = lambda v: 100 * sum(o["gana"] for o in v) / len(v)
    for h, x in (("09:45", rr04.OPS), ("11:00", O11)):
        a = {y: [o for o in x if o["anio"] == y] for y in (2025, 2026)}; xr = [o for o in x if C.regla(o)]
        print(f"{h}: n {len(x)} WR {wr(x):.1f}% (2025 {wr(a[2025]):.1f} / 2026 {wr(a[2026]):.1f}) eq {R.eq(x):.1f} racha {R.racha(x)} esperanza {sum(o['pnl'] for o in x)/len(x)*9:+.1f} | regla WR {wr(xr):.1f}% esperanza {sum(o['pnl'] for o in xr)/len(xr)*9:+.1f}")
        print("   día:", " ".join(f"{d} {wr([o for o in x if o['dia']==i]):.0f}%" for i, d in enumerate(["lun", "mar", "mié", "jue", "vie"])),
              "| cat:", "; ".join(f"{c[:16]} {wr([o for o in x if o['cat']==c]):.0f}%({sum(1 for o in x if o['cat']==c)})" for c in sorted({o['cat'] for o in x})))
    both = {d for d in d945 & d11}; a = {o["ses"]: o["gana"] for o in rr04.OPS}; b = {o["ses"]: o["gana"] for o in O11}
    pp = sum(1 for d in both if not a[d] and not b[d]); pa = 1 - sum(a[d] for d in both) / len(both); pb = 1 - sum(b[d] for d in both) / len(both)
    print(f"días con doble pérdida: {pp} de {len(both)} (si fueran independientes: {pa*pb*len(both):.1f})")
    V = [("09:45 sola, regla", ("09:45",), C.regla, None),
         ("11:00 sola, regla", ("11:00",), C.regla, None),
         ("09:45 + 11:00, todos los días", ("09:45", "11:00"), lambda o: True, None),
         ("09:45 + 11:00, regla (día entero)", ("09:45", "11:00"), C.regla, None),
         ("09:45 + 11:00, sin fer/rec/disc ni 10:00", ("09:45", "11:00"), lambda o: base(o) and not n10(o), None),
         ("regla, pero días 10:00 sí 11:00", ("09:45", "11:00"), lambda o: C.regla(o) or (n10(o) and o["hora"] == "11:00"), None)]
    for nom, hs, f, _ in V:
        D = C.dias(hs, f); e = C.resumen(nom, D)
        f2 = C.evaluar(D, obj=1000, cons=0, ndias=5); p1, p2 = e["pasa"] / 100, f2["pasa"] / 100; n, p, m, res = C.cadena(D)
        print(f"     fase 2 {f2['pasa']:.1f}% ({f2['dmed']} días) → retiro {100*p1*p2:.1f}% EV {p1*p2*500-65.3:+.0f} | evals/pase {1/p1:.2f} | 95%: {next(k for k in range(1,30) if 1-(1-p1)**k>=.95)} | {''.join('P' if r=='pasa' else 'x' for r,_,_ in res)}")
        print("     sin ventaja: pasa %.1f%% (p95 %.1f%%)" % C.nulo(D, reps=120))
