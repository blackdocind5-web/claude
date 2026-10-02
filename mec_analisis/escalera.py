"""Simulación de la gestión "Escalera de riesgo" (duplicar el riesgo tras cada pérdida hasta recuperar).

Reglas (tal como las definió Fabián):
- Riesgo base B (0,25%, 0,5% o 1% del capital). Tras una operación perdedora, la siguiente se opera al doble.
- Cuando el resultado acumulado desde que empezó la escalera vuelve a ser positivo, se reinicia al riesgo base.
- Una ganadora que no alcanza a recuperar todo (por ejemplo, un TP a 0,9R después de 5 pérdidas) mantiene el escalón.
- Objetivo diario: al llegar a +X% en el día (sobre el capital al inicio del día), no se opera más ese día.
- El riesgo nunca puede superar el capital disponible: si el escalón pide más de 100%, se opera con el 100% (ruina).
Resultado de cada operación en unidades de riesgo: u = PyG / (1% del capital del backtest). TP ≈ +0,9, SL ≈ −1.
"""
import random, statistics as st, datetime as dt
from collections import defaultdict

PERFILES = [("conservador", "Conservador", 0.25), ("moderado", "Moderado", 0.5), ("agresivo", "Agresivo", 1.0)]
OBJETIVOS = [1.0, 2.0]


def unidades(ts):
    return [dict(ent=t["ent"], sal=t["sal"], dia=t["ent"].date(), u=t["pnl"] / (0.01 * t["eq_bt"])) for t in sorted(ts, key=lambda t: t["ent"])]


def simular(trades, base, objetivo, escalera=True, detalle=False, tope=None, protocolo=False):
    E = 1000.0; pk = E; mdd = 0; k = 0; L = 0.0; ruina = False
    dia_actual = None; e_dia = E; parado = False
    max_k = 0; max_riesgo = 0; n = 0; w = 0; lvl_hist = defaultdict(int)
    dias = {}; meses = defaultdict(float); curve = []; ops = []
    for t in trades:
        if ruina:
            break
        if t["dia"] != dia_actual:
            if dia_actual is not None: dias[dia_actual] = (E - e_dia) / e_dia * 100
            dia_actual = t["dia"]; e_dia = E; parado = False
        if parado or ruina:
            continue
        riesgo = base * (2 ** k if escalera else 1)
        if riesgo > 100: riesgo = 100
        pnl = t["u"] * riesgo / 100 * E
        E0 = E; E += pnl; n += 1; w += pnl > 0; lvl_hist[k] += 1
        max_k = max(max_k, k); max_riesgo = max(max_riesgo, riesgo)
        meses[t["ent"].strftime("%Y-%m")] += pnl
        if detalle:
            ops.append(dict(f=t["ent"].strftime("%d/%m/%Y"), h=t["ent"].strftime("%H:%M"), esc=k, riesgo=round(riesgo, 2), u=round(t["u"], 2), pnl=round(pnl, 2), eq=round(E, 2)))
        if E <= 1:
            E = max(E, 0); ruina = True
        pk = max(pk, E); mdd = max(mdd, (pk - E) / pk)
        curve.append((t["sal"], E))
        if escalera:
            L += pnl
            if L > 0 or (protocolo and k == tope and L >= 0): k = 0; L = 0.0
            elif pnl < 0:
                k += 1
                if tope is not None and k > tope:
                    if protocolo: k = tope            # protocolo: se mantiene el último escalón hasta recuperar todo
                    else: k = 0; L = 0.0              # tope: se acepta la pérdida y se reinicia
        if (E - e_dia) / e_dia * 100 >= objetivo - 1e-9:
            parado = True
    if dia_actual is not None and e_dia > 0: dias[dia_actual] = (E - e_dia) / e_dia * 100
    # meses como % sobre el capital al inicio de cada mes
    mm = []; eq = 1000.0
    for m in sorted(meses):
        mm.append(dict(mes=m, pct=round(meses[m] / eq * 100, 2) if eq > 0 else 0, usd=round(meses[m], 2))); eq += meses[m]
    dv = list(dias.values())
    res = dict(final=round(E, 2), ret=round((E - 1000) / 10, 2), mdd=round(mdd * 100, 2), ruina=ruina, n=n, wr=round(100 * w / n, 1) if n else 0,
               max_k=max_k, max_riesgo=round(max_riesgo, 2), dias=len(dv), dias_pos=round(100 * sum(d > 0 for d in dv) / len(dv), 1) if dv else 0,
               dias_obj=round(100 * sum(d >= objetivo - 1e-9 for d in dv) / len(dv), 1) if dv else 0,
               dia_prom=round(st.mean(dv), 3) if dv else 0, peor_dia=round(min(dv), 2) if dv else 0, mejor_dia=round(max(dv), 2) if dv else 0,
               meses=mm, meses_pos=round(100 * sum(m["pct"] > 0 for m in mm) / len(mm), 1) if mm else 0,
               mes_prom=round(st.mean(m["pct"] for m in mm), 2) if mm else 0, peor_mes=min((m["pct"] for m in mm), default=0),
               niveles={str(a): b for a, b in sorted(lvl_hist.items())})
    if detalle:
        res["curve"] = [dict(t=s.strftime("%Y-%m-%d %H:%M"), eq=round(e, 2)) for s, e in curve]
        res["ops_max"] = sorted(ops, key=lambda o: -o["riesgo"])[:8]
    return res


def montecarlo(trades, base, objetivo, escalera=True, sims=3000, seed=11, tope=None, protocolo=False, recup=False):
    """Reordena al azar los resultados (manteniendo la estructura de días) para medir el riesgo de ruina."""
    rnd = random.Random(seed); us = [t["u"] for t in trades]; out = []
    for _ in range(sims):
        rnd.shuffle(us)
        ts = [dict(t, u=u) for t, u in zip(trades, us)]
        r = simular(ts, base, objetivo, escalera, tope=tope, protocolo=protocolo, detalle=recup)
        if recup:
            rc = recuperacion(r["curve"], ts)
            out.append((r["ret"], r["mdd"], r["ruina"], r["max_riesgo"], rc["max_dias_bajo_agua"], rc["max_ops_bajo_agua"]))
        else:
            out.append((r["ret"], r["mdd"], r["ruina"], r["max_riesgo"]))
    rets = sorted(o[0] for o in out); dds = sorted(o[1] for o in out)
    extra = {}
    if recup:
        dd_d = sorted(o[4] for o in out); dd_o = sorted(o[5] for o in out)
        extra = dict(bajo_agua_dias_med=dd_d[sims // 2], bajo_agua_dias_p95=dd_d[sims * 19 // 20], bajo_agua_ops_med=dd_o[sims // 2], bajo_agua_ops_p95=dd_o[sims * 19 // 20])
    return dict(**extra,p_ruina=round(100 * sum(o[2] for o in out) / sims, 1), p_dd50=round(100 * sum(o[1] >= 50 for o in out) / sims, 1),
                p_dd30=round(100 * sum(o[1] >= 30 for o in out) / sims, 1), p_perdida=round(100 * sum(o[0] < 0 for o in out) / sims, 1),
                ret_med=round(rets[sims // 2], 1), ret_p5=round(rets[sims // 20], 1), dd_med=round(dds[sims // 2], 1), dd_p95=round(dds[sims * 19 // 20], 1),
                riesgo_max_p95=round(sorted(o[3] for o in out)[sims * 19 // 20], 1))


def recuperacion(curve, trades=None):
    """Tiempo para recuperar la caída máxima y el período más largo bajo el agua.
    curve: [{t, eq}] tras cada operación. Días = días hábiles con operaciones del archivo entre pico y recuperación."""
    pts = [(dt.datetime.strptime(c["t"], "%Y-%m-%d %H:%M"), c["eq"]) for c in curve]
    pk = 1000.0; pk_i = -1; mdd = 0; ep = None; best_uw = (0, 0, None, None); cur_start = None
    for i, (t, e) in enumerate(pts):
        if e >= pk - 1e-9:
            if cur_start is not None:
                d0 = pts[cur_start][0] if cur_start >= 0 else pts[0][0]
                uw = ((t.date() - d0.date()).days, i - cur_start)
                if uw[0] > best_uw[0]: best_uw = (uw[0], uw[1], d0, t)
                cur_start = None
            pk = e; pk_i = i
        else:
            if cur_start is None: cur_start = pk_i
            dd = (pk - e) / pk
            if dd > mdd: mdd = dd; ep = dict(pico_i=pk_i, valle_i=i, pk=pk)
    abierto = cur_start is not None
    if abierto:
        d0 = pts[cur_start][0] if cur_start >= 0 else pts[0][0]
        uw = ((pts[-1][0].date() - d0.date()).days, len(pts) - 1 - cur_start)
        if uw[0] > best_uw[0]: best_uw = (uw[0], uw[1], d0, None)
    res = dict(max_dias_bajo_agua=best_uw[0], max_ops_bajo_agua=best_uw[1], bajo_agua_abierto=best_uw[3] is None and abierto)
    if ep:
        p = pts[ep["pico_i"]][0] if ep["pico_i"] >= 0 else pts[0][0]; v = pts[ep["valle_i"]][0]
        rec = next(((t, i) for i, (t, e) in enumerate(pts) if i > ep["valle_i"] and e >= ep["pk"] - 1e-9), None)
        res.update(mdd=round(mdd * 100, 2), pico=p.strftime("%d/%m/%Y"), valle=v.strftime("%d/%m/%Y"),
                   recupera=rec[0].strftime("%d/%m/%Y") if rec else None,
                   dias_pico_valle=(v.date() - p.date()).days, dias_valle_rec=(rec[0].date() - v.date()).days if rec else None,
                   dias_total=(rec[0].date() - p.date()).days if rec else None,
                   ops_total=(rec[1] - ep["pico_i"]) if rec else None)
    return res


def rachas(trades):
    best = cur = 0; hist = defaultdict(int)
    for t in trades:
        if t["u"] < 0: cur += 1
        else:
            if cur: hist[cur] += 1
            cur = 0
        best = max(best, cur)
    if cur: hist[cur] += 1
    return best, {str(a): b for a, b in sorted(hist.items())}


def calcular(OPS):
    out = {}
    for modelo in ("envolvente", "combinado", "start"):
        out[modelo] = {}
        for anio in ("2025", "2026", "2 años"):
            ts = OPS["2025"][modelo] + OPS["2026"][modelo] if anio == "2 años" else OPS[anio][modelo]
            T = unidades(ts)
            best, hist = rachas(T)
            x = dict(racha_max=best, rachas=hist, n=len(T), escenarios=[])
            for clave, nombre, base in PERFILES:
                for obj in OBJETIVOS:
                    r = simular(T, base, obj, True, detalle=(modelo == "envolvente"))
                    f = simular(T, base, obj, False)
                    mc = montecarlo(T, base, obj, True, sims=2000 if modelo == "envolvente" else 300)
                    x["escenarios"].append(dict(perfil=clave, nombre=nombre, base=base, obj=obj, escalera=r,
                                                fijo=dict(ret=f["ret"], mdd=f["mdd"], dias_pos=f["dias_pos"], meses_pos=f["meses_pos"], dias_obj=f["dias_obj"], mes_prom=f["mes_prom"]),
                                                mc=mc))
            if modelo == "envolvente":
                x["tope"] = []
                for clave, nombre, base in PERFILES:
                    for tope in (2, 3):
                        for obj in OBJETIVOS:
                            r = simular(T, base, obj, True, tope=tope)
                            mc = montecarlo(T, base, obj, True, sims=1500, tope=tope)
                            x["tope"].append(dict(perfil=clave, nombre=nombre, base=base, obj=obj, tope=tope, escalera={k: r[k] for k in ("ret", "mdd", "max_riesgo", "dias_pos", "dias_obj", "dia_prom", "meses_pos", "mes_prom", "peor_mes", "peor_dia")}, mc=mc))
                # probabilidad de ver una racha perdedora de k o más en una muestra como esta
                q = sum(t["u"] < 0 for t in T) / len(T); rnd = random.Random(5); cnt = defaultdict(int); S = 5000
                for _ in range(S):
                    b = c = 0
                    for _ in range(len(T)):
                        c = c + 1 if rnd.random() < q else 0; b = max(b, c)
                    for kk in range(3, 13):
                        if b >= kk: cnt[kk] += 1
                x["p_racha"] = {str(kk): round(100 * cnt[kk] / S, 1) for kk in range(3, 13)}
                x["q_perdida"] = round(100 * q, 1)
            out[modelo][anio] = x
            print(modelo, anio, "racha", best, [(e["perfil"], e["obj"], e["escalera"]["ret"], e["escalera"]["mdd"], e["escalera"]["max_riesgo"], e["escalera"]["ruina"], e["mc"]["p_ruina"], e["mc"]["p_dd50"], e["fijo"]["ret"]) for e in x["escenarios"]])
    return out


if __name__ == "__main__":
    import io, contextlib, json, metricas as M
    MOD, _ = M.MUESTRAS["sin_limite"]
    M.MODELOS = MOD
    with contextlib.redirect_stdout(io.StringIO()):
        OPS = {a: M.procesar_anio(a)[1] for a in MOD}
    d = json.load(open("datos_sin_limite.json"))
    d["escalera"] = calcular(OPS)
    json.dump(d, open("datos_sin_limite.json", "w"), ensure_ascii=False)
