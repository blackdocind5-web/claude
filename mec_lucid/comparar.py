"""Cuadro comparativo de estrategias para la fase 1 de Lucid Flex (25K y 50K, consistencia 40% o 50%), con el calendario
económico NY 2025–2026 (misma regla para MNQ y XAU: no operar feriado/receso, discurso 09–11, noticia 10:00, CPI o PIB).
  · Rascacielos: MNQ 09:45 SL 50 / TP 14 + 11:00 SL 70 / TP 14 (micros = piso(riesgo / pérdida por micro)).
  · Mica: XAUUSD sesión NY, 1R, solo el primer trade del día, en MGC (micros = piso(riesgo / (10 × distancia del SL))).
Cada trade lleva su resultado por micro; el tamaño sale del riesgo elegido y del máximo de micros de la cuenta."""
import collections, datetime as dt, random
import rr02 as R, combo3 as C, rr04, xau2 as X

CUENTAS = {"25K": dict(obj=1250, mll=1000, maxq=20), "50K": dict(obj=3000, mll=2000, maxq=40)}

def rascacielos():
    v = [dict(o, u1=o["pnl"], perd1=101.5, sl_hit=o["pnl"] <= -101.5) for o in rr04.OPS]
    V3, _ = R.cargar()
    v += [dict(o, ses=o["ent"].date(), u1=o["pnl"], perd1=141.0, sl_hit=o["pnl"] <= -141) for o in V3 if o["hora"] == "11:00" and o["sl"] == 70]
    return v

def mica():
    return [dict(o, perd1=X.VAL * o["dist"] + X.COM + X.DESL, sl_hit=o["res"] == "SL") for o in X.T[("NY", "1R")] if o["n"] == 1]

def usd_ras(o, q): return q * o["u1"]
def usd_mica(o, q): return X.usd(o, 1e9 if q is None else 0) if False else q * (X.VAL * o["dist"] * o["R"] - X.COM - (X.DESL if o["R"] <= -0.99 else 0))

ESTR = {"Rascacielos": (rascacielos(), usd_ras), "Mica": (mica(), usd_mica)}

def dias(nom, riesgo, maxq, filtro=C.regla):
    ops, f = ESTR[nom]; d = collections.defaultdict(list)
    for o in ops:
        if not filtro(o): continue
        q = min(maxq, int(riesgo / o["perd1"] + 1e-9)) if nom == "Rascacielos" else min(maxq, int(riesgo / (X.VAL * o["dist"]) + 1e-9))
        if q == 0: continue
        d[o["ses"]].append(dict(o, q=q, usd=f(o, q)))
    return [sorted(v, key=lambda o: o["ent"]) for _, v in sorted(d.items())]

def intento(D, i, obj, mll, cons, estricto=False, maxd=200):
    sal = pico = 0.0; pd = []
    for n, dia in enumerate(D[i:i + maxd], 1):
        piso = pico - mll; hoy = 0.0
        for o in dia:
            sal += o["usd"]; hoy += o["usd"]
            if sal <= piso + 1e-9 or (estricto and o["sl_hit"]): return "quemada", n
        pd.append(hoy); pico = max(pico, sal)
        if sal >= obj and max(pd) <= cons * sal + 1e-9: return "pasa", n
    return "sin terminar", n

def habiles(a, b): return sum(1 for k in range((b - a).days + 1) if (a + dt.timedelta(k)).weekday() < 5)

def cadena(D, **kw):
    i = 0; res = []
    while i < len(D):
        r, n = intento(D, i, **kw)
        if r == "sin terminar": break
        res.append((r, n, habiles(D[i][0]["ses"], D[i + n - 1][0]["ses"]))); i += n
    m = c = 0
    for r, _, _ in res: c = c + 1 if r == "quemada" else 0; m = max(m, c)
    return res, m

def montecarlo(D, n=4000, seed=1, nulo=None, **kw):
    """días sorteados con reposición; nulo = función que reemplaza el usd de un trade por un sorteo sin ventaja"""
    rnd = random.Random(seed); pasa = 0; dd = []
    for _ in range(n):
        sal = pico = 0.0; pd = []
        for k in range(1, 600):
            dia = rnd.choice(D); piso = pico - kw["mll"]; hoy = 0.0; q = False
            for o in dia:
                u, sl = nulo(o, rnd) if nulo else (o["usd"], o["sl_hit"])
                sal += u; hoy += u
                if sal <= piso + 1e-9 or (kw.get("estricto") and sl): q = True; break
            if q: break
            pd.append(hoy); pico = max(pico, sal)
            if sal >= kw["obj"] and max(pd) <= kw["cons"] * sal + 1e-9: pasa += 1; dd.append(k); break
    dd.sort()
    return 100 * pasa / n, dd[len(dd) // 2] if dd else None

def nulo_de(nom, D):
    """sin ventaja: cada trade gana o pierde con la probabilidad de equilibrio de su franja (ganada y pérdida reales)"""
    if nom == "Mica":
        return lambda o, r: ((o["q"] * (X.VAL * o["dist"] - X.COM), False) if r.random() < .5 else (-o["q"] * (X.VAL * o["dist"] + X.COM + X.DESL), True))
    def f(o, r):
        g, p = 27.0, o["perd1"]; return (o["q"] * g, False) if r.random() < p / (g + p) else (-o["q"] * p, True)
    return f
