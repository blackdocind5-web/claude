"""XAUUSD en la sesión de NY (09:00–11:00, m1): lectura, calendario NY, límite de sesión y costos reales (0,05 USD por operación)."""
import csv, os, statistics as st, sys
from collections import defaultdict
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "mec_ny")); sys.path.insert(0, os.path.join(RAIZ, "mec_diario"))
import ny, diario as Dd
H = ny.H
if "XAUUSD_NY" not in H.ACTIVOS: H.ACTIVOS.append("XAUUSD_NY")
COSTO = 0.05          # USD por onza: 0,02 de spread + 0,03 de comisión (3 USD por lote de 100 oz, ida y vuelta)
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]


def stops(patron):
    f = os.path.join(RAIZ, "mec_ny", "datos", f"XAUUSD_NY_m1_0900_2025-2026_{H.PATRONES[patron]}.csv")
    out = {}
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        if r["Tipo"].startswith("Entrada"):
            pnl = float(r["PyG netas USD"]); eq = 1000 + float(r["PyG acumuladas USD"]) - pnl
            out[r["Fecha y hora"]] = 0.01 * eq / float(r["Tamaño (cant.)"])
    return out


def cargar(patron, costos=True):
    """Operaciones válidas (sin días SIN_OPERAR ni bloqueos del calendario NY), con tags de noticia/FOMC y resultado neto."""
    ts, excl = ny.leer("XAUUSD_NY", "0900", patron)
    S = stops(patron)
    for t in ts:
        d = S[t["ent"].strftime("%Y-%m-%d %H:%M")]; t["stop"] = d
        t["costo"] = COSTO / d if costos else 0.0
        t["u_bruto"] = t["u"]; t["u"] = t["u"] - t["costo"]
    return ts, excl


def resumen(ts):
    us = [t["u"] for t in ts]
    if not us: return dict(n=0)
    r = H.resumen(ts)
    for y in (2025, 2026):
        x = [t for t in ts if t["ent"].year == y]
        r[f"R{y}"] = round(sum(t["u"] for t in x) / 0.9, 1); r[f"n{y}"] = len(x)
    r["costo_R"] = round(st.mean(t["costo"] for t in ts) / 0.9, 3)
    return r
