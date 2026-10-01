"""Métricas del sistema MEC a partir de exports de TradingView ya filtrados por calendario.

Uso:
    python metricas.py                      # procesa los modelos definidos en MODELOS
Requiere haber corrido antes ../mec_filtros/filtrar_trades.py sobre cada CSV
(genera <nombre>_validos.csv y <nombre>_excluidos.csv). Escribe datos.json.
"""
import csv, json, math, random, datetime as dt, statistics as st
from collections import OrderedDict, defaultdict

CAP = 1000.0
TP_FRAC = 0.009  # 1R = 1 TP = 0,9% del capital antes de la operación
MODELOS = {
    "2025": [("combinado", "Envolvente + START", "XAU_m1_2025_Envolvente_y_START"),
             ("envolvente", "Envolvente", "XAU_m1_2025_Envolvente"),
             ("start", "START", "XAU_m1_2025_START")],
    "2026": [("combinado", "Envolvente + START", "XAU_m1_2026_CORREGIDO_Envolvente_y_START"),
             ("envolvente", "Envolvente", "XAU_m1_2026_CORREGIDO_Envolvente"),
             ("start", "START", "XAU_m1_2026_CORREGIDO_START")],
}
MES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
CAL = defaultdict(list)
import glob as _glob
for _f in sorted(_glob.glob("../mec_filtros/calendario_*.csv")):
    for r in csv.DictReader(open(_f, encoding="utf-8-sig"), delimiter=";"):
        CAL[r["fecha"]].append(r)


def leer(path):
    ops = OrderedDict()
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        ops.setdefault(int(r["Número de operación"]), []).append(r)
    out = []
    for n, fs in ops.items():
        e = next(f for f in fs if f["Tipo"].startswith("Entrada"))
        s = next(f for f in fs if f["Tipo"].startswith("Salida"))
        pnl = float(e["PyG netas USD"])
        out.append(dict(
            n=n, dir="BUY" if "largo" in e["Tipo"] else "SELL",
            ent=dt.datetime.strptime(e["Fecha y hora"], "%Y-%m-%d %H:%M"),
            sal=dt.datetime.strptime(s["Fecha y hora"], "%Y-%m-%d %H:%M"),
            pnl=pnl, bars=int(e["Duración (barras)"]), salida=s["Señal"],
            eq_bt=CAP + float(e["PyG acumuladas USD"]) - pnl,  # capital antes, en el backtest completo
            motivo=e.get("Motivo de exclusión", ""),
            px=float(e["Precio USD"]),
        ))
    return out


def grupo(ts, base=CAP):
    if not ts:
        return dict(n=0, wr=0, pnl=0, pct=0, R=0)
    return dict(n=len(ts), wr=round(100 * sum(t["pnl"] > 0 for t in ts) / len(ts), 1),
                pnl=round(sum(t["pnl"] for t in ts), 2), pct=round(100 * sum(t["pnl"] for t in ts) / base, 2),
                R=round(sum(t["R"] for t in ts), 2))


def categorias(t):
    f = t["ent"].strftime("%d/%m/%Y")
    m = t["motivo"]
    out = []
    for c in CAL[f]:
        e = c["evento"]
        if c["regla"] == "SOLO_ENTRADA":
            if not m.startswith("Día"):
                out.append("BCE: entrada después de 08:00")
        elif c["regla"] == "BLOQUEO_NOTICIA":
            if m.startswith("Entrada dentro") and c["evento"].split(" (")[0] in m:
                out.append("ADP: entrada 08:05–08:18" if "ADP" in e else "Core PCE: entrada 08:20–08:33")
        elif m.startswith("Día"):
            if "NFP" in e: out.append("NFP (USD)")
            if "CPI m/m" in e or "CPI USD" in e: out.append("CPI (USD)")
            if "(GBP)" in e: out.append("CPI (GBP)")
            if "Discurso" in e: out.append("Discurso Trump / Warsh")
            if "Final GDP" in e: out.append("PIB final (USD)")
            if "Feriado" in e:
                fer = e[e.index("Feriado"):]
                if "EE. UU." in fer: out.append("Feriado EE. UU.")
                if "Reino Unido" in fer: out.append("Feriado Reino Unido")
                if "EE. UU." not in fer and "Reino Unido" not in fer: out.append("Feriado solo Europa continental")
    return out


def metricas(T):
    """T: operaciones válidas con 'R' ya calculado, ordenadas por salida."""
    eq = CAP; peak = CAP; mdd = 0; info = None; pk_t = None
    curve = [dict(t=T[0]["ent"].strftime("%Y-%m-%d") + " 00:00", eq=CAP)]
    for t in T:
        eq += t["pnl"]; t["eq1"] = eq
        curve.append(dict(t=t["sal"].strftime("%Y-%m-%d %H:%M"), eq=round(eq, 2), n=t["n"]))
        if eq > peak: peak = eq; pk_t = t
        if (peak - eq) / peak > mdd:
            mdd = (peak - eq) / peak
            info = dict(peak=peak, peak_t=pk_t["sal"] if pk_t else T[0]["ent"], trough=eq, trough_t=t["sal"])
    rec = next((t for t in T if t["sal"] > info["trough_t"] and t["eq1"] >= info["peak"]), None)
    pk = CAP; dd = []
    for c in curve:
        pk = max(pk, c["eq"]); dd.append(round(-(pk - c["eq"]) / pk * 100, 3))
    W = [t for t in T if t["pnl"] > 0]; L = [t for t in T if t["pnl"] <= 0]
    gw = sum(t["pnl"] for t in W); gl = -sum(t["pnl"] for t in L)

    def racha(flag):
        b = c = 0
        for t in T:
            c = c + 1 if (t["pnl"] > 0) == flag else 0; b = max(b, c)
        return b
    wk = defaultdict(list)
    for t in T: wk[t["ent"].isocalendar()[:2]].append(t)
    first = T[0]["ent"].date(); last = T[-1]["ent"].date()
    weeks_cal = (last - dt.timedelta(days=last.weekday()) - (first - dt.timedelta(days=first.weekday()))).days // 7 + 1
    weeks = []
    for k in sorted(wk):
        g = grupo(wk[k]); g["sem"] = dt.date.fromisocalendar(k[0], k[1], 1).strftime("%d/%m"); weeks.append(g)
    mo = defaultdict(list)
    for t in T: mo[t["ent"].month].append(t)
    months = []
    for m in sorted(mo):
        g = grupo(mo[m], mo[m][0]["eq1"] - mo[m][0]["pnl"]); g["mes"] = MES[m - 1]; months.append(g)
    days = []
    for d in range(5):
        g = grupo([t for t in T if t["ent"].weekday() == d]); g["dia"] = DIAS[d]; days.append(g)
    hours = []
    for lab, a, b in [("07:00–07:59", 7, 8), ("08:00–08:59", 8, 9), ("09:00 o más", 9, 24)]:
        ts = [t for t in T if a <= t["ent"].hour < b]
        if ts:
            g = grupo(ts); g["franja"] = lab; hours.append(g)
    ex = defaultdict(lambda: [0, 0.0])
    for t in T:
        k = t["salida"]
        if k.startswith("Salida PreNY"): k = "TP" if t["pnl"] > 0 else "SL"
        ex[k][0] += 1; ex[k][1] += t["pnl"]
    # Sharpe / Sortino con retornos diarios hábiles
    dpnl = defaultdict(float)
    for t in T: dpnl[t["sal"].date()] += t["pnl"]
    d = first; eqd = CAP; rets = []
    end = T[-1]["sal"].date()
    while d <= end:
        if d.weekday() < 5:
            p = dpnl.get(d, 0.0); rets.append(p / eqd); eqd += p
        d += dt.timedelta(days=1)
    mu = st.mean(rets); sd = st.pstdev(rets); dsd = math.sqrt(sum(min(0, r) ** 2 for r in rets) / len(rets))
    span = (end - first).days
    cagr = (eq / CAP) ** (365 / span) - 1
    hist = defaultdict(int)
    for t in T: hist[round(t["R"] * 4) / 4] += 1
    Rs = [t["R"] for t in T]
    # Monte Carlo: 5.000 órdenes al azar de las mismas operaciones
    rnd = random.Random(7); mdds = []
    pn = [t["pnl"] for t in T]
    for _ in range(5000):
        rnd.shuffle(pn); e = CAP; p = CAP; m = 0
        for x in pn:
            e += x; p = max(p, e); m = max(m, (p - e) / p)
        mdds.append(m * 100)
    mdds.sort()
    # bootstrap de la expectativa (R por operación)
    boots = []
    for _ in range(5000):
        boots.append(st.mean(rnd.choice(Rs) for _ in Rs))
    boots.sort()
    wr_list = [w["R"] for w in weeks]
    out = dict(
        n=len(T), eq_final=round(eq, 2), pnl=round(eq - CAP, 2), ret_pct=round((eq - CAP) / CAP * 100, 2),
        wr=round(100 * len(W) / len(T), 2), nw=len(W), nl=len(L), pf=round(gw / gl, 2), gw=round(gw, 2), gl=round(gl, 2),
        avg_w=round(gw / len(W), 2), avg_l=round(-gl / len(L), 2), payoff=round((gw / len(W)) / (gl / len(L)), 2),
        exp_usd=round((eq - CAP) / len(T), 2), R_tot=round(sum(Rs), 2), R_avg=round(st.mean(Rs), 3),
        R_w=round(st.mean(t["R"] for t in W), 2), R_l=round(st.mean(t["R"] for t in L), 2),
        R_week=round(sum(Rs) / weeks_cal, 2), R_week_med=round(st.median(wr_list), 2),
        R_week_best=max(wr_list), R_week_worst=min(wr_list),
        mdd_pct=round(mdd * 100, 2), mdd_usd=round(info["peak"] - info["trough"], 2),
        mdd_peak=info["peak_t"].strftime("%d/%m/%Y"), mdd_trough=info["trough_t"].strftime("%d/%m/%Y"),
        mdd_rec=rec["sal"].strftime("%d/%m/%Y") if rec else None,
        mdd_rec_days=(rec["sal"].date() - info["trough_t"].date()).days if rec else None,
        mdd_total_days=(rec["sal"].date() - info["peak_t"].date()).days if rec else None,
        mdd_open_days=None if rec else (end - info["peak_t"].date()).days,
        recovery_factor=round((eq - CAP) / (info["peak"] - info["trough"]), 2),
        calmar=round(cagr / mdd, 2), cagr=round(cagr * 100, 1),
        sharpe=round(mu / sd * math.sqrt(252), 2), sortino=round(mu / dsd * math.sqrt(252), 2) if dsd else None,
        t_stat=round(st.mean(Rs) / (st.stdev(Rs) / math.sqrt(len(Rs))), 2),
        exp_ci=[round(boots[125], 3), round(boots[4875], 3)], p_exp_pos=round(100 * sum(b > 0 for b in boots) / len(boots), 1),
        mc_dd50=round(mdds[2500], 2), mc_dd95=round(mdds[4750], 2),
        streak_w=racha(True), streak_l=racha(False),
        weeks_cal=weeks_cal, weeks_active=len(weeks), trades_week=round(len(T) / weeks_cal, 2),
        wk_pos=sum(w["pnl"] > 0 for w in weeks), wk_neg=sum(w["pnl"] < 0 for w in weeks) + (weeks_cal - len(weeks)) * 0,
        wk_empty=weeks_cal - len(weeks),
        best_week=max(weeks, key=lambda w: w["pnl"]), worst_week=min(weeks, key=lambda w: w["pnl"]),
        dur_avg=round(st.mean(t["bars"] for t in T), 1), dur_med=st.median(t["bars"] for t in T),
        dur_w=round(st.mean(t["bars"] for t in W), 1), dur_l=round(st.mean(t["bars"] for t in L), 1),
        long=grupo([t for t in T if t["dir"] == "BUY"]), short=grupo([t for t in T if t["dir"] == "SELL"]),
        exits={k: [v[0], round(v[1], 2)] for k, v in ex.items()},
        max_win=round(max(pn), 2), max_loss=round(min(pn), 2),
        first=first.strftime("%d/%m/%Y"), last=end.strftime("%d/%m/%Y"),
        curve=curve, dd=dd, weeks=weeks, months=months, days=days, hours=hours,
        hist=sorted([[k, v] for k, v in hist.items()]),
        trades=[dict(n=t["n"], d=t["ent"].strftime("%d/%m"), dir=t["dir"], h=t["ent"].strftime("%H:%M"),
                     pnl=round(t["pnl"], 2), R=round(t["R"], 2)) for t in T],
    )
    return out


def analizar(clave, nombre, base):
    V = sorted(leer(base + "_validos.csv"), key=lambda t: t["sal"])
    X = sorted(leer(base + "_excluidos.csv"), key=lambda t: t["n"])
    eq = CAP
    for t in V:
        t["R"] = t["pnl"] / (TP_FRAC * eq); eq += t["pnl"]
    for t in X:
        t["R"] = t["pnl"] / (TP_FRAC * t["eq_bt"]); t["cats"] = categorias(t)
    D = metricas(V)
    D.update(clave=clave, nombre=nombre, archivo=base, n_total=len(V) + len(X), n_excl=len(X))
    D["excl"] = [dict(n=t["n"], f=t["ent"].strftime("%d/%m"), h=t["ent"].strftime("%H:%M"), hs=t["sal"].strftime("%H:%M"),
                      dir=t["dir"], pnl=round(t["pnl"], 2), R=round(t["R"], 2), cats=t["cats"], m=t["motivo"]) for t in X]
    D["excl_pnl"] = round(sum(t["pnl"] for t in X), 2)
    D["excl_wr"] = round(100 * sum(t["pnl"] > 0 for t in X) / len(X), 1) if X else 0
    agg = {}
    for t in X:
        for c in t["cats"]:
            a = agg.setdefault(c, dict(cat=c, n=0, w=0, pnl=0.0, R=0.0, dias=set()))
            a["n"] += 1; a["w"] += t["pnl"] > 0; a["pnl"] += t["pnl"]; a["R"] += t["R"]; a["dias"].add(t["ent"].date())
    D["excl_cats"] = [dict(cat=a["cat"], n=a["n"], dias=len(a["dias"]), wr=round(100 * a["w"] / a["n"], 1),
                           pnl=round(a["pnl"], 2), R=round(a["R"], 2)) for a in sorted(agg.values(), key=lambda a: -a["R"])]
    # operaciones válidas en días con regla parcial (se operan con restricción horaria)
    parciales = {}
    for t in V:
        for c in CAL[t["ent"].strftime("%d/%m/%Y")]:
            if c["regla"] in ("SOLO_ENTRADA", "BLOQUEO_NOTICIA"):
                lab = "BCE" if "BCE" in c["evento"] else ("ADP" if "ADP" in c["evento"] else "Core PCE")
                parciales.setdefault(lab, []).append(t)
    D["dias_parciales"] = []
    for lab in ("Core PCE", "ADP", "BCE"):
        ts = parciales.get(lab, [])
        g = grupo(ts) if ts else dict(n=0, wr=0, pnl=0, pct=0, R=0)
        g.update(evento=lab, ops=[dict(f=t["ent"].strftime("%d/%m"), h=t["ent"].strftime("%H:%M"), hs=t["sal"].strftime("%H:%M"),
                                       dir=t["dir"], R=round(t["R"], 2), pnl=round(t["pnl"], 2)) for t in ts])
        D["dias_parciales"].append(g)
    gbp = [t for t in X if t["cats"] == ["CPI (GBP)"]]
    cpiu = [t for t in X if t["cats"] == ["CPI (USD)"] and t["ent"].hour < 8]
    s = lambda ts: (round(sum(t["R"] for t in ts), 2), round(sum(t["pnl"] for t in ts), 2))
    D["esc_gbp"] = dict(n=len(gbp), w=sum(t["pnl"] > 0 for t in gbp), R=s(gbp)[0], pnl=s(gbp)[1])
    D["esc_cpiu"] = dict(n=len(cpiu), w=sum(t["pnl"] > 0 for t in cpiu), R=s(cpiu)[0], pnl=s(cpiu)[1], ops=[t["n"] for t in cpiu])
    D["escenarios"] = [
        dict(nombre="Calendario actual", n=D["n"], R=D["R_tot"], pnl=D["pnl"]),
        dict(nombre="+ Habilitar CPI (GBP)", n=D["n"] + len(gbp), R=round(D["R_tot"] + s(gbp)[0], 2), pnl=round(D["pnl"] + s(gbp)[1], 2)),
        dict(nombre="+ CPI (USD) solo con entradas 07:00–07:59", n=D["n"] + len(gbp) + len(cpiu),
             R=round(D["R_tot"] + s(gbp)[0] + s(cpiu)[0], 2), pnl=round(D["pnl"] + s(gbp)[1] + s(cpiu)[1], 2)),
    ]
    # variantes de gestión sobre las operaciones válidas (para la comparativa)
    def var(nombre, pred):
        ts = [dict(t) for t in V if pred(t)]
        e = CAP
        for t in ts:
            t["R"] = t["pnl"] / (TP_FRAC * e); e += t["pnl"]
        m = metricas(ts)
        return dict(nombre=nombre, n=m["n"], wr=m["wr"], pf=m["pf"], R=m["R_tot"], R_avg=m["R_avg"], R_week=m["R_week"],
                    pnl=m["pnl"], mdd=m["mdd_pct"], mc_dd95=m["mc_dd95"], t=m["t_stat"], p_pos=m["p_exp_pos"],
                    trades_week=m["trades_week"])
    D["variantes"] = [
        var("Todas las válidas", lambda t: True),
        var("Solo entradas 07:00–07:59", lambda t: t["ent"].hour == 7),
        var("Entradas 07:00–08:59 (sin las de 09:00)", lambda t: t["ent"].hour < 9),
        var("Solo lunes y martes", lambda t: t["ent"].weekday() < 2),
    ]
    return D, V


def procesar_anio(anio):
    out = {}; ops = {}
    for clave, nombre, base in MODELOS[anio]:
        out[clave], ops[clave] = analizar(clave, nombre, base)
        out[clave]["anio"] = anio
        d = out[clave]
        print(f'{anio} {nombre:20} n={d["n"]} WR={d["wr"]} PF={d["pf"]} R={d["R_tot"]} R/sem={d["R_week"]} DD={d["mdd_pct"]} '
              f'MC95={d["mc_dd95"]} t={d["t_stat"]} Ppos={d["p_exp_pos"]} pnl={d["pnl"]} sharpe={d["sharpe"]}')
    key = lambda t: (t["ent"], t["dir"])
    E = {key(t): t for t in ops["envolvente"]}; S = {key(t): t for t in ops["start"]}; C = {key(t): t for t in ops["combinado"]}
    out["solapamiento"] = dict(
        ambos=len(E.keys() & S.keys()), solo_env=len(E.keys() - S.keys()), solo_start=len(S.keys() - E.keys()),
        comb_de_env=len(C.keys() & E.keys()), comb_de_start=len(C.keys() & S.keys()),
        comb_solo_start=len(C.keys() & (S.keys() - E.keys())),
        R_comb_solo_start=round(sum(C[k]["R"] for k in C.keys() & (S.keys() - E.keys())), 2),
        env_fuera_comb=len(E.keys() - C.keys()),
        R_env_fuera_comb=round(sum(E[k]["R"] for k in E.keys() - C.keys()), 2),
        start_solo_R=round(sum(S[k]["R"] for k in S.keys() - E.keys()), 2),
        start_solo_wr=round(100 * sum(S[k]["pnl"] > 0 for k in S.keys() - E.keys()) / max(1, len(S.keys() - E.keys())), 1),
    )
    return out, ops


if __name__ == "__main__":
    import anual
    datos = {}; OPS = {}
    for anio in MODELOS:
        datos[anio], OPS[anio] = procesar_anio(anio)
    datos["anual"] = anual.comparar(datos, OPS)
    json.dump(datos, open("datos.json", "w"), ensure_ascii=False)
