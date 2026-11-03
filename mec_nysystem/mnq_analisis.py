"""NY SYSTEM · MNQ (Nasdaq) — fase 1 y gestión híbrida con XAUUSD en orden cronológico.
Datos: mnq/MNQ.csv (TradingView, señal BIS, 1 operación por día, RR 1:1, SL/TP/cierre forzado).
Costo Multibank NAS100 (contrato 20 USD por punto, lote mínimo 0,01 = 0,20 USD por punto): spread 0,8 pt + comisión 6 USD por lote = 0,3 pt → 1,1 pt ida y vuelta.
Ventana común con XAUUSD: 08/01/2025–26/10/2026."""
import sys, os, math, collections, statistics as st, json, random, datetime as dt
import analisis as A
M = A.M; AQUI = A.AQUI
PV = 2.0; COSTO_PT = float(os.environ.get("COSTO_PT", 1.1))

def cargar_mnq():
    v = []
    for t in M.leer_tv(os.path.join(AQUI, "mnq", "MNQ.csv")):
        ses = t["ent"].date()
        if not (A.T0 <= ses <= A.T1): continue
        mov = t["lado"] * (t["ps"] - t["pe"])
        d = abs(mov) if t["res"] in ("SL", "TP") else 9950 / (PV * t["q"])
        b = M.base(t, ses)
        v.append(dict(ent=t["ent"], sal=t["sal"], ses=ses, anio=ses.year, n=1, Rb=mov / d, R=mov / d - COSTO_PT / d, gana=mov > 0, res=t["res"],
                      mae=max(-1.0, t["mae"] / (PV * t["q"] * d)), dist=d, tags=A.etiquetas(b["evs"], b["cat"]), cat=b["cat"],
                      dur=(t["sal"] - t["ent"]).total_seconds() / 60, lado=t["lado"], activo="MNQ"))
    return sorted(v, key=lambda t: t["ent"])

def sim_crono(ts, pesos, curva=False):
    """Orden real: el tamaño se fija con el capital realizado al abrir; el resultado se suma al cerrar.
    pesos: riesgo % por activo. Caída flotante: suma la MAE de las posiciones abiertas."""
    ev = []
    for i, t in enumerate(ts):
        ev.append((t["ent"], 1, i)); ev.append((t["sal"], 0, i))
    ev.sort(key=lambda e: (e[0], 2 if (e[1] == 0 and ts[e[2]]["ent"] == e[0]) else e[1]))   # cierres antes que aperturas en el mismo minuto (salvo la propia)
    eq = pk = A.CAP0; mdd = mddf = 0.0; abiertas = {}; cur = []; uw0 = None; uw = 0; sm = {}; eqw = {}
    for when, tipo, i in ev:
        t = ts[i]
        if tipo == 1:
            abiertas[i] = eq * pesos[t["activo"]] / 100
            flo = eq + sum(abiertas[j] * ts[j]["mae"] for j in abiertas); mddf = max(mddf, (pk - flo) / pk)
        else:
            e0 = eq; eq += abiertas.pop(i) * t["R"]; mdd = max(mdd, (pk - eq) / pk)
            if eq > pk:
                pk = eq
                if uw0: uw = max(uw, (when.date() - uw0).days); uw0 = None
            elif uw0 is None: uw0 = when.date()
            k = when.strftime("%Y-%m"); sm.setdefault(k, [e0, eq]); sm[k][1] = eq
            cur.append(dict(t=when.strftime("%Y-%m-%d"), eq=round(eq, 2))); eqw[A.lunes(when.date())] = eq
    if uw0: uw = max(uw, (A.T1 - uw0).days)
    sem = []; prev = A.CAP0; d = A.lunes(A.T0)
    while d <= A.T1:
        if d in eqw: sem.append(eqw[d] / prev - 1); prev = eqw[d]
        else: sem.append(0.0)
        d += dt.timedelta(days=7)
    anos = (A.T1 - A.T0).days / 365.25; cagr = (eq / A.CAP0) ** (1 / anos) - 1
    mw = st.mean(sem); sd = st.pstdev(sem); dn = math.sqrt(sum(min(0, x) ** 2 for x in sem) / len(sem))
    meses = [dict(mes=k, pct=round((v[1] / v[0] - 1) * 100, 2)) for k, v in sorted(sm.items())]
    e25 = [c["eq"] for c in cur if c["t"][:4] == "2025"][-1]
    out = dict(ret=round((eq / A.CAP0 - 1) * 100, 1), cagr=round(cagr * 100, 1), mdd=round(mdd * 100, 1), mdd_flot=round(mddf * 100, 1),
               calmar=round(cagr / mdd, 2), sharpe=round(mw / sd * math.sqrt(52), 2), sortino=round(mw / dn * math.sqrt(52), 2), bajo_agua=uw,
               mes_pos=round(100 * sum(m["pct"] > 0 for m in meses) / len(meses)), peor_mes=min(m["pct"] for m in meses), peor_sem=round(min(sem) * 100, 1),
               anios={"2025": round((e25 / A.CAP0 - 1) * 100, 1), "2026": round((eq / e25 - 1) * 100, 1)}, final=round(eq))
    if curva: out["curve"] = A.diaria(cur)
    return out

def mc_crono(ts, pesos, sims=3000, seed=7):
    """Montecarlo por días: se remuestrean días (con todas sus operaciones de ambos activos) para conservar la correlación."""
    rnd = random.Random(seed); g = collections.defaultdict(list)
    for t in ts: g[t["ses"]].append(t)
    dias = list(g.values()); n = len(dias); anos = (A.T1 - A.T0).days / 365.25; cg = []; dd = []
    for _ in range(sims):
        eq = pk = 1.0; m = 0
        for _ in range(n):
            ops = rnd.choice(dias); r = [eq * pesos[t["activo"]] / 100 for t in ops]
            flo = eq + sum(x * t["mae"] for x, t in zip(r, ops)); m = max(m, (pk - flo) / pk)
            eq += sum(x * t["R"] for x, t in zip(r, ops)); pk = max(pk, eq)
        cg.append(eq ** (1 / anos) - 1); dd.append(m)
    cg.sort(); dd.sort(); q = lambda v, f: v[int(f * len(v))]
    return dict(cagr_p5=round(q(cg, .05) * 100, 1), cagr_med=round(q(cg, .5) * 100, 1), dd_p95=round(q(dd, .95) * 100, 1), p_dd20=round(100 * sum(x > .2 for x in dd) / sims, 1))

def fmt(nom, b, s, mc=None):
    return (f"{nom:38} n {b['n']:3} WR {b['wr']:4.1f} R/op {b['R_op']:+.3f} t {b['t']} R {b['R']:+5.1f} PF {b['pf']} | CAGR {s['cagr']:5.1f} MDD {s['mdd']:4.1f} (flot {s['mdd_flot']:4.1f}) "
            f"Calmar {s['calmar']:5.2f} Sharpe {s['sharpe']:.2f} Sortino {s['sortino']:.2f} meses+ {s['mes_pos']} peor mes {s['peor_mes']:+.1f} sinmax {s['bajo_agua']}d años {s['anios']}"
            + (f" | MC p5 {mc['cagr_p5']} DD95 {mc['dd_p95']} P(DD>20) {mc['p_dd20']}" if mc else ""))

if __name__ == "__main__":
    mq = cargar_mnq(); xau = [dict(t, activo="XAU") for t in A.cargar() if A.FILTROS["Filtro sugerido"](t)]
    print("costo pt", COSTO_PT, "costo R med", round(st.median(COSTO_PT / t["dist"] for t in mq), 4), "dist med", st.median(t["dist"] for t in mq), "res", collections.Counter(t["res"] for t in mq))
    b = A.basicas(mq); print("BASE MNQ", b, "dur", st.median(t["dur"] for t in mq))
    for y in (2025, 2026): print(" ", y, A.basicas([t for t in mq if t["anio"] == y]))
    print("== noticias ==")
    for x in sorted(A.tabla(mq, lambda t: t["tags"]), key=lambda x: -x["n"]):
        print(f'  {x["k"]:26} n {x["n"]:3} WR {x["wr"]:5.1f} R/op {x["R_op"]:+.3f} R {x["R"]:+5.1f} | 2025 {x["R2025"]:+5.1f} ({x["n2025"]}) 2026 {x["R2026"]:+5.1f} ({x["n2026"]})')
    def fr(t):
        m = t["ent"].hour * 60 + t["ent"].minute
        return "09:45–09:59" if m < 600 else "10:00–10:14" if m < 615 else "10:15–10:29" if m < 630 else "10:30–10:44" if m < 645 else "10:45–10:59"
    for nom, f in (("día", lambda t: ["Lun", "Mar", "Mié", "Jue", "Vie"][t["ent"].weekday()]), ("franja", fr), ("lado", lambda t: "largo" if t["lado"] > 0 else "corto"), ("salida", lambda t: t["res"])):
        for x in sorted(A.tabla(mq, f), key=lambda x: x["k"]):
            print(f'  {nom:6} {x["k"]:14} n {x["n"]:3} WR {x["wr"]:5.1f} R/op {x["R_op"]:+.3f} t {x["t"]} | 2025 {x["R2025"]:+5.1f} ({x["n2025"]}) 2026 {x["R2026"]:+5.1f} ({x["n2026"]})')
    D10 = {"ISM", "JOLTS", "Confianza CB", "PCE"}
    FM = {"Sin filtro": lambda t: True, "Sin CPI/NFP": A.FILTROS["Filtro sugerido"], "Regla Rascacielos": A.FILTROS["Regla MNQ (Rascacielos)"],
          "Sin CPI/NFP ni datos 10:00": lambda t: A.FILTROS["Filtro sugerido"](t) and not (D10 & set(t["tags"]))}
    print("== filtros MNQ (1%) ==")
    for nom, f in FM.items():
        s = [t for t in mq if f(t)]; y = {a: A.basicas([t for t in s if t["anio"] == a])["R_op"] for a in (2025, 2026)}
        print(fmt(nom, A.basicas(s), sim_crono(s, {"MNQ": 1.0})), "R/op años", y)
    print("== perfiles MNQ (sin CPI/NFP) ==")
    ms = [t for t in mq if FM["Sin CPI/NFP"](t)]
    for p in (0.5, 1.0, 1.5, 2.0): print(fmt(f"MNQ {p}%", A.basicas(ms), sim_crono(ms, {"MNQ": p}), mc_crono(ms, {"MNQ": p})))
    print("== híbrida cronológica ==")
    todos = sorted(xau + ms, key=lambda t: t["ent"])
    for px, pm in ((1, 0), (0, 1), (1, 1), (1, .5), (1.5, 0), (1.5, 1.5), (1.5, .75), (2, 0), (0.75, 0.75), (1.2, 1.2)):
        sel = [t for t in todos if (px and t["activo"] == "XAU") or (pm and t["activo"] == "MNQ")]
        print(fmt(f"XAU {px}% + MNQ {pm}%", A.basicas(sel), sim_crono(sel, {"XAU": px, "MNQ": pm}), mc_crono(sel, {"XAU": px, "MNQ": pm})))
    # correlación mensual y diaria en R
    def mens(ts):
        d = collections.defaultdict(float)
        for t in ts: d[t["sal"].strftime("%Y-%m")] += t["R"]
        return d
    a, b2 = mens(xau), mens(ms); ks = sorted(set(a) | set(b2))
    print("corr mensual R XAU vs MNQ", round(st.correlation([a[k] for k in ks], [b2[k] for k in ks]), 2))
    dx = {t["ses"]: t["R"] for t in xau if t["n"] == 1}; dm = {t["ses"]: t["R"] for t in ms}; com = sorted(set(dx) & set(dm))
    print("días con ambos", len(com), "corr diaria", round(st.correlation([dx[k] for k in com], [dm[k] for k in com]), 2),
          "| ambos SL", sum(dx[k] < 0 and dm[k] < 0 for k in com), "ambos TP", sum(dx[k] > 0 and dm[k] > 0 for k in com))
    solap = sum(1 for x in xau for m in ms if x["ent"] < m["sal"] and m["ent"] < x["sal"]); print("operaciones solapadas en el tiempo", solap)
