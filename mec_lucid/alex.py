"""Alex (MNQ, orden limit en un nivel de Fibonacci, RR 1:1, un trade por día, 02/01/2025–22/10/2026; alex/).
TradingView con capital 1.000.000 y riesgo 1% por trade, sin comisión. Cada trade se pasa a R con la distancia del SL en
puntos (|salida − entrada| en SL y TP; en cierre forzado, 10.000 / (2 × contratos)). En Lucid: micros MNQ (2 USD/punto),
comisión 1 USD ida y vuelta + 1 tick (0,50 USD) en SL, por micro. Calendario y regla de noticias igual que Rascacielos."""
import csv, glob, os, re, collections, datetime as dt
import combo3 as C, comparar as K
AQUI = os.path.dirname(os.path.abspath(__file__)); PV = 2.0; COM = 1.0; DESL = 0.5

def nombre(f):
    b = os.path.basename(f)[:-4]
    filtro = "con EMA 200 + VWAP" if b.startswith("MNQ___con") else "sin filtro"
    fib = re.search(r"fibo_([\d.]+)", b).group(1); hora = re.search(r"hasta_las_([\d.]+)h", b).group(1)
    hora = hora.replace(".", ":") if ":" in hora.replace(".", ":") else hora + ":00"
    return f"Alex {filtro} · Fibo {fib.replace('.', ',')}% · hasta {hora}"

def cargar(f):
    filas = list(csv.DictReader(open(f, encoding="utf-8-sig")))
    sal = {r["Número de operación"]: r for r in filas if r["Tipo"].startswith("Salida")}; v = []
    for r in filas:
        if not r["Tipo"].startswith("Entrada"): continue
        s = sal[r["Número de operación"]]; e = dt.datetime.strptime(r["Fecha y hora"][:16], "%Y-%m-%d %H:%M")
        lado = 1 if "largo" in r["Tipo"] else -1; pe, ps = float(r["Precio USD"]), float(s["Precio USD"]); mov = lado * (ps - pe)
        q = int(r["Tamaño (cant.)"]); res = s["Señal"]
        d = abs(mov) if res in ("SL", "TP") and abs(mov) > 0 else 10000 / (PV * q)
        ses = e.date()
        v.append(dict(ent=e, ses=ses, anio=ses.year, hora=e.strftime("%H:%M"), res=res, dist=d, R=mov / d, q=q,
                      cat=C.F.categoria(ses, C.CAL), evs=" ".join(x for _, x in C.CAL.get(ses, [])), sl_hit=res == "SL",
                      perd1=PV * d + COM + DESL))
    return sorted(v, key=lambda o: o["ent"])

def neto(o): return o["R"] - (COM + (DESL if o["sl_hit"] else 0)) / (PV * o["dist"])

def usd(o, q): return q * (PV * o["dist"] * o["R"] - COM - (DESL if o["sl_hit"] else 0))

T = {nombre(f): cargar(f) for f in sorted(glob.glob(os.path.join(AQUI, "alex", "*.csv")))}
