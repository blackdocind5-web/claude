"""Consulta 03/11/2026 (no toca el informe): 1) lote mínimo con 1.000 USD; 2) NY SYSTEM + Mica por horario de corte."""
import sys, os, math, statistics as st, collections, datetime as dt
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import analisis as A
M = A.M
ny = [t for t in A.cargar() if A.FILTROS["Filtro sugerido"](t)]

# ---------- 1) lotes reales: 0,01 lote = 1 oz; siempre se abre (mínimo 1 oz), tamaño redondeado hacia abajo ----------
print("== Lotes con 1.000 USD (NY SYSTEM con filtro) ==")
for p in (0.5, 1.0, 1.25, 1.5, 2.0):
    for modo in ("abajo", "cercano"):
        eq = pk = 1000.0; mdd = 0; riesgos = []; sobre = 0
        for t in ny:
            obj = eq * p / 100; oz = obj / t["dist"]; oz = max(1, math.floor(oz) if modo == "abajo" else round(oz))
            r = oz * t["dist"] / eq * 100; riesgos.append(r); sobre += r > 1.25 * p
            eq += oz * t["dist"] * t["R"]; pk = max(pk, eq); mdd = max(mdd, (pk - eq) / pk)
        anos = (A.T1 - A.T0).days / 365.25
        print(f" {p:4}% {modo:7}: CAGR {100*((eq/1000)**(1/anos)-1):5.1f}% MDD {mdd*100:4.1f}% riesgo real med {st.median(riesgos):.2f}% máx {max(riesgos):.2f}% "
              f"| ops con riesgo >25% sobre lo previsto {100*sobre/len(ny):4.1f}% | primeras 30 ops: máx {max(riesgos[:30]):.2f}% med {st.median(riesgos[:30]):.2f}%")

# ---------- 2) Mica ----------
def mica(arch, obj):
    out = []
    for o in M.mica(arch, obj):
        d = o["perd1"] - M.X.COM - M.X.DESL; d /= M.X.VAL
        out.append(dict(ent=o["ent"], sal=o["sal"], anio=o["anio"], R=o["R"] - A.COSTO / d, gana=o["res"] == "TP", res=o["res"], dist=d,
                        mae=max(-1.0, o["m1"] / (M.X.VAL * d)), tags=A.etiquetas(o["evs"], o["cat"]), n=1, ses=o["ses"]))
    return out
def resumen(ts, nom):
    b = A.basicas(ts); y = {a: A.basicas([t for t in ts if t["anio"] == a]) for a in (2025, 2026)}
    print(f"  {nom:28} n {b['n']:3} WR {b['wr']:5.1f} R/op {b['R_op']:+.3f} t {b['t']:4} R {b['R']:+5.1f} | 2025 {y[2025]['R_op']:+.3f} ({y[2025]['n']}) 2026 {y[2026]['R_op']:+.3f} ({y[2026]['n']})")
def sim(ts, p=1.0):
    ts = sorted(ts, key=lambda t: t["sal"]); s = A.simular(ts, p); return s
for arch, obj, nom in (("xau_v2/XAUUSD_sesion_NY_1R.csv", 1.0, "Mica 1R"), ("xau_v4/XAUUSD_sesion_NY_0.5R.csv", 0.5, "Mica 0,5R")):
    mi = [t for t in mica(arch, obj) if A.FILTROS["Filtro sugerido"](t)]
    hs = sorted(t["ent"].strftime("%H:%M") for t in mi)
    print(f"\n== {nom} (filtro CPI/NFP, costo Multibank) entradas {hs[0]}–{hs[-1]}, {mi[0]['ent']:%d/%m/%Y}–{mi[-1]['ent']:%d/%m/%Y} ==")
    print(" Por franja de 15 min:")
    fr = collections.defaultdict(list)
    for t in mi:
        m = t["ent"].hour * 60 + t["ent"].minute; k = max(570, min(m // 15 * 15, 675)); fr[k].append(t)
    for k in sorted(fr): resumen(fr[k], f"{k//60:02d}:{k%60:02d}–{(k+14)//60:02d}:{(k+14)%60:02d}" + (" o más" if k == 675 else ""))
    print(" Acumulado hasta el corte:")
    nydias = {t["ses"] for t in ny}
    for corte in ("10:00", "10:15", "10:30", "10:45", "11:00", "todo"):
        sel = [t for t in mi if corte == "todo" or t["ent"].strftime("%H:%M") < corte]
        resumen(sel, f"Mica antes de {corte}")
        for variante in ("suma", "sin solapar"):
            add = sel if variante == "suma" else [t for t in sel if t["ses"] not in nydias]
            for p in (1.0,):
                s = sim(ny + add, p)
                print(f"     NY+Mica {variante:11} {p}%: n {len(ny)+len(add)} CAGR {s['cagr']:5.1f}% MDD {s['mdd']:4.1f}% (flot {s['mdd_flot']}) Calmar {s['calmar']:5.2f} Sharpe {s['sharpe']} meses+ {s['mes_pos']}% peor mes {s['peor_mes']} años {s['anios']}")
    s = sim(ny, 1.0); print(f"  NY SYSTEM solo 1%: CAGR {s['cagr']}% MDD {s['mdd']}% Calmar {s['calmar']} Sharpe {s['sharpe']} años {s['anios']}")
    # correlación mensual NY vs Mica (todo)
    def mens(ts):
        d = collections.defaultdict(float)
        for t in ts: d[t["sal"].strftime("%Y-%m")] += t["R"]
        return d
    a, b = mens(ny), mens(mi); ks = sorted(set(a) | set(b))
    print("  correlación mensual NY vs Mica:", round(st.correlation([a[k] for k in ks], [b[k] for k in ks]), 2))
