import io, contextlib, collections, statistics as st
import analisis as A, mnq_analisis as Q, nq_analisis as N
sinCPI = lambda t: "CPI EE. UU." not in t["tags"]
nq = [t for t in N.cargar(N.G["1TP y 3SL"]) if A.FILTROS["Filtro sugerido"](t)]
print("== 1TP3SL: solo sin CPI ==")
N.ficha("Sin CPI EE. UU.", [t for t in N.cargar(N.G["1TP y 3SL"]) if sinCPI(t)])
print("== perfiles 1TP3SL sin CPI/NFP ==")
for p in (0.25, 0.5, 0.75, 1.0): N.ficha(f"riesgo {p}%", nq, p=p)
xau = [dict(t, activo="XAU") for t in A.cargar() if A.FILTROS["Filtro sugerido"](t)]
mnq = [t for t in Q.cargar_mnq() if A.FILTROS["Filtro sugerido"](t)]
def mens(ts):
    d = collections.defaultdict(float)
    for t in ts: d[t["sal"].strftime("%Y-%m")] += t["R"]
    return d
for nom, o in (("XAU", xau), ("MNQ anterior", mnq)):
    a, b = mens(o), mens(nq); ks = sorted(set(a) | set(b))
    print("corr mensual NQ vs", nom, round(st.correlation([a[k] for k in ks], [b[k] for k in ks]), 2))
dx = collections.defaultdict(float); dn = collections.defaultdict(float)
for t in xau: dx[t["ses"]] += t["R"]
for t in nq: dn[t["ses"]] += t["R"]
com = sorted(set(dx) & set(dn)); print("días con ambos", len(com), "corr diaria", round(st.correlation([dx[k] for k in com], [dn[k] for k in com]), 2))
print("== híbrida cronológica XAU + NQ (1TP3SL sin CPI/NFP) ==")
todos = sorted(xau + nq, key=lambda t: t["ent"])
for px, pn in ((1, 0), (1.5, 0), (2, 0), (1, .25), (1, .5), (1.5, .25), (1.5, .5), (1, 1)):
    sel = [t for t in todos if (px and t["activo"] == "XAU") or (pn and t["activo"] == "NQ")]
    s = Q.sim_crono(sel, {"XAU": px, "NQ": pn}); mc = Q.mc_crono(sel, {"XAU": px, "NQ": pn}, sims=2000)
    print(f"XAU {px}% + NQ {pn}%: CAGR {s['cagr']:5.1f} MDD {s['mdd']:4.1f} (flot {s['mdd_flot']}) Calmar {s['calmar']:5.2f} Sharpe {s['sharpe']} Sortino {s['sortino']} meses+ {s['mes_pos']} peor mes {s['peor_mes']:+.1f} sinmax {s['bajo_agua']}d años {s['anios']} | MC p5 {mc['cagr_p5']} DD95 {mc['dd_p95']} P(DD>20) {mc['p_dd20']}")
ds = sorted(t["dist"] for t in nq)
for p in (0.25, 0.5, 0.75, 1.0):
    print(f"lote NAS100 {p}% con 1.000 USD: ejecutables {100*sum(0.2*d <= 10*p for d in ds)/len(ds):.0f}% · capital stop típico {0.2*st.median(ds)/(p/100):.0f} · p90 {0.2*ds[int(.9*len(ds))]/(p/100):.0f}")
