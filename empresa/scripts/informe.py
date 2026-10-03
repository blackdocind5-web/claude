#!/usr/bin/env python3
"""Generador de informes profesionales (nivel accionistas) en HTML autónomo.

Uso:
    python empresa/scripts/informe.py spec.json [--salida ruta.html]

El spec es un JSON (ver empresa/scripts/ejemplo_spec.json). Los gráficos son SVG
en línea: no requiere librerías externas ni conexión. Soporta modo claro/oscuro
e impresión (Ctrl+P -> PDF).

Tipos de gráfico: torta, barras, barras_h, linea.
Formato: números 1.250,50 · fechas DD/MM/YYYY · textos en español.
"""
import argparse
import html
import json
import math
import sys
from pathlib import Path

# Paleta categórica en orden fijo (slots 1-6), claro / oscuro
SERIES = [
    ("#2a78d6", "#3987e5"), ("#eb6834", "#d95926"), ("#1baf7a", "#199e70"),
    ("#eda100", "#c98500"), ("#4a3aa7", "#9085e9"), ("#e87ba4", "#d55181"),
]


def esc(s):
    return html.escape(str(s))


def num(v, dec=None):
    """Formato es: punto de miles, coma decimal."""
    if isinstance(v, str):
        return v
    if dec is None:
        dec = 0 if float(v).is_integer() else 1
    s = f"{v:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def css_series():
    luz = "".join(f"--s{i+1}:{c[0]};" for i, c in enumerate(SERIES))
    osc = "".join(f"--s{i+1}:{c[1]};" for i, c in enumerate(SERIES))
    return luz, osc


def color(i):
    return f"var(--s{(i % len(SERIES)) + 1})"


# ---------------------------------------------------------------- gráficos
def g_torta(datos, unidad=""):
    total = sum(d["valor"] for d in datos) or 1
    cx = cy = 110
    r, ri = 100, 62
    ang = -math.pi / 2
    paths = []
    for i, d in enumerate(datos):
        if d["valor"] <= 0:
            continue
        frac = d["valor"] / total
        a2 = ang + frac * 2 * math.pi
        if frac >= 0.9999:
            paths.append(f'<circle cx="{cx}" cy="{cy}" r="{(r+ri)/2}" fill="none" '
                         f'stroke="{color(i)}" stroke-width="{r-ri}"><title>{esc(d["etiqueta"])}: {num(d["valor"])}</title></circle>')
        else:
            x1, y1 = cx + r * math.cos(ang), cy + r * math.sin(ang)
            x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
            x3, y3 = cx + ri * math.cos(a2), cy + ri * math.sin(a2)
            x4, y4 = cx + ri * math.cos(ang), cy + ri * math.sin(ang)
            large = 1 if frac > 0.5 else 0
            paths.append(
                f'<path d="M{x1:.2f},{y1:.2f} A{r},{r} 0 {large} 1 {x2:.2f},{y2:.2f} '
                f'L{x3:.2f},{y3:.2f} A{ri},{ri} 0 {large} 0 {x4:.2f},{y4:.2f} Z" '
                f'fill="{color(i)}" stroke="var(--surf)" stroke-width="2">'
                f'<title>{esc(d["etiqueta"])}: {num(d["valor"])} ({num(frac*100)}%)</title></path>')
        ang = a2
    centro = (f'<text x="{cx}" y="{cy-2}" text-anchor="middle" class="big">{num(total)}</text>'
              f'<text x="{cx}" y="{cy+16}" text-anchor="middle" class="mut">total{(" " + esc(unidad)) if unidad else ""}</text>')
    svg = f'<svg viewBox="0 0 220 220" role="img" class="torta">{"".join(paths)}{centro}</svg>'
    leyenda = "".join(
        f'<li><i style="background:{color(i)}"></i><span>{esc(d["etiqueta"])}</span>'
        f'<b>{num(d["valor"])} · {num(d["valor"]/total*100)}%</b></li>'
        for i, d in enumerate(datos))
    return f'<div class="torta-wrap">{svg}<ul class="leyenda">{leyenda}</ul></div>'


def g_barras(datos, unidad="", horizontal=False):
    vmax = max([d["valor"] for d in datos] + [1])
    n = len(datos)
    if horizontal:
        fila, izq, der, w = 34, 190, 50, 520
        h = n * fila + 10
        out = []
        for i, d in enumerate(datos):
            y = 5 + i * fila
            bw = (w - izq - der) * d["valor"] / vmax
            out.append(
                f'<text x="{izq-8}" y="{y+17}" text-anchor="end" class="lab">{esc(d["etiqueta"])}</text>'
                f'<path d="M{izq},{y+4} h{max(bw-4,0):.1f} a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-{max(bw-4,0):.1f} z" '
                f'fill="{color(0)}"><title>{esc(d["etiqueta"])}: {num(d["valor"])}</title></path>'
                f'<text x="{izq+bw+8:.1f}" y="{y+18}" class="val">{num(d["valor"])}{esc(unidad)}</text>')
        return f'<svg viewBox="0 0 {w} {h}" role="img" class="barras">{"".join(out)}</svg>'
    w, h, base, top = 640, 260, 215, 25
    ancho = (w - 60) / n
    bw = min(46, ancho * 0.6)
    out = [f'<line x1="40" x2="{w-10}" y1="{base}" y2="{base}" class="eje"/>']
    for i, d in enumerate(datos):
        bh = (base - top) * d["valor"] / vmax
        x = 40 + i * ancho + (ancho - bw) / 2
        out.append(
            f'<path d="M{x:.1f},{base} v-{max(bh-4,0):.1f} a4,4 0 0 1 4,-4 h{bw-8:.1f} a4,4 0 0 1 4,4 v{max(bh-4,0):.1f} z" '
            f'fill="{color(0)}"><title>{esc(d["etiqueta"])}: {num(d["valor"])}</title></path>'
            f'<text x="{x+bw/2:.1f}" y="{base-bh-6:.1f}" text-anchor="middle" class="val">{num(d["valor"])}{esc(unidad)}</text>'
            f'<text x="{x+bw/2:.1f}" y="{base+16}" text-anchor="middle" class="lab">{esc(d["etiqueta"])}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" class="barras">{"".join(out)}</svg>'


def g_linea(datos, unidad=""):
    w, h, base, top, izq = 640, 250, 205, 25, 50
    vmax = max([d["valor"] for d in datos] + [1])
    vmin = min([0] + [d["valor"] for d in datos])
    n = max(len(datos) - 1, 1)
    pts = []
    for i, d in enumerate(datos):
        x = izq + (w - izq - 20) * i / n
        y = base - (base - top) * (d["valor"] - vmin) / ((vmax - vmin) or 1)
        pts.append((x, y, d))
    grilla = "".join(
        f'<line x1="{izq}" x2="{w-20}" y1="{base-(base-top)*k/4:.1f}" y2="{base-(base-top)*k/4:.1f}" class="grilla"/>'
        f'<text x="{izq-6}" y="{base-(base-top)*k/4+4:.1f}" text-anchor="end" class="lab">{num(vmin+(vmax-vmin)*k/4)}</text>'
        for k in range(5))
    linea = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)
    puntos = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color(0)}" stroke="var(--surf)" stroke-width="2">'
        f'<title>{esc(d["etiqueta"])}: {num(d["valor"])}{esc(unidad)}</title></circle>'
        f'<text x="{x:.1f}" y="{base+18}" text-anchor="middle" class="lab">{esc(d["etiqueta"])}</text>'
        for x, y, d in pts)
    return (f'<svg viewBox="0 0 {w} {h}" role="img" class="barras">{grilla}'
            f'<path d="{linea}" fill="none" stroke="{color(0)}" stroke-width="2"/>{puntos}</svg>')


def grafico(g):
    datos = g["datos"]
    if not datos:
        return ""
    t = g.get("tipo", "barras")
    u = g.get("unidad", "")
    if t == "torta":
        cuerpo = g_torta(datos, u)
    elif t == "barras_h":
        cuerpo = g_barras(datos, u, horizontal=True)
    elif t == "linea":
        cuerpo = g_linea(datos, u)
    else:
        cuerpo = g_barras(datos, u)
    # vista de tabla (accesibilidad): <details>
    filas = "".join(f"<tr><td>{esc(d['etiqueta'])}</td><td class='n'>{num(d['valor'])}{esc(u)}</td></tr>" for d in datos)
    tabla = f'<details class="tv"><summary>Ver como tabla</summary><table><tbody>{filas}</tbody></table></details>'
    pie = f'<p class="fuente">Fuente: {esc(g["fuente"])}</p>' if g.get("fuente") else ""
    return (f'<figure class="graf"><figcaption>{esc(g.get("titulo", ""))}</figcaption>'
            f'{cuerpo}{tabla}{pie}</figure>')


# ---------------------------------------------------------------- secciones
def tabla(t):
    cab = "".join(f"<th>{esc(c)}</th>" for c in t["columnas"])
    filas = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in f) + "</tr>" for f in t["filas"])
    return f'<div class="tabla-wrap"><table><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>'


def lista(items):
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def seccion(s, n):
    out = [f'<section><h2><span class="n">{n:02d}</span>{esc(s["titulo"])}</h2>']
    for p in s.get("texto", []):
        out.append(f"<p>{esc(p)}</p>")
    if s.get("viñetas"):
        out.append(lista(s["viñetas"]))
    graficos = s.get("graficos") or ([s["grafico"]] if s.get("grafico") else [])
    if graficos:
        out.append('<div class="grid-graf">' + "".join(grafico(g) for g in graficos) + "</div>")
    if s.get("tabla"):
        out.append(tabla(s["tabla"]))
    if s.get("callout"):
        out.append(f'<aside class="callout">{esc(s["callout"])}</aside>')
    out.append("</section>")
    return "".join(out)


CSS = """
:root{color-scheme:light;--bg:#f3f4f4;--surf:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mut:#7a7975;--rule:#dcdcd8;--acc:#2a78d6;--acc-soft:#e6eef8;%(luz)s}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#111110;--surf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#8f8e86;--rule:#33332f;--acc:#3987e5;--acc-soft:#1c2a3b;%(osc)s}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#111110;--surf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#8f8e86;--rule:#33332f;--acc:#3987e5;--acc-soft:#1c2a3b;%(osc)s}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:0 16px}
.wrap{max-width:960px;margin:0 auto;padding:32px 0 64px}
header.port{background:var(--surf);border:1px solid var(--rule);border-top:6px solid var(--acc);border-radius:6px;padding:32px}
.eyebrow{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);margin:0}
h1{font-size:clamp(1.8rem,4.5vw,2.6rem);line-height:1.15;margin:.3rem 0 .4rem}
.sub{color:var(--ink2);font-size:1.1rem;margin:0}
.meta{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:18px;font-size:.85rem;color:var(--mut)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:20px 0}
.kpi{background:var(--surf);border:1px solid var(--rule);border-radius:6px;padding:16px}
.kpi b{display:block;font-size:1.9rem;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi span{display:block;color:var(--ink2);font-size:.85rem;margin-top:4px}
.kpi small{display:block;color:var(--mut);font-size:.78rem;margin-top:2px}
section{background:var(--surf);border:1px solid var(--rule);border-radius:6px;padding:24px 28px;margin-top:16px;break-inside:avoid-page}
h2{font-size:1.35rem;margin:0 0 .6rem;display:flex;gap:12px;align-items:baseline}
h2 .n{color:var(--acc);font-size:.9rem;font-variant-numeric:tabular-nums}
p{margin:.5rem 0;color:var(--ink2)} li{color:var(--ink2);margin:.2rem 0}
.resumen p{color:var(--ink);font-size:1.05rem}
.grid-graf{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;margin-top:12px}
figure.graf{margin:0;border:1px solid var(--rule);border-radius:6px;padding:14px 16px}
figcaption{font-weight:600;margin-bottom:8px}
svg{width:100%%;height:auto;display:block}
.torta{max-width:220px;margin:0 auto}
.torta-wrap{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:center}
.leyenda{list-style:none;padding:0;margin:0;min-width:200px;flex:1}
.leyenda li{display:flex;gap:8px;align-items:center;font-size:.88rem;margin:.3rem 0}
.leyenda i{width:12px;height:12px;border-radius:3px;flex:none}
.leyenda b{margin-left:auto;color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap}
svg text{fill:var(--ink2);font-size:11px;font-family:inherit}
svg .val{fill:var(--ink);font-weight:600} svg .big{fill:var(--ink);font-size:26px;font-weight:700}
svg .mut{fill:var(--mut)} svg .eje{stroke:var(--rule);stroke-width:1} svg .grilla{stroke:var(--rule);stroke-width:1;stroke-dasharray:2 3}
.tv{margin-top:8px;font-size:.82rem;color:var(--mut)} .tv summary{cursor:pointer}
.fuente{font-size:.75rem;color:var(--mut);margin:6px 0 0}
.tabla-wrap{overflow-x:auto;margin-top:12px}
table{border-collapse:collapse;width:100%%;font-size:.88rem}
th{text-align:left;color:var(--mut);font-weight:600;border-bottom:2px solid var(--rule);padding:8px 10px}
td{border-bottom:1px solid var(--rule);padding:8px 10px;color:var(--ink2);vertical-align:top} td.n{text-align:right;font-variant-numeric:tabular-nums}
.callout{margin-top:14px;padding:12px 16px;background:var(--acc-soft);border-left:4px solid var(--acc);border-radius:4px;color:var(--ink)}
.pendientes section{border-left:4px solid var(--s2)}
footer{margin-top:24px;font-size:.78rem;color:var(--mut);text-align:center}
@media print{body{background:#fff;padding:0}.wrap{padding:0}section,header.port,.kpi{break-inside:avoid}.tv{display:none}}
@media (max-width:480px){.grid-graf{grid-template-columns:1fr}header.port,section{padding:18px}}
"""


def construir(spec):
    luz, osc = css_series()
    kpis = "".join(
        f'<div class="kpi"><b>{esc(k["valor"])}</b><span>{esc(k["label"])}</span>'
        f'{"<small>"+esc(k["detalle"])+"</small>" if k.get("detalle") else ""}</div>'
        for k in spec.get("kpis", []))
    n = 0
    cuerpo = []
    if spec.get("resumen_ejecutivo"):
        n += 1
        cuerpo.append(f'<section class="resumen"><h2><span class="n">{n:02d}</span>Resumen ejecutivo</h2>'
                      + "".join(f"<p>{esc(p)}</p>" for p in spec["resumen_ejecutivo"]) + "</section>")
    for s in spec.get("secciones", []):
        n += 1
        cuerpo.append(seccion(s, n))
    for clave, titulo in (("decisiones", "Decisiones que necesitan al CEO"),
                          ("proximos_pasos", "Próximos pasos"),
                          ("pendientes_datos", "Datos que faltan (no se inventan cifras)"),
                          ("fuentes", "Fuentes")):
        if spec.get(clave):
            n += 1
            cuerpo.append(f'<section><h2><span class="n">{n:02d}</span>{titulo}</h2>{lista(spec[clave])}</section>')
    meta = " ".join(f"<span>{esc(x)}</span>" for x in (
        spec.get("departamento"), spec.get("fecha"), spec.get("autor"), spec.get("periodo")) if x)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(spec["titulo"])}</title><style>{CSS % {"luz": luz, "osc": osc}}</style></head>
<body><div class="wrap">
<header class="port"><p class="eyebrow">{esc(spec.get("clasificacion", "Informe interno · Confidencial"))}</p>
<h1>{esc(spec["titulo"])}</h1><p class="sub">{esc(spec.get("subtitulo", ""))}</p><div class="meta">{meta}</div></header>
<div class="kpis">{kpis}</div>
{"".join(cuerpo)}
<footer>Documento generado por Jarvis · {esc(spec.get("fecha", ""))} · Cifras solo desde datos reales; lo que falta figura como pendiente.</footer>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--salida")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    salida = Path(a.salida or Path(a.spec).with_suffix(".html"))
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(construir(spec), encoding="utf-8")
    print(f"Informe generado: {salida}")


if __name__ == "__main__":
    sys.exit(main())
