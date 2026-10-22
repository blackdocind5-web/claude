"""XAUUSD 'Rango Apertura' (OANDA, TradingView), RR 1:0,7, abril–octubre 2026 (xau_v1/, 16 exportaciones de 2 semanas con solapes).
Un trade por día salvo que el primero toque SL: entonces puede haber un segundo. Se normaliza cada trade a R
(pérdida = −1R; ganada = +0,7R aprox.) porque TradingView arriesga ~100 USD con cantidades enteras."""
import csv, glob, os, collections, statistics as st, math, datetime as dt
AQUI = os.path.dirname(os.path.abspath(__file__))

def cargar():
    t = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "xau_v1", "*.csv"))):
        filas = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}
        for r in filas:
            if not r["Tipo"].startswith("Entrada"): continue
            s = sal[r["Número de operación"]]; e = dt.datetime.strptime(r["Fecha y hora"], "%Y-%m-%d %H:%M")
            t.setdefault(e, dict(ent=e, sal=dt.datetime.strptime(s["Fecha y hora"], "%Y-%m-%d %H:%M"), lado=r["Tipo"][11:],
                                 pe=float(r["Precio USD"]), ps=float(s["Precio USD"]), q=int(r["Tamaño (cant.)"]),
                                 pnl=float(r["PyG netas USD"]), res=s["Señal"]))
    ops = sorted(t.values(), key=lambda o: o["ent"])
    for o in ops:
        o["gana"] = o["res"] == "TP"; o["dist"] = abs(o["ps"] - o["pe"])
    # riesgo en USD: en SL es la pérdida; en TP, la distancia al TP / 0,7
    for o in ops:
        o["riesgo"] = -o["pnl"] if not o["gana"] else o["pnl"] / 0.7
        o["R"] = o["pnl"] / o["riesgo"] if not o["gana"] else 0.7
        o["sl_pts"] = o["dist"] if not o["gana"] else o["dist"] / 0.7
    dia = collections.defaultdict(list)
    for o in ops: dia[o["ent"].date()].append(o)
    for d, v in dia.items():
        for i, o in enumerate(v): o["n"] = i + 1
    return ops, dict(sorted(dia.items()))

OPS, DIA = cargar()

def rachas(seq):
    g = []; p = []; c = 0; s = None
    for x in seq:
        if s is None or x == s: c += 1
        else: (g if s else p).append(c); c = 1
        s = x
    (g if s else p).append(c)
    return g, p

if __name__ == "__main__":
    W, L = sum(o["gana"] for o in OPS), sum(not o["gana"] for o in OPS)
    print(f"trades {len(OPS)} días {len(DIA)} | TP {W} SL {L} WR {100*W/len(OPS):.1f}% | equilibrio {100/1.7:.1f}%")
    print("SL en puntos: mediana", round(st.median(o["sl_pts"] for o in OPS), 2), "min", round(min(o["sl_pts"] for o in OPS), 2), "max", round(max(o["sl_pts"] for o in OPS), 2))
    print("ganada en R (TV): media", round(st.mean(o["pnl"] / (o["pnl"] / 0.7) for o in OPS if o["gana"]), 2))
    P = [o for o in OPS if o["n"] == 1]; S = [o for o in OPS if o["n"] == 2]
    wr = lambda v: 100 * sum(o["gana"] for o in v) / len(v)
    print(f"primer trade: {len(P)} WR {wr(P):.1f}% | segundo trade (tras SL): {len(S)} WR {wr(S):.1f}% → {[(o['ent'].strftime('%d/%m'), o['res']) for o in S]}")
    print("esperanza R: primeros", round(sum(o["R"] for o in P) / len(P), 3), "segundos", round(sum(o["R"] for o in S) / len(S), 3), "todos", round(sum(o["R"] for o in OPS) / len(OPS), 3))
    m = collections.defaultdict(list)
    for o in P: m[o["ent"].strftime("%m/%Y")].append(o["gana"])
    print("primer trade por mes:", {k: f"{100*sum(v)/len(v):.0f}% ({len(v)})" for k, v in sorted(m.items(), key=lambda x: x[0][3:] + x[0][:2])})
    print("por día:", {d: f"{wr([o for o in P if o['ent'].weekday()==i]):.0f}%" for i, d in enumerate(["lun", "mar", "mié", "jue", "vie"])}, "| lado:", {l: f"{wr([o for o in P if o['lado']==l]):.0f}%" for l in ("largo", "corto")})
    for nom, seq in (("primeros trades (1 por día)", [o["gana"] for o in P]), ("todos los trades", [o["gana"] for o in OPS])):
        g, p = rachas(seq)
        print(f"{nom}: rachas TP media {st.mean(g):.2f} máx {max(g)} dist {sorted(collections.Counter(g).items())} | rachas SL media {st.mean(p):.2f} máx {max(p)} dist {sorted(collections.Counter(p).items())}")
    # Evaluación con la regla estricta: 2 TP seguidos (días distintos), cualquier SL = cuenta perdida
    dias = list(DIA.values())
    # A) solo el primer trade del día; la cuenta nueva empieza al día siguiente
    def cadena_A():
        i = 0; r = []
        while i < len(dias):
            a = dias[i][0]
            if not a["gana"]: r.append("x"); i += 1; continue
            if i + 1 >= len(dias): break
            b = dias[i + 1][0]; r.append("P" if b["gana"] else "x"); i += 2
        return r
    # B) si el primero da SL y hay segundo trade, ese segundo trade abre una cuenta nueva el mismo día
    def cadena_B():
        i = 0; k = 0; r = []
        while i < len(dias):
            o = dias[i][k]
            if not o["gana"]:
                r.append("x")
                if k + 1 < len(dias[i]): k += 1
                else: i += 1; k = 0
                continue
            if i + 1 >= len(dias): break
            b = dias[i + 1][0]
            if b["gana"]: r.append("P"); i += 2; k = 0
            else:
                r.append("x")
                if len(dias[i + 1]) > 1: i += 1; k = 1
                else: i += 2; k = 0
        return r
    def peor(r):
        m = c = 0
        for x in r: c = c + 1 if x == "x" else 0; m = max(m, c)
        return m
    pA = sum(1 for i in range(len(dias) - 1) if dias[i][0]["gana"] and dias[i + 1][0]["gana"]) / (len(dias) - 1)
    print(f"\nPase (empezando cada día, primer trade): {100*pA:.1f}% | teórico WR²: {wr(P)**2/100:.1f}% | sin ventaja (58,8%²): {58.8**2/100:.1f}%")
    for nom, r in (("A: un trade por día", cadena_A()), ("B: usa el 2.º trade para abrir cuenta nueva", cadena_B())):
        p = r.count("P"); n = len(r)
        print(f"{nom}: {p} pases / {n} cuentas = {100*p/n:.1f}% | evals por pase {n/p:.2f} (~{65.3*n/p:.0f} USD) | peor racha {peor(r)} quemadas | {''.join(r)}")
    p = pA
    print("cuentas para pasar al menos una:", {k: f"{100*(1-(1-p)**k):.0f}%" for k in (1, 2, 3, 4, 5, 6, 8, 10)})
