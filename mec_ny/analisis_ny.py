"""Análisis de la sesión NY por activo -> datos_ny.json (python analisis_ny.py)."""
import json, os, statistics as st, sys
from collections import defaultdict
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import ny
H = ny.H
for _a in ["NAS100", "SPX500", "US30", "BTCUSD_NY"]:
    if _a not in H.ACTIVOS: H.ACTIVOS.append(_a)

ACTIVOS_NY = ["NAS100"]                     # se suman S&P 500, US30 y BTCUSD a medida que lleguen
INICIOS = {"0900": "09:00", "0930": "09:30"}
R_PCT = 0.9
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
FRANJAS = [("09:00–09:29", 9 * 60, 9 * 60 + 30), ("09:30–09:59", 9 * 60 + 30, 10 * 60), ("10:00–10:29", 10 * 60, 10 * 60 + 30), ("10:30–11:00", 10 * 60 + 30, 11 * 60 + 1)]


def grupo(ts):
    us = [t["u"] for t in ts]
    if not us: return dict(n=0, wr=None, R=0, R25=0, R26=0, R_op=None)
    return dict(n=len(us), wr=round(100 * sum(u > 0 for u in us) / len(us), 1), R=round(sum(us) / R_PCT, 1),
                R25=round(sum(t["u"] for t in ts if t["ent"].year == 2025) / R_PCT, 1),
                R26=round(sum(t["u"] for t in ts if t["ent"].year == 2026) / R_PCT, 1),
                n25=sum(1 for t in ts if t["ent"].year == 2025), n26=sum(1 for t in ts if t["ent"].year == 2026),
                R_op=round(sum(us) / R_PCT / len(us), 3))


def tipo_tag(tag):
    ev = tag.split(": ", 1)[1]
    for k, v in (("NFP", "NFP"), ("CPI m/m", "CPI USD"), ("CPI y/y", "CPI GBP"), ("PPI", "PPI"), ("PIB final", "PIB final"),
                 ("Federal Funds", "FOMC: tasa y comunicado"), ("Economic Projections", "FOMC: proyecciones"), ("Minutes", "FOMC: minutas")):
        if k in ev: return v
    return ev


def decision(g):
    if g["n"] == 0: return "sin datos"
    if g["R25"] > 0 and g["R26"] > 0: return "operar"
    if g["R"] < 0: return "no operar"
    return "neutral"


def analizar_activo(a):
    res = dict(variantes=[])
    for ini, hora in INICIOS.items():
        for p in ("E", "S", "ES"):
            try: ts, ex = ny.leer(a, ini, p)
            except FileNotFoundError: continue
            todos = grupo(ts); r = H.resumen(ts)
            # días a analizar: por tipo de noticia
            cats = defaultdict(list)
            for t in ts:
                for tag in t["tags"]: cats[tipo_tag(tag)].append(t)
            cat = [dict(cat=k, grupo=("FOMC" if k.startswith("FOMC") else "Noticia"), **grupo(v), decision=decision(grupo(v))) for k, v in sorted(cats.items())]
            noti = [t for t in ts if any(x.startswith("Noticia") for x in t["tags"])]
            fomc = [t for t in ts if any(x.startswith("FOMC") for x in t["tags"])]
            limpio = [t for t in ts if not t["tags"]]
            sin_noti = [t for t in ts if not any(x.startswith("Noticia") for x in t["tags"])]
            sin_fomc = [t for t in ts if not any(x.startswith("FOMC") for x in t["tags"])]
            excl = defaultdict(list)
            for t in ex: excl["Bloqueo de noticia 09:50–10:03" if "bloqueo" in t["excl"] else ("Feriado" if "Feriado" in t["excl"] else "Receso" if "Receso" in t["excl"] else "Discurso")].append(t)
            res["variantes"].append(dict(inicio=ini, hora=hora, patron=p, n_excl=len(ex), todos=todos, resumen=r,
                                         noticia=grupo(noti), fomc=grupo(fomc), limpio=grupo(limpio), sin_noticia=grupo(sin_noti), sin_fomc=grupo(sin_fomc),
                                         limpio_res=H.resumen(limpio), categorias=cat,
                                         excluidas=[dict(cat=k, **grupo(v)) for k, v in excl.items()],
                                         sin_viernes=grupo([t for t in limpio if t["ent"].weekday() != 4])))
    # variante elegida: la de mejor R en días limpios entre las que ganan los dos años (sin días de noticia y FOMC)
    cand = [v for v in res["variantes"] if v["limpio"]["R25"] > 0 and v["limpio"]["R26"] > 0]
    mejor = max(cand, key=lambda v: v["limpio"]["R"]) if cand else max(res["variantes"], key=lambda v: v["limpio"]["R"])
    res["elegida"] = dict(inicio=mejor["inicio"], patron=mejor["patron"], gana_ambos=bool(cand))
    ts, _ = ny.leer(a, mejor["inicio"], mejor["patron"])
    lim = [t for t in ts if not t["tags"]]
    res["detalle"] = dict(
        franjas=[dict(franja=f, **grupo([t for t in lim if a_ <= t["ent"].hour * 60 + t["ent"].minute < b])) for f, a_, b in FRANJAS],
        dias=[dict(dia=DIAS[k], **grupo([t for t in lim if t["ent"].weekday() == k])) for k in range(5)],
        direccion=[dict(dir=d, **grupo([t for t in lim if t["dir"] == d])) for d in ("BUY", "SELL")],
        salidas=[dict(salida=m, **grupo([t for t in lim if t["m"] == m])) for m in sorted({t["m"] for t in lim})],
        primer_sl=H.primer_sl(lim),
        meses=[dict(mes=m, **grupo([t for t in lim if t["ent"].strftime("%Y-%m") == m])) for m in sorted({t["ent"].strftime("%Y-%m") for t in lim})],
        riesgo_real=dict(med=round(st.median(abs(t["u_real"]) for t in ts if t["salida"].startswith("Salida") and t["u"] < 0), 2),
                         min=round(min(abs(t["u_real"]) for t in ts if t["salida"].startswith("Salida") and t["u"] < 0), 2),
                         max=round(max(abs(t["u_real"]) for t in ts if t["salida"].startswith("Salida") and t["u"] < 0), 2)))
    # filtro candidato: sin entradas de 10:00 a 10:29 (datos de las 10:00: ISM, JOLTS, CB, ventas de viviendas, etc.)
    f10 = [t for t in lim if sin_franja_10(t)]
    res["filtro10"] = dict(con=grupo(lim), sin=grupo(f10), sin_vie=grupo([t for t in f10 if t["ent"].weekday() != 4]), con_vie=grupo([t for t in lim if t["ent"].weekday() != 4]),
                           por_variante=[dict(hora=v["hora"], patron=v["patron"], con=v["limpio"], sin=grupo([t for t in ny.leer(a, v["inicio"], v["patron"])[0] if not t["tags"] and sin_franja_10(t)])) for v in res["variantes"]],
                           mc_con=H.montecarlo(lim, None, sims=1000), mc_sin=H.montecarlo(f10, None, sims=1000))
    sim = H.simular(lim, None, curva=True)
    res["detalle"]["sim"] = {k: sim[k] for k in ("n", "wr", "ret", "cagr", "mes_geo", "mdd", "racha", "calmar", "pf", "anios", "curve", "meses", "bajo_agua", "sem_pos", "peor_mes")}
    res["detalle"]["mc"] = H.montecarlo(lim, None, sims=1000)
    return res, lim


def sin_franja_10(t): return not (t["ent"].hour == 10 and t["ent"].minute < 30)


def cartera_con_preny(lim_ny, a="NAS100"):
    """Gestión ganadora de Pre NY + la variante elegida de NY, misma gestión (sin viernes, freno semanal −3R)."""
    T = H.cargar()
    C = (("XAUUSD", "E"), ("EURUSD", "ES"), ("GBPUSD", "S"), ("BTCUSD", "E"))
    pre = [t for a, p in C for t in T[(a, p)] if t["ent"].weekday() != 4]
    out = []
    ny_ = [t for t in lim_ny if t["ent"].weekday() != 4]
    for nom, ts in (("Pre NY (gestión ganadora)", pre), (f"Pre NY + {a} NY", pre + ny_),
                    (f"Pre NY + {a} NY sin entradas 10:00–10:29", pre + [t for t in ny_ if sin_franja_10(t)])):
        r = H.simular(ts, None, stop_sem=3, curva=True); m = H.montecarlo(ts, None, sims=1000, stop_sem=3)
        out.append(dict(nombre=nom, curve=r["curve"], mc=m, **{k: r[k] for k in ("n", "wr", "ret", "cagr", "mes_geo", "mdd", "racha", "calmar", "anios", "pf", "peor_mes", "max_conc")}))
    return out


def main():
    data = dict(meta=dict(ini="13/01/2025", fin="02/10/2026", activos=ACTIVOS_NY,
                          calendario={r: sum(1 for v in ny.CAL.values() for x in v if x["regla"] == r) for r in ("SIN_OPERAR", "ANALIZAR_NOTICIA", "ANALIZAR_FOMC", "BLOQUEO_NOTICIA")}),
                activos={})
    for a in ACTIVOS_NY:
        res, lim = analizar_activo(a)
        res["cartera"] = cartera_con_preny(lim)
        data["activos"][a] = res
    json.dump(data, open(os.path.join(AQUI, "datos_ny.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return data


if __name__ == "__main__":
    d = main()
    for a, r in d["activos"].items():
        print(a, r["elegida"])
        for v in r["variantes"]: print(v["hora"], v["patron"], v["todos"], "| limpio", v["limpio"], "| noticia", v["noticia"]["R"], "fomc", v["fomc"]["R"])
        for c in r["cartera"]: print(c["nombre"], c["cagr"], c["mdd"], c["anios"], c["mc"]["cagr_p5"], c["n"])
        D = r["detalle"]; print(D["franjas"]); print(D["dias"]); print(D["riesgo_real"]); print(D["sim"]["cagr"], D["sim"]["mdd"], D["sim"]["anios"], D["mc"]["cagr_p5"], D["mc"]["p_anio_neg"])
        for v in r["variantes"]:
            if v["inicio"] == r["elegida"]["inicio"] and v["patron"] == r["elegida"]["patron"]:
                for c in v["categorias"]: print("  ", c)
