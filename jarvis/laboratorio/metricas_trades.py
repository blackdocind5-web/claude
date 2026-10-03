#!/usr/bin/env python3
"""Mide una estrategia como la mediría un trader, a partir de la "Lista de
operaciones" exportada del Strategy Tester de TradingView (Export data -> CSV).

Uso:
  python jarvis/laboratorio/metricas_trades.py datos_tv/01_cruce_ema_XAUUSD_M15.csv \
      --capital 10000 --riesgo-pct 1

Acepta encabezados en español o inglés y los dos formatos de TradingView
(dos filas por operación -entrada y salida- o una sola fila por operación).
Las horas se leen tal como las exporta TradingView: son las de la zona
horaria del gráfico, no necesariamente la de Nueva York.
"""
import argparse
import re
import unicodedata

import numpy as np
import pandas as pd


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9% ]", " ", s).strip()


def buscar(cols, *claves, excluir=()):
    for c in cols:
        n = norm(c)
        if all(k in n for k in claves) and not any(x in n for x in excluir):
            return c
    return None


def cargar(ruta):
    df = pd.read_csv(ruta, sep=None, engine="python")
    cols = list(df.columns)
    c_num = buscar(cols, "trade") or buscar(cols, "operacion") or buscar(cols, "n")
    c_tipo = buscar(cols, "type") or buscar(cols, "tipo")
    c_fecha = buscar(cols, "date") or buscar(cols, "fecha")
    c_pnl = (buscar(cols, "profit", excluir=("%", "cum")) or
             buscar(cols, "beneficio", excluir=("%", "acum")) or
             buscar(cols, "p l", excluir=("%", "cum")))
    if not all([c_num, c_tipo, c_fecha, c_pnl]):
        raise SystemExit(f"No reconozco las columnas del CSV: {cols}")

    df = df.rename(columns={c_num: "num", c_tipo: "tipo", c_fecha: "fecha", c_pnl: "pnl"})
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["pnl"] = pd.to_numeric(df["pnl"].astype(str).str.replace(",", ".").str.replace(r"[^0-9.\-]", "", regex=True),
                              errors="coerce")
    tipo = df["tipo"].map(norm)
    es_salida = tipo.str.contains("exit|salida")
    es_entrada = tipo.str.contains("entry|entrada")

    if es_salida.any():  # formato de dos filas
        salidas = df[es_salida].groupby("num").agg(fecha_salida=("fecha", "last"), pnl=("pnl", "last"))
        entradas = df[es_entrada].groupby("num").agg(fecha=("fecha", "first"), tipo=("tipo", "first"))
        t = entradas.join(salidas, how="inner").reset_index()
    else:  # una fila por operación
        t = df.rename(columns={"fecha": "fecha"}).assign(fecha_salida=df["fecha"])
    t["largo"] = t["tipo"].map(norm).str.contains("long|larg|compra")
    return t.dropna(subset=["pnl", "fecha"]).sort_values("fecha").reset_index(drop=True)


def racha(serie_bool):
    mejor = act = 0
    for v in serie_bool:
        act = act + 1 if v else 0
        mejor = max(mejor, act)
    return mejor


def es(v, dec=2):
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tabla_grupo(t, clave, etiquetas=None):
    g = t.groupby(clave)["pnl"].agg(["count", "sum", "mean", lambda x: (x > 0).mean() * 100])
    g.columns = ["oper", "neto", "promedio", "win"]
    for k, r in g.iterrows():
        nombre = etiquetas[k] if etiquetas else k
        print(f"   {str(nombre):<8} {int(r.oper):>5} oper.  neto {es(r.neto):>11}  prom. {es(r.promedio):>9}  acierto {es(r.win, 1):>6}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--capital", type=float, default=10000)
    ap.add_argument("--riesgo-pct", type=float, default=1.0, help="riesgo por operación (para expresar en R)")
    ap.add_argument("--simulaciones", type=int, default=2000)
    a = ap.parse_args()

    t = cargar(a.csv)
    n = len(t)
    if n == 0:
        raise SystemExit("El archivo no tiene operaciones cerradas.")
    ganadas, perdidas = t[t.pnl > 0].pnl, t[t.pnl < 0].pnl
    pf = ganadas.sum() / abs(perdidas.sum()) if len(perdidas) and perdidas.sum() != 0 else np.inf
    win = len(ganadas) / n
    prom_g = ganadas.mean() if len(ganadas) else 0.0
    prom_p = abs(perdidas.mean()) if len(perdidas) else 0.0
    payoff = prom_g / prom_p if prom_p else np.inf
    esperanza = t.pnl.mean()
    riesgo_usd = a.capital * a.riesgo_pct / 100
    equity = a.capital + t.pnl.cumsum()
    pico = np.maximum.accumulate(np.concatenate([[a.capital], equity.values]))[1:]
    dd = (equity - pico) / pico * 100
    neto = t.pnl.sum()

    print(f"\n=== {a.csv} ===")
    print(f"Período: {t.fecha.min():%d/%m/%Y} a {t.fecha_salida.max():%d/%m/%Y}   |   Operaciones: {n}")
    print(f"Neto: {es(neto)} ({es(neto / a.capital * 100, 1)}%)   Factor de ganancias: {es(pf)}")
    print(f"Acierto: {es(win * 100, 1)}%   Ganancia prom.: {es(prom_g)}   Pérdida prom.: {es(prom_p)}   Payoff: {es(payoff)}")
    print(f"Esperanza por operación: {es(esperanza)}  =  {es(esperanza / riesgo_usd)} R (1R = {es(riesgo_usd)})")
    print(f"Drawdown máximo: {es(dd.min(), 1)}%   Factor de recuperación: {es(neto / a.capital * 100 / abs(dd.min()))}" if dd.min() < 0 else "Sin drawdown")
    print(f"Racha máx. ganadora: {racha(t.pnl > 0)}   Racha máx. perdedora: {racha(t.pnl < 0)}")

    # Acierto mínimo para no perder dinero con este payoff (punto de equilibrio)
    if np.isfinite(payoff):
        print(f"Acierto de equilibrio con este payoff: {es(100 / (1 + payoff), 1)}%  (el real es {es(win * 100, 1)}%)")

    print("\nPor dirección:")
    tabla_grupo(t, t.largo.map({True: "Largos", False: "Cortos"}))
    print("Por día de la semana:")
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    tabla_grupo(t, t.fecha.dt.dayofweek, dias)
    print("Por hora de entrada (hora del gráfico):")
    tabla_grupo(t, t.fecha.dt.hour, {h: f"{h:02d}h" for h in range(24)})

    # Monte Carlo: ¿qué tan mala puede ser la racha si el orden hubiera sido otro?
    rng = np.random.default_rng(42)
    pnl = t.pnl.values
    peores, ruinas = [], 0
    for _ in range(a.simulaciones):
        eq = a.capital + np.cumsum(rng.permutation(pnl))
        pk = np.maximum.accumulate(np.concatenate([[a.capital], eq]))[1:]
        d = ((eq - pk) / pk * 100).min()
        peores.append(d)
        ruinas += eq.min() < a.capital * 0.5
    print(f"\nMonte Carlo ({a.simulaciones} reordenamientos de las mismas operaciones):")
    print(f"   Drawdown mediano: {es(np.median(peores), 1)}%   Peor 5%: {es(np.percentile(peores, 5), 1)}%")
    print(f"   Probabilidad de perder más del 50% del capital: {es(ruinas / a.simulaciones * 100, 1)}%")

    avisos = []
    if n < 100:
        avisos.append(f"solo {n} operaciones: muestra chica, no concluyente (mínimo 100)")
    if pf > 3:
        avisos.append("factor de ganancias > 3: sospechá sobreajuste o falta de costos")
    if abs(dd.min()) > 25:
        avisos.append("drawdown > 25%: difícil de sostener psicológicamente")
    if avisos:
        print("\nAlertas:")
        for v in avisos:
            print(f" - {v}")


if __name__ == "__main__":
    main()
