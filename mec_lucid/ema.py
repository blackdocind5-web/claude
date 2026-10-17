"""EMA 20 (datos/, sin costos en el archivo) contra EMA 200 (datos_v2/, con comisión y 1 tick de deslizamiento).
A EMA 20 se le aplican los mismos costos: ganada −1 USD, perdida −1,5 USD por micro (comisión + 1 tick de deslizamiento)."""
import os, collections, statistics as st, random
os.environ.setdefault("LUCID_DATOS", "datos")
import fase1 as F, evaluacion as E
FU = E.FUERA
def cargar(v):
    ops = [o for o in F.cargar(v) if o["ent"].hour == 9]
    if v == "datos":
        for o in ops: o["pnl"] = o["pnl"] - (1.0 if o["pnl"] > 0 else 1.5)
    return ops
V = {"EMA 20": cargar("datos"), "EMA 200": cargar("datos_v2")}
DIA = ["Lun", "Mar", "Mié", "Jue", "Vie"]
def seq(ops, hora, f): return sorted([o for o in ops if o["hora"] == hora and f(o)], key=lambda o: o["ent"])
def eq(o): return 100 * (o["sl"] * 2 + 1.5) / (o["sl"] * 2 + 1.5 + o["tp"] * 2 - 1)   # win rate de equilibrio
def fila(x):
    r = F.resumen(x); R = sum(o["pnl"] for o in x)
    return dict(n=r["n"], wr=r["wr"], ww=r["ww"], racha=r["racha_perd"], usd=round(R, 1), eq=round(st.mean(eq(o) for o in x), 1),
                wr25=F.resumen([o for o in x if o["anio"] == 2025])["wr"], wr26=F.resumen([o for o in x if o["anio"] == 2026])["wr"])
FILTROS = {"todos los días": lambda o: True,
           "sin feriados, receso, discursos ni 08:30": lambda o: o["cat"] not in FU + ("Noticia 08:30 (NFP, CPI, PPI, PIB)",),
           "lo anterior + sin martes ni jueves": lambda o: o["cat"] not in FU + ("Noticia 08:30 (NFP, CPI, PPI, PIB)",) and o["ent"].weekday() not in (1, 3)}
if __name__ == "__main__":
    for v, ops in V.items():
        for h in ("09:30", "09:45"):
            print(f"===== {v} · {h}")
            for i in range(5):
                x = seq(ops, h, lambda o, i=i: o["ent"].weekday() == i); r = fila(x)
                print(f"   {DIA[i]}: n {r['n']} WR {r['wr']} (2025 {r['wr25']} / 2026 {r['wr26']}) USD/micro {r['usd']}")
            for fn, f in FILTROS.items():
                x = seq(ops, h, f); r = fila(x)
                p = E.evaluar(x, 1000, 0.0)["p_pasa"]
                py = [E.evaluar([o for o in x if o["anio"] == y], 1000, 0.0)["p_pasa"] for y in (2025, 2026)]
                print(f"  {fn:42} n {r['n']} WR {r['wr']} (25 {r['wr25']} / 26 {r['wr26']}) equilibrio {r['eq']} racha {r['racha']} USD/micro {r['usd']} | pasa {p}% (25 {py[0]} / 26 {py[1]})")
