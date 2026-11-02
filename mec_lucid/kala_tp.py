import sys, os; AQ=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQ); os.chdir(AQ)
import motor as M, statistics as st, math
reg = M.C.regla; todo = lambda o: True
def recorte(ops, t):
    v = []
    for o in ops:
        if o["res"] == "TP" or o["mfe"] >= t - 1e-9:
            u1 = M.X.VAL * o["dist"] * t - M.X.COM; v.append(dict(o, R=t, res="TP", u1=u1, sl_hit=False, m1=min(o["m1"], 0)))
        else: v.append(o)
    return v
K = M.kala()
for t in (1.0, 0.7, 0.5):
    ops = recorte(K, t); x = [o for o in ops if reg(o)]; r = [o["u1"] / o["perd1"] for o in x]; m = st.mean(r); se = st.stdev(r) / math.sqrt(len(r))
    y = {a: st.mean([q for q, o in zip(r, x) if o["anio"] == a]) for a in (2025, 2026)}
    lin = f"KALA TP {t}R regla: WR {100*sum(o['res']=='TP' for o in x)/len(x):.1f}% (equil {100/(1+t):.1f}) E[R] {m:+.3f} t {m/se:.1f} 2025 {y[2025]:+.3f} 2026 {y[2026]:+.3f}"
    for rr in (500, 700, 1000):
        f = M.ficha("", [(ops, rr, reg)]); D = M.dias([(ops, rr, reg)]); res, peor = M.cadena(D, obj=1250, mll=1000, cons=0.4); P = [h for q, h in res if q == "pasa"]
        lin += f" | @{rr}: {f['pasa']:.0f}% ({f['p25']:.0f}/{f['p26']:.0f}) {sum(h for _, h in res)/len(P):.0f} días/cuenta peor {peor}"
    print(lin, flush=True)
