"""Gestión Híbrida: cartera de XAUUSD, AUDUSD, EURUSD y GBPUSD (sistema MEC, sesión Pre NY).

Simula todas las combinaciones de activos y patrones de entrada (Envolvente, START, Envolvente y START)
como una operativa en vivo: las operaciones de todos los activos se ejecutan en orden cronológico
de entrada, con riesgo fijo del 1% del capital realizado al momento de entrar y un freno semanal
(al alcanzar el objetivo de la semana se deja de abrir operaciones hasta el lunes siguiente).

Uso: python hibrida.py  -> datos_hibrida.json
"""
import csv, datetime as dt, itertools, json, math, os, random, statistics as st, sys
from collections import defaultdict, OrderedDict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "mec_filtros"))
import filtrar_trades as F

CAP = 1000.0
R_PCT = 0.9                     # 1R = 1 TP = 0,9% del capital
CAL = F.cargar_calendario()
ACTIVOS = ["XAUUSD", "AUDUSD", "EURUSD", "GBPUSD"]
PATRONES = {"E": "Envolvente", "S": "START", "ES": "Envolvente_y_START"}
NOMBRE_PAT = {"E": "Envolvente", "S": "START", "ES": "Envolvente + START"}
INI, FIN = dt.date(2025, 1, 13), dt.date(2026, 10, 2)
RECESO = (dt.date(2025, 12, 22), dt.date(2026, 1, 16))
OBJETIVOS = [None, 2, 3, 4, 5, 6, 7, 8]


def archivos(activo, pat):
    if activo == "XAUUSD":
        p = PATRONES[pat]
        return [os.path.join(AQUI, "..", "mec_analisis", f"XAU_m1_2025_{p}.csv"),
                os.path.join(AQUI, "..", "mec_analisis", f"XAU_m1_2026_CORREGIDO_{p}.csv")]
    return [os.path.join(AQUI, "datos", f"{activo}_m1_2025-2026_{PATRONES[pat]}.csv")]


def leer(path, activo):
    ops = OrderedDict()
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        ops.setdefault(int(r["Número de operación"]), []).append(r)
    out = []
    for n, fs in ops.items():
        e = next(f for f in fs if f["Tipo"].startswith("Entrada"))
        s = next(f for f in fs if f["Tipo"].startswith("Salida"))
        pnl = float(e["PyG netas USD"]); eq = CAP + float(e["PyG acumuladas USD"]) - pnl
        ent = dt.datetime.strptime(e["Fecha y hora"], "%Y-%m-%d %H:%M")
        out.append(dict(a=activo, ent=ent, sal=dt.datetime.strptime(s["Fecha y hora"], "%Y-%m-%d %H:%M"),
                        u=pnl / (0.01 * eq), salida=s["Señal"], dir="BUY" if "largo" in e["Tipo"] else "SELL"))
    return out


def motivo(s):
    if s.startswith("Reset"): return "Reset antes de nueva entrada"
    if s.startswith("Salida PreNY") or s.startswith("Salida NY") or s.startswith("SL alcanzado") or s.startswith("TP alcanzado"):
        return "Salida Pre NY / NY (SL o TP)"
    if s.startswith("CHoCH"): return "CHoCH en contra"
    if s.startswith("Cierre fin"): return "Cierre fin de sesión"
    return s


def cargar():
    T = {}
    for a in ACTIVOS:
        for p in PATRONES:
            fs = archivos(a, p)
            if not all(os.path.exists(f) for f in fs): continue
            ts = [t for f in fs for t in leer(f, a)]
            ts = [t for t in ts if not F.motivo_exclusion(t["ent"], CAL)]
            ts.sort(key=lambda t: t["ent"])
            for t in ts: t["m"] = motivo(t["salida"])
            T[(a, p)] = ts
    return T


def duplicados():
    """Detecta exportaciones idénticas (p. ej. un START igual al Envolvente)."""
    import hashlib
    dup = []
    for a in ACTIVOS[1:]:
        h = {p: hashlib.md5(open(archivos(a, p)[0], "rb").read()).hexdigest() for p in PATRONES if os.path.exists(archivos(a, p)[0])}
        if h.get("S") and h.get("S") == h.get("E"): dup.append(a)
    return dup


# ---------- estadística básica ----------
def racha(us):
    b = c = 0
    for u in us:
        c = c + 1 if u < 0 else 0; b = max(b, c)
    return b


def resumen(ts):
    us = [t["u"] for t in ts]
    if not us: return dict(n=0)
    E = CAP; pk = E; mdd = 0
    for u in us:
        E *= 1 + u / 100; pk = max(pk, E); mdd = max(mdd, (pk - E) / pk)
    w = [u for u in us if u > 0]; l = [u for u in us if u <= 0]
    return dict(n=len(us), wr=round(100 * len(w) / len(us), 1), R=round(sum(us) / R_PCT, 1), R_op=round(sum(us) / R_PCT / len(us), 3),
                ret=round((E / CAP - 1) * 100, 1), mdd=round(mdd * 100, 1), racha=racha(us),
                pf=round(sum(w) / -sum(l), 2) if l and sum(l) < 0 else None)


# ---------- reglas de sesión ----------
def aplicar_regla(ts, regla):
    """regla: 'cont' (datos tal cual), 'stop1' (tras perder la 1.ª operación del día no se opera más ese activo),
    'stop_reset' (solo si la 1.ª se cerró por Reset), 'stop_precio' (solo si se cerró por SL de precio)."""
    if regla == "cont": return ts
    out = []; dia = None; corta = False
    for t in ts:
        d = (t["a"], t["ent"].date())
        if d != dia:
            dia = d; corta = False; out.append(t)
            if t["u"] < 0:
                corta = (regla == "stop1" or (regla == "stop_reset" and t["m"].startswith("Reset"))
                         or (regla == "stop_precio" and t["m"].startswith("Salida")))
            continue
        if not corta: out.append(t)
    return out


# ---------- simulación de cartera ----------
def lunes(d): return d - dt.timedelta(days=d.weekday())


def simular(ts, objetivo=None, curva=False, stop_sem=None, riesgo=1.0):
    """ts: operaciones de todos los activos. Orden cronológico por hora de entrada.
    Riesgo = 1% del capital realizado al entrar. Freno semanal sobre el resultado realizado de la semana."""
    ts = sorted(ts, key=lambda t: (t["ent"], ACTIVOS.index(t["a"])))
    E = CAP; pk = E; mdd = 0; abiertas = []; sem = None; e_sem = E; frenada = False
    tomadas = []; semanas = OrderedDict(); meses = defaultdict(float); anios = {}
    pk_t = None; max_bajo = 0; ini_bajo = None; max_conc = 0; curve = []; dd_ini = dd_fin = None; pk_fecha = None
    def cerrar_hasta(tiempo):
        nonlocal E, pk, mdd, ini_bajo, max_bajo, dd_ini, dd_fin, pk_fecha
        abiertas.sort(key=lambda x: x[0])
        while abiertas and (tiempo is None or abiertas[0][0] <= tiempo):
            sal, pnl, t = abiertas.pop(0)
            E += pnl; meses[sal.strftime("%Y-%m")] += pnl
            if E > pk:
                if ini_bajo: max_bajo = max(max_bajo, (sal.date() - ini_bajo).days)
                pk = E; ini_bajo = None; pk_fecha = sal
            elif ini_bajo is None and E < pk: ini_bajo = pk_fecha.date() if pk_fecha else INI
            if (pk - E) / pk > mdd: mdd = (pk - E) / pk; dd_ini = pk_fecha; dd_fin = sal
            if curva: curve.append((sal, E))
    for t in ts:
        cerrar_hasta(t["ent"])
        l = lunes(t["ent"].date())
        if l != sem:
            if sem is not None: semanas[sem] = semanas.get(sem, 0)
            sem = l; e_sem = E; frenada = False
        if frenada: continue
        g = (E - e_sem) / e_sem * 100
        if objetivo is not None and g >= objetivo * R_PCT - 1e-9: frenada = True; continue
        if stop_sem is not None and g <= -stop_sem * R_PCT + 1e-9: frenada = True; continue
        pnl = t["u"] * riesgo / 100 * E
        abiertas.append((t["sal"], pnl, t)); tomadas.append(dict(t, pnl=pnl, e0=E, sem=l))
        max_conc = max(max_conc, len(abiertas))
    cerrar_hasta(None)
    if ini_bajo: max_bajo = max(max_bajo, (FIN - ini_bajo).days)
    # semanas: % sobre el capital al inicio de cada semana (todas las semanas del calendario, receso incluido)
    pw = defaultdict(float)
    for x in tomadas: pw[x["sem"]] += x["pnl"]
    eq = CAP; wk = []; d = INI
    while d <= FIN:
        p = pw.get(d, 0.0); wk.append(dict(s=d, pct=p / eq * 100, ops=sum(1 for x in tomadas if x["sem"] == d) if curva else None)); eq += p; d += dt.timedelta(7)
    us = [x["u"] for x in tomadas]; n = len(us)
    if E <= 0: E = 0.01
    dias = (FIN - INI).days + 1; anios_n = dias / 365.25
    tot = E / CAP - 1
    cagr = (E / CAP) ** (1 / anios_n) - 1 if E > 0 else -1
    wpct = [w["pct"] for w in wk]
    act = [w for w in wk if not (RECESO[0] <= w["s"] <= RECESO[1])]
    obj_hit = sum(1 for w in act if objetivo and w["pct"] >= objetivo * R_PCT - 1e-6) if objetivo else None
    por_anio = {}
    for y in (2025, 2026):
        xs = [x for x in tomadas if x["ent"].year == y]
        if xs:
            e0 = xs[0]["e0"]; e1 = e0 + sum(x["pnl"] for x in xs)
            por_anio[str(y)] = round((e1 / e0 - 1) * 100, 1)
    mm = []; eqm = CAP
    for m in sorted(meses): mm.append(dict(m=m, pct=round(meses[m] / eqm * 100, 2))); eqm += meses[m]
    mcomp = [x for x in mm if x["m"] not in ("2025-12", "2026-01", "2026-10")]   # meses completos (sin receso ni el parcial)
    sd = st.pstdev(wpct) if len(wpct) > 1 else 0
    res = dict(n=n, wr=round(100 * sum(u > 0 for u in us) / n, 1) if n else 0, R=round(sum(us) / R_PCT, 1),
               ret=round(tot * 100, 1), cagr=round(cagr * 100, 1),
               sem_geo=round(((E / CAP) ** (1 / len(wk)) - 1) * 100, 2), mes_geo=round(((E / CAP) ** (30.4375 / dias) - 1) * 100, 2),
               sem_prom=round(st.mean(wpct), 2), sem_pos=round(100 * sum(w["pct"] > 0 for w in act) / len(act), 1),
               sem_neg=round(100 * sum(w["pct"] < 0 for w in act) / len(act), 1),
               peor_sem=round(min(wpct), 2), mejor_sem=round(max(wpct), 2),
               obj_hit=round(100 * obj_hit / len(act), 1) if objetivo else None,
               mes_pos=round(100 * sum(x["pct"] > 0 for x in mcomp) / len(mcomp), 1) if mcomp else 0,
               peor_mes=round(min((x["pct"] for x in mcomp), default=0), 2),
               mdd=round(mdd * 100, 1), bajo_agua=max_bajo, racha=racha(us),
               calmar=round(cagr * 100 / (mdd * 100), 2) if mdd > 0 else None,
               sharpe=round(st.mean(wpct) / sd * math.sqrt(52), 2) if sd else None,
               anios=por_anio, max_conc=max_conc,
               dd_ini=dd_ini.strftime("%d/%m/%Y") if dd_ini else None, dd_fin=dd_fin.strftime("%d/%m/%Y") if dd_fin else None)
    if curva:
        res["curve"] = [dict(t=s.strftime("%Y-%m-%d %H:%M"), eq=round(e, 2)) for s, e in curve]
        res["semanas"] = [dict(s=w["s"].strftime("%d/%m/%Y"), pct=round(w["pct"], 2), ops=w["ops"]) for w in wk]
        res["meses"] = mm
        res["por_activo"] = {a: dict(n=sum(1 for x in tomadas if x["a"] == a), R=round(sum(x["u"] for x in tomadas if x["a"] == a) / R_PCT, 1),
                                     wr=round(100 * sum(x["u"] > 0 for x in tomadas if x["a"] == a) / max(1, sum(1 for x in tomadas if x["a"] == a)), 1),
                                     usd=round(sum(x["pnl"] for x in tomadas if x["a"] == a), 2)) for a in ACTIVOS if any(x["a"] == a for x in tomadas)}
    return res


def montecarlo(ts, objetivo, sims=1000, seed=7, stop_sem=None):
    """Remuestreo con reposición de los resultados de cada activo (se mantienen fechas, horas y activos):
    mide qué pasa si la ventaja real fuera algo mejor o peor que la observada y las rachas llegaran en otro orden."""
    rnd = random.Random(seed); por = defaultdict(list)
    for i, t in enumerate(ts): por[t["a"]].append(i)
    R = []
    for _ in range(sims):
        nu = [t["u"] for t in ts]
        for a, idx in por.items():
            v = [ts[i]["u"] for i in idx]
            for i in idx: nu[i] = rnd.choice(v)
        r = simular([dict(t, u=u) for t, u in zip(ts, nu)], objetivo, stop_sem=stop_sem); R.append(r)
    q = lambda xs, p: sorted(xs)[min(len(xs) - 1, int(p * len(xs)))]
    rets = [r["ret"] for r in R]; dds = [r["mdd"] for r in R]; cg = [r["cagr"] for r in R]
    anio_neg = sum(1 for r in R if any(v < 0 for v in r["anios"].values()))
    return dict(sims=sims, ret_med=round(st.median(rets), 1), ret_p5=round(q(rets, .05), 1), cagr_med=round(st.median(cg), 1), cagr_p5=round(q(cg, .05), 1),
                cagr_p95=round(q(cg, .95), 1), dd_med=round(st.median(dds), 1), dd_p95=round(q(dds, .95), 1), p_perd=round(100 * sum(x < 0 for x in rets) / len(rets), 1),
                p_anio_neg=round(100 * anio_neg / len(R), 1), p_dd20=round(100 * sum(x > 20 for x in dds) / len(dds), 1),
                racha_med=q([r["racha"] for r in R], .5), racha_p95=q([r["racha"] for r in R], .95),
                bajo_agua_p95=q([r["bajo_agua"] for r in R], .95), mes_med=round(st.median([r["mes_geo"] for r in R]), 2),
                peor_mes_p5=round(q([r["peor_mes"] for r in R], .05), 1))


# ---------- análisis del primer SL de la sesión ----------
def primer_sl(ts):
    dias = defaultdict(list)
    for t in ts: dias[t["ent"].date()].append(t)
    out = defaultdict(lambda: dict(dias=0, u1=0.0, cont=0, n2=0, w2=0, u2=0.0, sl2=0))
    tot = dict(sesiones=len(dias), primera_pierde=0)
    for d, xs in dias.items():
        xs.sort(key=lambda t: t["ent"]); f = xs[0]
        if f["u"] >= 0: continue
        tot["primera_pierde"] += 1
        for k in (f["m"], "Todas"):
            o = out[k]; o["dias"] += 1; o["u1"] += f["u"]
            resto = xs[1:]
            if resto:
                o["cont"] += 1; o["n2"] += len(resto); o["w2"] += sum(x["u"] > 0 for x in resto)
                o["u2"] += sum(x["u"] for x in resto); o["sl2"] += sum(x["u"] < 0 for x in resto)
    res = []
    for k, o in out.items():
        res.append(dict(motivo=k, dias=o["dias"], R1=round(o["u1"] / R_PCT / o["dias"], 2), sesiones_sigue=o["cont"], ops=o["n2"],
                        wr=round(100 * o["w2"] / o["n2"], 1) if o["n2"] else None, R=round(o["u2"] / R_PCT, 1),
                        R_op=round(o["u2"] / R_PCT / o["n2"], 2) if o["n2"] else None))
    res.sort(key=lambda r: (r["motivo"] == "Todas", -r["dias"]))
    return dict(sesiones=tot["sesiones"], primera_pierde=tot["primera_pierde"], motivos=res)


def correlaciones(T, pat="E"):
    d = {a: defaultdict(float) for a in ACTIVOS}
    for a in ACTIVOS:
        for t in T.get((a, pat), []): d[a][t["ent"].date()] += t["u"]
    out = {}
    for a, b in itertools.combinations(ACTIVOS, 2):
        comunes = sorted(set(d[a]) & set(d[b]))
        if len(comunes) < 10: continue
        x = [d[a][k] for k in comunes]; y = [d[b][k] for k in comunes]
        mx, my = st.mean(x), st.mean(y); sx, sy = st.pstdev(x), st.pstdev(y)
        r = sum((i - mx) * (j - my) for i, j in zip(x, y)) / len(x) / (sx * sy) if sx and sy else 0
        ambos_pierden = sum(1 for i, j in zip(x, y) if i < 0 and j < 0)
        out[f"{a}-{b}"] = dict(dias=len(comunes), r=round(r, 2), ambos_pierden=round(100 * ambos_pierden / len(comunes), 1))
    return out


def etiqueta(combo):
    return " + ".join(f"{a} {NOMBRE_PAT[p]}" for a, p in combo)


def main():
    T = cargar(); dup = duplicados()
    for a in dup: T.pop((a, "S"), None)          # START idéntico al Envolvente: no se usa hasta tener el archivo correcto
    opciones = {a: [p for p in PATRONES if (a, p) in T] for a in ACTIVOS}

    # 1) cada activo por separado
    activos = {}
    for a in ACTIVOS:
        activos[a] = {}
        for p in opciones[a]:
            ts = T[(a, p)]
            activos[a][p] = dict(total=resumen(ts), **{str(y): resumen([t for t in ts if t["ent"].year == y]) for y in (2025, 2026)},
                                 sin_viernes=resumen([t for t in ts if t["ent"].weekday() != 4]),
                                 dias=[resumen([t for t in ts if t["ent"].weekday() == k]) for k in range(5)],
                                 primer_sl=primer_sl(ts))
            for regla in ("stop1", "stop_reset", "stop_precio"):
                activos[a][p][regla] = resumen(aplicar_regla(ts, regla))

    # 2) todas las combinaciones de activos y patrones
    combos = []
    for k in range(1, 5):
        for sub in itertools.combinations(ACTIVOS, k):
            for pats in itertools.product(*[opciones[a] for a in sub]):
                combos.append(tuple(zip(sub, pats)))
    grid = []
    for c in combos:
        base = [t for a, p in c for t in T[(a, p)]]
        for vie in (True, False):
            ts0 = base if vie else [t for t in base if t["ent"].weekday() != 4]
            for regla in ("cont", "stop1"):
                ts = aplicar_regla(sorted(ts0, key=lambda t: (t["a"], t["ent"])), regla)
                for obj in OBJETIVOS:
                    r = simular(ts, obj)
                    grid.append(dict(c=[[a, p] for a, p in c], k=len(c), vie=vie, regla=regla, obj=obj, **{x: r[x] for x in (
                        "n", "wr", "R", "ret", "cagr", "mes_geo", "sem_geo", "sem_prom", "sem_pos", "obj_hit", "mes_pos", "peor_mes", "peor_sem",
                        "mdd", "bajo_agua", "racha", "calmar", "sharpe", "anios", "max_conc")}))
    print("simulaciones:", len(grid))

    def ts_de(c, vie=True, regla="cont"):
        base = [t for a, p in c for t in T[(a, p)]]
        if not vie: base = [t for t in base if t["ent"].weekday() != 4]
        return aplicar_regla(sorted(base, key=lambda t: (t["a"], t["ent"])), regla)

    robusto = lambda g: all(v > 0 for v in g["anios"].values()) and len(g["anios"]) == 2
    def puntaje(g):     # preservar y crecer: crecimiento por unidad de caída, exigiendo los dos años positivos
        return (g["calmar"] or 0) if robusto(g) else -99

    # 3) validación fuera de muestra: elegir la combinación con 2025 y medirla en 2026, y al revés
    def elegir_en(y, obj=5, vie=True, regla="cont"):
        cand = [g for g in grid if g["obj"] == obj and g["vie"] == vie and g["regla"] == regla and str(y) in g["anios"]]
        return max(cand, key=lambda g: g["anios"][str(y)])
    validacion = []
    for y, z in (("2025", "2026"), ("2026", "2025")):
        g = elegir_en(y)
        validacion.append(dict(elegido_en=y, medido_en=z, combo=g["c"], en_muestra=g["anios"][y], fuera=g["anios"].get(z)))

    data = dict(meta=dict(ini=INI.strftime("%d/%m/%Y"), fin=FIN.strftime("%d/%m/%Y"), receso="22/12/2025 al 16/01/2026",
                          start_duplicado=dup, objetivos=OBJETIVOS, simulaciones=len(grid), combinaciones=len(combos),
                          meta_usuario=dict(semanal=5, mensual=20, anual=240)),
                activos=activos, correlaciones=dict(E=correlaciones(T, "E"), ES=correlaciones(T, "ES")),
                validacion=validacion)

    base_usuario = lambda g: g["obj"] == 5 and g["vie"] and g["regla"] == "cont"
    # todas las combinaciones con los parámetros planteados (riesgo 1%, límite de sesión, objetivo semanal 5R)
    data["todas"] = sorted([dict(g, robusto=robusto(g)) for g in grid if base_usuario(g)], key=lambda g: -(g["calmar"] or -9))
    data["ranking"] = dict(rendimiento=sorted([g for g in grid if base_usuario(g)], key=lambda g: -g["cagr"])[:10])

    # efecto promedio de cada objetivo semanal sobre todas las combinaciones de 2 o más activos (con viernes, sin regla)
    efecto = []
    claves = {}
    for g in grid:
        if g["k"] >= 2 and g["vie"] and g["regla"] == "cont": claves.setdefault(str(g["c"]), {})[g["obj"]] = g
    for o in OBJETIVOS[1:]:
        d_c = [v[o]["cagr"] - v[None]["cagr"] for v in claves.values()]
        d_dd = [v[o]["mdd"] - v[None]["mdd"] for v in claves.values()]
        d_wr = [v[o]["wr"] - v[None]["wr"] for v in claves.values()]
        d_r = [v[o]["racha"] - v[None]["racha"] for v in claves.values()]
        mejora = sum(1 for v in claves.values() if all(v[o]["anios"].get(y, 0) > v[None]["anios"].get(y, 0) for y in ("2025", "2026")))
        efecto.append(dict(obj=o, d_cagr=round(st.median(d_c), 1), d_dd=round(st.median(d_dd), 1), d_wr=round(st.median(d_wr), 1),
                           d_racha=round(st.median(d_r), 1), mejora_ambos=round(100 * mejora / len(claves), 1),
                           hit=round(st.median([v[o]["obj_hit"] for v in claves.values()]), 1)))
    data["efecto_objetivo"] = efecto

    # efecto del freno de pérdida semanal sobre todas las combinaciones de 2 o más activos
    efs = []
    multi = [c for c in combos if len(c) >= 2]
    bases = {c: simular([t for a, p in c for t in T[(a, p)]], None) for c in multi}
    for s_ in (2, 3, 4):
        L = []
        for c in multi:
            b_ = bases[c]; r_ = simular([t for a, p in c for t in T[(a, p)]], None, stop_sem=s_)
            L.append((r_["cagr"] - b_["cagr"], r_["mdd"] - b_["mdd"], r_["racha"] - b_["racha"], (r_["calmar"] or 0) - (b_["calmar"] or 0),
                      r_["peor_mes"] - b_["peor_mes"], all(r_["anios"][y] > b_["anios"][y] for y in ("2025", "2026"))))
        pc = lambda f: round(100 * sum(1 for x in L if f(x)) / len(L), 1)
        efs.append(dict(stop=s_, combos=len(L), d_cagr=round(st.median(x[0] for x in L), 1), d_dd=round(st.median(x[1] for x in L), 1),
                        d_racha=st.median(x[2] for x in L), calmar_mejora=pc(lambda x: x[3] > 0), dd_baja=pc(lambda x: x[1] < 0),
                        peor_mes_mejora=pc(lambda x: x[4] > 0), ambos=pc(lambda x: x[5])))
    data["efecto_stop"] = efs

    # combinaciones pedidas: XAU + cada par y los cuatro juntos (mejor patrón por activo, y mismos patrones en todos)
    pedidas = [("XAUUSD", "AUDUSD"), ("XAUUSD", "EURUSD"), ("XAUUSD", "GBPUSD"), tuple(ACTIVOS), ("XAUUSD",)]
    data["pedidas"] = []
    for sub in pedidas:
        cand = [g for g in grid if tuple(a for a, _ in g["c"]) == sub and base_usuario(g)]
        mejor = max(cand, key=lambda g: (robusto(g), g["calmar"] or 0))
        solo_e = next(g for g in cand if all(p == "E" for _, p in g["c"]))
        solo_es = next((g for g in cand if all(p == "ES" for _, p in g["c"])), None)
        c = [tuple(x) for x in mejor["c"]]
        tsm = ts_de(c)
        data["pedidas"].append(dict(activos=list(sub), mejor=mejor, solo_e=solo_e, solo_es=solo_es, mc=montecarlo(tsm, 5, sims=500),
                                    objetivos=[dict(obj=o, **{k: v for k, v in simular(tsm, o).items() if k in (
                                        "n", "wr", "cagr", "mes_geo", "mdd", "racha", "obj_hit", "anios", "sem_pos", "calmar")}) for o in OBJETIVOS],
                                    curve=simular(tsm, 5, curva=True)["curve"]))
    data["por_k"] = [max([g for g in grid if g["k"] == k and base_usuario(g)], key=lambda g: (robusto(g), g["calmar"] or 0)) for k in (1, 2, 3, 4)]

    # 4) recomendada, con reglas explícitas para no sobreoptimizar
    #   a) un activo-patrón entra solo si gana en 2025 y en 2026 por separado; por activo, el patrón con más R
    califica = {}
    for a in ACTIVOS:
        ok = [(activos[a][p]["total"]["R"], p) for p in opciones[a]
              if activos[a][p]["2025"].get("R", 0) > 0 and activos[a][p]["2026"].get("R", 0) > 0]
        califica[a] = dict(ok=[p for _, p in sorted(ok, reverse=True)], elegido=max(ok)[1] if ok else None)
    C = tuple((a, califica[a]["elegido"]) for a in ACTIVOS if califica[a]["elegido"])
    #   b) cada activo tiene que sumar en los dos años dentro de la cartera
    marg = []
    full = simular(ts_de(C), None)
    for x in C:
        sin = tuple(y for y in C if y != x)
        r = simular(ts_de(sin), None) if sin else None
        marg.append(dict(activo=x[0], patron=x[1], con=full["anios"], sin=r["anios"] if r else None,
                         suma=all(full["anios"][y] > (r["anios"][y] if r else 0) for y in ("2025", "2026"))))
    #   c) reglas de gestión: se acepta una regla solo si mejora el resultado de los dos años sin empeorar la caída máxima
    def corre(vie=True, regla="cont", obj=None, stop=None, mc=False, curva=False):
        ts = ts_de(C, vie, regla); r = simular(ts, obj, stop_sem=stop, curva=curva)
        if mc: r["mc"] = montecarlo(ts, obj, stop_sem=stop)
        return r
    base = corre()
    pruebas = [("Sin viernes", dict(vie=False))] + [(f"Objetivo semanal +{o}R", dict(obj=o)) for o in OBJETIVOS[1:]] + \
              [(f"Freno de pérdida semanal −{s_}R", dict(stop=s_)) for s_ in (2, 3, 4)] + \
              [("Cortar el activo tras perder la 1.ª operación", dict(regla="stop1")),
               ("Cortar solo si la 1.ª se cerró por Reset", dict(regla="stop_reset")),
               ("Cortar solo si la 1.ª se cerró por SL de precio", dict(regla="stop_precio"))]
    decis = []
    for nom, kw in pruebas:
        r = corre(**kw)
        ok = all(r["anios"][y] > base["anios"][y] for y in ("2025", "2026")) and r["mdd"] <= base["mdd"] + 1e-9
        decis.append(dict(regla=nom, kw=kw, ok=ok, **{k: r[k] for k in ("n", "wr", "cagr", "mes_geo", "mdd", "racha", "calmar", "anios", "sem_pos", "obj_hit", "bajo_agua", "peor_mes")}))
    # combinación final: una regla de cada tipo (la de mejor Calmar entre las aceptadas)
    final = {}
    for tipo in ("vie", "obj", "stop", "regla"):
        acc = [d_ for d_ in decis if d_["ok"] and tipo in d_["kw"]]
        if acc: final.update(max(acc, key=lambda d_: d_["calmar"] or 0)["kw"])
    rf = corre(mc=True, curva=True, **final)
    # comprobar que la suma de reglas sigue mejorando los dos años; si no, quedarse con la mejor regla sola
    if not all(rf["anios"][y] > base["anios"][y] for y in ("2025", "2026")):
        acc = [d_ for d_ in decis if d_["ok"]]
        final = max(acc, key=lambda d_: d_["calmar"] or 0)["kw"] if acc else {}
        rf = corre(mc=True, curva=True, **final)
    base_det = corre(mc=True, curva=True)
    usuario = corre(obj=5, mc=True, curva=True)
    data["recomendada"] = dict(combo=[list(x) for x in C], etiqueta=etiqueta(C), califica=califica, marginal=marg, decisiones=decis,
                               final=final, detalle=rf, base=base_det, usuario=usuario,
                               objetivos=[dict(obj=o, **{k: v for k, v in corre(obj=o, **{k2: v2 for k2, v2 in final.items() if k2 != "obj"}).items() if k in (
                                   "n", "wr", "cagr", "mes_geo", "sem_geo", "mdd", "racha", "obj_hit", "anios", "sem_pos", "calmar", "peor_sem", "bajo_agua")}) for o in OBJETIVOS])
    # riesgo por operación que haría falta para la meta de 240% anual (solo como referencia de lo que implica)
    tsf = ts_de(C, final.get("vie", True), final.get("regla", "cont"))
    nec = []
    for rk in (1, 1.5, 2, 2.5, 3, 3.5, 4, 5):
        r = simular(tsf, final.get("obj"), stop_sem=final.get("stop"), riesgo=rk)
        nec.append(dict(riesgo=rk, cagr=r["cagr"], mes=r["mes_geo"], sem=r["sem_geo"], mdd=r["mdd"], peor_mes=r["peor_mes"], anios=r["anios"]))
    data["riesgo_necesario"] = nec
    # referencias: XAU solo y los cuatro activos con Envolvente, con la misma gestión final
    ref = {}
    for nombre, c in (("xau", (("XAUUSD", "E"),)), ("cuatro", tuple((a, "E") for a in ACTIVOS))):
        ts = ts_de(c, final.get("vie", True), final.get("regla", "cont"))
        r = simular(ts, final.get("obj"), stop_sem=final.get("stop"), curva=True); r["mc"] = montecarlo(ts, final.get("obj"), sims=500, stop_sem=final.get("stop"))
        ref[nombre] = dict(etiqueta=etiqueta(c), detalle=r)
    data["referencias"] = ref
    json.dump(data, open(os.path.join(AQUI, "datos_hibrida.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return data


if __name__ == "__main__":
    d = main()
    print("recomendada:", d["recomendada"]["etiqueta"], d["recomendada"]["final"])
