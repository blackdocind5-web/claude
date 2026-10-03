"""Bot Oro — replica en Python la estrategia XAU Scalping MEC/MER (Pine v5).

Corre la misma lógica del indicador de TradingView sobre velas de 1 minuto y
devuelve las operaciones, el resultado en R y un diagnóstico de cada cambio de
estructura (ChOC) en el que NO se disparó MER, que es la discrepancia abierta
con la operativa de Fabian.

Fuente de la lógica: rama claude/trading-strategy-inconsistencies-w9S9b,
archivo "XAU scalping/XAU_estrategia_Scalping.pine".

Datos:
  --csv  export de TradingView (time, open, high, low, close) en M1
  --ticker GC=F / MGC=F vía Yahoo Finance (solo últimos ~7 días en M1)

Ejemplos:
  python jarvis/scripts/bot_oro.py --csv datos/XAUUSD_M1.csv
  python jarvis/scripts/bot_oro.py --ticker MGC=F --dias 5 --guardar
  python jarvis/scripts/bot_oro.py --csv x.csv --noticias-alto 0820-0833 --doji-min 0.05
"""

import argparse
import json
import os
import sys
from datetime import datetime, time as dtime

import pandas as pd

NY = "America/New_York"

# Valor por punto de cada contrato (USD por 1,00 de movimiento del oro)
CONTRATOS = {"MGC": 10.0, "GC": 100.0}

DIR_REPORTES = os.path.join(
    "jarvis", "sector_soluciones_financieras", "trading", "oro", "reportes"
)


# ── PARÁMETROS (mismos defaults que el Pine) ────────────────────────────────
def parametros(args):
    return {
        "sesion": (dtime(9, 1), dtime(10, 59)),
        "rr_tp": args.rr,
        "body_min": 0.85,
        "body_warn": 0.75,
        "mart_min": 0.50,
        "doji_min": args.doji_min,
        "max_sl_pts": 200.0,
        "sl_red": 0.40,
        "min_brk": 0.0001,
        "use_limite": args.limite,
        "use_cooldown": not args.sin_cooldown,
        "spike_size": 10.0,
        "cooldown_bars": 15,
        "noticias": _ventanas(args.noticias_alto) + _ventanas(args.noticias_medio),
    }


def _ventanas(texto):
    """'0820-0833,1000-1003' → [(08:20, 08:33), (10:00, 10:03)]"""
    out = []
    for tramo in (texto or "").split(","):
        tramo = tramo.strip()
        if not tramo:
            continue
        a, b = tramo.split("-")
        out.append((dtime(int(a[:2]), int(a[2:])), dtime(int(b[:2]), int(b[2:]))))
    return out


def _en_rango(t, rangos):
    return any(a <= t < b for a, b in rangos)


# ── DATOS ────────────────────────────────────────────────────────────────────
def cargar_csv(ruta):
    df = pd.read_csv(ruta)
    df.columns = [c.strip().lower() for c in df.columns]
    col_t = next(c for c in df.columns if c in ("time", "datetime", "date", "fecha"))
    t = df[col_t]
    if pd.api.types.is_numeric_dtype(t):
        idx = pd.to_datetime(t, unit="s", utc=True)
    else:
        idx = pd.to_datetime(t, utc=True)
    df.index = idx.dt.tz_convert(NY)
    return df[["open", "high", "low", "close"]].astype(float).sort_index()


def cargar_yahoo(ticker, dias):
    import yfinance as yf

    d = yf.download(ticker, period=f"{dias}d", interval="1m", progress=False)
    if d.empty:
        raise RuntimeError(
            f"Yahoo Finance no devolvió datos para {ticker}. "
            "Probá con --csv (export de TradingView)."
        )
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    d.columns = [c.lower() for c in d.columns]
    d.index = d.index.tz_convert(NY) if d.index.tz else d.index.tz_localize("UTC").tz_convert(NY)
    return d[["open", "high", "low", "close"]].astype(float)


def niveles_m3(df):
    """Altos/bajos m3 como request.security('3', lookahead_off, gaps_on).

    El valor aparece solo en la vela M1 donde cierra la vela M3.
    """
    m3 = df.resample("3min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    ).dropna()
    prev = m3.shift(1)
    alto = (prev["close"] > prev["open"]) & (m3["close"] < m3["open"])
    bajo = (prev["close"] < prev["open"]) & (m3["close"] > m3["open"])
    m3["m3_high"] = m3[["high"]].join(prev[["high"]], rsuffix="_p").max(axis=1).where(alto)
    m3["m3_low"] = m3[["low"]].join(prev[["low"]], rsuffix="_p").min(axis=1).where(bajo)
    # la vela M3 que abre a las HH:MM cierra en la M1 de HH:MM+2
    m3.index = m3.index + pd.Timedelta(minutes=2)
    return df.join(m3[["m3_high", "m3_low"]], how="left")


# ── VELAS ────────────────────────────────────────────────────────────────────
def forma(o, h, l, c, p):
    rng = h - l
    body = abs(c - o)
    bpct = body / rng if rng > 0 else 0.0
    upct = (h - max(o, c)) / rng if rng > 0 else 0.0
    lpct = (min(o, c) - l) / rng if rng > 0 else 0.0
    bm, mm, dm = p["body_min"], p["mart_min"], p["doji_min"]
    alc, baj = c > o, c < o
    tipo_bull = tipo_bear = None
    if alc and bpct >= bm and upct < 1 - bm:
        tipo_bull = "ENV"
    elif alc and mm <= bpct < bm and upct < 1 - bm:
        tipo_bull = "MART"
    elif alc and dm <= bpct < mm and lpct >= 0.15 and upct >= 0.15:
        tipo_bull = "DOJI"
    if baj and bpct >= bm and lpct < 1 - bm:
        tipo_bear = "ENV"
    elif baj and mm <= bpct < bm and lpct < 1 - bm:
        tipo_bear = "MART"
    elif baj and dm <= bpct < mm and lpct >= 0.15 and upct >= 0.15:
        tipo_bear = "DOJI"
    return {"bpct": bpct, "upct": upct, "lpct": lpct, "bull": tipo_bull, "bear": tipo_bear}


def _por_que_no(f, alcista):
    """Explica por qué una vela de ChOC no califica como entrada."""
    b, u, lo = f["bpct"], f["upct"], f["lpct"]
    contra = u if alcista else lo  # mecha a favor de la entrada
    if b < 0.15 and u >= 0.15 and lo >= 0.15:
        return f"cuerpo {b:.0%} < 15% con ambas mechas ≥15% (¿doji de Fabian? ver pendiente doji)"
    if b < 0.15:
        return f"cuerpo {b:.0%} demasiado chico"
    if b < 0.50:
        return f"cuerpo {b:.0%}: no es doji (mechas {lo:.0%}/{u:.0%})"
    return f"mecha a favor {contra:.0%} ≥ 15%"


# ── MOTOR ────────────────────────────────────────────────────────────────────
def correr(df, p):
    df = niveles_m3(df)
    O, H, L, C = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    M3H, M3L = df["m3_high"].to_numpy(), df["m3_low"].to_numpy()
    ts = df.index

    last_h = last_l = prev_h = prev_l = None
    struct = 0
    last_spike = None
    pos = 0  # 1 largo, -1 corto
    trade = None
    pendiente = None  # orden a ejecutar en la apertura de la próxima vela
    trades, chocs = [], []
    dia, day_tp, day_sl = None, 0, 0
    mb = p["min_brk"]

    def cerrar(i, precio, motivo):
        nonlocal pos, trade, day_tp, day_sl
        riesgo = abs(trade["entrada"] - trade["sl"])
        pts = (precio - trade["entrada"]) * trade["dir"]
        trade.update(salida=precio, hora_salida=ts[i], motivo=motivo, puntos=pts,
                     r=pts / riesgo if riesgo else 0.0)
        trades.append(trade)
        if pts > 0:
            day_tp += 1
        else:
            day_sl += 1
        pos, trade = 0, None

    for i in range(len(df)):
        t = ts[i]
        if dia != t.date():
            dia, day_tp, day_sl = t.date(), 0, 0

        # 1) ejecutar orden pendiente en la apertura (broker emulator de Pine)
        if pendiente is not None:
            if trade is not None and trade["dir"] != pendiente["dir"]:
                cerrar(i, O[i], "reversa")
            if trade is None:
                trade = dict(pendiente, entrada=O[i], hora_entrada=t)
                pos = trade["dir"]
            pendiente = None

        # 2) SL / TP intrabar (camino OHLC de Pine: lado más cercano a la apertura primero)
        if trade is not None:
            d, sl, tp = trade["dir"], trade["sl"], trade["tp"]
            toca_sl = (L[i] <= sl) if d == 1 else (H[i] >= sl)
            toca_tp = (H[i] >= tp) if d == 1 else (L[i] <= tp)
            if toca_sl and toca_tp:
                alto_primero = abs(O[i] - H[i]) < abs(O[i] - L[i])
                sl_primero = (not alto_primero) if d == 1 else alto_primero
                cerrar(i, sl if sl_primero else tp, "SL" if sl_primero else "TP")
            elif toca_sl:
                cerrar(i, sl, "SL")
            elif toca_tp:
                cerrar(i, tp, "TP")

        # 3) niveles m3
        if not pd.isna(M3H[i]):
            prev_h, last_h = last_h, M3H[i]
        if not pd.isna(M3L[i]):
            prev_l, last_l = last_l, M3L[i]

        # 4) estructura
        o, h, l, c = O[i], H[i], L[i], C[i]
        brk_h = last_h is not None and c > last_h and c > o and (c - last_h) / last_h >= mb
        brk_l = last_l is not None and c < last_l and c < o and (last_l - c) / last_l >= mb
        choc_bull = brk_h and struct == -1
        choc_bear = brk_l and struct == 1
        if brk_h:
            struct = 1
        if brk_l:
            struct = -1

        # 5) filtros
        tt = t.time()
        if h - l >= p["spike_size"]:
            last_spike = i
        cooldown = p["use_cooldown"] and last_spike is not None and i - last_spike < p["cooldown_bars"]
        en_sesion = p["sesion"][0] <= tt < p["sesion"][1]
        noticia = _en_rango(tt, p["noticias"])
        limite_ok = not p["use_limite"] or (day_tp == 0 and day_sl < 2)
        can_trade = en_sesion and limite_ok and not noticia
        can_long, can_short = pos <= 0, pos >= 0

        f = forma(o, h, l, c, p)
        eb, es = f["bull"] is not None, f["bear"] is not None

        # 6) MEC
        mec_buy = mec_sell = False
        sub_buy = sub_sell = "ENV"
        if i >= 3:
            o1, c1, h1, l1 = O[i-1], C[i-1], H[i-1], L[i-1]
            o2, c2, h2, l2 = O[i-2], C[i-2], H[i-2], L[i-2]
            o3, c3, h3, l3 = O[i-3], C[i-3], H[i-3], L[i-3]
            rng1 = h1 - l1
            bpct1 = abs(c1 - o1) / rng1 if rng1 > 0 else 0.0
            ind_bull, ind_bear = bpct1 <= 0.5001 and c1 > o1, bpct1 <= 0.5001 and c1 < o1
            not3bull = not (c > o and c1 > o1 and c2 > o2)
            not3bear = not (c < o and c1 < o1 and c2 < o2)
            env_b = c1 < o1 and eb and c > h1 and (c - h1) / h1 >= mb
            env_s = c1 > o1 and es and c < l1 and (l1 - c) / l1 >= mb
            ph, pl = max(h1, h2), min(l1, l2)
            st1_b = c2 < o2 and ind_bull and eb and not3bull and c > ph and (c - ph) / ph >= mb
            st1_s = c2 > o2 and ind_bear and es and not3bear and c < pl and (pl - c) / pl >= mb
            ph2, pl2 = max(h1, h2, h3), min(l1, l2, l3)
            st2_b = c2 < o2 and c3 < o3 and ind_bull and eb and not3bull and c > ph2 and (c - ph2) / ph2 >= mb
            st2_s = c2 > o2 and c3 > o3 and ind_bear and es and not3bear and c < pl2 and (pl2 - c) / pl2 >= mb
            base = can_trade and not cooldown
            mec_buy = base and can_long and struct == 1 and (env_b or st1_b or st2_b)
            mec_sell = base and can_short and struct == -1 and (env_s or st1_s or st2_s)
            sub_buy = "ENV" if env_b else "START"
            sub_sell = "ENV" if env_s else "START"

        # 7) MER (regla de nivel único)
        sl_long = last_l
        if last_l is not None and prev_l is not None and prev_l < c and last_l < c \
                and abs(last_l - prev_l) / last_l <= mb:
            sl_long = min(last_l, prev_l)
        sl_short = last_h
        if last_h is not None and prev_h is not None and prev_h > c and last_h > c \
                and abs(last_h - prev_h) / last_h <= mb:
            sl_short = max(last_h, prev_h)
        mer_buy = can_trade and can_long and choc_bull and eb and sl_long is not None
        mer_sell = can_trade and can_short and choc_bear and es and sl_short is not None

        # diagnóstico de cada ChOC
        if choc_bull or choc_bear:
            alc = bool(choc_bull)
            disparo = mer_buy if alc else mer_sell
            if disparo:
                motivo = "MER disparado"
            elif not en_sesion:
                motivo = "fuera de sesión"
            elif noticia:
                motivo = "bloqueo por noticia"
            elif not limite_ok:
                motivo = "límite diario"
            elif not (can_long if alc else can_short):
                motivo = "ya hay posición en esa dirección"
            else:
                motivo = _por_que_no(f, alc)
            chocs.append({"hora": t, "tipo": "ALCISTA" if alc else "BAJISTA",
                          "en_sesion": en_sesion, "mer": disparo, "motivo": motivo,
                          "cuerpo": f["bpct"]})

        # 8) orden + SL/TP
        go_long, go_short = mec_buy or mer_buy, mec_sell or mer_sell
        if go_long:
            ref = sl_long if mer_buy else (last_l if last_l is not None else c - c * 0.002)
            dist = c - ref
            if dist > p["max_sl_pts"]:
                dist *= 1 - p["sl_red"]
            modelo = "MER" if mer_buy else f"MEC {sub_buy}"
            pendiente = {"dir": 1, "modelo": modelo, "vela": f["bull"], "senal": t,
                         "sl": c - dist, "tp": c + dist * p["rr_tp"]}
        if go_short:
            ref = sl_short if mer_sell else (last_h if last_h is not None else c + c * 0.002)
            dist = ref - c
            if dist > p["max_sl_pts"]:
                dist *= 1 - p["sl_red"]
            modelo = "MER" if mer_sell else f"MEC {sub_sell}"
            pendiente = {"dir": -1, "modelo": modelo, "vela": f["bear"], "senal": t,
                         "sl": c + dist, "tp": c - dist * p["rr_tp"]}

    if trade is not None:
        trade.update(salida=None, motivo="abierta", puntos=None, r=None)
        trades.append(trade)
    return trades, chocs


# ── RESUMEN ──────────────────────────────────────────────────────────────────
def resumir(trades):
    cerradas = [t for t in trades if t["r"] is not None]
    if not cerradas:
        return {"operaciones": 0}
    rs = [t["r"] for t in cerradas]
    ganadas = [r for r in rs if r > 0]
    perdidas = [r for r in rs if r <= 0]
    eq, pico, dd = 0.0, 0.0, 0.0
    for r in rs:
        eq += r
        pico = max(pico, eq)
        dd = min(dd, eq - pico)
    por_modelo = {}
    for t in cerradas:
        m = por_modelo.setdefault(t["modelo"], {"n": 0, "r": 0.0, "ganadas": 0})
        m["n"] += 1
        m["r"] += t["r"]
        m["ganadas"] += t["r"] > 0
    puntos = sum(t["puntos"] for t in cerradas)
    return {
        "operaciones": len(cerradas),
        "win_rate": len(ganadas) / len(cerradas),
        "r_total": sum(rs),
        "r_promedio": sum(rs) / len(rs),
        "profit_factor": (sum(ganadas) / abs(sum(perdidas))) if perdidas and sum(perdidas) else None,
        "max_drawdown_r": dd,
        "puntos": puntos,
        "usd_por_contrato": {k: puntos * v for k, v in CONTRATOS.items()},
        "por_modelo": por_modelo,
    }


def _n(x, dec=2):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _signo(x, dec=2, suf=""):
    return ("+" if x > 0 else "") + _n(x, dec) + suf


def _usd(x):
    return ("+" if x > 0 else "-" if x < 0 else "") + "$" + _n(abs(x))


def a_markdown(trades, chocs, res, fuente, p):
    hoy = datetime.now().strftime("%d/%m/%Y")
    L = [f"# Bot Oro — Reporte del {hoy}", "",
         f"**Fuente de datos:** {fuente}  ",
         f"**Sesión:** 09:01–10:59 NY · **RR:** 1:{_n(p['rr_tp'])} · "
         f"**Cooldown:** {'sí' if p['use_cooldown'] else 'no'} · "
         f"**Límite diario:** {'sí' if p['use_limite'] else 'no'} · "
         f"**Doji mínimo:** {_n(p['doji_min'] * 100, 0)}%", ""]
    L += ["## Resumen", ""]
    if not res.get("operaciones"):
        L += ["Sin operaciones cerradas en el período.", ""]
    else:
        L += ["| Métrica | Valor |", "|---|---|",
              f"| Operaciones | {res['operaciones']} |",
              f"| Win rate | {_n(res['win_rate'] * 100, 1)}% |",
              f"| Resultado | {_signo(res['r_total'])}R |",
              f"| R promedio | {_signo(res['r_promedio'])}R |",
              f"| Profit factor | {_n(res['profit_factor']) if res['profit_factor'] else '—'} |",
              f"| Máx. drawdown | {_n(res['max_drawdown_r'])}R |",
              f"| Puntos | {_signo(res['puntos'])} |",
              f"| 1 MGC (micro, $10/pto) | {_usd(res['usd_por_contrato']['MGC'])} |",
              f"| 1 GC (estándar, $100/pto) | {_usd(res['usd_por_contrato']['GC'])} |", ""]
        L += ["### Por modelo", "", "| Modelo | Ops | Ganadas | R |", "|---|---|---|---|"]
        for m, v in sorted(res["por_modelo"].items()):
            L.append(f"| {m} | {v['n']} | {v['ganadas']} | {_signo(v['r'])} |")
        L.append("")
    L += ["## Operaciones", "",
          "| Fecha | Señal | Dir | Modelo | Vela | Entrada | SL | TP | Salida | Motivo | R |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in trades:
        L.append("| {f} | {h} | {d} | {m} | {v} | {e} | {sl} | {tp} | {s} | {mo} | {r} |".format(
            f=t["senal"].strftime("%d/%m/%Y"), h=t["senal"].strftime("%H:%M"),
            d="COMPRA" if t["dir"] == 1 else "VENTA", m=t["modelo"], v=t["vela"] or "—",
            e=_n(t["entrada"]), sl=_n(t["sl"]), tp=_n(t["tp"]),
            s=_n(t["salida"]) if t["salida"] is not None else "—", mo=t["motivo"],
            r=_signo(t["r"]) if t["r"] is not None else "—"))
    L.append("")
    en_ses = [c for c in chocs if c["en_sesion"]]
    L += ["## Cambios de estructura en sesión (diagnóstico MER)", "",
          "Cada ChOC en sesión y si disparó MER. Los marcados como posible doji son "
          "candidatos a la discrepancia con Fabian (pendiente umbral doji).", "",
          "| Fecha | Hora | ChOC | ¿MER? | Motivo |", "|---|---|---|---|---|"]
    for c in en_ses:
        L.append(f"| {c['hora'].strftime('%d/%m/%Y')} | {c['hora'].strftime('%H:%M')} | "
                 f"{c['tipo']} | {'sí' if c['mer'] else 'no'} | {c['motivo']} |")
    if not en_ses:
        L.append("| — | — | — | — | Sin ChOC en sesión |")
    L += ["", "> Réplica en Python del Pine v5. Diferencias conocidas: sin slippage de 2 ticks; "
          "fill de entrada en la apertura de la vela siguiente (igual que Pine sin "
          "`process_orders_on_close`). Validar contra TradingView antes de sacar conclusiones."]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Bot Oro — réplica de la estrategia XAU MEC/MER")
    fuente = ap.add_mutually_exclusive_group(required=True)
    fuente.add_argument("--csv", help="CSV M1 exportado de TradingView (time,open,high,low,close)")
    fuente.add_argument("--ticker", help="Ticker Yahoo: GC=F, MGC=F")
    ap.add_argument("--dias", type=int, default=5, help="Días de historia con --ticker (máx. ~7)")
    ap.add_argument("--rr", type=float, default=0.9, help="Ratio TP (default 0.9)")
    ap.add_argument("--doji-min", type=float, default=0.15,
                    help="Cuerpo mínimo doji (default 0.15; probar 0.05 para la hipótesis doji)")
    ap.add_argument("--noticias-alto", default="", help="Ventanas HHMM-HHMM separadas por coma")
    ap.add_argument("--noticias-medio", default="", help="Ventanas HHMM-HHMM separadas por coma")
    ap.add_argument("--limite", action="store_true", help="Activar límite diario (1TP / 1SL+1TP / 2SL)")
    ap.add_argument("--sin-cooldown", action="store_true", help="Desactivar cooldown post-spike")
    ap.add_argument("--guardar", action="store_true", help=f"Guardar reporte en {DIR_REPORTES}/")
    ap.add_argument("--json", action="store_true", help="Salida JSON en vez de markdown")
    args = ap.parse_args()

    p = parametros(args)
    try:
        df = cargar_csv(args.csv) if args.csv else cargar_yahoo(args.ticker, args.dias)
    except Exception as e:  # noqa: BLE001
        print(f"Error cargando datos: {e}", file=sys.stderr)
        sys.exit(1)
    fuente_txt = args.csv or f"{args.ticker} (Yahoo Finance, {args.dias} días)"

    trades, chocs = correr(df, p)
    res = resumir(trades)

    if args.json:
        print(json.dumps({"resumen": res, "operaciones": trades, "chocs": chocs},
                         default=str, ensure_ascii=False, indent=2))
        return
    md = a_markdown(trades, chocs, res, fuente_txt, p)
    print(md)
    if args.guardar:
        os.makedirs(DIR_REPORTES, exist_ok=True)
        ruta = os.path.join(DIR_REPORTES, f"{datetime.now():%Y-%m-%d}_bot_oro.md")
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        print(f"\nReporte guardado en: {ruta}")


if __name__ == "__main__":
    main()
