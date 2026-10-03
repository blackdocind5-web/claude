#!/usr/bin/env python3
"""Rankea las estrategias cargadas en resultados.csv.

Uso:  python jarvis/tradingview/ranking.py [--min-trades 100]

Criterio: se descartan las corridas con pocas operaciones (no son
estadísticamente confiables) y se ordena por factor de recuperación
(rentabilidad neta / drawdown máximo), con el factor de ganancias de desempate.
"""
import argparse
from pathlib import Path

import pandas as pd

ARCHIVO = Path(__file__).parent / "resultados.csv"


def es(valor, dec=2):
    """Formato español: punto de miles, coma decimal."""
    if pd.isna(valor):
        return "-"
    return f"{valor:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-trades", type=int, default=100)
    args = ap.parse_args()

    df = pd.read_csv(ARCHIVO)
    for col in ["neto_pct", "trades", "win_pct", "factor_ganancia", "dd_max_pct", "sharpe"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["recuperacion"] = df["neto_pct"] / df["dd_max_pct"].abs()
    df["valida"] = df["trades"] >= args.min_trades
    df["con_costos"] = (df["comision_pct"].fillna(0) > 0) | (df["slippage_ticks"].fillna(0) > 0)

    df = df.sort_values(
        ["valida", "recuperacion", "factor_ganancia"], ascending=[False, False, False]
    )

    print(f"{'Estrategia':<44}{'Activo':<9}{'TF':<5}{'Neto %':>9}{'Oper.':>7}{'PF':>7}{'DD %':>8}{'Recup.':>8}  Notas")
    for _, r in df.iterrows():
        marca = "" if r["valida"] else " [pocas operaciones]"
        marca += "" if r["con_costos"] else " [SIN costos]"
        print(
            f"{str(r['estrategia'])[:43]:<44}{str(r['activo']):<9}{str(r['timeframe']):<5}"
            f"{es(r['neto_pct']):>9}{es(r['trades'], 0):>7}{es(r['factor_ganancia']):>7}"
            f"{es(r['dd_max_pct']):>8}{es(r['recuperacion']):>8} {marca}"
        )


if __name__ == "__main__":
    main()
