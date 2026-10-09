"""Hoja de ruta del sistema MEC: junta lo mejor de cada etapa -> datos_informe.json.
Todo sobre 1.000 USD iniciales, 13/01/2025 al 02/10/2026, con los datos vigentes de cada carpeta.
Correr antes: ../mec_analisis/metricas.py, ../mec_ny/analisis_ny.py y ../mec_cartera/analisis.py."""
import datetime as dt, json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "mec_hibrida")); sys.path.insert(0, os.path.join(RAIZ, "mec_analisis"))
import hibrida as H
import escalera as ESC
sys.path.insert(0, os.path.join(RAIZ, "mec_ny"))
import ny as NY
rd = lambda *p: json.load(open(os.path.join(RAIZ, *p), encoding="utf-8"))


def diaria(curve):
    """Último valor de cada día (curvas más livianas para el gráfico)."""
    out = {}
    for c in curve: out[c["t"][:10]] = c["eq"]
    return [dict(t=k, eq=round(v, 2)) for k, v in sorted(out.items())]


def por_anio(curve):
    fin25 = [c["eq"] for c in curve if c["t"][:4] == "2025"]
    e25 = fin25[-1] if fin25 else 1000.0
    return {"2025": round((e25 / 1000 - 1) * 100, 1), "2026": round((curve[-1]["eq"] / e25 - 1) * 100, 1)}


def mdd_de(curve):
    pk = 1000.0; m = 0
    for c in curve: pk = max(pk, c["eq"]); m = max(m, (pk - c["eq"]) / pk)
    return round(m * 100, 1)


def cagr_de(curve):
    d0 = dt.date(2025, 1, 13); d1 = dt.date(2026, 10, 2)
    return round(((curve[-1]["eq"] / 1000) ** (365.25 / (d1 - d0).days) - 1) * 100, 1)


def precio(patrones):
    """Serie de precios del propio TradingView: precio de cada entrada y salida de todas las exportaciones del activo.
    Base = primer precio del 13/01/2025; curva = 1.000 USD comprados y mantenidos (sin apalancamiento ni dividendos)."""
    import csv, glob
    px = {}
    for pat in patrones:
        for f in glob.glob(os.path.join(RAIZ, pat)):
            if f.endswith(("_excluidos.csv", "_validos.csv")): continue
            for r in csv.DictReader(open(f, encoding="utf-8-sig")): px[r["Fecha y hora"]] = float(r["Precio USD"])
    ts = sorted(t for t in px if "2025-01-13" <= t[:10] <= "2026-10-02")
    p0 = px[ts[0]]
    curve = diaria([dict(t=t, eq=1000 * px[t] / p0) for t in ts])
    return dict(curve=curve, ret=round((curve[-1]["eq"] / 1000 - 1) * 100, 1), cagr=cagr_de(curve), mdd=mdd_de(curve), anios=por_anio(curve),
                p0=p0, p1=px[ts[-1]], dias=len(curve))


def main():
    T = H.cargar()
    xau = T[("XAUUSD", "E")]
    xau_lj = [t for t in xau if t["ent"].weekday() != 4]
    out = {}

    # 1) Backtest XAUUSD Envolvente (riesgo fijo 1%, con viernes): métricas por año del primer artefacto + curva continua
    bt = rd("mec_analisis", "datos.json")
    claves = ("n", "ret_pct", "wr", "pf", "payoff", "R_tot", "R_avg", "R_week", "mdd_pct", "sharpe", "sortino", "streak_w", "streak_l",
              "wk_pos", "wk_neg", "weeks_active", "first", "last", "max_win", "max_loss", "mc_dd95", "trades_week", "dur_avg")
    anios = {y: {k: bt[y]["envolvente"].get(k) for k in claves} for y in ("2025", "2026")}
    for y in anios: anios[y]["meses"] = [dict(mes=m["mes"], R=m["R"], pct=m["pct"]) for m in bt[y]["envolvente"]["months"]]
    s1 = H.simular(xau, curva=True)
    c1 = diaria(s1["curve"])
    out["etapa1"] = dict(anios=anios, total={k: s1[k] for k in ("n", "wr", "R", "ret", "cagr", "mdd", "racha", "pf", "R_op", "mes_pos", "peor_mes", "sharpe", "bajo_agua", "calmar")},
                         curve=c1, sin_viernes={k: H.simular(xau_lj)[k] for k in ("n", "wr", "R", "ret", "mdd", "pf", "R_op")})

    # 2) Escalera de riesgo sobre la operativa elegida: Envolvente, límite 1 TP / 2 SL, sin viernes, 0,5% -> 1% -> 2% -> 4%, tope 3
    U = ESC.unidades([dict(ent=t["ent"], sal=t["sal"], pnl=t["u"], eq_bt=100.0) for t in xau_lj])
    e = ESC.simular(U, 0.5, 999, True, detalle=True, tope=3)
    mc = ESC.montecarlo(U, 0.5, 999, True, sims=3000, tope=3, recup=True)
    f1 = H.simular(xau_lj, curva=True)
    ce = diaria(e["curve"])
    out["etapa2"] = dict(escalera=dict(ret=e["ret"], mdd=e["mdd"], n=e["n"], wr=e["wr"], max_riesgo=e["max_riesgo"], niveles=e["niveles"],
                                       meses_pos=e["meses_pos"], mes_prom=e["mes_prom"], peor_mes=e["peor_mes"], dias_pos=e["dias_pos"],
                                       anios=por_anio(ce), cagr=cagr_de(ce), meses=e["meses"]),
                         mc=mc, curve=ce,
                         fijo=dict(ret=f1["ret"], mdd=f1["mdd"], cagr=f1["cagr"], mes_pos=f1["mes_pos"], peor_mes=f1["peor_mes"], anios=f1["anios"]),
                         curve_fijo=diaria(f1["curve"]))

    # 3) y 4) Gestión híbrida = cartera recomendada (Pre NY), y lo estudiado en NY
    hb = rd("mec_hibrida", "datos_hibrida.json"); ca = rd("mec_cartera", "datos_cartera.json"); ny = rd("mec_ny", "datos_ny.json")
    rec = hb["recomendada"]
    out["hibrida"] = dict(combinaciones=hb["meta"]["combinaciones"], califica=rec["califica"], marginal=rec["marginal"],
                          viernes=[{k: v[k] for k in ("variante", "cagr", "mdd", "anios")} for v in rec["viernes"][:2]],
                          activos=[a for a in ca["activos"] if a["sesion"] == "Pre NY"])
    fin = []
    for f in ca["finales"]:
        g = {k: f[k] for k in ("nombre", "activos", "n", "wr", "R", "cagr", "mes_geo", "mdd", "racha", "calmar", "anios", "sem_pos", "mes_pos",
                               "peor_mes", "peor_sem", "pf", "sharpe", "mc", "max_conc", "sem_neg_seg", "bajo_agua")}
        g["curve"] = diaria(f["curve"]); g["meses"] = f["meses"]
        fin.append(g)
    out["finales"] = fin
    filas = []
    for a in ny["meta"]["activos"]:
        el = ny["activos"][a]["elegida"]
        ts, _ = NY.leer(a, el["inicio"], el["patron"])
        ts = [t for t in ts if not t["tags"] and t["ent"].weekday() != 4]          # días sin noticia ni FOMC, lunes a jueves
        R = lambda xs: round(sum(t["u"] for t in xs) / 0.9, 1)
        filas.append(dict(activo=a, patron=el["patron"], inicio=el["inicio"], gana_ambos=el["gana_ambos"], n=len(ts),
                          wr=round(100 * sum(t["u"] > 0 for t in ts) / len(ts), 1), R=R(ts),
                          R25=R([t for t in ts if t["ent"].year == 2025]), R26=R([t for t in ts if t["ent"].year == 2026]),
                          R_op=round(sum(t["u"] for t in ts) / 0.9 / len(ts), 3),
                          con={k: ny["activos"][a]["cartera"][1][k] for k in ("cagr", "mdd", "anios")},
                          base={k: ny["activos"][a]["cartera"][0][k] for k in ("cagr", "mdd", "anios")}))
    out["ny"] = dict(filas=filas, robustez=ny["cartera_ny"]["robustez"], calendario=ny["meta"]["calendario"],
                     cand_pre=[x for x in ca["estabilidad"]["pre"]], reglas_pre=[{k: r[k] for k in ("grupo", "regla", "cagr", "mdd", "anios", "ok")} for r in ca["reglas"]["pre"]],
                     concentracion=ca["concentracion"]["pre"]["top20"])
    out["bench"] = dict(spx=precio(["mec_ny/datos/SPX500_*.csv"]), oro=precio(["mec_hibrida/datos/XAUUSD_m1_2025-2026_*.csv"]))
    json.dump(out, open(os.path.join(AQUI, "datos_informe.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return out


if __name__ == "__main__":
    o = main()
    print("E1", o["etapa1"]["total"], {y: (v["ret_pct"], v["mdd_pct"]) for y, v in o["etapa1"]["anios"].items()}, o["etapa1"]["sin_viernes"])
    e = o["etapa2"]; print("E2", {k: v for k, v in e["escalera"].items() if k != "meses"}, e["mc"], e["fijo"])
    for f in o["finales"]: print(f["nombre"], f["cagr"], f["mdd"], f["anios"], f["calmar"], f["sharpe"], f["pf"])
    for k, b in o["bench"].items(): print(k, {x: b[x] for x in b if x != "curve"})
