"""Filtra un CSV de "Lista de operaciones" de TradingView según el calendario de
restricciones del sistema MEC (sesión Pre NY, horario de Nueva York).

Uso:
    python filtrar_trades.py <export_tradingview.csv> [--salida DIR]

Genera en DIR (por defecto, junto al CSV de entrada):
    <nombre>_validos.csv     operaciones que el sistema sí toma
    <nombre>_excluidos.csv   operaciones descartadas, con el motivo
"""
import argparse
import csv
import datetime as dt
import glob
import os
from collections import OrderedDict

AQUI = os.path.dirname(os.path.abspath(__file__))


def cargar_calendario():
    cal = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "calendario_*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8-sig"), delimiter=";"):
            if r["estado"].strip().lower() != "confirmado":
                continue
            cal[dt.datetime.strptime(r["fecha"], "%d/%m/%Y").date()] = r
    return cal


def motivo_exclusion(entrada, cal):
    r = cal.get(entrada.date())
    if not r:
        return None
    if r["regla"] == "SIN_OPERAR":
        return f'Día sin operar: {r["evento"]}'
    if r["regla"].startswith("SOLO_"):
        ini, fin = r["ventana_permitida_NY"].split("-")
        t = entrada.time()
        if not (dt.time.fromisoformat(ini) <= t < dt.time.fromisoformat(fin)):
            return f'Fuera de ventana {ini}-{fin}: {r["evento"]}'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--salida")
    a = ap.parse_args()
    cal = cargar_calendario()

    filas = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    campos = list(filas[0].keys())
    ops = OrderedDict()
    for f in filas:
        ops.setdefault(f["Número de operación"], []).append(f)

    base = os.path.splitext(os.path.basename(a.csv))[0]
    out = a.salida or os.path.dirname(os.path.abspath(a.csv))
    val = csv.writer(open(os.path.join(out, base + "_validos.csv"), "w", newline="", encoding="utf-8-sig"))
    exc = csv.writer(open(os.path.join(out, base + "_excluidos.csv"), "w", newline="", encoding="utf-8-sig"))
    val.writerow(campos)
    exc.writerow(["Motivo de exclusión"] + campos)
    nv = ne = 0
    for n, fs in ops.items():
        ent = next(f for f in fs if f["Tipo"].startswith("Entrada"))
        m = motivo_exclusion(dt.datetime.strptime(ent["Fecha y hora"], "%Y-%m-%d %H:%M"), cal)
        for f in fs:
            (exc.writerow([m] + list(f.values())) if m else val.writerow(list(f.values())))
        if m:
            ne += 1
            print(f'  #{n:>4} {ent["Fecha y hora"]} {ent["Señal"]:<10} -> {m}')
        else:
            nv += 1
    print(f"\nOperaciones: {nv + ne} | válidas: {nv} | excluidas: {ne}")


if __name__ == "__main__":
    main()
