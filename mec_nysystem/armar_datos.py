"""Arma datos_nysystem.json completo: oro (analisis.py) + Nasdaq NQ «1TP y 3SL» + cartera híbrida + flujo de caja.
python armar_datos.py && python build_nysystem.py"""
import collections, statistics as st, math, json, os, datetime as dt
import analisis as A, mnq_analisis as Q, nq_analisis as N, nq_filtros as F

PERF_NQ = [("Mínimo", 0.25), ("Conservador", 0.5), ("Moderado", 1.0), ("Moderado+", 1.5), ("Arriesgado", 2.0)]

def flujo(curve):
    """Flujo de caja sobre TODAS las semanas y meses del período (también los que no tuvieron operaciones)."""
    eqd = {c["t"]: c["eq"] for c in curve}; e = A.CAP0; d = A.T0; serie = []
    while d <= A.T1:
        e = eqd.get(d.isoformat(), e); serie.append((d, e)); d += dt.timedelta(days=1)
    def rets(clave):
        fin = collections.OrderedDict()
        for d, e in serie: fin[clave(d)] = e
        v = list(fin.values()); prev = A.CAP0; out = []
        for x in v: out.append(x / prev - 1); prev = x
        return out
    sem = rets(lambda d: A.lunes(d)); mes = rets(lambda d: (d.year, d.month))
    def racha(xs):
        m = c = 0
        for x in xs:
            c = c + 1 if x <= 0 else 0; m = max(m, c)
        return m
    return dict(semanas=len(sem), sem_pos=round(100 * sum(x > 0 for x in sem) / len(sem), 1), sem_neg=round(100 * sum(x < 0 for x in sem) / len(sem), 1),
                sem_cero=round(100 * sum(x == 0 for x in sem) / len(sem), 1), sem_med=round(100 * st.median(sem), 2), sem_prom=round(100 * st.mean(sem), 2),
                sem_sd=round(100 * st.pstdev(sem), 2), peor_sem=round(100 * min(sem), 1), racha_sem=racha(sem),
                meses=len(mes), mes_pos=round(100 * sum(x > 0 for x in mes) / len(mes), 1), mes_med=round(100 * st.median(mes), 2), mes_prom=round(100 * st.mean(mes), 2),
                mes_sd=round(100 * st.pstdev(mes), 2), peor_mes=round(100 * min(mes), 1), racha_mes=racha(mes),
                sem_serie=[round(100 * x, 2) for x in sem])

def dist_sem(ts):
    """Operaciones por semana y % de semanas con al menos una operación."""
    w = collections.Counter(A.lunes(t["ent"].date()) for t in ts); n = 0; d = A.lunes(A.T0); act = 0
    while d <= A.T1:
        n += 1; act += d in w; d += dt.timedelta(days=7)
    return dict(ops_sem=round(len(ts) / n, 2), sem_act=round(100 * act / n, 1))

def main():
    out, _ = A.main()
    xau = [dict(t, activo="XAU") for t in A.cargar() if A.FILTROS["Filtro sugerido"](t)]
    # ---------------- NQ ----------------
    g = {}
    for nom, arch in N.G.items():
        ts = N.cargar(arch); sen = F.senales(arch)
        for t in ts: t["sen"] = sen[t["ent"].strftime("%Y-%m-%d %H:%M")]
        g[nom] = ts
    nq_all = g["1TP y 3SL"]
    def base(ts):
        b = A.basicas(ts); c = collections.Counter(t["res"] for t in ts); m, md, dR = N.rach(ts); dv = list(dR.values())
        b.update(tp=round(100 * c["TP"] / len(ts), 1), be=round(100 * c["BE"] / len(ts), 1), sl=round(100 * c["SL"] / len(ts), 1), racha_sl=m, racha_dias=md,
                 dias=len(dR), dia_pos=round(100 * sum(x > 0 for x in dv) / len(dv), 1), peor_dia=round(min(dv), 2), R_dia=round(st.mean(dv), 3),
                 costo_R=round(st.mean(N.COSTO_PT / t["dist"] for t in ts), 4), dist_med=round(st.median(t["dist"] for t in ts), 1),
                 dist_p90=round(sorted(t["dist"] for t in ts)[int(.9 * len(ts))], 1), dur=round(st.median(t["dur"] for t in ts)), **dist_sem(ts))
        return b
    nq = dict(base=base(nq_all), anios={str(y): base([t for t in nq_all if t["anio"] == y]) for y in (2025, 2026)})
    # gestiones
    k1 = {t["clave"]: t for t in g["1TP y 3SL"]}; k3 = {t["clave"]: t for t in g["Máx. 3 por día"]}
    ges = []
    for nom, ts in g.items():
        s = Q.sim_crono(ts, {"NQ": 1.0}); b = base(ts)
        ges.append(dict(nombre=nom, n=b["n"], R_op=b["R_op"], t=b["t"], pf=b["pf"], cagr=s["cagr"], mdd=s["mdd"], bajo_agua=s["bajo_agua"], tp=b["tp"], be=b["be"], sl=b["sl"]))
    tras = collections.defaultdict(list)
    for t in g["Máx. 3 por día"]:
        pass
    prev = {}
    for t in g["Máx. 3 por día"]:
        p = prev.get(t["ses"]); tras["1.ª del día" if p is None else {"SL": "Tras un SL", "BE": "Tras un BE", "TP": "Tras un TP", "Cierre forzado": "Tras un cierre"}[p]].append(t); prev[t["ses"]] = t["res"]
    solo3 = [t for c, t in k3.items() if c not in k1]; solo1 = [t for c, t in k1.items() if c not in k3]; com = [t for c, t in k3.items() if c in k1]
    nq["gestiones"] = ges
    nq["diferencia"] = [dict(k=k, **{x: A.basicas(v)[x] for x in ("n", "wr", "R_op", "R", "t")}) for k, v in
                        (("Comunes a las dos", com), ("Solo en «Máx. 3» (sobre todo tras un TP)", solo3), ("Solo en «1TP y 3SL» (4.ª y 5.ª tras un BE)", solo1))]
    nq["tras"] = [dict(k=k, n=len(v), R_op=round(st.mean(t["R"] for t in v), 3)) for k, v in tras.items() if len(v) > 10]
    # noticias, filtros
    nq["noticias"] = sorted(A.tabla(nq_all, lambda t: t["tags"]), key=lambda x: -x["n"])
    FIL = [("Sin filtro", F.FIL["Sin filtro"]), ("Filtro sugerido", F.FIL["Sin CPI/NFP"]), ("Regla del Nasdaq", F.FIL["Regla Rascacielos"]), ("Sin datos de las 10:00", F.FIL["Sin CPI/NFP ni datos 10:00"])]
    nq["filtros"] = []
    for nom, f in FIL:
        sel = [t for t in nq_all if f(t)]; s = Q.sim_crono(sel, {"NQ": 1.0}); b = A.basicas(sel)
        nq["filtros"].append(dict(nombre=nom, n=b["n"], wr=b["wr"], R_op=b["R_op"], t=b["t"], cagr=s["cagr"], mdd=s["mdd"], calmar=s["calmar"], sharpe=s["sharpe"]))
    sel = [t for t in nq_all if A.FILTROS["Filtro sugerido"](t)]
    nq["fbase"] = base(sel); nq["fanios"] = {str(y): base([t for t in sel if t["anio"] == y]) for y in (2025, 2026)}
    nq["perfiles"] = []
    for nom, p in PERF_NQ:
        s = Q.sim_crono(sel, {"NQ": p}, curva=True); s["mc"] = Q.mc_crono(sel, {"NQ": p}, sims=3000); s.update(nombre=nom, p=p); nq["perfiles"].append(s)
    ds = sorted(t["dist"] for t in sel)
    nq["capital"] = [dict(nombre=n, p=p, ok1000=round(100 * sum(0.2 * d <= 10 * p for d in ds) / len(ds)), med=round(0.2 * st.median(ds) / (p / 100), -1),
                          p90=round(0.2 * ds[int(.9 * len(ds))] / (p / 100), -1), rec=round(5 * 0.2 * st.median(ds) / (p / 100), -2)) for n, p in PERF_NQ]
    mr = collections.defaultdict(float)
    for t in sel: mr[t["sal"].strftime("%Y-%m")] += t["R"]
    nq["meses_R"] = [dict(mes=k, R=round(v, 2)) for k, v in sorted(mr.items())]
    def fr(t):
        m = t["ent"].hour * 60 + t["ent"].minute
        return "09:30–09:44" if m < 585 else "09:45–09:59" if m < 600 else "10:00–10:14" if m < 615 else "10:15–10:29" if m < 630 else "10:30–10:59"
    nq["dia"] = A.tabla(sel, lambda t: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"][t["ent"].weekday()])
    nq["franja"] = A.tabla(sel, fr)
    nq["orden"] = A.tabla(sel, lambda t: ["1.ª del día", "2.ª del día", "3.ª del día", "4.ª o más"][min(t["n"], 4) - 1])
    nq["senal"] = A.tabla(sel, lambda t: {"EXT": "Señal EXT", "COR": "Señal COR"}.get(t["sen"], t["sen"]))
    nq["lado"] = A.tabla(sel, lambda t: "Compras" if t["lado"] > 0 else "Ventas")
    # sensibilidad al costo
    nq["costo_sens"] = []
    for c in (0.0, 1.1, 1.4, 2.0):
        R = [t["R"] + (N.COSTO_PT - c) / t["dist"] for t in sel]; m = st.mean(R)
        nq["costo_sens"].append(dict(pt=c, R_op=round(m, 3), t=round(m / (st.stdev(R) / math.sqrt(len(R))), 1)))
    def mens(ts):
        d = collections.defaultdict(float)
        for t in ts: d[t["sal"].strftime("%Y-%m")] += t["R"]
        return d
    a, b = mens(xau), mens(sel); ks = sorted(set(a) | set(b))
    nq["corr_xau"] = round(st.correlation([a[k] for k in ks], [b[k] for k in ks]), 2)
    p1 = next(x for x in nq["perfiles"] if x["p"] == 1.0); mm = {m["mes"]: m["pct"] for m in p1["meses"]}
    for bn in ("oro", "nasdaq"):
        last = {}
        for c in out["bench"][bn]["curve"]: last[c["t"][:7]] = c["eq"]
        kk = sorted(last); bm = {k: (last[k] / (last[kk[i - 1]] if i else A.CAP0) - 1) * 100 for i, k in enumerate(kk)}
        com_k = [k for k in bm if k in mm]; nq[f"corr_{bn}"] = round(st.correlation([mm[k] for k in com_k], [bm[k] for k in com_k]), 2)
    out["nq"] = nq
    # ---------------- cartera híbrida (orden cronológico real) ----------------
    todos = sorted(xau + sel, key=lambda t: t["ent"]); hib = []
    for px, pn in ((1.0, 0), (1.5, 0), (2.0, 0), (0, 0.5), (1.0, 0.25), (1.5, 0.25), (1.5, 0.5), (1.0, 1.0)):
        ts = [t for t in todos if (px and t["activo"] == "XAU") or (pn and t["activo"] == "NQ")]
        s = Q.sim_crono(ts, {"XAU": px, "NQ": pn}, curva=True); s["mc"] = Q.mc_crono(ts, {"XAU": px, "NQ": pn}, sims=3000)
        s.update(px=px, pn=pn, fl=flujo(s["curve"]), **dist_sem(ts)); hib.append(s)
    out["hibrida"] = hib
    dx = collections.defaultdict(float); dn = collections.defaultdict(float)
    for t in xau: dx[t["ses"]] += t["R"]
    for t in sel: dn[t["ses"]] += t["R"]
    cd = sorted(set(dx) & set(dn))
    out["hib_meta"] = dict(corr_mes=nq["corr_xau"], corr_dia=round(st.correlation([dx[k] for k in cd], [dn[k] for k in cd]), 2), dias_ambos=len(cd),
                           dias_xau=len(dx), dias_nq=len(dn))
    # MNQ anterior (BIS), como referencia descartada
    mq = [t for t in Q.cargar_mnq() if A.FILTROS["Filtro sugerido"](t)]; s = Q.sim_crono(mq, {"MNQ": 1.0}); b = A.basicas(mq)
    out["mnq_bis"] = dict(n=b["n"], wr=b["wr"], R_op=b["R_op"], t=b["t"], pf=b["pf"], cagr=s["cagr"], mdd=s["mdd"], sharpe=s["sharpe"])
    out["meta"]["nq_desde"] = "02/01/2025"; out["meta"]["nq_hasta"] = "13/11/2026"; out["meta"]["fecha"] = "20/11/2026"
    json.dump(out, open(os.path.join(A.AQUI, "datos_nysystem.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return out

if __name__ == "__main__":
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): o = main()
    q = o["nq"]; print("NQ base", q["base"]); print("fbase", q["fbase"])
    for x in q["gestiones"]: print(x)
    print(q["diferencia"]); print(q["tras"]); print(q["filtros"]); print(q["costo_sens"]); print(q["capital"])
    for p in q["perfiles"]: print(p["nombre"], p["p"], {k: p[k] for k in ("cagr", "mdd", "calmar", "sharpe", "peor_mes", "mes_pos", "bajo_agua", "anios")}, p["mc"])
    print("corr", q["corr_xau"], q["corr_oro"], q["corr_nasdaq"], o["hib_meta"], o["mnq_bis"])
    for h in o["hibrida"]:
        f = h["fl"]; print(f"XAU {h['px']} NQ {h['pn']}: CAGR {h['cagr']} MDD {h['mdd']} Sharpe {h['sharpe']} ops/sem {h['ops_sem']} sem_act {h['sem_act']}% | sem+ {f['sem_pos']}% sem- {f['sem_neg']}% sem0 {f['sem_cero']}% med {f['sem_med']} prom {f['sem_prom']} sd {f['sem_sd']} peor {f['peor_sem']} racha sem sin ganar {f['racha_sem']} | mes+ {f['mes_pos']}% med {f['mes_med']} sd {f['mes_sd']} peor {f['peor_mes']} racha {f['racha_mes']} | MC {h['mc']}")
