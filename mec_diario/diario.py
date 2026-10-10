"""Objetivo de ganancia diario + escalera de riesgo sobre la cartera recomendada (Pre NY, m1, lunes a jueves).

Reglas de la simulación (orden cronológico de entradas, resultados conocidos al cerrar cada operación):
- Riesgo de cada operación = base × 2^k del capital realizado al entrar; k = escalón de la escalera (k ≤ tope).
- Escalera de cartera (una sola para los 4 activos), como en el artefacto de la escalera: tras una pérdida k sube;
  cuando lo acumulado desde que empezó la escalera vuelve a positivo, k = 0; si se pierde en el último escalón se acepta y k = 0.
  Una ganadora que no recupera todo mantiene el escalón. Con varias operaciones abiertas, el escalón se actualiza al cerrar cada una.
- Objetivo diario: cuando el resultado realizado del día llega a +X% del capital al inicio del día, no se abren más operaciones
  ese día (las abiertas siguen hasta su salida: no hay precio intradía para cerrarlas antes).
- Freno semanal opcional en % del capital al inicio de la semana.
- El límite de 1 TP / 2 pérdidas por activo y sesión ya viene en los datos.
"""
import datetime as dt, json, math, os, random, statistics as st, sys
from collections import defaultdict
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "mec_cartera"))
import base as B
PRE = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD"]
D0, D1 = dt.date(2025, 1, 13), dt.date(2026, 10, 2)


def lunes(d): return d - dt.timedelta(days=d.weekday())


def simular(ts, base=1.0, tope=0, obj=None, freno=2.7, escalera_dia=False, detalle=False):
    """ts ordenadas por entrada. obj y freno en % del capital. tope=0: riesgo fijo."""
    E = 1000.0; pk = E; mdd = 0.0; k = 0; L = 0.0
    abiertas = []; dia = None; e_dia = E; parado_dia = False; sem = None; e_sem = E; parado_sem = False
    res_dia = defaultdict(float); ini_dia = {}; res_sem = defaultdict(float); ini_sem = {}; res_mes = defaultdict(float); ini_mes = {}
    obj_ok = set(); n = w = 0; max_r = 0.0; max_abierto = 0.0; curve = []; niveles = defaultdict(int); fin_anio = {}

    def cerrar(hasta):
        nonlocal E, pk, mdd, k, L, abiertas, parado_dia, parado_sem
        quedan = []
        for t in sorted(abiertas, key=lambda x: x["sal"]):
            if t["sal"] <= hasta:
                pnl = t["u"] * t["riesgo"] / 100 * t["E0"]
                E += pnl; pk = max(pk, E); mdd = max(mdd, (pk - E) / pk)
                d = t["ent"].date(); res_dia[d] += pnl; res_sem[lunes(d)] += pnl; res_mes[d.strftime("%Y-%m")] += pnl
                curve.append((t["sal"], E)); fin_anio[t["sal"].year] = E
                if tope:
                    L += pnl
                    if L > 0: k = 0; L = 0.0
                    elif pnl < 0:
                        k += 1
                        if k > tope: k = 0; L = 0.0
                if obj is not None and d == dia and res_dia[d] >= obj / 100 * ini_dia[d] - 1e-9:
                    parado_dia = True; obj_ok.add(d)
                if freno is not None and lunes(d) == sem and res_sem[sem] <= -freno / 100 * ini_sem[sem] + 1e-9: parado_sem = True
            else: quedan.append(t)
        abiertas = quedan

    for t in ts:
        cerrar(t["ent"])
        d = t["ent"].date()
        if d != dia:
            cerrar(dt.datetime.combine(d, dt.time(0)))
            dia = d; parado_dia = False; ini_dia[d] = E
            if escalera_dia: k = 0; L = 0.0
            if lunes(d) != sem: sem = lunes(d); parado_sem = False; ini_sem[sem] = E
            ini_mes.setdefault(d.strftime("%Y-%m"), E)
        if parado_dia or parado_sem: continue
        r = base * 2 ** k; niveles[k] += 1
        x = dict(t, riesgo=r, E0=E); abiertas.append(x); n += 1; w += t["u"] > 0
        max_r = max(max_r, r); max_abierto = max(max_abierto, sum(a["riesgo"] for a in abiertas))
    cerrar(dt.datetime(2100, 1, 1))
    dias = [res_dia[d] / ini_dia[d] * 100 for d in res_dia]
    sems = [res_sem[s] / ini_sem[s] * 100 for s in res_sem]
    meses = [res_mes[m] / ini_mes[m] * 100 for m in sorted(res_mes)]
    anios = {}; prev = 1000.0
    for y in (2025, 2026):
        if y in fin_anio: anios[str(y)] = round((fin_anio[y] / prev - 1) * 100, 1); prev = fin_anio[y]
    cagr = ((E / 1000) ** (365.25 / (D1 - D0).days) - 1) * 100 if E > 0 else -100
    out = dict(n=n, wr=round(100 * w / n, 1), ret=round((E / 1000 - 1) * 100, 1), cagr=round(cagr, 1), mdd=round(mdd * 100, 1),
               calmar=round(cagr / (mdd * 100), 2) if mdd else None, anios=anios,
               dias=len(dias), dias_pos=round(100 * sum(x > 0 for x in dias) / len(dias), 1), dias_obj=round(100 * len(obj_ok) / len(dias), 1),
               dia_prom=round(st.mean(dias), 3), dia_med=round(st.median(dias), 3), peor_dia=round(min(dias), 2), mejor_dia=round(max(dias), 2),
               sem_pos=round(100 * sum(x > 0 for x in sems) / len(sems), 1), peor_sem=round(min(sems), 2), sem_med=round(st.median(sems), 2),
               mes_pos=round(100 * sum(x > 0 for x in meses) / len(meses), 1), peor_mes=round(min(meses), 2), mes_med=round(st.median(meses), 2),
               mes_geo=round(((E / 1000) ** (30.4375 / (D1 - D0).days) - 1) * 100, 2) if E > 0 else -100,
               max_riesgo=round(max_r, 2), max_abierto=round(max_abierto, 2), niveles=dict(niveles))
    if detalle:
        out["curve"] = [dict(t=s.strftime("%Y-%m-%d %H:%M"), eq=round(e, 2)) for s, e in curve]
        out["meses"] = [round(x, 2) for x in meses]; out["dias_lista"] = [round(x, 3) for x in dias]
    return out


def montecarlo(ts, sims=1000, seed=7, **kw):
    rnd = random.Random(seed); por = defaultdict(list)
    for i, t in enumerate(ts): por[t["a"]].append(i)
    R = []
    for _ in range(sims):
        nu = [t["u"] for t in ts]
        for a, idx in por.items():
            v = [ts[i]["u"] for i in idx]
            for i in idx: nu[i] = rnd.choice(v)
        R.append(simular([dict(t, u=u) for t, u in zip(ts, nu)], **kw))
    q = lambda xs, p: sorted(xs)[min(len(xs) - 1, int(p * len(xs)))]
    cg = [r["cagr"] for r in R]; dd = [r["mdd"] for r in R]
    return dict(cagr_med=round(st.median(cg), 1), cagr_p5=round(q(cg, .05), 1), dd_med=round(st.median(dd), 1), dd_p95=round(q(dd, .95), 1),
                p_dd30=round(100 * sum(x >= 30 for x in dd) / sims, 1), p_dd50=round(100 * sum(x >= 50 for x in dd) / sims, 1),
                p_anio_neg=round(100 * sum(any(v < 0 for v in r["anios"].values()) for r in R) / sims, 1),
                dias_pos_med=round(st.median([r["dias_pos"] for r in R]), 1), mes_pos_med=round(st.median([r["mes_pos"] for r in R]), 1),
                peor_mes_p5=round(q([r["peor_mes"] for r in R], .05), 1))


def cargar():
    T = B.cargar()
    return sorted([t for a in PRE for t in T[a]], key=lambda t: (t["ent"], B.H.ACTIVOS.index(t["a"])))


if __name__ == "__main__":
    ts = cargar()
    r = simular(ts); print("control fijo 1%, freno 2,7%:", {k: r[k] for k in ("n", "cagr", "mdd", "anios", "dias_pos", "sem_pos", "mes_pos")})
