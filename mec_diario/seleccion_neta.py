"""Re-selección de patrones con costos Multibank (lunes a jueves, sin enero) y prueba de stop mínimo."""
import json, statistics as st, os, diario as Dd, costos as C
B = Dd.B; H = B.H
S = C.stops(); PIP = 0.0001
COST = dict(XAUUSD=0.05, EURUSD=0.4 * PIP, GBPUSD=0.8 * PIP)
T = H.cargar()
def neto(a, p):
    xs = []
    for t in T[(a, p)]:
        if t["ent"].weekday() == 4 or t["ent"].month == 1: continue
        k = (a, t["ent"].strftime("%Y-%m-%d %H:%M"))
        if k not in S: continue
        d = S[k][1]; xs.append(dict(t, u=t["u"] - COST[a] / d, stop=d))
    return xs
res = {}
for a in COST:
    for p in ("E", "S", "ES"):
        xs = neto(a, p)
        f = lambda xs, y: round(sum(t["u"] for t in xs if t["ent"].year == y) / 0.9, 1)
        res[f"{a} {p}"] = dict(n=len(xs), R_op=round(sum(t["u"] for t in xs) / 0.9 / len(xs), 3), R25=f(xs, 2025), R26=f(xs, 2026))
        print(a, p, res[f"{a} {p}"], "stop med", round(st.median(t["stop"] for t in xs), 5))
json.dump(res, open("seleccion_neta.json", "w"))
# stop mínimo: excluir operaciones cuyo costo supera x% del stop
print("== filtro por costo/stop")
for a, p in (("XAUUSD", "E"), ("EURUSD", "ES"), ("GBPUSD", "S"), ("EURUSD", "S")):
    xs = neto(a, p)
    for lim in (1.0, 0.10, 0.07, 0.05):
        ys = [t for t in xs if COST[a] / t["stop"] <= lim]
        print(" ", a, p, f"costo<= {lim:.0%} del stop", len(ys), round(sum(t["u"] for t in ys) / 0.9 / max(1, len(ys)), 3),
              round(sum(t["u"] for t in ys if t["ent"].year == 2025) / 0.9, 1), round(sum(t["u"] for t in ys if t["ent"].year == 2026) / 0.9, 1))
