import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_script(script, *args):
    cmd = [sys.executable, str(Path("jarvis/scripts") / script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except Exception:
        return result.stdout


def fmt_pct(val):
    if val is None:
        return "N/A"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.1f}%".replace(".", ",")


def fmt_price(val):
    if val is None:
        return "N/A"
    return f"${val:,.2f}".replace(",", ".")


def fmt_pct_mult(val):
    if val is None:
        return "N/A"
    return f"{val * 100:.1f}%".replace(".", ",")


CSS = """
body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; margin: 0; }
h1 { color: #64b5f6; } h2 { color: #90caf9; border-bottom: 1px solid #333; padding-bottom: 8px; }
table { width: 100%; border-collapse: collapse; margin: 16px 0; }
th { background: #0d47a1; color: #fff; padding: 10px; text-align: left; }
td { padding: 9px; border-bottom: 1px solid #333; }
tr:hover { background: #1e3a5f; }
.card { background: #16213e; border-radius: 8px; padding: 16px; margin: 8px;
        display: inline-block; min-width: 180px; text-align: center; vertical-align: top; }
.card-value { font-size: 24px; font-weight: bold; margin-top: 6px; }
.badge { display:inline-block; padding:4px 12px; border-radius:20px; font-weight:bold; background:#1e3a5f; }
.footer { color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #333; padding-top: 12px; }
"""


def build_portfolio_report(data):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    resumen = data.get("resumen") or {}
    posiciones = data.get("posiciones") or []

    rows = ""
    for p in posiciones:
        color = "#4CAF50" if p["pnl"] >= 0 else "#F44336"
        rows += f"""<tr>
            <td><strong>{p['ticker']}</strong></td>
            <td>{p['cantidad']}</td>
            <td>{fmt_price(p['precio_compra'])}</td>
            <td>{fmt_price(p['precio_actual'])}</td>
            <td style="color:{color}">{fmt_pct(p['variacion_dia_pct'])}</td>
            <td>{fmt_price(p['invertido'])}</td>
            <td>{fmt_price(p['valor_actual'])}</td>
            <td style="color:{color}"><strong>{fmt_price(p['pnl'])} ({fmt_pct(p['pnl_pct'])})</strong></td>
        </tr>"""

    pnl_color = "#4CAF50" if (resumen.get("pnl_total") or 0) >= 0 else "#F44336"

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Portfolio — {fecha}</title><style>{CSS}</style></head><body>
<h1>&#x1F4BC; Reporte de Portfolio</h1><p>Generado: {fecha}</p>
<h2>Resumen</h2>
<div>
  <div class="card"><div>Invertido</div><div class="card-value">{fmt_price(resumen.get('total_invertido'))}</div></div>
  <div class="card"><div>Valor Actual</div><div class="card-value">{fmt_price(resumen.get('valor_actual'))}</div></div>
  <div class="card"><div>P&amp;L Total</div>
    <div class="card-value" style="color:{pnl_color}">
      {fmt_price(resumen.get('pnl_total'))} ({fmt_pct(resumen.get('pnl_total_pct'))})
    </div>
  </div>
</div>
<h2>Posiciones ({resumen.get('num_posiciones', 0)})</h2>
<table><tr><th>Ticker</th><th>Cant.</th><th>Compra</th><th>Actual</th>
<th>Var. Día</th><th>Invertido</th><th>Valor</th><th>P&amp;L</th></tr>
{rows}</table>
<p class="footer">Jarvis &#x2014; Asistente Financiero Personal | Datos via Yahoo Finance</p>
</body></html>"""


def build_market_report(data):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    indices = data.get("indices") or {}
    sectores = data.get("sectores") or {}
    macro = data.get("macro") or {}

    def row(nombre, info):
        var = info.get("variacion")
        precio = info.get("precio")
        if var is None:
            return f"<tr><td>{nombre}</td><td>{fmt_price(precio)}</td><td>N/A</td></tr>"
        color = "#4CAF50" if var >= 0 else "#F44336"
        return f"<tr><td>{nombre}</td><td>{fmt_price(precio)}</td><td style='color:{color}'>{fmt_pct(var)}</td></tr>"

    idx_rows = "".join(row(k, v) for k, v in indices.items())
    sec_rows = "".join(row(k, v) for k, v in sectores.items())
    mac_rows = "".join(row(k, v) for k, v in macro.items())

    vix_val = data.get("vix", {}).get("valor", "N/A")
    vix_txt = data.get("vix", {}).get("interpretacion", "")
    sentimiento = data.get("sentimiento_general", "neutral")
    curva = data.get("yield_curve") or {}
    mejor = data.get("mejor_sector", "N/A")
    peor = data.get("peor_sector", "N/A")

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Briefing Mercado — {fecha}</title><style>{CSS}</style></head><body>
<h1>&#x1F4CA; Briefing de Mercado</h1>
<p>Generado: {fecha} | Sentimiento: <span class="badge">{sentimiento.upper()}</span></p>
<p>&#x1F4C8; Mejor sector: <strong>{mejor}</strong> &nbsp;|&nbsp; &#x1F4C9; Peor sector: <strong>{peor}</strong></p>
<h2>&#xD83C;&#xDFE6; Índices Principales</h2>
<table><tr><th>Índice</th><th>Precio</th><th>Variación Día</th></tr>{idx_rows}</table>
<h2>&#x1F3ED; Sectores S&amp;P 500</h2>
<table><tr><th>Sector</th><th>Precio</th><th>Variación Día</th></tr>{sec_rows}</table>
<h2>&#x1F30D; Mercados Macro</h2>
<table><tr><th>Activo</th><th>Precio</th><th>Variación Día</th></tr>{mac_rows}</table>
<h2>&#x26A0;&#xFE0F; VIX &amp; Yield Curve</h2>
<p><strong>VIX:</strong> {vix_val} — {vix_txt}</p>
<p><strong>Yield 10Y:</strong> {curva.get('yield_10y','N/A')} |
   <strong>Yield 2Y:</strong> {curva.get('yield_2y','N/A')} |
   <strong>Spread:</strong> {curva.get('spread','N/A')} |
   <strong>Invertida:</strong> {'Sí &#x26A0;&#xFE0F;' if curva.get('invertida') else 'No &#x2705;'}</p>
<p class="footer">Jarvis &#x2014; Asistente Financiero Personal | Datos via Yahoo Finance</p>
</body></html>"""


def build_company_report(ticker, period="1y"):
    data = run_script("analyze_company.py", ticker, "--period", period)
    if not data or isinstance(data, str):
        return f"<html><body><p>Error obteniendo datos para {ticker}</p></body></html>"

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    tec = data.get("tecnico") or {}
    val = data.get("valuacion") or {}
    sal = data.get("salud") or {}

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>{data.get('ticker')} — Análisis</title><style>{CSS}</style></head><body>
<h1>&#x1F50D; {data.get('nombre', ticker)} ({data.get('ticker')})</h1>
<p>Generado: {fecha} | Precio: <strong>{fmt_price(data.get('precio_actual'))}</strong> |
Var. día: <strong>{fmt_pct(data.get('variacion_dia'))}</strong> |
Tendencia: <strong>{(data.get('tendencia') or 'N/A').upper()}</strong></p>
<h2>Análisis Técnico</h2>
<table><tr><th>Indicador</th><th>Valor</th><th>Señal</th></tr>
<tr><td>MA20</td><td>{fmt_price(tec.get('ma20'))}</td><td>{tec.get('senal_ma','')}</td></tr>
<tr><td>MA50</td><td>{fmt_price(tec.get('ma50'))}</td><td></td></tr>
<tr><td>MA200</td><td>{fmt_price(tec.get('ma200'))}</td><td></td></tr>
<tr><td>RSI (14)</td><td>{tec.get('rsi','N/A')}</td><td>{tec.get('senal_rsi','')}</td></tr>
<tr><td>Soporte</td><td>{fmt_price(tec.get('soporte'))}</td><td></td></tr>
<tr><td>Resistencia</td><td>{fmt_price(tec.get('resistencia'))}</td><td></td></tr>
</table>
<h2>Valuación</h2>
<table><tr><th>Métrica</th><th>Valor</th></tr>
<tr><td>PE Trailing</td><td>{val.get('pe_trailing','N/A')}</td></tr>
<tr><td>PE Forward</td><td>{val.get('pe_forward','N/A')}</td></tr>
<tr><td>Precio Objetivo Analistas</td><td>{fmt_price(val.get('precio_objetivo'))}</td></tr>
<tr><td>Upside vs Target</td><td>{fmt_pct(val.get('upside_pct'))}</td></tr>
<tr><td>Recomendación</td><td>{val.get('recomendacion','N/A')}</td></tr>
<tr><td>N° Analistas</td><td>{val.get('num_analistas','N/A')}</td></tr>
</table>
<h2>Salud Financiera</h2>
<table><tr><th>Métrica</th><th>Valor</th></tr>
<tr><td>Margen Bruto</td><td>{fmt_pct_mult(sal.get('margen_bruto'))}</td></tr>
<tr><td>Margen Neto</td><td>{fmt_pct_mult(sal.get('margen_neto'))}</td></tr>
<tr><td>ROE</td><td>{fmt_pct_mult(sal.get('roe'))}</td></tr>
<tr><td>Deuda/Capital</td><td>{sal.get('deuda_capital','N/A')}</td></tr>
<tr><td>Crecimiento Ingresos</td><td>{fmt_pct_mult(sal.get('crecimiento_ingresos'))}</td></tr>
<tr><td>Crecimiento Ganancias</td><td>{fmt_pct_mult(sal.get('crecimiento_ganancias'))}</td></tr>
<tr><td>Beta</td><td>{sal.get('beta','N/A')}</td></tr>
<tr><td>Máx. 52 semanas</td><td>{fmt_price(sal.get('52w_max'))}</td></tr>
<tr><td>Mín. 52 semanas</td><td>{fmt_price(sal.get('52w_min'))}</td></tr>
</table>
<p class="footer">Jarvis &#x2014; Sector: {data.get('sector','N/A')} | {data.get('industria','N/A')}</p>
</body></html>"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar reporte HTML")
    parser.add_argument("--type", choices=["portfolio", "market", "company", "opportunities"],
                        required=True)
    parser.add_argument("--ticker", help="Para --type company")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--list", dest="lista", default="tech", help="Para --type opportunities")
    args = parser.parse_args()

    reports_dir = Path("jarvis/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.type == "portfolio":
        data = run_script("portfolio_tracker.py")
        html = build_portfolio_report(data or {})
        filename = f"reporte_portfolio_{fecha_str}.html"

    elif args.type == "market":
        data = run_script("market_briefing.py")
        html = build_market_report(data or {})
        filename = f"reporte_mercado_{fecha_str}.html"

    elif args.type == "company":
        if not args.ticker:
            print("Error: --ticker requerido para --type company", file=sys.stderr)
            sys.exit(1)
        html = build_company_report(args.ticker, args.period)
        filename = f"reporte_{args.ticker.upper()}_{fecha_str}.html"

    elif args.type == "opportunities":
        data = run_script("scan_opportunities.py", "--list", args.lista, "--top", "5")
        html = f"<html><body style='background:#1a1a2e;color:#eee;font-family:Arial'><pre>{json.dumps(data, ensure_ascii=False, indent=2)}</pre></body></html>"
        filename = f"reporte_oportunidades_{args.lista}_{fecha_str}.html"

    output_path = reports_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(str(output_path))
