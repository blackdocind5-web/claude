"""NY SYSTEM (antes KALA): XAUUSD, sesión NY, RR 1:1, hasta 2 operaciones por día (la 2.ª solo tras un SL).
Datos: ../mec_lucid/kala/XAU_ATR.csv (TradingView, 08/01/2025–26/10/2026). Capital propio: CFD XAUUSD en Multibank,
costo 0,05 USD por onza ida y vuelta (spread 0,02 + comisión 0,03), medido contra la distancia del stop.
Perfiles de riesgo con interés compuesto sobre 1.000 USD: 0,5%, 1%, 1,5% y 2% por operación.
Calendario NY (../mec_ny/calendario_ny.csv) para el filtro por noticias. → datos_nysystem.json"""
import collections, datetime as dt, json, os, random, statistics as st, sys, math, glob, csv
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "mec_lucid"))
import motor as M
COSTO = 0.05; CAP0 = 1000.0
T0, T1 = dt.date(2025, 1, 8), dt.date(2026, 10, 26)
PERFILES = [("Conservador", 0.5), ("Moderado", 1.0), ("Moderado+", 1.5), ("Arriesgado", 2.0)]

def etiquetas(evs, cat):
    e = evs.lower(); t = []
    if "nfp" in e: t.append("NFP")
    if "cpi m/m (usd)" in e or ("cpi" in e and "usd" in e and "gbp" not in e): t.append("CPI EE. UU.")
    if "ppi" in e: t.append("PPI")
    if "gdp" in e or "pib" in e: t.append("PIB")
    if "federal funds" in e or "fomc statement" in e: t.append("FOMC (decisión)")
    elif "minutes" in e: t.append("Minutas FOMC")
    if "ism" in e: t.append("ISM")
    if "jolts" in e: t.append("JOLTS")
    if "cb consumer" in e: t.append("Confianza CB")
    if "pce" in e: t.append("PCE")
    if "discurso" in e: t.append("Discurso 09–11")
    if "receso" in e: t.append("Receso fin de año")
    elif "feriado" in e:
        t.append("Feriado EE. UU." if "ee. uu" in e else "Feriado Europa / R. Unido")
    if "(gbp)" in e: t.append("CPI R. Unido")
    return t or ["Sin noticias"]

def cargar():
    ts = []
    for o in M.kala():
        c = COSTO / o["dist"]; R = o["R"] - c
        ts.append(dict(ent=o["ent"], sal=o["sal"], ses=o["ses"], anio=o["anio"], n=o["n"], R=R, Rb=o["R"], gana=o["res"] == "TP",
                       mae=max(-1.0, o["m1"] / (M.X.VAL * o["dist"])), dist=o["dist"], tags=etiquetas(o["evs"], o["cat"]), cat=o["cat"],
                       lado=None, dur=(o["sal"] - o["ent"]).total_seconds() / 60))
    return sorted(ts, key=lambda t: t["ent"])

lunes = lambda d: d - dt.timedelta(days=d.weekday())

def simular(ts, p, curva=False):
    eq = pk = CAP0; mdd = mddf = 0.0; cur = []; uw0 = None; uw = 0; sw = collections.defaultdict(float); sm = collections.defaultdict(lambda: [None, None])
    for t in ts:
        e0 = eq; flo = eq * (1 + p / 100 * t["mae"]); mddf = max(mddf, (pk - flo) / pk)
        eq *= 1 + p / 100 * t["R"]; mdd = max(mdd, (pk - eq) / pk)
        if eq > pk:
            pk = eq
            if uw0: uw = max(uw, (t["sal"].date() - uw0).days); uw0 = None
        elif uw0 is None: uw0 = t["sal"].date()
        k = t["sal"].strftime("%Y-%m")
        if sm[k][0] is None: sm[k][0] = e0
        sm[k][1] = eq
        cur.append(dict(t=t["sal"].strftime("%Y-%m-%d"), eq=round(eq, 2)))
    if uw0: uw = max(uw, (T1 - uw0).days)
    # semanas (todas las semanas del período, con o sin operaciones)
    eqw = {}; e = CAP0
    for t in ts: e *= 1 + p / 100 * t["R"]; eqw[lunes(t["sal"].date())] = e
    sem = []; prev = CAP0; d = lunes(T0)
    while d <= T1:
        if d in eqw: sem.append(eqw[d] / prev - 1); prev = eqw[d]
        else: sem.append(0.0)
        d += dt.timedelta(days=7)
    anos = (T1 - T0).days / 365.25; ret = eq / CAP0 - 1; cagr = (eq / CAP0) ** (1 / anos) - 1
    mw = st.mean(sem); sd = st.pstdev(sem); dn = math.sqrt(sum(min(0, x) ** 2 for x in sem) / len(sem))
    meses = [dict(mes=k, pct=round((v[1] / v[0] - 1) * 100, 2)) for k, v in sorted(sm.items())]
    fin25 = [t for t in ts if t["sal"].year == 2025]; e25 = CAP0
    for t in fin25: e25 *= 1 + p / 100 * t["R"]
    out = dict(ret=round(ret * 100, 1), cagr=round(cagr * 100, 1), mdd=round(mdd * 100, 1), mdd_flot=round(mddf * 100, 1),
               calmar=round(cagr / mdd, 2) if mdd else None, sharpe=round(mw / sd * math.sqrt(52), 2) if sd else None,
               sortino=round(mw / dn * math.sqrt(52), 2) if dn else None, final=round(eq, 0), bajo_agua=uw,
               sem_pos=round(100 * sum(x > 0 for x in sem) / sum(x != 0 for x in sem), 1), sem_act=sum(x != 0 for x in sem), semanas=len(sem),
               peor_sem=round(min(sem) * 100, 1), mejor_sem=round(max(sem) * 100, 1),
               mes_pos=round(100 * sum(m["pct"] > 0 for m in meses) / len(meses), 0), peor_mes=min(m["pct"] for m in meses), mejor_mes=max(m["pct"] for m in meses),
               mes_prom=round(st.mean(m["pct"] for m in meses), 2), meses=meses,
               anios={"2025": round((e25 / CAP0 - 1) * 100, 1), "2026": round((eq / e25 - 1) * 100, 1)})
    if curva: out["curve"] = diaria(cur)
    return out

def diaria(cur):
    d = {}
    for c in cur: d[c["t"]] = c["eq"]
    return [dict(t=k, eq=v) for k, v in sorted(d.items())]

def montecarlo(ts, p, sims=5000, seed=11):
    rnd = random.Random(seed); Rs = [t["R"] for t in ts]; maes = [t["mae"] for t in ts]; n = len(Rs); anos = (T1 - T0).days / 365.25
    cg = []; dd = []; neg = 0
    for _ in range(sims):
        eq = pk = 1.0; m = 0
        for _ in range(n):
            i = rnd.randrange(n); flo = eq * (1 + p / 100 * maes[i]); m = max(m, (pk - flo) / pk)
            eq *= 1 + p / 100 * Rs[i]; pk = max(pk, eq)
        cg.append(eq ** (1 / anos) - 1); dd.append(m); neg += eq < 1
    cg.sort(); dd.sort(); q = lambda v, f: v[int(f * len(v))]
    return dict(cagr_med=round(q(cg, .5) * 100, 1), cagr_p5=round(q(cg, .05) * 100, 1), dd_med=round(q(dd, .5) * 100, 1), dd_p95=round(q(dd, .95) * 100, 1),
                p_perdida=round(100 * neg / sims, 1), p_dd20=round(100 * sum(x > .2 for x in dd) / sims, 1), p_dd30=round(100 * sum(x > .3 for x in dd) / sims, 1))

def basicas(ts):
    if not ts: return None
    R = [t["R"] for t in ts]; g = [r for r in R if r > 0]; l = [-r for r in R if r <= 0]
    sem = (T1 - T0).days / 7; rach = lambda s: max((len(x) for x in "".join("g" if t["gana"] else "p" for t in ts).split("g" if s == "p" else "p")), default=0)
    return dict(n=len(ts), wr=round(100 * len(g) / len(R), 1), R=round(sum(R), 1), R_op=round(st.mean(R), 3), R_sem=round(sum(R) / sem, 3),
                pf=round(sum(g) / sum(l), 2) if l else None, payoff=round(st.mean(g) / st.mean(l), 2) if l and g else None,
                racha_p=rach("p"), racha_g=rach("g"), t=round(st.mean(R) / (st.stdev(R) / math.sqrt(len(R))), 1) if len(R) > 2 else None)

def tabla(ts, clave):
    d = collections.defaultdict(list)
    for t in ts:
        ks = clave(t); ks = ks if isinstance(ks, list) else [ks]
        for k in ks: d[k].append(t)
    out = []
    for k, v in d.items():
        b = basicas(v); b["k"] = k
        for y in (2025, 2026):
            vy = [t for t in v if t["anio"] == y]; b[f"R{y}"] = round(sum(t["R"] for t in vy), 1); b[f"n{y}"] = len(vy)
        out.append(b)
    return out

def precio(patrones, pv=1):
    px = {}
    for pat in patrones:
        for f in glob.glob(os.path.join(RAIZ, pat)):
            for r in csv.DictReader(open(f, encoding="utf-8-sig")):
                t = r["Fecha y hora"][:16]
                if T0.isoformat() <= t[:10] <= T1.isoformat(): px[t] = float(r["Precio USD"])
    ts = sorted(px); p0 = px[ts[0]]
    cur = diaria([dict(t=t[:10], eq=round(CAP0 * px[t] / p0, 2)) for t in ts])
    pk = CAP0; m = 0
    for c in cur: pk = max(pk, c["eq"]); m = max(m, (pk - c["eq"]) / pk)
    anos = (T1 - T0).days / 365.25; e25 = [c["eq"] for c in cur if c["t"][:4] == "2025"][-1]
    return dict(curve=cur, ret=round((cur[-1]["eq"] / CAP0 - 1) * 100, 1), cagr=round(((cur[-1]["eq"] / CAP0) ** (1 / anos) - 1) * 100, 1),
                mdd=round(m * 100, 1), anios={"2025": round((e25 / CAP0 - 1) * 100, 1), "2026": round((cur[-1]["eq"] / e25 - 1) * 100, 1)}, fin=cur[-1]["t"])

FILTROS = {
    "Sin filtro": lambda t: True,
    "Filtro sugerido": lambda t: not ({"CPI EE. UU.", "NFP"} & set(t["tags"])),
    "Regla MNQ (Rascacielos)": lambda t: not ({"Feriado EE. UU.", "Feriado Europa / R. Unido", "Receso fin de año", "Discurso 09–11", "ISM", "JOLTS", "Confianza CB", "PCE", "CPI EE. UU.", "PIB"} & set(t["tags"])),
}

def main():
    ts = cargar(); out = dict(meta=dict(desde=T0.strftime("%d/%m/%Y"), hasta=T1.strftime("%d/%m/%Y"), costo=COSTO, cap0=CAP0,
                                         dist_med=round(st.median(t["dist"] for t in ts), 2), dist_p90=round(sorted(t["dist"] for t in ts)[int(.9 * len(ts))], 2),
                                         cal_hasta="22/10/2026"))
    out["base"] = basicas(ts); out["base"]["costo_R"] = round(st.mean(COSTO / t["dist"] for t in ts), 4)
    out["base"]["dur"] = round(st.median(t["dur"] for t in ts)); out["base"]["dias"] = len({t["ses"] for t in ts})
    out["base"]["por_sem"] = round(len(ts) / ((T1 - T0).days / 7), 2)
    out["anios"] = {str(y): basicas([t for t in ts if t["anio"] == y]) for y in (2025, 2026)}
    out["noticias"] = sorted(tabla(ts, lambda t: t["tags"]), key=lambda x: -x["n"])
    out["dia"] = tabla(ts, lambda t: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"][t["ent"].weekday()])
    def franja(t):
        m = t["ent"].hour * 60 + t["ent"].minute
        return "09:30–09:44" if m < 585 else "09:45–09:59" if m < 600 else "10:00–10:29" if m < 630 else "10:30 o más"
    out["franja"] = tabla(ts, franja)
    out["orden"] = tabla(ts, lambda t: "1.ª del día" if t["n"] == 1 else "2.ª del día (tras un SL)")
    out["perfiles"] = {}
    for nf, f in FILTROS.items():
        sel = [t for t in ts if f(t)]
        out["perfiles"][nf] = dict(base=basicas(sel), anios={str(y): basicas([t for t in sel if t["anio"] == y]) for y in (2025, 2026)},
                                   p=[dict(nombre=n, p=p, **simular(sel, p, curva=True), mc=montecarlo(sel, p)) for n, p in PERFILES])
    out["bench"] = dict(oro=precio(["mec_lucid/kala/*.csv", "mec_lucid/xau_v2/*.csv", "mec_lucid/xau_v4/*.csv"]),
                        nasdaq=precio(["mec_lucid/alex/*.csv", "mec_lucid/datos_v7/*.csv"]))
    sug = [t for t in ts if FILTROS["Filtro sugerido"](t)]
    mr = collections.defaultdict(float)
    for t in sug: mr[t["sal"].strftime("%Y-%m")] += t["R"]
    out["meses_R"] = [dict(mes=k, R=round(v, 2)) for k, v in sorted(mr.items())]
    ds = sorted(t["dist"] for t in sug)
    out["capital"] = [dict(nombre=n, p=p, med=round(st.median(ds) / (p / 100), -1), p90=round(ds[int(.9 * len(ds))] / (p / 100), -1),
                           ok1000=round(100 * sum(d <= 1000 * p / 100 for d in ds) / len(ds), 0),
                           rec=round(5 * st.median(ds) / (p / 100), -2)) for n, p in PERFILES]
    # correlación mensual con el oro y el Nasdaq (perfil 1%)
    p1 = next(x for x in out["perfiles"]["Filtro sugerido"]["p"] if x["p"] == 1.0); mm = {m["mes"]: m["pct"] for m in p1["meses"]}
    def mensual(curve):
        last = {}
        for c in curve: last[c["t"][:7]] = c["eq"]
        ks = sorted(last); return {k: (last[k] / (last[ks[i - 1]] if i else CAP0) - 1) * 100 for i, k in enumerate(ks)}
    for b in ("oro", "nasdaq"):
        bm = mensual(out["bench"][b]["curve"]); ks = [k for k in bm if k in mm]
        a = [mm[k] for k in ks]; c = [bm[k] for k in ks]
        out["bench"][b]["corr"] = round(st.correlation(a, c), 2)
    return out, ts

if __name__ == "__main__":
    o, ts = main()
    print("base", o["base"]); print("años", o["anios"])
    for x in o["noticias"]: print(f'  {x["k"]:26} n {x["n"]:3} WR {x["wr"]:5.1f} R/op {x["R_op"]:+.3f} R {x["R"]:+5.1f} | 2025 {x["R2025"]:+5.1f} ({x["n2025"]}) 2026 {x["R2026"]:+5.1f} ({x["n2026"]})')
    for k in ("dia", "franja", "orden"):
        for x in o[k]: print(f'  {k} {x["k"]:24} n {x["n"]:3} WR {x["wr"]:5.1f} R/op {x["R_op"]:+.3f} 2025 {x["R2025"]:+5.1f} 2026 {x["R2026"]:+5.1f}')
    for nf, v in o["perfiles"].items():
        print(nf, v["base"])
        for p in v["p"]: print(f'   {p["nombre"]:11} {p["p"]}%: ret {p["ret"]}% CAGR {p["cagr"]}% MDD {p["mdd"]}% (flot {p["mdd_flot"]}) Calmar {p["calmar"]} Sharpe {p["sharpe"]} Sortino {p["sortino"]} años {p["anios"]} meses+ {p["mes_pos"]}% peor mes {p["peor_mes"]} bajo agua {p["bajo_agua"]}d | MC {p["mc"]}')
    for k, b in o["bench"].items(): print(k, {x: b[x] for x in b if x != "curve"})
    print(o["capital"]); print(o["meses_R"])
    json.dump(o, open(os.path.join(AQUI, "datos_nysystem.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
