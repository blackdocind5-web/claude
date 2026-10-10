"""Costos reales de Multibank (10/10/2026): spreads + comisión ECN de 3 USD por lote ida y vuelta; BTCUSD como CFD con 50 USD de spread."""
import json, os, statistics as st, diario as Dd, costos as C
S = C.stops(); ts = Dd.cargar(); PIP = 0.0001
MB = dict(XAUUSD=0.02 + 0.03, EURUSD=(0.1 + 0.3) * PIP, GBPUSD=(0.5 + 0.3) * PIP, BTC_spread=50, fee_btc=0)
T = C.aplicar(ts, MB, S); T0 = C.aplicar(ts, C.ESC["Sin costos (backtest)"], S)
out = {"por_activo": {}, "carteras": {}, "btc_stop": []}
for a in Dd.PRE:
    x = [t for t in T if t["a"] == a]; x0 = [t for t in T0 if t["a"] == a]
    R = lambda xs, y=None: round(sum(t["u"] for t in xs if y is None or t["ent"].year == y) / 0.9, 1)
    out["por_activo"][a] = dict(n=len(x), costo_R=round(st.mean(t["costo"] for t in x) / 0.9, 3), R_op_bruto=round(R(x0) / len(x), 3), R_op_neto=round(R(x) / len(x), 3),
                                R25=R(x, 2025), R26=R(x, 2026), R25_bruto=R(x0, 2025), R26_bruto=R(x0, 2026))
    print(a, out["por_activo"][a])
# BTCUSD por tamaño de stop: ¿hay operaciones donde el spread de 50 USD pese poco?
bt = [t for t in T if t["a"] == "BTCUSD"]
for lo, hi in ((0, 75), (75, 125), (125, 200), (200, 10 ** 9)):
    x = [t for t in bt if lo <= S[(t["a"], t["ent"].strftime("%Y-%m-%d %H:%M"))][1] < hi]
    if x: out["btc_stop"].append(dict(desde=lo, hasta=hi, n=len(x), R_op_neto=round(sum(t["u"] for t in x) / 0.9 / len(x), 3),
                                      R25=round(sum(t["u"] for t in x if t["ent"].year == 2025) / 0.9, 1), R26=round(sum(t["u"] for t in x if t["ent"].year == 2026) / 0.9, 1)))
print(out["btc_stop"])
for nom, X in (("4 activos, costos Multibank", T), ("Sin BTCUSD, costos Multibank", [t for t in T if t["a"] != "BTCUSD"]),
               ("Sin BTCUSD, sin costos", [t for t in T0 if t["a"] != "BTCUSD"]), ("4 activos, sin costos", T0)):
    for b in (1.0, 1.25):
        r = Dd.simular(X, base=b, freno=2.7 * b, detalle=True); m = Dd.montecarlo(X, sims=800, base=b, freno=2.7 * b)
        out["carteras"][f"{nom} · {b}%"] = dict(r={k: v for k, v in r.items() if k not in ("niveles", "curve", "dias_lista")}, mc=m)
        print(f"{nom:32} {b}% | {r['cagr']:6} dd {r['mdd']:5} {r['anios']} wr {r['wr']} mes+ {r['mes_pos']} peor_mes {r['peor_mes']} | MC med {m['cagr_med']} p5 {m['cagr_p5']} dd95 {m['dd_p95']} dd30 {m['p_dd30']} añoneg {m['p_anio_neg']}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "multibank.json"), "w"), ensure_ascii=False)
