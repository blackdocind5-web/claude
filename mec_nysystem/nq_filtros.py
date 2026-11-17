import io, contextlib, csv, os, collections, statistics as st
import analisis as A, mnq_analisis as Q, nq_analisis as N
def senales(arch):
    s = {}
    for r in csv.DictReader(open(os.path.join(A.AQUI, arch), encoding="utf-8-sig")):
        if r["Tipo"].startswith("Entrada"): s[r["Fecha y hora"][:16]] = r["Señal"]
    return s
D10 = {"ISM", "JOLTS", "Confianza CB", "PCE"}
FIL = {"Sin filtro": lambda t: True, "Sin CPI/NFP": A.FILTROS["Filtro sugerido"], "Regla Rascacielos": A.FILTROS["Regla MNQ (Rascacielos)"],
       "Sin CPI/NFP ni datos 10:00": lambda t: A.FILTROS["Filtro sugerido"](t) and not (D10 & set(t["tags"]))}
def fr(t):
    m = t["ent"].hour * 60 + t["ent"].minute
    return "09:30–09:44" if m < 585 else "09:45–09:59" if m < 600 else "10:00–10:14" if m < 615 else "10:15–10:29" if m < 630 else "10:30–10:59"
for g, f in N.G.items():
    ts = N.cargar(f); sen = senales(f)
    for t in ts: t["sen"] = sen[t["ent"].strftime("%Y-%m-%d %H:%M")]
    print(f"\n######## {g} ########")
    print("== noticias ==")
    for x in sorted(A.tabla(ts, lambda t: t["tags"]), key=lambda x: -x["n"]):
        print(f'  {x["k"]:26} n {x["n"]:4} WR {x["wr"]:5.1f} R/op {x["R_op"]:+.3f} R {x["R"]:+6.1f} | 2025 {x["R2025"]:+6.1f} ({x["n2025"]}) 2026 {x["R2026"]:+6.1f} ({x["n2026"]})')
    for nom, fn in (("día", lambda t: ["1Lun", "2Mar", "3Mié", "4Jue", "5Vie"][t["ent"].weekday()]), ("franja", fr), ("lado", lambda t: "largo" if t["lado"] > 0 else "corto"), ("señal", lambda t: t["sen"])):
        for x in sorted(A.tabla(ts, fn), key=lambda x: x["k"]):
            print(f'  {nom:6} {x["k"]:14} n {x["n"]:4} WR {x["wr"]:5.1f} R/op {x["R_op"]:+.3f} t {x["t"]} | 2025 {x["R2025"]:+6.1f} ({x["n2025"]}) 2026 {x["R2026"]:+6.1f} ({x["n2026"]})')
    print("== filtros por noticias (a nivel día: si el día se filtra, no se opera nada) ==")
    for nom, fn in FIL.items():
        N.ficha(nom, [t for t in ts if fn(t)], mc=(g == "1TP y 3SL"))
