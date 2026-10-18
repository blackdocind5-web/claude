"""RR ~1:0,28 a las 09:45 (SL 50 / TP 14, datos_v7/). 9 micros (10 darían −1.015 USD: una pérdida quema la cuenta): ganada +243, perdida −913,5 (equilibrio ~79%).
Algunos trades se cierran al final de la sesión (16:00) sin tocar SL ni TP. Se ignora dic 2024."""
import csv, glob, os, random, collections, datetime as dt
import fase1 as F, rr02 as R, combo3 as C
AQUI = os.path.dirname(os.path.abspath(__file__))

def cargar7():
    ops = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "datos_v7", "*.csv"))):
        filas = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}
        for r in filas:
            if not r["Tipo"].startswith("Entrada"): continue
            t = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M")
            if t.year < 2025 or t.strftime("%H:%M") != "09:45": continue
            pnl = float(r["PyG netas USD"]); s = sal[r["Número de operación"]]
            ops.setdefault(t.date(), dict(hora="09:45", sl=50, tp=14, ent=t, ses=t.date(), pnl=pnl, gana=pnl > 0, anio=t.year,
                                          cierre=s["Señal"] == "Cierre sesión", cat=F.categoria(t.date(), C.CAL), dia=t.weekday(),
                                          lado="largo" if "largo" in r["Tipo"] else "corto"))
    return list(ops.values())

MICROS = int(os.environ.get("MICROS", 9)); _c = F.contratos; F.contratos = lambda sl: MICROS if sl == 50 else _c(sl)
OPS = cargar7(); C.OPS = OPS; K = F.contratos(50)

if __name__ == "__main__":
    random.seed(4)
    x = sorted(OPS, key=lambda o: o["ent"]); wr = lambda v: 100 * sum(o["gana"] for o in v) / len(v)
    print("n", len(x), "micros", K, "| cierre de sesión:", sum(o["cierre"] for o in x), "neto", sum(o["pnl"] for o in x if o["cierre"]),
          "| otros:", collections.Counter(o["pnl"] for o in x if o["pnl"] not in (27, -101.5) and not o["cierre"]))
    for nom, f in (("todos", lambda o: True), ("regla", C.regla)):
        v = [o for o in x if f(o)]; a = {y: [o for o in v if o["anio"] == y] for y in (2025, 2026)}
        print(f"{nom}: n {len(v)} WR {wr(v):.1f}% (2025 {wr(a[2025]):.1f} / 2026 {wr(a[2026]):.1f}) eq {R.eq(v):.1f} racha {R.racha(v)} esperanza {sum(o['pnl'] for o in v)/len(v)*K:+.1f} USD/trade")
    print("día:", " ".join(f"{d} {wr([o for o in x if o['dia']==i]):.0f}%" for i, d in enumerate(["lun", "mar", "mié", "jue", "vie"])),
          "| lado:", " ".join(f"{l} {wr([o for o in x if o['lado']==l]):.0f}%" for l in ("largo", "corto")))
    print("cat:", "; ".join(f"{c[:16]} {wr([o for o in x if o['cat']==c]):.0f}%({sum(1 for o in x if o['cat']==c)})" for c in sorted({o['cat'] for o in x})))
    m = collections.defaultdict(list)
    for o in x: m[o["ent"].strftime("%y-%m")].append(o["gana"])
    print("meses:", " ".join(f"{k} {100*sum(v)/len(v):.0f}" for k, v in sorted(m.items())))
    for nom, f in (("todos los días", lambda o: True), ("regla recomendada", C.regla),
                   ("sin feriados/receso/discursos", lambda o: o["cat"] not in R.E.FUERA),
                   ("sin feriados/receso/discursos ni 10:00", lambda o: o["cat"] not in R.E.FUERA and not o["cat"].startswith("Noticia 10:00"))):
        D = C.dias(("09:45",), f); e = C.resumen(nom, D)
        f2 = C.evaluar(D, obj=1000, cons=0, ndias=5); p1, p2 = e["pasa"] / 100, f2["pasa"] / 100
        n, p, mm, res = C.cadena(D)
        print(f"     fase 2 {f2['pasa']:.1f}% ({f2['dmed']} días) → primer retiro {100*p1*p2:.1f}% EV {p1*p2*500-65.3:+.0f} USD | evals/pase {1/p1:.2f} | 95%: {next(k for k in range(1,30) if 1-(1-p1)**k>=.95)} evals | {''.join('P' if r=='pasa' else 'x' for r,_,_ in res)}")
        print("     sin ventaja: pasa %.1f%% (p95 %.1f%%)" % C.nulo(D, reps=150))
