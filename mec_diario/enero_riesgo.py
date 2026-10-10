import diario as Dd, random, json, collections
ts = Dd.cargar(); out = {}
# 1) ¿Es raro que un mes pierda en los dos años? Se reparten al azar las operaciones entre meses (mismo tamaño por mes y año).
rnd = random.Random(3); cnt = 0; cnt_peor = 0; S = 3000
real = collections.defaultdict(float)
for t in ts: real[(t["ent"].month, t["ent"].year)] += t["u"] / 0.9
for _ in range(S):
    por_anio = {}
    for y in (2025, 2026):
        xs = [t for t in ts if t["ent"].year == y]; us = [t["u"] for t in xs]; rnd.shuffle(us)
        acc = collections.defaultdict(float)
        for t, u in zip(xs, us): acc[t["ent"].month] += u / 0.9
        por_anio[y] = acc
    ambos = [m for m in range(1, 13) if m in por_anio[2025] and m in por_anio[2026] and por_anio[2025][m] < 0 and por_anio[2026][m] < 0]
    cnt += bool(ambos)
    if any(por_anio[2025][m] + por_anio[2026][m] <= -5.1 for m in ambos): cnt_peor += 1
out["p_algun_mes_pierde_ambos"] = round(100 * cnt / S, 1); out["p_algun_mes_tan_malo"] = round(100 * cnt_peor / S, 1)
# 2) Sin enero, con 1% y 1,25%
sin = [t for t in ts if t["ent"].month != 1]
out["var"] = []
for nom, T, b in (("1% con enero", ts, 1.0), ("1% sin enero", sin, 1.0), ("1,25% con enero", ts, 1.25), ("1,25% sin enero", sin, 1.25)):
    r = Dd.simular(T, base=b, freno=2.7 * b); m = Dd.montecarlo(T, sims=1000, base=b, freno=2.7 * b)
    out["var"].append(dict(nombre=nom, r={k: v for k, v in r.items() if k != "niveles"}, mc=m))
# 3) Escalera de riesgo fijo, con la ventaja del backtest y con la ventaja recortada (costos de ejecución: −0,1R y −0,2R por operación)
out["riesgo"] = []
for b in (1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0):
    fila = dict(base=b)
    for corte in (0.0, 0.09, 0.18):
        T = [dict(t, u=t["u"] - corte) for t in ts]
        r = Dd.simular(T, base=b, freno=2.7 * b); m = Dd.montecarlo(T, sims=600, base=b, freno=2.7 * b)
        fila[str(corte)] = dict(cagr=r["cagr"], mdd=r["mdd"], peor_mes=r["peor_mes"], mc=m)
    out["riesgo"].append(fila)
json.dump(out, open("enero_riesgo.json", "w"), ensure_ascii=False)
print(out["p_algun_mes_pierde_ambos"], out["p_algun_mes_tan_malo"])
for v in out["var"]: print(v["nombre"], v["r"]["cagr"], v["r"]["mdd"], v["r"]["anios"], v["r"]["peor_mes"], v["r"]["mes_pos"], v["r"]["n"], "| MC", v["mc"]["cagr_med"], v["mc"]["cagr_p5"], v["mc"]["dd_med"], v["mc"]["dd_p95"], v["mc"]["p_dd30"], v["mc"]["p_anio_neg"], v["mc"]["peor_mes_p5"])
for f in out["riesgo"]:
    print(f["base"], *[(c, f[c]["cagr"], f[c]["mdd"], f[c]["mc"]["cagr_med"], f[c]["mc"]["cagr_p5"], f[c]["mc"]["dd_p95"], f[c]["mc"]["p_dd30"], f[c]["mc"]["p_anio_neg"], f[c]["mc"]["peor_mes_p5"]) for c in ("0.0", "0.09", "0.18")], sep="\n  ")
