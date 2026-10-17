"""Simulación de la evaluación Lucid 25K Flex empezando en cada día del histórico.
- Contratos = piso(riesgo / (SL en puntos × 2 USD)), máximo 20 micros; resultado real de cada operación (incluye gaps) × contratos − comisión.
- Pérdida máxima: 1.000 USD trailing sobre el saldo de cierre más alto. Se quema si el saldo cae a ese nivel o por debajo.
- Pasa al llegar a +1.250 USD con el mejor día ≤ 50% de la ganancia total (si no, sigue operando)."""
import json, statistics as st, fase1 as F
OPS = [o for o in F.cargar() if o["ent"].hour == 9]
FUERA = ("Feriado o receso", "Discurso 09:00–11:00")

def secuencia(hora, filtro):
    return sorted([o for o in OPS if o["hora"] == hora and filtro(o)], key=lambda o: o["ent"])

def intento(seq, i, riesgo, comision):
    sal = 25000.0; pico = sal; dias = {}; n = 0
    for t in seq[i:]:
        k = F.contratos(t["sl"]) if riesgo == 1000 else min(F.MAX_MICROS, int(riesgo // (t["sl"] * F.PUNTO)))
        pnl = t["pnl"] * k - comision * k
        sal += pnl; n += 1; d = t["ent"].date(); dias[d] = dias.get(d, 0) + pnl
        if sal <= pico - 1000 + 1e-9: return ("quemada", n, sal - 25000)
        pico = max(pico, sal)
        g = sal - 25000
        if g >= F.OBJ and max(dias.values()) <= 0.5 * g + 1e-9: return ("pasa", n, g)
        if n > 60: return ("sin terminar", n, g)
    return ("sin datos", n, sal - 25000)

def evaluar(seq, riesgo, comision):
    res = [intento(seq, i, riesgo, comision) for i in range(len(seq) - 1)]
    res = [r for r in res if r[0] in ("pasa", "quemada")]
    p = [r for r in res if r[0] == "pasa"]
    return dict(intentos=len(res), p_pasa=round(100 * len(p) / len(res), 1), dias_med=st.median(r[1] for r in p) if p else None,
                dias_quema=st.median(r[1] for r in res if r[0] == "quemada") if len(p) < len(res) else None)

if __name__ == "__main__":
    out = {}
    for hora in ("09:30", "09:45"):
        for fnom, f in (("todos los días", lambda o: True), ("sin feriados, receso ni discursos", lambda o: o["cat"] not in FUERA)):
            seq = secuencia(hora, f)
            for riesgo in (1000, 750, 500, 400, 300):
                for com in (0.0, 1.0):
                    r = evaluar(seq, riesgo, com); out[f"{hora}|{fnom}|{riesgo}|{com}"] = r
                    print(hora, fnom, riesgo, com, r)
    json.dump(out, open("evaluacion.json", "w"), ensure_ascii=False, indent=1)
