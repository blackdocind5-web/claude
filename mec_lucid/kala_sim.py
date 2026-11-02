import sys, os; AQ=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQ); os.chdir(AQ)
import motor as M, random
reg = M.C.regla; todo = lambda o: True
K = M.kala(); K1 = [o for o in K if o["n"] == 1]
RAS = M.rascacielos(); M05 = M.mica("xau_v4/XAUUSD_sesion_NY_0.5R.csv", 0.5)
def vel(D, cu):
    kw = dict(obj=cu["obj"], mll=cu["mll"], cons=0.4); res, peor = M.cadena(D, **kw); P = [h for r, h in res if r == "pasa"]
    return (sum(h for _, h in res) / len(P) if P else None), f"{len(P)}/{len(res)}", peor
def nulo(D, cu, reps=1000):
    """sin ventaja: cada trade TP/SL al 50% (RR 1:1) con su flotante real recortado al resultado"""
    rnd = random.Random(7); kw = dict(obj=cu["obj"], mll=cu["mll"], cons=0.4); acc = 0
    for k in range(5):
        D2 = [[dict(o, usd=(o["q"] * (o["perd1"] - 2 * (M.X.COM + M.X.DESL / 2))) if rnd.random() < .5 else -o["q"] * o["perd1"], mae=min(o["mae"], 0)) for o in d] for d in D]
        acc += M.montecarlo(D2, n=reps, **kw)[0]
    return acc / 5
for c, rs in (("25K", (300, 500, 700, 1000)), ("50K", (600, 1000, 1400, 2000))):
    cu = M.CUENTAS[c]
    for nom, ops, f in (("KALA todos los trades, regla", K, reg), ("KALA 1º trade, regla", K1, reg), ("KALA todos los trades, sin regla", K, todo)):
        for r in rs:
            x = M.ficha(nom, [(ops, r, f)], c); D = M.dias([(ops, r, f)], c); v, cad, peor = vel(D, cu)
            print(f'{c} {nom:34} @{r:5}: pasa {x["pasa"]:5.1f} (25 {x["p25"]:3.0f}/26 {x["p26"]:3.0f}) azar {nulo(D, cu):4.0f} | por intento ≈{x["hab"]} háb | DÍAS POR CUENTA {v:.0f} | cadena {cad} peor {peor} | {x["costo"]:.0f} USD', flush=True)
