"""Sesión NY: lectura y filtro de operaciones con el calendario NY (ver CLAUDE.md)."""
import csv, datetime as dt, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "mec_hibrida"))
import hibrida as H

def cargar_calendario():
    cal = {}
    for r in csv.DictReader(open(os.path.join(AQUI, "calendario_ny.csv"), encoding="utf-8"), delimiter=";"):
        cal.setdefault(dt.datetime.strptime(r["fecha"], "%d/%m/%Y").date(), []).append(r)
    return cal

CAL = cargar_calendario()

def clasificar(t):
    """Devuelve (motivo de exclusión o None, etiquetas de análisis)."""
    reglas = CAL.get(t["ent"].date(), []); tags = []
    for r in reglas:
        if r["regla"] == "SIN_OPERAR": return f'Día sin operar: {r["evento"]}', tags
    for r in reglas:
        if r["regla"] == "BLOQUEO_NOTICIA":
            a, b = [dt.time.fromisoformat(x) for x in r["ventana_NY"].split("-")]
            if a <= t["ent"].time() <= b: return f'Entrada dentro del bloqueo {r["ventana_NY"]}: {r["evento"]}', tags
        elif r["regla"].startswith("ANALIZAR"):
            tags.append(("FOMC" if r["regla"] == "ANALIZAR_FOMC" else "Noticia") + ": " + r["evento"])
    return None, tags

def leer_csv(f, activo):
    """Lee la lista de operaciones y lleva cada una a riesgo exacto de 1%.
    Con 1.000 USD y lote mínimo de 0,1 el riesgo real no es 1% (va de ~0,1% a ~1,1%). u = resultado en unidades de 1%:
    - Salida por la orden de la estrategia (SL o TP de precio): SL = -1, TP = +0,9 (R:R 1:0,9).
    - Otras salidas (CHoCH, cierre de sesión, Reset): riesgo estimado con el tamaño. La estrategia redondea hacia abajo
      cantidad = 1% del capital / distancia del stop en pasos de 0,1, así que riesgo ≈ cantidad × 1% / (cantidad + 0,05)."""
    from collections import OrderedDict
    ops = OrderedDict()
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        ops.setdefault(int(r["Número de operación"]), []).append(r)
    # capital inicial del backtest (1.000 o 100.000 USD), deducido de PyG acumuladas en USD y en %
    cap = 1000.0
    for fs in ops.values():
        e = next(x for x in fs if x["Tipo"].startswith("Entrada"))
        if abs(float(e["PyG acumuladas %"])) >= 0.5:
            cap = round(float(e["PyG acumuladas USD"]) / (float(e["PyG acumuladas %"]) / 100), -3); break
    exacto = cap >= 10000   # con capital grande el tamaño sale exacto: no hace falta normalizar
    out = []
    for n, fs in ops.items():
        e = next(x for x in fs if x["Tipo"].startswith("Entrada")); s_ = next(x for x in fs if x["Tipo"].startswith("Salida"))
        pnl = float(e["PyG netas USD"]); eq = cap + float(e["PyG acumuladas USD"]) - pnl; uno = 0.01 * eq
        q = float(e["Tamaño (cant.)"]); sal = s_["Señal"]
        if exacto:
            u = pnl / uno
        elif sal.startswith(("Salida", "SL alcanzado", "TP alcanzado")):
            u = 0.9 if pnl > 0 else -1.0
        else:
            u = max(-1.0, min(0.9, pnl / (q * uno / (q + 0.05))))
        out.append(dict(a=activo, n=n, ent=dt.datetime.strptime(e["Fecha y hora"], "%Y-%m-%d %H:%M"),
                        sal=dt.datetime.strptime(s_["Fecha y hora"], "%Y-%m-%d %H:%M"), u=u, u_real=pnl / uno,
                        salida=sal, dir="BUY" if "largo" in e["Tipo"] else "SELL", qty=q, capital=cap))
    return out

def leer(activo, inicio, patron):
    f = os.path.join(AQUI, "datos", f"{activo}_m1_{inicio}_2025-2026_{H.PATRONES[patron]}.csv")
    ts = leer_csv(f, activo); out = []; excl = []
    for t in sorted(ts, key=lambda t: t["ent"]):
        m, tags = clasificar(t); t["tags"] = tags; t["m"] = H.motivo(t["salida"].replace("Salida NY", "Salida PreNY").replace("Salida WallStreet", "Salida PreNY"))
        (excl if m else out).append(dict(t, excl=m) if m else t)
    return H.limite_perdidas(out), excl
