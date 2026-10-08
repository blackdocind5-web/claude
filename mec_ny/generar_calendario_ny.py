"""Calendario de restricciones de la sesión NY (09:00-11:00 hora de Nueva York).

Reglas (definidas por Fabián, 08/10/2026):
- SIN_OPERAR: los mismos días "sin operar" de Pre NY que son feriados bancarios, el receso de fin de año y los
  discursos dentro de la ventana 09:00-11:00 (archivo fuentes/discursos_ny_2025_2026.csv, incluidos los de las 11:00).
  Los discursos de Pre NY no cuentan (otro horario).
- ANALIZAR_NOTICIA: NFP, CPI (USD y GBP), PPI y PIB final. En Pre NY no se opera; en NY la noticia ya pasó:
  no se excluyen de entrada, se analiza si conviene operar esos días.
- ANALIZAR_FOMC: días de FOMC Statement / Federal Funds Rate, Economic Projections y Meeting Minutes (14:00 NY).
- BLOQUEO_NOTICIA 09:50-10:03: ISM Manufacturing PMI, JOLTS Job Openings, CB Consumer Confidence y Core PCE de las 10:00.
Las reglas de Pre NY que no afectan a la ventana NY (BCE solo entrada 07:00-08:00, ADP 08:15, Core PCE 08:30) no se copian.

Uso: python generar_calendario_ny.py  -> calendario_ny.csv
"""
import csv, datetime as dt, glob, os
AQUI = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(AQUI, "..", "mec_filtros")

FOMC_TASA = ["2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
             "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16"]
FOMC_PROY = ["2025-03-19", "2025-06-18", "2025-09-17", "2025-12-10", "2026-03-18", "2026-06-17", "2026-09-16"]
FOMC_MINUTAS = ["2025-01-08", "2025-02-19", "2025-04-09", "2025-05-28", "2025-07-09", "2025-08-20", "2025-10-08", "2025-11-19",
                "2025-12-30", "2026-02-18", "2026-04-08", "2026-05-20", "2026-07-08", "2026-08-19", "2026-10-07"]
ISM = ["2025-01-03", "2025-02-03", "2025-03-03", "2025-04-01", "2025-05-01", "2025-06-02", "2025-07-01", "2025-08-01", "2025-09-02",
       "2025-10-01", "2025-11-03", "2025-12-01", "2026-01-05", "2026-02-02", "2026-03-02", "2026-04-01", "2026-05-01", "2026-06-01",
       "2026-07-01", "2026-08-03", "2026-09-01", "2026-10-01"]
JOLTS = ["2025-01-07", "2025-02-04", "2025-03-11", "2025-04-01", "2025-04-29", "2025-06-03", "2025-07-01", "2025-07-29", "2025-09-03",
         "2025-09-30", "2025-12-09", "2026-01-07", "2026-02-05", "2026-03-13", "2026-03-31", "2026-05-05", "2026-06-02", "2026-06-30",
         "2026-08-04", "2026-09-01", "2026-09-29"]
CB_CONF = ["2025-01-28", "2025-02-25", "2025-03-25", "2025-04-29", "2025-05-27", "2025-06-24", "2025-07-29", "2025-08-26", "2025-09-30",
           "2025-10-28", "2025-11-25", "2025-12-23", "2026-01-27", "2026-02-24", "2026-03-31", "2026-04-28", "2026-05-26", "2026-06-30",
           "2026-07-28", "2026-08-25", "2026-09-29"]

def fila(f, regla, ventana, divisa, evento, fuente):
    return dict(fecha=dt.date.fromisoformat(f).strftime("%d/%m/%Y"), regla=regla, ventana_NY=ventana, divisa=divisa,
                evento=evento, estado="confirmado", fuente=fuente)

def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(PRE, "calendario_*.csv"))):
        for r in csv.DictReader(open(path, encoding="utf-8-sig"), delimiter=";"):
            ev = r["evento"]; f = dt.datetime.strptime(r["fecha"], "%d/%m/%Y").date().isoformat()
            if r["regla"] == "SIN_OPERAR":
                if any(k in ev for k in ("NFP", "CPI", "PPI", "PIB final")):
                    rows.append(fila(f, "ANALIZAR_NOTICIA", "", r["divisa"], ev, r["fuente"] + " (Pre NY)"))
                elif "Discurso" not in ev:   # feriados y receso (los discursos de Pre NY no cuentan para NY: otro horario)
                    rows.append(fila(f, "SIN_OPERAR", "", r["divisa"], ev, r["fuente"] + " (Pre NY)"))
            elif r["regla"] == "BLOQUEO_NOTICIA" and r["ventana_NY"] >= "09:00":
                rows.append(fila(f, "BLOQUEO_NOTICIA", "09:50-10:03", r["divisa"], ev.replace(", fuera de la sesión", ""), r["fuente"] + " (Pre NY)"))
    for f in FOMC_TASA: rows.append(fila(f, "ANALIZAR_FOMC", "", "USD", "FOMC: Federal Funds Rate + FOMC Statement (14:00)", "Captura FF FOMC"))
    for f in FOMC_PROY: rows.append(fila(f, "ANALIZAR_FOMC", "", "USD", "FOMC Economic Projections (14:00)", "Captura FF FOMC"))
    for f in FOMC_MINUTAS: rows.append(fila(f, "ANALIZAR_FOMC", "", "USD", "FOMC Meeting Minutes (14:00)", "Captura FF FOMC"))
    for f in ISM: rows.append(fila(f, "BLOQUEO_NOTICIA", "09:50-10:03", "USD", "ISM Manufacturing PMI (dato 10:00)", "Captura FF ISM"))
    for f in JOLTS: rows.append(fila(f, "BLOQUEO_NOTICIA", "09:50-10:03", "USD", "JOLTS Job Openings (dato 10:00)", "Captura FF JOLTS"))
    for f in CB_CONF: rows.append(fila(f, "BLOQUEO_NOTICIA", "09:50-10:03", "USD", "CB Consumer Confidence (dato 10:00)", "Captura FF CB"))
    for r in csv.DictReader(open(os.path.join(AQUI, "fuentes", "discursos_ny_2025_2026.csv"), encoding="utf-8")):
        rows.append(fila(r["date"], "SIN_OPERAR", "", "USD", f'Discurso: {r["event_name"]} ({r["time_est"]})', "Discursos NY (archivo de Fabián)"))
    rows.sort(key=lambda r: (dt.datetime.strptime(r["fecha"], "%d/%m/%Y"), r["regla"]))
    w = csv.DictWriter(open(os.path.join(AQUI, "calendario_ny.csv"), "w", newline="", encoding="utf-8"), fieldnames=list(rows[0]), delimiter=";")
    w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r["regla"] for r in rows))

if __name__ == "__main__":
    main()
