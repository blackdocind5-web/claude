import json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_xau as X
out = {"patrones": {}}
for p in ("E", "S", "ES"):
    ts, excl = X.cargar(p)
    limpio = [t for t in ts if not t["tags"]]
    res = dict(todas=X.resumen(ts), limpio=X.resumen(limpio), noticia=X.resumen([t for t in ts if any(g.startswith("Noticia") for g in t["tags"])]),
               fomc=X.resumen([t for t in ts if any(g.startswith("FOMC") for g in t["tags"])]),
               lj=X.resumen([t for t in limpio if t["ent"].weekday() != 4]), lj_sin_enero=X.resumen([t for t in limpio if t["ent"].weekday() != 4 and t["ent"].month != 1]),
               bruto_limpio=X.resumen([dict(t, u=t["u_bruto"]) for t in limpio]), n_excl=len(excl),
               dias=[X.resumen([t for t in limpio if t["ent"].weekday() == d]) for d in range(5)],
               horas={h: X.resumen([t for t in limpio if t["ent"].hour == h]) for h in (9, 10)},
               meses={m: round(sum(t["u"] for t in limpio if t["ent"].month == m) / 0.9, 1) for m in range(1, 13)})
    out["patrones"][p] = res
    print("==", p, "excluidas", len(excl))
    for k in ("todas", "limpio", "noticia", "fomc", "lj", "lj_sin_enero", "bruto_limpio"):
        r = res[k]; print(f"  {k:13}", {kk: r.get(kk) for kk in ("n", "wr", "R", "R_op", "R2025", "R2026", "pf", "mdd", "racha", "costo_R")})
    print("  dias", [(X.DIAS[i], r.get("n"), r.get("R"), r.get("R2025"), r.get("R2026")) for i, r in enumerate(res["dias"])])
    print("  horas", {h: (r.get("n"), r.get("R"), r.get("R2025"), r.get("R2026")) for h, r in res["horas"].items()})
    print("  meses", res["meses"])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "estudio.json"), "w"), ensure_ascii=False, default=str)
