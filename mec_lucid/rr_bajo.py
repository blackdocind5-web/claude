"""Estimación de TP más cercano (0,5R / 0,7R) con la excursión favorable máxima (MFE) de TradingView (26/10/2026).
Un trade con TP t habría ganado si su MFE ≥ t·R antes de salir: en TP a 1R siempre; en SL, si la MFE previa al SL
llegó a t; en cierre forzado, si la MFE llegó a t (si no, queda el resultado del cierre). Supuesto: el orden
dentro de la vela no cambia el resultado."""
import csv, glob, os, datetime as dt, collections
import alex as A, xau2 as X, combo3 as C
AQUI = os.path.dirname(os.path.abspath(__file__))

def mfe_map(f, pv):
    filas = list(csv.DictReader(open(f, encoding="utf-8-sig"))); m = {}
    for r in filas:
        if r["Tipo"].startswith("Entrada"):
            m[dt.datetime.strptime(r["Fecha y hora"][:16], "%Y-%m-%d %H:%M")] = float(r["Desviación favorable USD"]) / (pv * int(r["Tamaño (cant.)"]))
    return m

def recortar(ops, mfe, t):
    """devuelve copias de los trades con TP a t·R (R en puntos/precio = o['dist'])"""
    v = []
    for o in ops:
        mf = mfe[o["ent"]] / o["dist"]
        if o["res"] == "TP" or mf >= t - 1e-9: R, res = t, "TP"
        else: R, res = o["R"], o["res"]
        v.append(dict(o, R=R, res=res, sl_hit=res == "SL"))
    return v

def alex_t(nombre, t):
    f = [g for g in glob.glob(os.path.join(AQUI, "alex", "*.csv")) if A.nombre(g) == nombre][0]
    return recortar(A.T[nombre], mfe_map(f, A.PV), t)

def mica_t(t):
    mfe = mfe_map(os.path.join(AQUI, "xau_v2", "XAUUSD_sesion_NY_1R.csv"), 1.0)
    return recortar([o for o in X.T[("NY", "1R")] if o["n"] == 1], mfe, t)
