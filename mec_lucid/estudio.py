import json, collections, fase1 as F
ops = [o for o in F.cargar() if o["ent"].hour == 9]          # fuera: una entrada a las 18:00 del 09/01/2025 (mercado cerrado)
out = {}
def S(x): return F.resumen(sorted(x, key=lambda o: o["ent"]))
for h in ("09:30", "09:45"):
    H = [o for o in ops if o["hora"] == h]
    out[h] = dict(total=S(H), anios={y: S([o for o in H if o["anio"] == y]) for y in (2025, 2026)},
                  trims={f"{o['trim']} {o['anio']}": None for o in H})
    for k in out[h]["trims"]: out[h]["trims"][k] = S([o for o in H if f"{o['trim']} {o['anio']}" == k])
    cats = sorted({o["cat"] for o in H})
    out[h]["cats"] = {c: dict(S([o for o in H if o["cat"] == c]), **{f"wr{y}": F.resumen([o for o in H if o["cat"] == c and o["anio"] == y]).get("wr") for y in (2025, 2026)}) for c in cats}
    out[h]["dias"] = {d: dict(S([o for o in H if o["ent"].weekday() == i]), **{f"wr{y}": F.resumen([o for o in H if o["ent"].weekday() == i and o["anio"] == y]).get("wr") for y in (2025, 2026)}) for i, d in enumerate(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])}
    out[h]["lado"] = {l: S([o for o in H if o["lado"] == l]) for l in ("largo", "corto")}
    # filtros de calendario: la secuencia se arma solo con los días operables
    for nom, ok in (("todos", lambda o: True), ("sin feriados/receso/discursos", lambda o: o["cat"] not in ("Feriado o receso", "Discurso 09:00–11:00")),
                    ("solo días normales", lambda o: o["cat"] == "Día normal"),
                    ("sin 08:30 ni FOMC ni feriados", lambda o: o["cat"] not in ("Feriado o receso", "Discurso 09:00–11:00", "Noticia 08:30 (NFP, CPI, PPI, PIB)", "FOMC"))):
        x = [o for o in H if ok(o)]
        out[h].setdefault("filtros", {})[nom] = dict(S(x), **{f"ww{y}": F.resumen(sorted([o for o in x if o["anio"] == y], key=lambda o: o["ent"])).get("ww") for y in (2025, 2026)})
json.dump(out, open("estudio.json", "w"), ensure_ascii=False, indent=1)
for h in out:
    print("=====", h, out[h]["total"]); print(" años", out[h]["anios"])
    for k, v in out[h]["trims"].items(): print("  ", k, v["n"], v["wr"], v["ww"], v["racha_perd"])
    for k, v in out[h]["cats"].items(): print("  cat", k, v["n"], v["wr"], v.get("wr2025"), v.get("wr2026"))
    for k, v in out[h]["dias"].items(): print("  dia", k, v["n"], v["wr"], v.get("wr2025"), v.get("wr2026"))
    for k, v in out[h]["lado"].items(): print("  lado", k, v["n"], v["wr"])
    for k, v in out[h]["filtros"].items(): print("  filtro", k, v["n"], v["wr"], "WW", v["ww"], v["ww2025"], v["ww2026"], "racha", v["racha_perd"])
