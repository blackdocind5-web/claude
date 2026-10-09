"""Cartera completa: gestión ganadora de Pre NY + S&P 500 y BTCUSD de la sesión NY.
Reglas de corte por ganancia y por pérdida medidas en R realizados (1R = 0,9%)."""
import datetime as dt, os, sys
from collections import defaultdict
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "mec_ny"))
import ny
H = ny.H
for _a in ["SPX500", "BTCUSD_NY"]:
    if _a not in H.ACTIVOS: H.ACTIVOS.append(_a)
R_PCT = 0.9
PRE = (("XAUUSD", "E"), ("EURUSD", "ES"), ("GBPUSD", "S"), ("BTCUSD", "E"))
NY_ = (("SPX500", "0900", "E"), ("BTCUSD_NY", "0900", "ES"))
NOMBRE = {"XAUUSD": "XAUUSD", "EURUSD": "EURUSD", "GBPUSD": "GBPUSD", "BTCUSD": "BTCUSD Pre NY", "SPX500": "S&P 500 NY", "BTCUSD_NY": "BTCUSD NY"}


def cargar():
    T = H.cargar(); out = {}
    for a, p in PRE: out[a] = [t for t in T[(a, p)] if t["ent"].weekday() != 4]
    for a, ini, p in NY_:
        ts, _ = ny.leer(a, ini, p)
        out[a] = [t for t in ts if not t["tags"] and t["ent"].weekday() != 4]
    return out


def lunes(d): return d - dt.timedelta(days=d.weekday())


def filtrar(ts, freno_sem=3, obj_sem=None, obj_mes=None, obj_act_sem=None, candado=None, obj_dia=None):
    """Decide qué operaciones se toman, en orden cronológico de entrada, con el resultado ya cerrado al entrar.
    freno_sem: deja de operar la semana al llegar a -nR. obj_sem / obj_mes: deja de operar la semana / el mes al llegar a +nR.
    obj_act_sem: por activo, deja de operar ese activo en la semana al llegar a +nR. obj_dia: igual por día (cartera).
    candado=(a, b): cuando la semana llegó a +aR, si vuelve a +bR o menos se deja de operar hasta el lunes."""
    ts = sorted(ts, key=lambda t: (t["ent"], H.ACTIVOS.index(t["a"])))
    tomadas = []; abiertas = []
    sem = defaultdict(float); mes = defaultdict(float); act = defaultdict(float); dia = defaultdict(float)
    pico = defaultdict(float); cerrada_sem = set(); cerrada_mes = set(); cerrada_act = set(); cerrada_dia = set()
    def cerrar(hasta):
        nonlocal abiertas
        rest = []
        for t in sorted(abiertas, key=lambda t: t["sal"]):
            if t["sal"] <= hasta:
                r = t["u"] / R_PCT; w = lunes(t["ent"].date()); m = t["ent"].strftime("%Y-%m")
                sem[w] += r; mes[m] += r; act[(t["a"], w)] += r; dia[t["ent"].date()] += r
                pico[w] = max(pico[w], sem[w])
                if freno_sem is not None and sem[w] <= -freno_sem + 1e-9: cerrada_sem.add(w)
                if obj_sem is not None and sem[w] >= obj_sem - 1e-9: cerrada_sem.add(w)
                if candado and pico[w] >= candado[0] - 1e-9 and sem[w] <= candado[1] + 1e-9: cerrada_sem.add(w)
                if obj_mes is not None and mes[m] >= obj_mes - 1e-9: cerrada_mes.add(m)
                if obj_act_sem is not None and act[(t["a"], w)] >= obj_act_sem - 1e-9: cerrada_act.add((t["a"], w))
                if obj_dia is not None and dia[t["ent"].date()] >= obj_dia - 1e-9: cerrada_dia.add(t["ent"].date())
            else: rest.append(t)
        abiertas = rest
    for t in ts:
        cerrar(t["ent"])
        w = lunes(t["ent"].date()); m = t["ent"].strftime("%Y-%m")
        if w in cerrada_sem or m in cerrada_mes or (t["a"], w) in cerrada_act or t["ent"].date() in cerrada_dia: continue
        tomadas.append(t); abiertas.append(t)
    return tomadas


def metricas(tomadas, mc=False, curva=False):
    r = H.simular(tomadas, None, curva=curva)
    us = [t["u"] for t in tomadas]
    # semanas y meses en R (para la regularidad)
    sw = defaultdict(float); sm = defaultdict(float)
    for t in tomadas: sw[lunes(t["ent"].date())] += t["u"] / R_PCT; sm[t["ent"].strftime("%Y-%m")] += t["u"] / R_PCT
    out = {k: r[k] for k in ("n", "wr", "R", "ret", "cagr", "mes_geo", "sem_geo", "mdd", "racha", "calmar", "anios", "sem_pos", "mes_pos",
                             "peor_mes", "peor_sem", "bajo_agua", "pf", "sharpe", "sem_neg_seg", "max_conc")}
    out["sem_R"] = dict(sw); out["mes_R"] = dict(sm)
    if curva: out["curve"] = r["curve"]; out["meses"] = r["meses"]; out["semanas"] = r["semanas"]
    if mc:
        m = H.montecarlo(tomadas, None, sims=1000)
        out["mc"] = {k: m[k] for k in ("cagr_med", "cagr_p5", "dd_med", "dd_p95", "p_anio_neg", "racha_p95", "mes_med")}
    return out
