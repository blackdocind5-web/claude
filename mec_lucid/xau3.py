"""Mica con filtros de entrada (xau_v3/, TradingView sin interés compuesto, 13/01–23/10/2026, sesión NY, RR 1:1):
EMA 200, VWAP y EMA 200 + VWAP, con 1 o 2 entradas por sesión. EMA 200 + VWAP es idéntico byte a byte a VWAP en los dos
grupos. Cada trade a R con la distancia del SL (1R: |salida − entrada|); en cierre forzado se toma la distancia del mismo
trade en xau_v2/ o, si no está, 100 / cantidad (TradingView arriesga ~100 USD)."""
import csv, os, collections, datetime as dt
import combo3 as C, xau2 as X, comparar as K
AQUI = os.path.dirname(os.path.abspath(__file__))
VAR = {"EMA 200 · 1 entrada": "EMA_200_1_entrada", "EMA 200 · 2 entradas": "EMA_200_2_entradas",
       "VWAP · 1 entrada": "VWAP_1_entrada", "VWAP · 2 entradas": "VWAP_2_entradas"}
DESDE, HASTA = dt.date(2026, 1, 13), dt.date(2026, 10, 22)   # período común con xau_v2 (que termina el 22/10)

def cargar(nombre):
    filas = list(csv.DictReader(open(os.path.join(AQUI, "xau_v3", f"XAU_sesion_NY_{nombre}.csv"), encoding="utf-8-sig")))
    sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}; v = []
    for r in filas:
        if not r["Tipo"].startswith("Entrada"): continue
        s = sal[r["Número de operación"]]; e = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M")
        lado = 1 if "largo" in r["Tipo"] else -1; pe, ps = float(r["Precio USD"]), float(s["Precio USD"]); mov = lado * (ps - pe)
        res = s["Señal"]; q = int(r["Tamaño (cant.)"])
        if res in ("SL", "TP"): d = abs(mov)
        else: d = X.DIST.get(("NY", e)); d = sorted(d)[len(d) // 2] if d else 100 / q
        ses = e.date()
        v.append(dict(ent=e, ses=ses, anio=ses.year, lado=lado, pe=pe, ps=ps, mov=mov, res=res, q=q, dist=d, R=mov / d,
                      pnl=float(r["PyG netas USD"]), cat=C.F.categoria(ses, C.CAL), evs=" ".join(x for _, x in C.CAL.get(ses, [])),
                      sl_hit=res == "SL"))
    v.sort(key=lambda o: o["ent"]); n = collections.Counter()
    for o in v: n[o["ses"]] += 1; o["n"] = n[o["ses"]]
    return v

T = {k: cargar(f) for k, f in VAR.items()}
# referencia: Mica original (xau_v2, NY 1R) en el mismo período, solo primer trade y con todos los trades
BASE = {"Mica original · 1 entrada": [o for o in X.T[("NY", "1R")] if o["n"] == 1],
        "Mica original · todas": X.T[("NY", "1R")]}
for k, v in BASE.items():
    T[k] = [dict(o, sl_hit=o["res"] == "SL") for o in v]
for k in T: T[k] = [o for o in T[k] if DESDE <= o["ses"] <= HASTA]
for k, v in T.items():   # registrar en el motor del cuadro comparativo
    K.ESTR[k] = ([dict(o, perd1=X.VAL * o["dist"] + X.COM + X.DESL) for o in v], K.usd_mica)

def neto(o): return o["R"] - (X.COM + (X.DESL if o["R"] <= -0.99 else 0)) / (X.VAL * o["dist"])
