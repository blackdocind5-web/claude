"""Cuadro final Alex vs Rascacielos vs Mica (26/10/2026): 25K/50K, riesgo 250–2.000, consistencia 40/50%, azar, años, cadena real."""
import sys; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import alex as A, comparar as K, statistics as st
P = {"25K": 65.30, "50K": 115.0}
C = {"Rascacielos": None, "Mica": None,
     "Alex con VWAP · Fibo 50% · hasta 10:45|regla": None, "Alex con VWAP · Fibo 50% · hasta 10:45|todos": None,
     "Alex con VWAP · Fibo 38,2% · hasta 11:00|todos": None, "Alex con VWAP · Fibo 38,2% · hasta 10:45|regla": None,
     "Alex con EMA 200 · Fibo 38,2% · hasta 10:30|regla": None, "Alex sin filtro · Fibo 38,2% · hasta 10:45|todos": None}
for nom in C:
    for c, rs in (("25K", (250, 500, 1000)), ("50K", (500, 1000, 2000))):
        cu = K.CUENTAS[c]
        for r in rs:
            if nom in ("Rascacielos", "Mica"):
                D = K.dias(nom, r, cu["maxq"]); nul = K.nulo_de(nom, D)
            else:
                k, f = nom.split("|"); D = A.dias(k, r, cu["maxq"], A.C.regla if f == "regla" else (lambda o: True)); nul = A.nulo
            fila = []
            for cons in (0.4, 0.5):
                kw = dict(obj=cu["obj"], mll=cu["mll"], cons=cons)
                p, d = K.montecarlo(D, n=3000, **kw)
                fila.append(p)
            kw = dict(obj=cu["obj"], mll=cu["mll"], cons=0.4)
            pn, _ = K.montecarlo(D, n=1500, nulo=nul, **kw)
            y = {a: K.montecarlo([x for x in D if x[0]["anio"] == a], n=1500, **kw)[0] for a in (2025, 2026)}
            res, peor = K.cadena(D, **kw); pa = sorted(x[2] for x in res if x[0] == "pasa")
            hab = round(d * 464 / len(D))
            print(f"{nom:52} {c} r{r:5} c40 {fila[0]:5.1f} c50 {fila[1]:5.1f} azar {pn:4.0f} (25 {y[2025]:3.0f}/26 {y[2026]:3.0f}) | {100/fila[0]:.2f} evals {100/fila[0]*P[c]:4.0f} USD | días-trade {d} ≈ hábiles {hab} (cadena med {pa[len(pa)//2] if pa else '-'}) | cadena {len(pa)}/{len(res)} peor {peor} | trades/día-año {len(D)}")
