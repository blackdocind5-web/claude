"""Lucid 25K Flex · fase 1 (evaluación): MNQ, una operación por día a las 09:30 o 09:45 NY.
Objetivo del plan: ganar 2 operaciones seguidas (en días distintos) arriesgando ~1.000 USD con RR 1:0,7."""
import csv, glob, os, re, json, datetime as dt, statistics as st
from collections import defaultdict
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
PUNTO = 2.0              # MNQ: 2 USD por punto y contrato
RIESGO = 1000.0; MAX_MICROS = 20; OBJ = 1250.0


def calendario():
    cal = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(RAIZ, "mec_ny", "calendario_ny.csv"), encoding="utf-8-sig"), delimiter=";"):
        cal[dt.datetime.strptime(r["fecha"], "%d/%m/%Y").date()].append((r["regla"], r["evento"]))
    return cal


def categoria(d, cal):
    ev = cal.get(d, [])
    reglas = {e[0] for e in ev}
    if "SIN_OPERAR" in reglas:
        txt = " ".join(e[1] for e in ev if e[0] == "SIN_OPERAR").lower()
        return "Feriado o receso" if ("feriado" in txt or "receso" in txt) else "Discurso 09:00–11:00"
    if "ANALIZAR_NOTICIA" in reglas: return "Noticia 08:30 (NFP, CPI, PPI, PIB)"
    if "ANALIZAR_FOMC" in reglas: return "FOMC"
    if "BLOQUEO_NOTICIA" in reglas: return "Noticia 10:00 (ISM, JOLTS, CB, PCE)"
    return "Día normal"


def cargar():
    cal = calendario(); ops = []
    for f in sorted(glob.glob(os.path.join(AQUI, "datos", "FASE_1-MNQ_*.csv"))):
        m = re.search(r"MNQ_(Q[\w_]+?)_(\d{4})_(\d\d\.\d\d)h_SL_(\d+)_TP_(\d+)", os.path.basename(f))
        trim, anio, hora, sl, tp = m.group(1), int(m.group(2)), m.group(3).replace(".", ":"), int(m.group(4)), int(m.group(5))
        filas = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        ent = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Entrada")}
        sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}
        for k, e in ent.items():
            s = sal[k]; t = dt.datetime.strptime(e["Fecha y hora"], "%Y-%m-%d %H:%M"); pnl = float(e["PyG netas USD"])
            ops.append(dict(archivo=os.path.basename(f), trim=trim, anio=anio, hora=hora, sl=sl, tp=tp, ent=t,
                            sal=dt.datetime.strptime(s["Fecha y hora"], "%Y-%m-%d %H:%M"), pnl=pnl, gana=pnl > 0,
                            normal=abs(pnl - tp * PUNTO) < 0.01 or abs(pnl + sl * PUNTO) < 0.01,
                            cat=categoria(t.date(), cal), lado="largo" if "largo" in e["Tipo"] else "corto"))
    return ops


def contratos(sl):
    return min(MAX_MICROS, int(RIESGO // (sl * PUNTO)))


def ww(seq):
    """Probabilidad de pasar empezando en cada día: las dos próximas operaciones ganan."""
    n = len(seq) - 1
    return sum(seq[i]["gana"] and seq[i + 1]["gana"] for i in range(n)) / n if n > 0 else 0


def racha(seq):
    b = c = 0
    for t in seq:
        c = 0 if t["gana"] else c + 1; b = max(b, c)
    return b


def resumen(seq):
    if not seq: return dict(n=0)
    w = sum(t["gana"] for t in seq)
    return dict(n=len(seq), wr=round(100 * w / len(seq), 1), ww=round(100 * ww(seq), 1), racha_perd=racha(seq),
                anomalas=sum(not t["normal"] for t in seq), peor=min(t["pnl"] for t in seq), mejor=max(t["pnl"] for t in seq))
