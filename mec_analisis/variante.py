"""Compara el backtest original contra la variante sin salidas por CHoCH en contra ni cierre de fin de sesión.
Agrega a datos.json: datos[<clave>_v] (informe completo de la variante) y datos['variante'] (comparación)."""
import json, datetime as dt, statistics as st
import metricas as M

PARES = [("combinado", "XAU_m1_2026_VARIANTE_Envolvente_y_START"),
         ("envolvente", "XAU_m1_2026_VARIANTE_Envolvente"),
         ("start", "XAU_m1_2026_VARIANTE_START")]
GESTION = ("CHoCH en contra (arrastre)", "Cierre fin de sesión (estructura en contra)")

datos = json.load(open("datos.json"))
comp = {}
for clave, base in PARES:
    nombre = datos[clave]["nombre"]
    DV, V = M.analizar(clave + "_v", nombre + " · variante SL/TP", base)
    DO, O = M.analizar(clave, nombre, datos[clave]["archivo"])
    datos[clave + "_v"] = DV
    key = lambda t: (t["ent"], t["dir"])
    Om = {key(t): t for t in O}; Vm = {key(t): t for t in V}
    comunes = Om.keys() & Vm.keys()
    cambios = []
    for k in sorted(comunes):
        o, v = Om[k], Vm[k]
        if o["salida"] in GESTION or o["sal"] != v["sal"]:
            cambios.append(dict(f=o["ent"].strftime("%d/%m"), h=o["ent"].strftime("%H:%M"), dir=o["dir"],
                                sal_o=o["salida"], hs_o=o["sal"].strftime("%H:%M"), R_o=round(o["R"], 2),
                                hs_v=v["sal"].strftime("%H:%M") if v["sal"].date() == v["ent"].date() else v["sal"].strftime("%d/%m %H:%M"),
                                sal_v="TP" if v["pnl"] > 0 and v["salida"].startswith("Salida PreNY") else ("SL" if v["salida"].startswith("Salida PreNY") else v["salida"]),
                                R_v=round(v["R"], 2), min_v=v["bars"], min_o=o["bars"]))
    solo_o = [Om[k] for k in Om.keys() - Vm.keys()]; solo_v = [Vm[k] for k in Vm.keys() - Om.keys()]
    tardias = [t for t in V if (t["sal"] - t["ent"].replace(hour=9, minute=0)).total_seconds() > 30 * 60]
    comp[clave] = dict(
        nombre=nombre, cambios=cambios, n_cambios=len(cambios),
        dR_cambios=round(sum(c["R_v"] - c["R_o"] for c in cambios), 2),
        cambios_mejor=sum(c["R_v"] > c["R_o"] + 0.05 for c in cambios), cambios_peor=sum(c["R_v"] < c["R_o"] - 0.05 for c in cambios),
        cambios_a_tp=sum(c["sal_v"] == "TP" for c in cambios), cambios_a_sl=sum(c["sal_v"] == "SL" for c in cambios),
        solo_o=len(solo_o), solo_v=len(solo_v),
        R_solo_o=round(sum(t["R"] for t in solo_o), 2), R_solo_v=round(sum(t["R"] for t in solo_v), 2),
        max_min=max(t["bars"] for t in V), max_min_o=max(t["bars"] for t in O),
        tardias=len(tardias), tardias_list=[dict(f=t["ent"].strftime("%d/%m"), h=t["ent"].strftime("%H:%M"), sal=t["sal"].strftime("%H:%M"), min=t["bars"], R=round(t["R"], 2)) for t in sorted(tardias, key=lambda t: -t["bars"])],
    )
    por_tipo = []
    for g, lab in ((GESTION[0], "CHoCH en contra"), (GESTION[1], "Cierre fin de sesión")):
        cs = [c for c in cambios if c["sal_o"] == g]
        por_tipo.append(dict(tipo=lab, n=len(cs), R_o=round(sum(c["R_o"] for c in cs), 2), R_v=round(sum(c["R_v"] for c in cs), 2),
                             tp=sum(c["sal_v"] == "TP" for c in cs), sl=sum(c["sal_v"] == "SL" for c in cs)))
    comp[clave]["por_tipo"] = por_tipo
    o, v = datos[clave], DV
    print(f'{nombre:20} R {o["R_tot"]:+6.2f} -> {v["R_tot"]:+6.2f} | WR {o["wr"]}->{v["wr"]} PF {o["pf"]}->{v["pf"]} DD {o["mdd_pct"]}->{v["mdd_pct"]} MC95 {o["mc_dd95"]}->{v["mc_dd95"]} t {o["t_stat"]}->{v["t_stat"]} P {o["p_exp_pos"]}->{v["p_exp_pos"]} dur {o["dur_avg"]}->{v["dur_avg"]}')
    c = comp[clave]
    print("   cambios", c["n_cambios"], "dR", c["dR_cambios"], "mejor/peor", c["cambios_mejor"], c["cambios_peor"], "->TP/SL", c["cambios_a_tp"], c["cambios_a_sl"],
          c["por_tipo"], "solo_o/v", c["solo_o"], c["solo_v"], c["R_solo_o"], c["R_solo_v"], "max min", c["max_min_o"], c["max_min"], "tardías>09:30", c["tardias"])
datos["variante"] = comp
json.dump(datos, open("datos.json", "w"), ensure_ascii=False)
