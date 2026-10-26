"""Motor de evaluación con pérdida flotante (26/10/2026). Lucid quema la cuenta si el saldo CON lo abierto toca el MLL
(pico de cierre diario − MLL), no solo al cerrar el trade. Cada trade lleva, por micro: u1 (resultado neto), m1
(peor flotante, desviación adversa de TradingView, ≤ 0) y perd1 (pérdida en SL con costos, para dimensionar).
Si dos trades se solapan en el tiempo, se suman sus peores flotantes (supuesto conservador).
Estrategias: Rascacielos (MNQ 09:45 SL50 + 11:00 SL70), Mica (XAU NY, MGC), Alex (MNQ, Fibonacci + VWAP)."""
import csv, glob, os, re, random, collections, datetime as dt
import combo3 as C, rr02 as R, rr04, xau2 as X, alex as A
AQUI = os.path.dirname(os.path.abspath(__file__))
CUENTAS = {"25K": dict(obj=1250, mll=1000, maxq=20, precio=65.30), "50K": dict(obj=3000, mll=2000, maxq=40, precio=115.0)}

def leer_tv(f):
    filas = list(csv.DictReader(open(f, encoding="utf-8-sig"))); sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}
    for r in filas:
        if not r["Tipo"].startswith("Entrada"): continue
        s = sal[r["Número de operación"]]; p = lambda x: dt.datetime.strptime(x[:16], "%Y-%m-%d %H:%M")
        yield dict(ent=p(r["Fecha y hora"]), sal=p(s["Fecha y hora"]), q=int(r["Tamaño (cant.)"]), res=s["Señal"],
                   lado=1 if "largo" in r["Tipo"] else -1, pe=float(r["Precio USD"]), ps=float(s["Precio USD"]),
                   mae=float(r["Desviación adversa USD"]), mfe=float(r["Desviación favorable USD"]), pnl=float(r["PyG netas USD"]))

def base(o, ses):
    return dict(ses=ses, anio=ses.year, cat=C.F.categoria(ses, C.CAL), evs=" ".join(x for _, x in C.CAL.get(ses, [])))

def rascacielos():
    mae = {}
    for f in glob.glob(os.path.join(AQUI, "datos_v7", "*.csv")):
        for t in leer_tv(f): mae[("09:45", 50, t["ent"].date())] = (t["mae"] / t["q"], t["sal"])
    for f in glob.glob(os.path.join(AQUI, "datos_v3", "*11.00h_SL_70*.csv")):
        for t in leer_tv(f): mae.setdefault(("11:00", 70, t["ent"].date()), (t["mae"] / t["q"], t["sal"]))
    V3, _ = R.cargar(); v = []
    for o in rr04.OPS + [x for x in V3 if x["hora"] == "11:00" and x["sl"] == 70]:
        m, s = mae[(o["hora"], o["sl"], o["ent"].date())]; p1 = 101.5 if o["sl"] == 50 else 141.0
        v.append(dict(base(o, o["ent"].date()), ent=o["ent"], sal=s, u1=o["pnl"], m1=min(m, o["pnl"], 0.0), perd1=p1, sl_hit=o["pnl"] <= -p1 + 1e-9, pata="Rascacielos"))
    return v

def mica(archivo="xau_v2/XAUUSD_sesion_NY_1R.csv", obj=1.0):
    v = []; vistos = set()
    for t in leer_tv(os.path.join(AQUI, archivo)):
        ses = C.sesion(t["ent"])
        if ses in vistos: continue          # solo el primer trade del día
        vistos.add(ses); mov = t["lado"] * (t["ps"] - t["pe"])
        if t["res"] == "SL": d = -mov
        elif t["res"] == "TP": d = mov / obj
        else:
            d = X.DIST.get(("NY", t["ent"])); d = sorted(d)[len(d) // 2] if d else 100 / t["q"]
        Rr = mov / d; maeR = t["mae"] / (t["q"] * d); sl = t["res"] == "SL"
        u1 = X.VAL * d * Rr - X.COM - (X.DESL if sl else 0)
        v.append(dict(base(t, ses), ent=t["ent"], sal=t["sal"], R=Rr, res=t["res"], u1=u1, m1=min(X.VAL * d * maeR, u1, 0.0),
                      perd1=X.VAL * d + X.COM + X.DESL, sl_hit=sl, pata="Mica"))
    return v

def alex(nombre):
    f = [g for g in glob.glob(os.path.join(AQUI, "alex", "*.csv")) if A.nombre(g) == nombre][0]; v = []
    for t in leer_tv(f):
        mov = t["lado"] * (t["ps"] - t["pe"]); d = abs(mov) if t["res"] in ("SL", "TP") and mov else 10000 / (A.PV * t["q"])
        Rr = mov / d; sl = t["res"] == "SL"; u1 = A.PV * d * Rr - A.COM - (A.DESL if sl else 0)
        v.append(dict(base(t, t["ent"].date()), ent=t["ent"], sal=t["sal"], R=Rr, res=t["res"], u1=u1,
                      m1=min(t["mae"] / t["q"], u1, 0.0),
                      perd1=A.PV * d + A.COM + A.DESL, sl_hit=sl, pata="Alex"))
    return v

def dias(patas, cuenta="25K"):
    """patas: lista de (trades, riesgo, filtro). Devuelve días con micros, usd y peor flotante por trade."""
    mx = CUENTAS[cuenta]["maxq"]; d = collections.defaultdict(list)
    for ops, r, f in patas:
        for o in ops:
            if not f(o): continue
            q = min(mx, int(r / o["perd1"] + 1e-9))
            if q: d[o["ses"]].append(dict(o, q=q, usd=q * o["u1"], mae=q * o["m1"]))
    return [sorted(v, key=lambda o: o["ent"]) for _, v in sorted(d.items())]

def dia(sal, piso, trades, flotante=True):
    """recorre el día; devuelve (saldo final, quemada)"""
    abiertos = []
    for o in trades:
        for a in [a for a in abiertos if a["sal"] <= o["ent"]]: sal += a["usd"]; abiertos.remove(a)
        if sal <= piso + 1e-9: return sal, True
        peor = sal + (o["mae"] + sum(a["mae"] for a in abiertos) if flotante else 0)
        if peor <= piso + 1e-9: return sal + o["usd"] + sum(a["usd"] for a in abiertos), True
        abiertos.append(o)
    sal += sum(a["usd"] for a in abiertos)
    return sal, sal <= piso + 1e-9

def intento(D, i, obj, mll, cons, flotante=True, maxd=300, **_):
    sal = pico = 0.0; pd = []
    for n, d_ in enumerate(D[i:i + maxd], 1):
        antes = sal; sal, q = dia(sal, pico - mll, d_, flotante)
        if q: return "quemada", n
        pd.append(sal - antes); pico = max(pico, sal)
        if sal >= obj and max(pd) <= cons * sal + 1e-9: return "pasa", n
    return "sin terminar", n

def montecarlo(D, obj, mll, cons, n=3000, seed=1, flotante=True, **_):
    rnd = random.Random(seed); pasa = 0; dd = []
    for _ in range(n):
        sal = pico = 0.0; pd = []
        for k in range(1, 800):
            d_ = rnd.choice(D)
            antes = sal; sal, q = dia(sal, pico - mll, d_, flotante)
            if q: break
            pd.append(sal - antes); pico = max(pico, sal)
            if sal >= obj and max(pd) <= cons * sal + 1e-9: pasa += 1; dd.append(k); break
    dd.sort()
    return 100 * pasa / n, dd[len(dd) // 2] if dd else None

def cadena(D, **kw):
    i = 0; res = []
    while i < len(D):
        r, n = intento(D, i, **kw)
        if r == "sin terminar": break
        a, b = D[i][0]["ses"], D[i + n - 1][0]["ses"]
        res.append((r, sum(1 for k in range((b - a).days + 1) if (a + dt.timedelta(k)).weekday() < 5))); i += n
    m = c = 0
    for r, _ in res: c = c + 1 if r == "quemada" else 0; m = max(m, c)
    return res, m

def ficha(nombre, patas, cuenta="25K", cons=0.4, n=3000):
    cu = CUENTAS[cuenta]; D = dias(patas, cuenta); kw = dict(obj=cu["obj"], mll=cu["mll"], cons=cons)
    p, d = montecarlo(D, n=n, **kw); p0, _ = montecarlo(D, n=n, flotante=False, **kw)
    y = {a: montecarlo([x for x in D if x[0]["anio"] == a], n=n // 2, **kw)[0] for a in (2025, 2026)}
    res, peor = cadena(D, **kw); pa = sorted(h for r, h in res if r == "pasa")
    return dict(nombre=nombre, cuenta=cuenta, pasa=p, sin_flot=p0, p25=y[2025], p26=y[2026], dias_trade=d, dias=len(D),
                hab=round(d * 464 / len(D)) if d else None, hab_cad=pa[len(pa) // 2] if pa else None,
                cadena=f"{len(pa)}/{len(res)}", peor=peor, costo=100 / p * cu["precio"] if p else None)
