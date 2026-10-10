"""Investigación m3 contra m1 (Pre NY): mismas reglas que la gestión ganadora.
Calendario de restricciones + receso, límite de 2 pérdidas por sesión, sin viernes, freno semanal −3R, riesgo 1%."""
import itertools, json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "mec_cartera"))
import base as B
H = B.H
ACT = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD"]
PAT = H.PATRONES
GAN = {"XAUUSD": "E", "EURUSD": "ES", "GBPUSD": "S", "BTCUSD": "E"}     # gestión ganadora en m1


def cargar_m3():
    T = {}
    for a in ACT:
        for p, nom in PAT.items():
            f = os.path.join(AQUI, "datos", f"{a}_m3_2025-2026_{nom}.csv")
            ts = [t for t in H.leer(f, a) if not H.F.motivo_exclusion(t["ent"], H.CAL)]
            ts.sort(key=lambda t: t["ent"])
            for t in ts: t["m"] = H.motivo(t["salida"])
            T[(a, p)] = H.limite_perdidas(ts)
    return T


def stats(ts):
    lj = [t for t in ts if t["ent"].weekday() != 4]
    r = H.resumen(lj)
    for y in (2025, 2026):
        x = [t for t in lj if t["ent"].year == y]
        r[f"R{y}"] = round(sum(t["u"] for t in x) / 0.9, 1); r[f"n{y}"] = len(x)
        r[f"wr{y}"] = round(100 * sum(t["u"] > 0 for t in x) / len(x), 1) if x else 0
    r["dur"] = round(sum((t["sal"] - t["ent"]).total_seconds() / 60 for t in lj) / len(lj), 1) if lj else 0
    r["vie"] = round(sum(t["u"] for t in ts if t["ent"].weekday() == 4) / 0.9, 1)
    return r


def cartera(T, combo, mc=False):
    ts = [t for a, p in combo for t in T[(a, p)] if t["ent"].weekday() != 4]
    return B.metricas(B.filtrar(ts, freno_sem=3), mc=mc, curva=mc)


def main():
    T1 = H.cargar(); T3 = cargar_m3()
    out = {"activos": []}
    for a in ACT:
        for p in PAT:
            s1 = stats(T1[(a, p)]); s3 = stats(T3[(a, p)])
            out["activos"].append(dict(a=a, p=p, m1=s1, m3=s3))
    # mismo sistema elegido, solo cambia el timeframe
    base1 = [(a, GAN[a]) for a in ACT]
    res = {"m1": cartera(T1, base1, mc=True), "m3": cartera(T3, base1, mc=True)}
    # mejor cartera posible en m3 con la misma regla: cada activo-patrón debe ganar 2025 y 2026 (lunes a jueves)
    ok3 = {a: [p for p in PAT if stats(T3[(a, p)])["R2025"] > 0 and stats(T3[(a, p)])["R2026"] > 0] for a in ACT}
    mejores = []
    opciones = [[None] + [(a, p) for p in ok3[a]] for a in ACT]
    for c in itertools.product(*opciones):
        c = [x for x in c if x]
        if not c: continue
        m = cartera(T3, c); mejores.append((m["calmar"] or 0, c, m))
    mejores.sort(key=lambda x: -x[0])
    res["m3_mejor"] = cartera(T3, mejores[0][1], mc=True); res["m3_mejor"]["combo"] = mejores[0][1]
    # mezcla: cada activo en el timeframe que más R por operación da (variante ganadora)
    Tm = {}
    for a in ACT:
        Tm[(a, GAN[a])] = T3[(a, GAN[a])] if stats(T3[(a, GAN[a])])["R_op"] > stats(T1[(a, GAN[a])])["R_op"] else T1[(a, GAN[a])]
    res["mixta"] = cartera(Tm, base1, mc=True)
    res["mixta"]["usa_m3"] = [a for a in ACT if Tm[(a, GAN[a])] is T3[(a, GAN[a])]]
    out["ok3"] = ok3; out["carteras"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("sem_R", "mes_R", "semanas")} for k, v in res.items()}
    for v in out["carteras"].values():
        if "curve" in v:
            dd = {}
            for c in v["curve"]: dd[c["t"][:10]] = c["eq"]
            v["curve"] = [dict(t=k, eq=e) for k, e in sorted(dd.items())]
    out["top_m3"] = [dict(combo=c, cagr=m["cagr"], mdd=m["mdd"], anios=m["anios"], calmar=m["calmar"]) for _, c, m in mejores[:5]]
    # coincidencia de días operados entre m1 y m3 (¿son las mismas oportunidades?)
    out["solape"] = {}
    for a in ACT:
        d1 = {t["ent"].date() for t in T1[(a, GAN[a])]}; d3 = {t["ent"].date() for t in T3[(a, GAN[a])]}
        out["solape"][a] = dict(d1=len(d1), d3=len(d3), comunes=len(d1 & d3))
    json.dump(out, open(os.path.join(AQUI, "resultados_m3.json"), "w", encoding="utf-8"), ensure_ascii=False, default=str, indent=1)
    return out


if __name__ == "__main__":
    o = main()
    print("activo pat | m1: n wr R R_op R25 R26 pf mdd | m3: n wr R R_op R25 R26 pf mdd")
    for x in o["activos"]:
        f = lambda s: f"{s['n']:4} {s['wr']:5} {s['R']:6} {s['R_op']:6} {s['R2025']:6} {s['R2026']:6} {s['pf']} {s['mdd']} vie{s['vie']} dur{s['dur']}"
        print(f"{x['a']} {x['p']:2} | {f(x['m1'])} | {f(x['m3'])}")
    print("ok3", o["ok3"])
    for k, v in o["carteras"].items():
        print(k, v.get("combo", ""), v.get("usa_m3", ""), {kk: v[kk] for kk in ("n", "wr", "R", "cagr", "mdd", "calmar", "anios", "racha", "pf", "sharpe", "mes_pos", "peor_mes")}, v["mc"])
    for t in o["top_m3"]: print(t)
    print(o["solape"])
