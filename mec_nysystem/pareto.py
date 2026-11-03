"""Consulta 03/11/2026: ¿sacar los lunes? Pareto / dosis mínima sobre NY SYSTEM con filtro sugerido (no toca el informe)."""
import io, contextlib, math, statistics as st, collections, random
import analisis as A
ts = [t for t in A.cargar() if A.FILTROS["Filtro sugerido"](t)]
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie"]
def fr(t):
    m = t["ent"].hour * 60 + t["ent"].minute
    return "09:30–09:44" if m < 585 else "09:45–09:59" if m < 600 else "10:00 o más"
def linea(nom, sel, p=1.0):
    b = A.basicas(sel); s = A.simular(sorted(sel, key=lambda t: t["sal"]), p); mc = A.montecarlo(sel, p, sims=3000)
    y = {a: A.basicas([t for t in sel if t["anio"] == a]) for a in (2025, 2026)}
    dias = len({t["ses"] for t in sel})
    print(f"{nom:34} n {b['n']:3} días {dias:3} WR {b['wr']:4.1f} R/op {b['R_op']:+.3f} t {b['t']:3} R {b['R']:+5.1f} R/día {b['R']/dias:+.3f} PF {b['pf']:.2f} "
          f"| 1%: CAGR {s['cagr']:5.1f} MDD {s['mdd']:3.1f} Calmar {s['calmar']:5.2f} Sharpe {s['sharpe']:.2f} meses+ {s['mes_pos']:.0f} sinmax {s['bajo_agua']:3}d "
          f"MCp5 {mc['cagr_p5']:5.1f} DD95 {mc['dd_p95']:4.1f} | 25 {y[2025]['R_op']:+.3f} ({y[2025]['n']}) 26 {y[2026]['R_op']:+.3f} ({y[2026]['n']})")
print("== Pareto: aporte de cada grupo al R neto ==")
tot = sum(t["R"] for t in ts)
for nom, f in (("día", lambda t: DIAS[t["ent"].weekday()]), ("franja", fr), ("orden", lambda t: "1.ª" if t["n"] == 1 else "2.ª")):
    g = collections.defaultdict(list)
    for t in ts: g[f(t)].append(t)
    for k, v in sorted(g.items(), key=lambda kv: -sum(t["R"] for t in kv[1])):
        R = sum(t["R"] for t in v); y = {a: sum(t["R"] for t in v if t["anio"] == a) for a in (2025, 2026)}
        print(f"  {nom:6} {k:12} {100*len(v)/len(ts):5.1f}% de ops → {100*R/tot:5.1f}% del R  (R/op {R/len(v):+.3f}, n {len(v)}, 2025 {y[2025]:+.1f} 2026 {y[2026]:+.1f})")
# días ordenados por aporte: cuántos días de trading dan el 80% del R bruto ganado
dR = collections.defaultdict(float)
for t in ts: dR[t["ses"]] += t["R"]
pos = sorted((v for v in dR.values() if v > 0), reverse=True); G = sum(pos)
print(f"  días con resultado: {len(dR)}, ganadores {len(pos)} → R neto {tot:.1f}; R bruto ganado {G:.1f}, perdido {G-tot:.1f}")
print("\n== Variantes ==")
V = [("Base (filtro sugerido)", lambda t: True),
     ("Sin lunes", lambda t: t["ent"].weekday() != 0),
     ("Sin lunes ni viernes", lambda t: t["ent"].weekday() not in (0, 4)),
     ("Solo mar-mié-jue", lambda t: t["ent"].weekday() in (1, 2, 3)),
     ("Solo 1.ª operación", lambda t: t["n"] == 1),
     ("Solo entradas 09:30–09:44", lambda t: fr(t) == "09:30–09:44"),
     ("Sin entradas 09:45–09:59", lambda t: fr(t) != "09:45–09:59"),
     ("Sin lunes, solo 1.ª", lambda t: t["ent"].weekday() != 0 and t["n"] == 1)]
for nom, f in V: linea(nom, [t for t in ts if f(t)])
print("\n== ¿Los lunes son distintos o es azar? ==")
lun = [t["R"] for t in ts if t["ent"].weekday() == 0]; res = [t["R"] for t in ts if t["ent"].weekday() != 0]
d = st.mean(lun) - st.mean(res); se = math.sqrt(st.variance(lun) / len(lun) + st.variance(res) / len(res))
print(f"  lunes {st.mean(lun):+.3f} (n {len(lun)}) vs resto {st.mean(res):+.3f} (n {len(res)}): diferencia {d:+.3f}, t {d/se:.2f}")
rnd = random.Random(5); allR = [t["R"] for t in ts]; k = len(lun); peor = 0; N = 20000
for _ in range(N):
    rnd.shuffle(allR); m = [st.mean(allR[i:i+k]) if False else None for i in ()]  # placeholder
# ¿cuántas veces el peor de 5 grupos aleatorios de tamaño parecido es tan malo como el lunes?
dias = [t["ent"].weekday() for t in ts]; obs = st.mean(lun); cnt = 0
for _ in range(N):
    rnd.shuffle(dias); g = collections.defaultdict(list)
    for dd, t in zip(dias, ts): g[dd].append(t["R"])
    cnt += min(st.mean(v) for v in g.values()) <= obs
print(f"  prob. de que, por puro azar, el peor día de la semana rinda {obs:+.3f} o menos: {100*cnt/N:.0f}%")
# fuera de muestra: lo que se hubiera decidido con 2025
print("\n== Fuera de muestra: elegir con 2025, mirar 2026 ==")
for a in (2025, 2026):
    print(" ", a, {DIAS[w]: round(A.basicas([t for t in ts if t["anio"] == a and t["ent"].weekday() == w])["R_op"], 2) for w in range(5)})
