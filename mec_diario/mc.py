import json, diario as Dd
ts = Dd.cargar()
C = [("Actual: fijo 1%", dict(base=1.0, tope=0, obj=None)),
     ("Fijo 1% + objetivo 0,9%", dict(base=1.0, tope=0, obj=0.9)),
     ("A pedida: 0,5% tope 3 + obj 0,45%", dict(base=0.5, tope=3, obj=0.45)),
     ("B pedida: 1% tope 3 + obj 0,9%", dict(base=1.0, tope=3, obj=0.9)),
     ("0,5% tope 2 + obj 0,45%", dict(base=0.5, tope=2, obj=0.45)),
     ("0,5% tope 2 sin obj", dict(base=0.5, tope=2, obj=None)),
     ("1% tope 2 + obj 0,9%", dict(base=1.0, tope=2, obj=0.9)),
     ("1% tope 2 sin obj", dict(base=1.0, tope=2, obj=None)),
     ("0,5% tope 1 sin obj", dict(base=0.5, tope=1, obj=None)),
     ("1% tope 1 sin obj", dict(base=1.0, tope=1, obj=None)),
     ("0,75% tope 2 sin obj", dict(base=0.75, tope=2, obj=None)),
     ("0,5% tope 3 sin obj", dict(base=0.5, tope=3, obj=None))]
out = []
for nom, kw in C:
    r = Dd.simular(ts, freno=2.7, **kw); m = Dd.montecarlo(ts, sims=1000, freno=2.7, **kw)
    out.append(dict(nombre=nom, kw=kw, r={k: v for k, v in r.items() if k != "niveles"}, mc=m))
    print(nom, '|', r['cagr'], r['mdd'], r['anios'], r['dias_pos'], r['mes_pos'], '| MC', m)
json.dump(out, open("mc.json", "w"), ensure_ascii=False)
