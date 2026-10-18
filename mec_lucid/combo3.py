"""Tercera franja para la estrategia RR 1:0,2 (SL 70/TP 14, ~1.000 USD por trade): 12:00 o 20:00 (datos_v4/).
El trade de las 20:00 pertenece a la sesión del día hábil siguiente (CME abre a las 18:00), así que el día operativo es
20:00 (noche anterior) → 09:45 → 11:00 → 12:00. Calendario y año por día de sesión. Se ignora dic 2024."""
import csv, glob, os, random, statistics as st, collections, datetime as dt, math
import fase1 as F, rr02 as R
AQUI = os.path.dirname(os.path.abspath(__file__)); CAL = F.calendario(); EVAL = 65.30

def sesion(t):
    if t.hour < 18: return t.date()
    d = t.date() + dt.timedelta(days=1)
    while d.weekday() >= 5: d += dt.timedelta(days=1)
    return d

def cargar4():
    ops = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "datos_v4", "*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if not r["Tipo"].startswith("Entrada"): continue
            t = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M"); s = sesion(t)
            if s.year < 2025 or t.hour not in (12, 20): continue
            h = f"{t.hour}:00"; pnl = float(r["PyG netas USD"])
            ops.setdefault((h, s), dict(hora=h, sl=70, tp=14, ent=t, ses=s, pnl=pnl, gana=pnl > 0, anio=s.year,
                                        cat=F.categoria(s, CAL), dia=s.weekday(), lado="largo" if "largo" in r["Tipo"] else "corto"))
    return list(ops.values())

V3, _ = R.cargar()
for o in V3: o["ses"] = o["ent"].date()
OPS = [o for o in V3 if o["sl"] == 70] + cargar4()

def ev(o): return " ".join(e for _, e in CAL.get(o["ses"], []))
def regla(o):   # regla recomendada (no operar: feriado/receso, discurso 09–11, noticia 10:00, CPI o PIB)
    c = o["cat"]
    return not (c in R.E.FUERA or c.startswith("Noticia 10:00") or (c.startswith("Noticia 08:30") and ("CPI" in ev(o) or "PIB" in ev(o))))
def usd(o): return o["pnl"] * F.contratos(o["sl"])

def dias(horas, filtro=lambda o: True, filtro20=None):
    d = collections.defaultdict(list)
    for o in OPS:
        if o["hora"] not in horas: continue
        f = filtro20 if (o["hora"] == "20:00" and filtro20) else filtro
        if f(o): d[o["ses"]].append(o)
    return [sorted(v, key=lambda o: o["ent"]) for k, v in sorted(d.items())]

def intento(D, i, obj=F.OBJ, cons=0.5, ndias=0, maxd=80):
    sal = pico = 0.0; pd = []
    for n, dia in enumerate(D[i:i + maxd], 1):
        piso = pico - 1000; hoy = 0.0
        for o in dia:
            sal += usd(o); hoy += usd(o)
            if sal <= piso + 1e-9: return "quemada", n
        pd.append(hoy); pico = max(pico, sal)
        if sal >= obj and (not cons or max(pd) <= cons * sal + 1e-9) and sum(x >= 100 for x in pd) >= ndias: return "pasa", n
    return "sin terminar", n

def evaluar(D, **kw):
    r = [intento(D, i, **kw) for i in range(len(D))]; r = [x for x in r if x[0] != "sin terminar"]
    p = [x[1] for x in r if x[0] == "pasa"]; q = [x[1] for x in r if x[0] == "quemada"]
    return dict(n=len(r), pasa=100 * len(p) / len(r), dmed=st.median(p) if p else None, qmed=st.median(q) if q else None)

def cadena(D, **kw):
    i = 0; res = []
    while i < len(D):
        r, n = intento(D, i, **kw)
        if r == "sin terminar": break
        res.append((r, n, D[i][0]["ses"])); i += n
    pases = sum(r == "pasa" for r, _, _ in res); m = c = 0
    for r, _, _ in res: c = c + 1 if r == "quemada" else 0; m = max(m, c)
    return len(res), pases, m, res

def nulo(D, reps=150, **kw):
    eqs = {h: R.eq([o for d in D for o in d if o["hora"] == h]) / 100 for h in {o["hora"] for d in D for o in d}}
    G = {h: collections.Counter(o["pnl"] for d in D for o in d if o["hora"] == h and o["gana"]).most_common(1)[0][0] for h in eqs}
    P = {h: min(o["pnl"] for d in D for o in d if o["hora"] == h) for h in eqs}
    rs = sorted(evaluar([[dict(o, pnl=G[o["hora"]] if random.random() < eqs[o["hora"]] else P[o["hora"]]) for o in d] for d in D], **kw)["pasa"] for _ in range(reps))
    return st.mean(rs), rs[int(.95 * reps)]

def franja(h):
    x = sorted([o for o in OPS if o["hora"] == h], key=lambda o: o["ent"]); wr = lambda v: 100 * sum(o["gana"] for o in v) / len(v)
    a = {y: [o for o in x if o["anio"] == y] for y in (2025, 2026)}; e = R.eq(x)
    w = [o["pnl"] for o in x if o["gana"]]; l = [o["pnl"] for o in x if not o["gana"]]
    k = F.contratos(70); E = (sum(o["pnl"] for o in x) / len(x)) * k
    xf = [o for o in x if regla(o)]
    print(f"{h}: n {len(x)} WR {wr(x):.1f}% (2025 {wr(a[2025]):.1f} / 2026 {wr(a[2026]):.1f}) eq {e:.1f} racha {R.racha(x)} "
          f"esperanza {E:+.1f} USD/trade ({E/ (k*141):+.3f} R) | con regla: n {len(xf)} WR {wr(xf):.1f}% esperanza {sum(o['pnl'] for o in xf)/len(xf)*k:+.1f}")
    print("   día:", " ".join(f"{d} {wr([o for o in x if o['dia']==i]):.0f}%" for i, d in enumerate(["lun", "mar", "mié", "jue", "vie"])),
          "| cat:", "; ".join(f"{c[:16]} {wr([o for o in x if o['cat']==c]):.0f}%({sum(1 for o in x if o['cat']==c)})" for c in sorted({o['cat'] for o in x})))

def resumen(nom, D, **kw):
    t = [o for d in D for o in d]; dd = [sum(usd(o) for o in d) for d in D]
    eq = pk = mdd = 0
    for x in dd: eq += x; pk = max(pk, eq); mdd = min(mdd, eq - pk)
    e = evaluar(D, **kw); a = {y: evaluar([d for d in D if d[0]["anio"] == y], **kw)["pasa"] for y in (2025, 2026)}
    n, p, m, _ = cadena(D, **kw); dobles = sum(sum(not o["gana"] for o in d) >= 2 for d in D)
    print(f"  {nom:40} días {len(D)} trades {len(t)} WR {100*sum(o['gana'] for o in t)/len(t):.1f}% días ≥2 pérdidas {dobles} | neto {sum(dd):+.0f} caída máx {mdd:.0f} "
          f"| pasa {e['pasa']:.1f}% (2025 {a[2025]:.1f} / 2026 {a[2026]:.1f}) días med {e['dmed']} quema med {e['qmed']} | cadena {p}/{n} (peor racha {m} quemadas)")
    return e

if __name__ == "__main__":
    random.seed(3)
    for h in ("09:45", "11:00", "12:00", "20:00"): franja(h)
    print("\nfaltan:", sorted({o["ses"] for o in OPS if o["hora"] == "09:45"} - {o["ses"] for o in OPS if o["hora"] == "12:00"}),
          sorted({o["ses"] for o in OPS if o["hora"] == "09:45"} - {o["ses"] for o in OPS if o["hora"] == "20:00"}))
    COMB = [("09:45 + 11:00", ("09:45", "11:00")), ("09:45 + 11:00 + 12:00", ("09:45", "11:00", "12:00")),
            ("20:00 + 09:45 + 11:00", ("20:00", "09:45", "11:00")), ("las cuatro", ("20:00", "09:45", "11:00", "12:00"))]
    for nom, hs in COMB:
        print(f"\n{nom}")
        resumen("todos los días", dias(hs))
        resumen("regla recomendada", dias(hs, regla))
        if "20:00" in hs: resumen("regla, pero la de 20:00 siempre", dias(hs, regla, lambda o: True))
        print("  sin ventaja (regla): pasa %.1f%% (p95 %.1f%%)" % nulo(dias(hs, regla)))
