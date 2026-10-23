"""XAUUSD 'Rango Apertura' con datos completos (xau_v2/, TradingView premium, 12/01/2025–22/10/2026):
sesiones NY (09:30–11:00) y Asia (20:00–22:00, cuenta para el día hábil siguiente) × objetivos 0,7R, 1R, 2R sin
y con break even. Cada trade se normaliza a R con la distancia del SL (en precio) de esa misma entrada; en Lucid se
operaría con MGC (micro oro, 10 USD por punto, máx. 20 micros, comisión 0,50 USD por lado)."""
import csv, os, collections, datetime as dt
import combo3 as C
AQUI = os.path.dirname(os.path.abspath(__file__))
SES = ("NY", "Asia"); OBJ = {"0.7R": 0.7, "1R": 1.0, "2R_sin_break_even": 2.0, "2R_con_break_even": 2.0}

def leer(ses, obj):
    filas = list(csv.DictReader(open(os.path.join(AQUI, "xau_v2", f"XAUUSD_sesion_{ses}_{obj}.csv"), encoding="utf-8-sig")))
    sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}; ops = {}
    for r in filas:
        if not r["Tipo"].startswith("Entrada"): continue
        s = sal[r["Número de operación"]]; e = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M")
        lado = 1 if "largo" in r["Tipo"] else -1; pe, ps = float(r["Precio USD"]), float(s["Precio USD"])
        ops[e] = dict(ent=e, sal=dt.datetime.strptime(s["Fecha y hora"], "%Y-%m-%d %H:%M"), lado=lado, pe=pe, ps=ps,
                      mov=lado * (ps - pe), res=s["Señal"], pnl=float(r["PyG netas USD"]), q=int(r["Tamaño (cant.)"]))
    return ops

RAW = {(s, o): leer(s, o) for s in SES for o in OBJ}

def distancias():
    """distancia del SL por entrada, deducida de cualquier archivo donde el trade terminó en SL o TP"""
    d = collections.defaultdict(list)
    for (s, o), ops in RAW.items():
        for e, t in ops.items():
            if t["res"] == "SL": d[(s, e)].append(-t["mov"])
            elif t["res"] == "TP": d[(s, e)].append(t["mov"] / OBJ[o])
    return d

DIST = distancias()
CAL = C.CAL; VAL = 10.0; MAXQ = 20; COM = 1.0; DESL = 1.0   # MGC: 10 USD/punto; comisión ida y vuelta y 1 tick de deslizamiento en SL, por micro

def trades(ses, obj):
    v = []
    for e, t in sorted(RAW[(ses, obj)].items()):
        d = DIST.get((ses, e)); d = sorted(d)[len(d) // 2] if d else 100 / t["q"]
        s = C.sesion(e)
        v.append(dict(t, ses_nom=ses, obj=obj, ses=s, anio=s.year, dist=d, R=t["mov"] / d, cat=C.F.categoria(s, CAL),
                      evs=" ".join(x for _, x in CAL.get(s, []))))
    n = collections.Counter()
    for o in v: n[o["ses"]] += 1; o["n"] = n[o["ses"]]
    return v

T = {(s, o): trades(s, o) for s in SES for o in OBJ}

def regla(o):   # misma regla que el MNQ: sin feriado/receso, discurso 09–11, noticia 10:00, CPI o PIB
    c = o["cat"]
    return not (c in ("Feriado o receso", "Discurso 09:00–11:00") or c.startswith("Noticia 10:00") or
                (c.startswith("Noticia 08:30") and ("CPI" in o["evs"] or "PIB" in o["evs"])))

def micros(o, riesgo): return min(MAXQ, int(riesgo / (VAL * o["dist"]) + 1e-9))
def usd(o, riesgo, R=None):
    q = micros(o, riesgo); R = o["R"] if R is None else R
    return q * VAL * o["dist"] * R - q * COM - (q * DESL if R <= -0.99 else 0)

def dias(sesiones, obj, riesgo, filtro=lambda o: True, solo1=True):
    d = collections.defaultdict(list)
    for s in sesiones:
        for o in T[(s, obj)]:
            if (solo1 and o["n"] > 1) or not filtro(o) or micros(o, riesgo) == 0: continue
            d[o["ses"]].append(dict(o, usd=usd(o, riesgo)))
    return [sorted(v, key=lambda o: o["ent"]) for _, v in sorted(d.items())]

def intento(D, i, obj=1250, cons=0.5, maxd=120, estricto=False):
    sal = pico = 0.0; pd = []
    for n, dia in enumerate(D[i:i + maxd], 1):
        piso = pico - 1000; hoy = 0.0
        for o in dia:
            sal += o["usd"]; hoy += o["usd"]
            if sal <= piso + 1e-9 or (estricto and o["R"] <= -0.99): return "quemada", n
        pd.append(hoy); pico = max(pico, sal)
        if sal >= obj and max(pd) <= cons * sal + 1e-9: return "pasa", n
    return "sin terminar", n

def evaluar(D, **kw):
    r = [x for x in (intento(D, i, **kw) for i in range(len(D))) if x[0] != "sin terminar"]
    p = sorted(x[1] for x in r if x[0] == "pasa")
    return dict(n=len(r), pasa=100 * len(p) / len(r) if r else 0, dmed=p[len(p) // 2] if p else None)

def cadena(D, **kw):
    i = 0; res = []
    while i < len(D):
        r, n = intento(D, i, **kw)
        if r == "sin terminar": break
        res.append(r); i += n
    m = c = 0
    for r in res: c = c + 1 if r == "quemada" else 0; m = max(m, c)
    return len(res), res.count("pasa"), m

def nulo(D, obj, riesgo, reps=60, **kw):
    """sin ventaja: cada trade es SL o TP con la probabilidad de equilibrio (se mantiene la proporción de break even)"""
    import random
    t = OBJ[obj]; be = sum(abs(o["R"]) < 0.2 for d in D for o in d) / sum(len(d) for d in D) if "con" in obj else 0
    def sorteo(o):
        u = random.random(); R = 0.0 if u < be else (t if random.random() < 1 / (1 + t) else -1.0)
        return dict(o, R=R, usd=usd(o, riesgo, R))
    rs = sorted(evaluar([[sorteo(o) for o in d] for d in D], **kw)["pasa"] for _ in range(reps))
    return sum(rs) / reps, rs[int(.95 * reps)]

def montecarlo(D, obj, riesgo, n=3000, nulo=False, estricto=False, seed=1):
    """evaluaciones con días sorteados (con reposición) de D; nulo=True reemplaza el resultado por un sorteo sin ventaja"""
    import random
    rnd = random.Random(seed); t = OBJ[obj]
    be = sum(abs(o["R"]) < 0.2 for d in D for o in d) / sum(len(d) for d in D) if "con" in obj else 0
    def R(o):
        if not nulo: return o["usd"], o["R"]
        u = rnd.random(); r = 0.0 if u < be else (t if rnd.random() < 1 / (1 + t) else -1.0)
        return usd(o, riesgo, r), r
    pasa = 0; dd = []
    for _ in range(n):
        sal = pico = 0.0; pd = []
        for k in range(1, 400):
            dia = rnd.choice(D); piso = pico - 1000; hoy = 0.0; fin = None
            for o in dia:
                u, r = R(o); sal += u; hoy += u
                if sal <= piso + 1e-9 or (estricto and r <= -0.99): fin = "q"; break
            if fin: break
            pd.append(hoy); pico = max(pico, sal)
            if sal >= 1250 and max(pd) <= 0.5 * sal + 1e-9: pasa += 1; dd.append(k); break
    dd.sort()
    return 100 * pasa / n, dd[len(dd) // 2] if dd else None
