"""Estrategia RR 1:0,2 (datos_v3/, ya con comisión y deslizamiento): 09:30 o 09:45, SL 70/TP 14 o SL 60/TP 12.
Periodos Ene–Jun 2025 (dic 2024 se ignora), Jun–Oct 2025, Nov 2025–Abr 2026 y Mar–Oct 2026 (se solapan mar–abr 2026: se queda una sola operación por día)."""
import glob, os, re, csv, random, collections, datetime as dt
import fase1 as F, evaluacion as E
AQUI = os.path.dirname(os.path.abspath(__file__)); CAL = F.calendario()
DIAS = ["lun", "mar", "mié", "jue", "vie"]

def cargar():
    ops = {}; difs = 0
    for f in sorted(glob.glob(os.path.join(AQUI, "datos_v3", "FASE_1-MNQ_*.csv"))):
        m = re.search(r"_(\d\d\.\d\d)h_SL_(\d+)_TP_(\d+)", f); hora, sl, tp = m.group(1).replace(".", ":"), int(m.group(2)), int(m.group(3))
        filas = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        for r in filas:
            if not r["Tipo"].startswith("Entrada"): continue
            t = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M"); pnl = float(r["PyG netas USD"])
            if t.year < 2025 or t.hour != int(hora[:2]): continue   # Fabián: ignorar dic 2024; fuera de horario (09/01/2025 18:00)
            k = (hora, sl, t.date())
            if k in ops:
                difs += ops[k]["pnl"] != pnl; continue
            ops[k] = dict(hora=hora, sl=sl, tp=tp, ent=t, pnl=pnl, gana=pnl > 0, anio=t.year, normal=abs(pnl) <= sl * F.PUNTO + 3,
                          cat=F.categoria(t.date(), CAL), dia=t.weekday(), lado="largo" if "largo" in r["Tipo"] else "corto")
    return list(ops.values()), difs

def racha(s):
    m = c = 0
    for o in s: c = 0 if o["gana"] else c + 1; m = max(m, c)
    return m

def eq(s):
    g = [o["pnl"] for o in s if o["gana"]]; p = [-o["pnl"] for o in s if not o["gana"]]
    G, P = sum(g) / len(g), sum(p) / len(p); return 100 * P / (G + P)

def nulo(s, reps=300):
    """Misma secuencia de días y tamaños, resultados al azar con win rate = equilibrio (sin ventaja)."""
    w = eq(s) / 100; G = [o for o in s if o["gana"]][0]["pnl"]; P = [o for o in s if not o["gana"]][0]["pnl"]
    rs = []
    for _ in range(reps):
        x = [dict(o, pnl=G if random.random() < w else P) for o in s]
        rs.append(E.evaluar(x, 1000, 0.0)["p_pasa"])
    rs.sort(); return sum(rs) / len(rs), rs[int(.95 * len(rs))]

def fila(nom, s):
    wr = lambda x: f"{100 * sum(o['gana'] for o in x) / len(x):.1f}" if x else "-"
    a = {y: [o for o in s if o["anio"] == y] for y in (2025, 2026)}
    ev = E.evaluar(s, 1000, 0.0); eva = {y: E.evaluar(a[y], 1000, 0.0)["p_pasa"] for y in a}
    k = F.contratos(s[0]["sl"])
    print(f"  {nom:52} n={len(s):3} WR {wr(s)} ({wr(a[2025])}/{wr(a[2026])}) eq {eq(s):.1f} racha {racha(s)} "
          f"USD/micro {sum(o['pnl'] for o in s):+.0f} pasa {ev['p_pasa']} ({eva[2025]}/{eva[2026]}) días med {ev['dias_med']} quema med {ev['dias_quema']}")

FILTROS = [("todos los días", lambda o: True),
           ("sin feriados, receso, discursos ni 08:30", lambda o: o["cat"] not in E.FUERA and not o["cat"].startswith("Noticia 08:30")),
           ("sin feriados, receso ni discursos", lambda o: o["cat"] not in E.FUERA)]

if __name__ == "__main__":
    random.seed(7); OPS, difs = cargar()
    print("operaciones distintas en el solape:", difs, "| anómalas (pérdida > SL):", sum(not o["normal"] for o in OPS))
    for hora in ("09:30", "09:45"):
        for sl in (70, 60):
            s = sorted([o for o in OPS if o["hora"] == hora and o["sl"] == sl], key=lambda o: o["ent"])
            k = F.contratos(sl)
            print(f"\n{hora} SL {sl} TP {s[0]['tp']} · {k} micros: gana {k * s[0]['pnl'] if s[0]['gana'] else k * [o for o in s if o['gana']][0]['pnl']:.0f}, pierde {k * [o for o in s if not o['gana']][0]['pnl']:.0f} · {s[0]['ent']:%d/%m/%Y}–{s[-1]['ent']:%d/%m/%Y}")
            print("  por día:", " ".join(f"{DIAS[d]} {100 * sum(o['gana'] for o in s if o['dia'] == d) / max(1, sum(1 for o in s if o['dia'] == d)):.1f}%({sum(1 for o in s if o['dia'] == d)})" for d in range(5)))
            cats = collections.defaultdict(list)
            for o in s: cats[o["cat"]].append(o["gana"])
            print("  por categoría:", "; ".join(f"{c} {100 * sum(v) / len(v):.1f}%({len(v)})" for c, v in cats.items()))
            print("  por lado:", "; ".join(f"{l} {100 * sum(o['gana'] for o in s if o['lado'] == l) / sum(1 for o in s if o['lado'] == l):.1f}%" for l in ("largo", "corto")))
            for fn, f in FILTROS:
                x = [o for o in s if f(o)]; fila(fn, x)
            x = [o for o in s if FILTROS[1][1](o)]; m, p95 = nulo(x)
            print(f"  sin ventaja (azar al {eq(x):.1f}%, filtro 2): pasa {m:.1f}% (p95 {p95:.1f}%)")
