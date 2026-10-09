"""Cartera esencial (Pre NY + NY): Pareto por activo y reglas de corte por ganancia -> datos_cartera.json."""
import itertools, json, os, statistics as st, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import base as B

T = B.cargar()
TODOS = list(T)                                           # 6 activos planteados
CINCO = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "SPX500"]
PRE = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD"]
RES = ("n", "wr", "R", "cagr", "mes_geo", "mdd", "racha", "calmar", "anios", "sem_pos", "mes_pos", "peor_mes", "peor_sem", "pf", "sharpe")


def corre(acts, mc=False, curva=False, **kw):
    return B.metricas(B.filtrar([t for a in acts for t in T[a]], **kw), mc=mc, curva=curva)


def recorta(m): return {k: m[k] for k in RES}


def mejora(r, b): return all(r["anios"][y] > b["anios"][y] for y in ("2025", "2026")) and r["mdd"] <= b["mdd"] + 1e-9


def main():
    data = dict(nombres=B.NOMBRE)
    # 1) Pareto por activo
    tot = sum(t["u"] for a in T for t in T[a]); n = sum(len(T[a]) for a in T)
    act = []
    for a in TODOS:
        g = sum(t["u"] for t in T[a])
        act.append(dict(a=a, n=len(T[a]), pct_ops=round(100 * len(T[a]) / n, 1), R=round(g / 0.9, 1), pct_R=round(100 * g / tot, 1),
                        R_op=round(g / 0.9 / len(T[a]), 3), wr=round(100 * sum(t["u"] > 0 for t in T[a]) / len(T[a]), 1),
                        R25=round(sum(t["u"] for t in T[a] if t["ent"].year == 2025) / 0.9, 1), R26=round(sum(t["u"] for t in T[a] if t["ent"].year == 2026) / 0.9, 1),
                        sesion="NY" if a in ("SPX500", "BTCUSD_NY") else "Pre NY"))
    act.sort(key=lambda x: -x["R_op"])
    data["activos"] = act
    # 2) todas las combinaciones de los 6 activos (base: sin viernes, freno −3R)
    filas = []
    for k in range(1, len(TODOS) + 1):
        for sub in itertools.combinations(TODOS, k):
            r = corre(sub); filas.append(dict(activos=list(sub), **recorta(r)))
    filas.sort(key=lambda f: -(f["calmar"] or 0))
    data["combinaciones"] = filas
    # 3) concentración del resultado en el tiempo
    conc = {}
    for nom, acts in (("seis", TODOS), ("cinco", CINCO)):
        m = corre(acts); sw = sorted(m["sem_R"].values(), reverse=True); sm = sorted(m["mes_R"].values(), reverse=True)
        k = max(1, round(0.2 * len(sw))); km = max(1, round(0.2 * len(sm)))
        conc[nom] = dict(semanas=len(sw), media=round(st.mean(sw), 2), mediana=round(st.median(sw), 2),
                         top20=round(100 * sum(sw[:k]) / sum(sw), 0), sobre_media=round(sum(x for x in sw if x > st.mean(sw)), 1), neto=round(sum(sw), 1),
                         p=[round(sw[::-1][int(q * (len(sw) - 1))], 1) for q in (.1, .25, .5, .75, .9)],
                         mes_media=round(st.mean(sm), 2), mes_top20=round(100 * sum(sm[:km]) / sum(sm), 0),
                         hist=sorted(round(x, 2) for x in sw))
    data["concentracion"] = conc
    # 4) reglas de corte sobre los 6 y los 5 activos
    reglas = ([("Objetivo semanal", "obj_sem", x, f"+{x}R") for x in (2, 3, 4, 5, 6)] +
              [("Objetivo mensual", "obj_mes", x, f"+{x}R") for x in (4, 6, 8, 10, 12)] +
              [("Objetivo semanal por activo", "obj_act_sem", x, f"+{x}R") for x in (1, 2, 3)] +
              [("Objetivo diario", "obj_dia", x, f"+{x}R") for x in (1, 2, 3)] +
              [("Candado semanal", "candado", x, f"llega a +{x[0]}R, corta en {'+' if x[1] else ''}{x[1]}R") for x in ((2, 0), (2, 1), (3, 0), (3, 1), (3, 2), (4, 2))])
    data["reglas"] = {}
    for nom, acts in (("seis", TODOS), ("cinco", CINCO)):
        b = corre(acts); rows = [dict(grupo="Base", regla="Sin corte por ganancia", ok=None, **recorta(b))]
        for g, k, v, txt in reglas:
            r = corre(acts, **{k: v}); rows.append(dict(grupo=g, regla=txt, ok=mejora(r, b), **recorta(r)))
        data["reglas"][nom] = rows
    # estabilidad del candado (5 activos)
    b5 = corre(CINCO); est = []
    for a_ in (1.5, 2, 2.5, 3):
        for c_ in (0, 0.5, 1):
            r = corre(CINCO, candado=(a_, c_)); est.append(dict(a=a_, c=c_, cagr=r["cagr"], mdd=r["mdd"], anios=r["anios"], ok=mejora(r, b5)))
    data["estabilidad"] = est
    # 5) carteras finales con simulaciones
    fin = []
    for nom, acts, kw in (("Pre NY (gestión ganadora)", PRE, {}), ("Planteada: Pre NY + S&P 500 + BTCUSD NY", TODOS, {}),
                          ("Esencial: Pre NY + S&P 500", CINCO, {}), ("Esencial + candado semanal (+2R → 0R)", CINCO, dict(candado=(2, 0)))):
        m = corre(acts, mc=True, curva=True, **kw)
        fin.append(dict(nombre=nom, activos=acts, regla=kw, curve=m["curve"], meses=m["meses"], mc=m["mc"], max_conc=m["max_conc"],
                        sem_neg_seg=m["sem_neg_seg"], bajo_agua=m["bajo_agua"], **recorta(m)))
    data["finales"] = fin
    json.dump(data, open(os.path.join(AQUI, "datos_cartera.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return data


if __name__ == "__main__":
    d = main()
    for f in d["finales"]: print(f["nombre"], f["cagr"], f["mdd"], f["anios"], f["wr"], f["racha"], f["n"], f["mc"])
    for e in d["estabilidad"]: print(e)
