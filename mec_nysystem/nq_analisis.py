"""Consulta 17/11/2026 (no toca el informe): estrategia NQ con dos gestiones — «1TP y 3SL» y «Máx. 3 por día».
RR 1:2 con break even (BE). Costo Multibank NAS100: 1,1 pt ida y vuelta (spread 0,8 + comisión 6 USD/lote = 0,3 pt).
Ventana común con XAUUSD: 08/01/2025–26/10/2026 (calendario cargado hasta el 22/10/2026)."""
import os, sys, collections, statistics as st, math, datetime as dt
import analisis as A, mnq_analisis as Q
M = A.M; PV = 20.0; COSTO_PT = float(os.environ.get("COSTO_PT", 1.1))
G = {"1TP y 3SL": "nq/NQ_1TP3SL.csv", "Máx. 3 por día": "nq/NQ_max3.csv"}

def cargar(arch, ventana=True):
    v = []; k = collections.Counter()
    for t in M.leer_tv(os.path.join(A.AQUI, arch)):
        ses = t["ent"].date()
        if ventana and not (A.T0 <= ses <= A.T1): continue
        mov = t["lado"] * (t["ps"] - t["pe"])
        d = -mov if t["res"] == "SL" else mov / 2 if t["res"] == "TP" else 10000 / (PV * t["q"])
        k[ses] += 1; b = M.base(t, ses)
        v.append(dict(ent=t["ent"], sal=t["sal"], ses=ses, anio=ses.year, n=k[ses], Rb=mov / d, R=mov / d - COSTO_PT / d, gana=t["res"] == "TP",
                      res=t["res"], sen=t.get("sen", ""), mae=max(-1.0, t["mae"] / (PV * t["q"] * d)), dist=d, tags=A.etiquetas(b["evs"], b["cat"]),
                      cat=b["cat"], dur=(t["sal"] - t["ent"]).total_seconds() / 60, lado=t["lado"], activo="NQ", clave=(t["ent"], t["lado"], t["pe"])))
    return sorted(v, key=lambda t: t["ent"])

def rach(ts):  # peor racha de SL seguidos (BE no corta ni suma) y peor racha de días negativos
    m = c = 0
    for t in ts:
        if t["res"] == "SL": c += 1; m = max(m, c)
        elif t["res"] == "TP": c = 0
    dR = collections.defaultdict(float)
    for t in ts: dR[t["ses"]] += t["R"]
    md = cd = 0
    for k in sorted(dR):
        cd = cd + 1 if dR[k] < 0 else 0; md = max(md, cd)
    return m, md, dR

def ficha(nom, ts, p=1.0, mc=True):
    b = A.basicas(ts); c = collections.Counter(t["res"] for t in ts); m, md, dR = rach(ts)
    s = Q.sim_crono(ts, {"NQ": p}); y = {a: A.basicas([t for t in ts if t["anio"] == a]) for a in (2025, 2026)}
    mcx = Q.mc_crono(ts, {"NQ": p}, sims=2000) if mc else {}
    dv = list(dR.values())
    print(f"{nom:34} n {b['n']:4} días {len(dR)} TP {100*c['TP']/b['n']:4.1f}% BE {100*c['BE']/b['n']:4.1f}% SL {100*c['SL']/b['n']:4.1f}% R/op {b['R_op']:+.3f} t {b['t']} R {b['R']:+6.1f} "
          f"R/día {st.mean(dv):+.3f} días+ {100*sum(x>0 for x in dv)/len(dv):.0f}% PF {b['pf']} rachaSL {m} rachaDías- {md} peor día {min(dv):+.2f}R")
    print(f"{'':34} {p}%: CAGR {s['cagr']:5.1f} MDD {s['mdd']:4.1f} (flot {s['mdd_flot']}) Calmar {s['calmar']:.2f} Sharpe {s['sharpe']} Sortino {s['sortino']} meses+ {s['mes_pos']} "
          f"peor mes {s['peor_mes']:+.1f} sinmax {s['bajo_agua']}d años {s['anios']} | R/op 25 {y[2025]['R_op']:+.3f} t {y[2025]['t']} · 26 {y[2026]['R_op']:+.3f} t {y[2026]['t']}"
          + (f" | MC p5 {mcx['cagr_p5']} DD95 {mcx['dd_p95']} P(DD>20) {mcx['p_dd20']}" if mc else ""))
    return s

if __name__ == "__main__":
    D = {g: cargar(f) for g, f in G.items()}
    for g, ts in D.items():
        print(f"\n######## {g} ########  costo R med {st.median(COSTO_PT/t['dist'] for t in ts):.3f}  stop med {st.median(t['dist'] for t in ts):.1f} pt")
        ficha("Sin filtro", ts)
        print(" por orden en el día:")
        for x in sorted(A.tabla(ts, lambda t: min(t["n"], 4)), key=lambda x: x["k"]):
            print(f"   op {x['k']}{'+' if x['k']==4 else ' '} n {x['n']:4} WR {x['wr']:4.1f} R/op {x['R_op']:+.3f} t {x['t']} | 2025 {x['R2025']:+6.1f} ({x['n2025']}) 2026 {x['R2026']:+6.1f} ({x['n2026']})")
    # diferencia entre gestiones: operaciones que solo toma una de ellas
    k1 = {t["clave"]: t for t in D["1TP y 3SL"]}; k3 = {t["clave"]: t for t in D["Máx. 3 por día"]}
    solo3 = [t for c, t in k3.items() if c not in k1]; solo1 = [t for c, t in k1.items() if c not in k3]; com = [t for c, t in k3.items() if c in k1]
    print(f"\ncomunes {len(com)} | solo Máx.3 {len(solo3)} | solo 1TP3SL {len(solo1)}")
    for nom, s in (("comunes", com), ("solo en Máx. 3 (tras un TP)", solo3), ("solo en 1TP3SL (4.ª/5.ª tras BE)", solo1)):
        b = A.basicas(s); y = {a: A.basicas([t for t in s if t["anio"] == a]) for a in (2025, 2026)}
        print(f"  {nom:34} n {b['n']:4} WR {b['wr']:4.1f} R/op {b['R_op']:+.3f} t {b['t']} R {b['R']:+.1f} | 2025 {y[2025]['R_op']:+.3f} ({y[2025]['n']}) 2026 {y[2026]['R_op']:+.3f} ({y[2026]['n']})")
    # tras TP en Máx 3: ¿qué hace la siguiente?
    for g, ts in D.items():
        prev = {}; after = collections.defaultdict(list)
        for t in ts:
            p = prev.get(t["ses"]); after["1.ª del día" if p is None else "tras " + p].append(t); prev[t["ses"]] = t["res"]
        print(g, {k: (len(v), round(st.mean(x["R"] for x in v), 3)) for k, v in after.items()})
