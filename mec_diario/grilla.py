import itertools, json, diario as Dd
ts = Dd.cargar(); rows = []
for base, tope, obj, freno, ed in itertools.product((0.5, 1.0), (0, 1, 2, 3, 4), (None, 0.45, 0.9), (None, 1.35, 2.7), (False, True)):
    if tope == 0 and ed: continue
    r = Dd.simular(ts, base=base, tope=tope, obj=obj, freno=freno, escalera_dia=ed)
    rows.append(dict(base=base, tope=tope, obj=obj, freno=freno, ed=ed, **{k: v for k, v in r.items() if k != "niveles"}))
json.dump(rows, open("grilla.json", "w"))
