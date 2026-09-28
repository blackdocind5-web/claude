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
    """Devuelve {fecha: [filas]}; un mismo día puede tener varias reglas."""
    cal = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "calendario_*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8-sig"), delimiter=";"):
            if r["estado"].strip().lower() != "confirmado":
                continue
            cal.setdefault(dt.datetime.strptime(r["fecha"], "%d/%m/%Y").date(), []).append(r)
    return cal


def ventana(r):
    ini, fin = r["ventana_NY"].split("-")
    return dt.time.fromisoformat(ini), dt.time.fromisoformat(fin)


def motivo_exclusion(entrada, salida, cal):
    """Reglas (hora de NY):
    SIN_OPERAR       -> se descarta toda operación con entrada ese día.
    SOLO_ENTRADA     -> la entrada debe estar en [inicio, fin); la salida no importa.
    BLOQUEO_NOTICIA  -> ni la entrada ni la salida pueden caer en [inicio, fin] (ambos extremos incluidos).
    """
    reglas = cal.get(entrada.date(), [])
    for r in reglas:
        if r["regla"] == "SIN_OPERAR":
            return f'Día sin operar: {r["evento"]}'
    for r in reglas:
        ini, fin = ventana(r)
        if r["regla"] == "SOLO_ENTRADA" and not (ini <= entrada.time() < fin):
            return f'Entrada fuera de la ventana {r["ventana_NY"]}: {r["evento"]}'
        if r["regla"] == "BLOQUEO_NOTICIA":
            if ini <= entrada.time() <= fin:
                return f'Entrada dentro del bloqueo {r["ventana_NY"]}: {r["evento"]}'
            if salida.date() == entrada.date() and ini <= salida.time() <= fin:
                return f'Salida dentro del bloqueo {r["ventana_NY"]}: {r["evento"]}'
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
        sal = next(f for f in fs if f["Tipo"].startswith("Salida"))
        hora = lambda f: dt.datetime.strptime(f["Fecha y hora"], "%Y-%m-%d %H:%M")
        m = motivo_exclusion(hora(ent), hora(sal), cal)
        for f in fs:
            (exc.writerow([m] + list(f.values())) if m else val.writerow(list(f.values())))
        if m:
            ne += 1
            print(f'  #{n:>4} {ent["Fecha y hora"]} -> {sal["Fecha y hora"][11:]} {ent["Señal"]:<10} {m}')
        else:
            nv += 1
    print(f"\nOperaciones: {nv + ne} | válidas: {nv} | excluidas: {ne}")


if __name__ == "__main__":
    main()
