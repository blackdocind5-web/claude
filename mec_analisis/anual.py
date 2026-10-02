"""Comparación 2025 vs 2026 y prueba de filtros de operativa en los dos años (validación cruzada)."""
import datetime as dt, statistics as st, math
from collections import defaultdict
import metricas as M

PCE_0830 = None  # se calcula desde el calendario


def recalc(ts):
    ts = sorted((dict(t) for t in ts), key=lambda t: t["sal"])
    e = M.CAP
    for t in ts:
        t["R"] = t["pnl"] / (M.TP_FRAC * e); e += t["pnl"]
    return ts


def resumen(ts):
    if len(ts) < 3:
        return None
    m = M.metricas(recalc(ts))
    return dict(n=m["n"], wr=m["wr"], pf=m["pf"], R=m["R_tot"], R_avg=m["R_avg"], R_week=m["R_week"], pnl=m["pnl"],
                mdd=m["mdd_pct"], mc95=m["mc_dd95"], t=m["t_stat"], p=m["p_exp_pos"], tw=m["trades_week"], sharpe=m["sharpe"])


def por_dia(ts):
    d = defaultdict(list)
    for t in sorted(ts, key=lambda t: t["ent"]): d[t["ent"].date()].append(t)
    return d


def max_por_dia(ts, k):
    return [x for v in por_dia(ts).values() for x in v[:k]]


def stop_perdidas_dia(ts, k):
    out = []
    for v in por_dia(ts).values():
        l = 0
        for t in v:
            if l >= k: break
            out.append(t); l += t["pnl"] <= 0
    return out


def limite_sesion(ts):
    """Límite de la estrategia original: se deja de operar en la sesión tras 1 ganadora o 2 perdedoras."""
    out = []
    for v in por_dia(ts).values():
        g = p = 0
        for t in v:
            if g >= 1 or p >= 2: break
            out.append(t)
            if t["pnl"] > 0: g += 1
            else: p += 1
    return out


def stop_semanal(ts, limite):
    out = []; wk = defaultdict(list)
    for t in sorted(ts, key=lambda t: t["ent"]): wk[t["ent"].isocalendar()[:2]].append(t)
    for v in wk.values():
        acc = 0
        for t in v:
            if acc <= -limite: break
            out.append(t); acc += t["pnl"] / 9.0  # aproximación: 1R ≈ 9 USD con 1.000 USD de capital
    return out


def tendencia(ts_ref, dias=20):
    """Devuelve una función que dice si la operación va a favor de la tendencia de N días,
    usando como referencia el precio medio de entrada de todas las operaciones del archivo en ese lapso."""
    pts = sorted((t["ent"], t["px"]) for t in ts_ref)
    def fav(t):
        ini = t["ent"] - dt.timedelta(days=dias)
        prev = [p for (d, p) in pts if ini <= d < t["ent"] - dt.timedelta(days=1)]
        if len(prev) < 3: return True
        sube = t["px"] > st.mean(prev)
        return (t["dir"] == "BUY") == sube
    return fav


def comparar(datos, OPS):
    pce_dias = {f for f, rs in M.CAL.items() if any("Core PCE" in r["evento"] and r["ventana_NY"].startswith("08:20") for r in rs)}
    out = {"filtros": [], "anios": {}}
    for anio in ("2025", "2026"):
        out["anios"][anio] = {k: resumen(OPS[anio][k]) for k in ("combinado", "envolvente", "start")}
    # base y filtros sobre Envolvente
    for anio in ("2025", "2026"):
        E = OPS[anio]["envolvente"]; fav = tendencia(OPS[anio]["combinado"] + E)
        F = [
            ("base", "Envolvente, reglas actuales", E),
            ("viernes", "Sin operar los viernes", [t for t in E if t["ent"].weekday() != 4]),
            ("h7", "Solo entradas 07:00–07:59", [t for t in E if t["ent"].hour == 7]),
            ("h8", "Solo entradas 08:00–08:59", [t for t in E if t["ent"].hour == 8]),
            ("sesion", "Límite por sesión: 1 TP o 2 SL", limite_sesion(E)),
            ("max1", "Máximo 1 operación por día", max_por_dia(E, 1)),
            ("stop1", "Cortar el día tras la 1.ª pérdida", stop_perdidas_dia(E, 1)),
            ("sem2", "Cortar la semana al llegar a −2R", stop_semanal(E, 2)),
            ("pce", "Core PCE: solo entradas 07:00–07:59", [t for t in E if not (t["ent"].strftime("%d/%m/%Y") in pce_dias and t["ent"].hour >= 8)]),
            ("tend", "Solo a favor de la tendencia de 20 días", [t for t in E if fav(t)]),
            ("contra", "Solo en contra de la tendencia de 20 días", [t for t in E if not fav(t)]),
            ("long", "Solo compras", [t for t in E if t["dir"] == "BUY"]),
            ("short", "Solo ventas", [t for t in E if t["dir"] == "SELL"]),
        ]
        for key, nombre, ts in F:
            r = resumen(ts)
            f = next((x for x in out["filtros"] if x["key"] == key), None)
            if not f:
                f = dict(key=key, nombre=nombre); out["filtros"].append(f)
            f[anio] = r
    for f in out["filtros"]:
        b5, b6 = out["filtros"][0]["2025"], out["filtros"][0]["2026"]
        a, b = f.get("2025"), f.get("2026")
        if a and b:
            f["dR"] = [round(a["R"] - b5["R"], 2), round(b["R"] - b6["R"], 2)]
            f["dRop"] = [round(a["R_avg"] - b5["R_avg"], 3), round(b["R_avg"] - b6["R_avg"], 3)]
            f["dmdd"] = [round(a["mdd"] - b5["mdd"], 2), round(b["mdd"] - b6["mdd"], 2)]
            f["robusto"] = f["key"] != "base" and f["dR"][0] > 0 and f["dR"][1] > 0
    # dos años juntos (Envolvente)
    E2 = OPS["2025"]["envolvente"] + OPS["2026"]["envolvente"]
    C2 = OPS["2025"]["combinado"] + OPS["2026"]["combinado"]
    S2 = OPS["2025"]["start"] + OPS["2026"]["start"]
    out["dos_anios"] = {k: resumen(v) for k, v in (("envolvente", E2), ("combinado", C2), ("start", S2))}
    Ep = recalc(E2)
    W = [t for t in Ep if t["pnl"] > 0]; L = [t for t in Ep if t["pnl"] <= 0]
    wr = len(W) / len(Ep); payoff = (sum(t["pnl"] for t in W) / len(W)) / (-sum(t["pnl"] for t in L) / len(L))
    out["kelly2"] = round(wr - (1 - wr) / payoff, 3)
    # desglose por dirección, hora, día y mes para Envolvente en cada año
    def g(ts):
        ts = recalc(ts) if ts else []
        return dict(n=len(ts), wr=round(100 * sum(t["pnl"] > 0 for t in ts) / len(ts), 1) if ts else 0,
                    R=round(sum(t["R"] for t in ts), 2), R_avg=round(st.mean(t["R"] for t in ts), 3) if ts else 0)
    det = {}
    for anio in ("2025", "2026"):
        E = OPS[anio]["envolvente"]
        dd = por_dia(E)
        det[anio] = dict(
            dir={"Compras": g([t for t in E if t["dir"] == "BUY"]), "Ventas": g([t for t in E if t["dir"] == "SELL"])},
            hora={h: g([t for t in E if t["ent"].hour == hh]) for h, hh in (("07:00–07:59", 7), ("08:00–08:59", 8), ("09:00", 9))},
            dia={n: g([t for t in E if t["ent"].weekday() == i]) for i, n in enumerate(M.DIAS)},
            orden={"1.ª del día": g([v[0] for v in dd.values()]), "2.ª o más del día": g([x for v in dd.values() for x in v[1:]])},
            dur={"Hasta 10 min": g([t for t in E if t["bars"] <= 10]), "11 a 30 min": g([t for t in E if 10 < t["bars"] <= 30]), "Más de 30 min": g([t for t in E if t["bars"] > 30])},
            precio=dict(ini=round(min(E, key=lambda t: t["ent"])["px"]), fin=round(max(E, key=lambda t: t["ent"])["px"]),
                        mn=round(min(t["px"] for t in E)), mx=round(max(t["px"] for t in E))),
        )
    out["detalle"] = det
    # reglas de tamaño de riesgo (sobre la secuencia de R de Envolvente en cada año)
    def sim(ts, regla, fav):
        ts = sorted(ts, key=lambda t: t["sal"]); eq = M.CAP; pk = M.CAP; mdd = 0
        for t in ts:
            r = regla(t, eq, pk, fav)
            eq += t["R"] * M.TP_FRAC * eq * r
            pk = max(pk, eq); mdd = max(mdd, (pk - eq) / pk)
        return dict(ret=round((eq - M.CAP) / M.CAP * 100, 2), mdd=round(mdd * 100, 2))
    reglas = [
        ("1% fijo (actual)", lambda t, eq, pk, f: 1.0),
        ("0,75% fijo", lambda t, eq, pk, f: 0.75),
        ("1%, baja a 0,5% con caída ≥ 5% (vuelve a 1% en nuevo máximo)", lambda t, eq, pk, f: 0.5 if (pk - eq) / pk >= 0.05 else 1.0),
        ("1%, baja a 0,5% con caída ≥ 3% (vuelve a 1% en nuevo máximo)", lambda t, eq, pk, f: 0.5 if (pk - eq) / pk >= 0.03 else 1.0),
        ("1% a favor de la tendencia, 0,5% en contra", lambda t, eq, pk, f: 1.0 if f(t) else 0.5),
    ]
    out["riesgo"] = []
    for nombre, regla in reglas:
        x = dict(nombre=nombre)
        for anio in ("2025", "2026"):
            E = OPS[anio]["envolvente"]; fav = tendencia(OPS[anio]["combinado"] + E)
            x[anio] = sim(E, regla, fav)
        out["riesgo"].append(x)
    # eventos excluidos: los dos años juntos (Envolvente)
    ev = defaultdict(lambda: dict(n=0, w=0, R=0.0, pnl=0.0))
    for anio in ("2025", "2026"):
        for c in datos[anio]["envolvente"]["excl_cats"]:
            e = ev[c["cat"]]; e["n"] += c["n"]; e["w"] += round(c["n"] * c["wr"] / 100); e["R"] += c["R"]; e["pnl"] += c["pnl"]
            e.setdefault("por_anio", {})[anio] = dict(n=c["n"], R=c["R"], wr=c["wr"])
    out["eventos"] = sorted([dict(cat=k, n=v["n"], wr=round(100 * v["w"] / v["n"], 1), R=round(v["R"], 2), pnl=round(v["pnl"], 2), por_anio=v["por_anio"]) for k, v in ev.items()], key=lambda x: -x["R"])
    par = defaultdict(lambda: dict(n=0, R=0.0, w=0))
    for anio in ("2025", "2026"):
        for p in datos[anio]["envolvente"]["dias_parciales"]:
            x = par[p["evento"]]; x["n"] += p["n"]; x["R"] += p["R"]; x["w"] += sum(o["R"] > 0 for o in p["ops"])
            x.setdefault("por_anio", {})[anio] = dict(n=p["n"], R=p["R"], ops=p["ops"])
    out["europa_pura"] = {}
    for anio in ("2025", "2026"):
        xs = [x for x in datos[anio]["envolvente"]["excl"] if x["cats"] == ["Feriado solo Europa continental"]]
        out["europa_pura"][anio] = dict(n=len(xs), R=round(sum(x["R"] for x in xs), 2), w=sum(x["pnl"] > 0 for x in xs),
                                        ops=[dict(f=x["f"], R=x["R"]) for x in xs])
    meses = {}
    for anio in ("2025", "2026"):
        meses[anio] = {m["mes"]: m["R"] for m in datos[anio]["envolvente"]["months"]}
    out["meses"] = meses
    out["parciales"] = [dict(evento=k, n=v["n"], R=round(v["R"], 2), wr=round(100 * v["w"] / v["n"], 1) if v["n"] else 0, por_anio=v["por_anio"]) for k, v in par.items()]
    return out
