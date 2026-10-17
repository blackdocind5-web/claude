"""RR 1:0,2 con dos franjas por día: 09:30 o 09:45 + 11:00 (datos_v3/), ~1.000 USD de riesgo por trade.
Evaluación Lucid 25K Flex: +1.250 USD, consistencia 50% (mejor día), pérdida máxima 1.000 USD trailing de fin de día
(el nivel de quema queda fijo en el día; se quema si cualquier trade lo toca)."""
import random, statistics as st, collections
import fase1 as F, rr02 as R
OPS, _ = R.cargar(); EVAL = 65.30
DIAS = ["lun", "mar", "mié", "jue", "vie"]

def dias(h1, sl, filtro):
    d = collections.defaultdict(list)
    for o in OPS:
        if o["sl"] == sl and o["hora"] in (h1, "11:00") and filtro(o): d[o["ent"].date()].append(o)
    return [sorted(v, key=lambda o: o["ent"]) for k, v in sorted(d.items())]

def usd(o): return o["pnl"] * F.contratos(o["sl"])

def intento(D, i, maxd=60):
    sal = pico = 0.0; pd = []
    for n, dia in enumerate(D[i:i + maxd], 1):
        piso = pico - 1000; hoy = 0.0
        for o in dia:
            sal += usd(o); hoy += usd(o)
            if sal <= piso + 1e-9: return "quemada", n
        pd.append(hoy); pico = max(pico, sal)
        if sal >= F.OBJ and max(pd) <= 0.5 * sal + 1e-9: return "pasa", n
    return "sin terminar", n

def evaluar(D):
    r = [intento(D, i) for i in range(len(D))]; r = [x for x in r if x[0] != "sin terminar"]
    p = [x[1] for x in r if x[0] == "pasa"]; q = [x[1] for x in r if x[0] == "quemada"]
    return dict(n=len(r), pasa=100 * len(p) / len(r), dmed=st.median(p) if p else None, qmed=st.median(q) if q else None)

def cadena(D):
    """Evaluaciones en orden real: al pasar o quemarse se compra otra al día siguiente."""
    i = pases = evals = 0
    while i < len(D):
        res, n = intento(D, i)
        if res == "sin terminar": break
        evals += 1; pases += res == "pasa"; i += n
    return evals, pases

def nulo(D, reps=200):
    """Mismos días y tamaños; cada trade gana al azar con el win rate de equilibrio de su franja (sin ventaja)."""
    eqs = {}
    for h in {o["hora"] for d in D for o in d}:
        x = [o for d in D for o in d if o["hora"] == h]; eqs[h] = R.eq(x) / 100
    G = {h: [o["pnl"] for d in D for o in d if o["hora"] == h and o["gana"]][0] for h in eqs}
    P = {h: [o["pnl"] for d in D for o in d if o["hora"] == h and not o["gana"]][0] for h in eqs}
    rs = sorted(evaluar([[dict(o, pnl=G[o["hora"]] if random.random() < eqs[o["hora"]] else P[o["hora"]]) for o in d] for d in D])["pasa"] for _ in range(reps))
    return st.mean(rs), rs[int(.95 * reps)]

def resumen(nom, D):
    t = [o for d in D for o in d]; tipo = collections.Counter("".join("G" if o["gana"] else "P" for o in d) for d in D)
    dd = [sum(usd(o) for o in d) for d in D]
    eq = 0; pk = 0; mdd = 0
    for x in dd: eq += x; pk = max(pk, eq); mdd = min(mdd, eq - pk)
    racha = m = 0
    for x in dd: racha = racha + 1 if x < 0 else 0; m = max(m, racha)
    ev = evaluar(D); a = {y: evaluar([d for d in D if d[0]["anio"] == y])["pasa"] for y in (2025, 2026)}
    e, p = cadena(D)
    print(f"  {nom:44} días {len(D)} trades {len(t)} WR {100*sum(o['gana'] for o in t)/len(t):.1f}% | días: GG {tipo['GG']} GP/PG {tipo['GP']+tipo['PG']} PP {tipo['PP']} solo1 {sum(v for k,v in tipo.items() if len(k)==1)} "
          f"| neto {sum(dd):+.0f} USD, peor caída {mdd:.0f}, racha días neg {m} | pasa {ev['pasa']:.1f}% (2025 {a[2025]:.1f} / 2026 {a[2026]:.1f}) días med {ev['dmed']} quema med {ev['qmed']} | cadena {p} pases/{e} evals = {e*EVAL/max(p,1):.0f} USD por cuenta")

FIL = [("todos los días", lambda o: True),
       ("sin feriados, receso ni discursos", lambda o: o["cat"] not in R.E.FUERA),
       ("+ sin noticias 10:00", lambda o: o["cat"] not in R.E.FUERA and not o["cat"].startswith("Noticia 10:00")),
       ("+ sin noticias 08:30 ni 10:00", lambda o: o["cat"] not in R.E.FUERA and not o["cat"].startswith(("Noticia 10:00", "Noticia 08:30")))]

if __name__ == "__main__":
    random.seed(11)
    for sl in (70, 60):
        x = sorted([o for o in OPS if o["hora"] == "11:00" and o["sl"] == sl], key=lambda o: o["ent"])
        a = {y: [o for o in x if o["anio"] == y] for y in (2025, 2026)}
        print(f"11:00 SL {sl}: n {len(x)} WR {100*sum(o['gana'] for o in x)/len(x):.1f}% (2025 {100*sum(o['gana'] for o in a[2025])/len(a[2025]):.1f} / 2026 {100*sum(o['gana'] for o in a[2026])/len(a[2026]):.1f}) eq {R.eq(x):.1f} racha {R.racha(x)} USD/micro {sum(o['pnl'] for o in x):+.0f}")
        print("   por día:", " ".join(f"{DIAS[k]} {100*sum(o['gana'] for o in x if o['dia']==k)/sum(1 for o in x if o['dia']==k):.1f}%" for k in range(5)),
              "| cat:", "; ".join(f"{c[:14]} {100*sum(o['gana'] for o in x if o['cat']==c)/sum(1 for o in x if o['cat']==c):.0f}%({sum(1 for o in x if o['cat']==c)})" for c in sorted({o['cat'] for o in x})))
        for h in ("09:30", "09:45"):
            y = sorted([o for o in OPS if o["hora"] == h and o["sl"] == sl], key=lambda o: o["ent"])
            print(f"   {h} SL {sl}: WR {100*sum(o['gana'] for o in y)/len(y):.1f}% racha {R.racha(y)}")
    for h1 in ("09:30", "09:45"):
        for sl in (70, 60):
            print(f"\n{h1} + 11:00 · SL {sl} (pérdida −{-F.contratos(sl)*[o for o in OPS if o['sl']==sl and not o['gana']][0]['pnl']:.0f} / ganada +{F.contratos(sl)*[o for o in OPS if o['sl']==sl and o['gana'] and o['pnl']<40][0]['pnl']:.0f})")
            for fn, f in FIL:
                D = dias(h1, sl, f); resumen(fn, D)
            D = dias(h1, sl, FIL[2][1]); m, p95 = nulo(D)
            print(f"  sin ventaja (filtro sin 10:00): pasa {m:.1f}% (p95 {p95:.1f}%)")
