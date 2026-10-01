"""Regenera la tabla del calendario en README.md a partir de calendario_2026.csv."""
import csv, datetime as dt, collections

DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
LAB = {"SIN_OPERAR": "⛔ No operar", "SOLO_ENTRADA": "⚠️ Solo entradas {v}", "BLOQUEO_NOTICIA": "⏸️ Sin abrir {v}"}
out_all = []
for anio in ("2026", "2025"):
    rows = list(csv.DictReader(open(f"calendario_{anio}.csv", encoding="utf-8-sig"), delimiter=";"))
    c = collections.Counter(r["regla"] for r in rows)
    out = [f"## Calendario {anio} ({len({r['fecha'] for r in rows})} días · {len(rows)} eventos: {c['SIN_OPERAR']} ⛔ · {c['SOLO_ENTRADA']} ⚠️ · {c['BLOQUEO_NOTICIA']} ⏸️)"]
    cur = None
    for r in rows:
        d = dt.datetime.strptime(r["fecha"], "%d/%m/%Y")
        if d.month != cur:
            cur = d.month
            out.append(f"\n### {MESES[cur - 1]}\n\n| Fecha | Día | Regla | Divisa | Evento |\n|---|---|---|---|---|")
        out.append(f'| {r["fecha"]} | {DIAS[d.weekday()]} | {LAB[r["regla"]].format(v=r["ventana_NY"].replace("-", "–"))} | {r["divisa"]} | {r["evento"]} |')
    out_all += out + [""]
readme = open("README.md", encoding="utf-8").read()
head = readme[:readme.index("## Calendario 2026")]
open("README.md", "w", encoding="utf-8").write(head + "\n".join(out_all))
print("ok")
