import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_script(script, *args):
    cmd = [sys.executable, str(Path("jarvis/scripts") / script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except Exception:
        return None


def calcular_ma(precios, periodo):
    if len(precios) < periodo:
        return None
    return round(sum(precios[-periodo:]) / periodo, 2)


def calcular_rsi(precios, periodos=14):
    if len(precios) < periodos + 1:
        return None
    cambios = [precios[i] - precios[i - 1] for i in range(1, len(precios))]
    recientes = cambios[-periodos:]
    ganancias = [c for c in recientes if c > 0]
    perdidas = [abs(c) for c in recientes if c < 0]
    avg_g = sum(ganancias) / periodos if ganancias else 0
    avg_p = sum(perdidas) / periodos if perdidas else 0
    if avg_p == 0:
        return 100.0
    rs = avg_g / avg_p
    return round(100 - (100 / (1 + rs)), 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis completo de empresa")
    parser.add_argument("ticker")
    parser.add_argument("--period", default="1y")
    args = parser.parse_args()

    ticker = args.ticker.upper()

    data = run_script("fetch_market.py", ticker, "--period", args.period, "--info")
    if not data:
        print(f"Error: no se pudo obtener datos para {ticker}", file=sys.stderr)
        sys.exit(1)

    info = data.get("info", {})
    historia = data.get("historia", {})
    cierres = historia.get("cierre", [])
    precio = data.get("precio_actual") or info.get("precio_actual")

    ma20 = calcular_ma(cierres, 20)
    ma50 = calcular_ma(cierres, 50)
    ma200 = calcular_ma(cierres, 200)
    rsi = calcular_rsi(cierres)
    soporte = round(min(cierres[-20:]), 2) if len(cierres) >= 20 else None
    resistencia = round(max(cierres[-20:]), 2) if len(cierres) >= 20 else None

    if precio and ma20:
        if precio > ma20:
            tendencia = "alcista"
            senal_ma = "precio por encima de MA20 — señal positiva"
        else:
            tendencia = "bajista"
            senal_ma = "precio por debajo de MA20 — señal negativa"
    else:
        tendencia = "neutral"
        senal_ma = "datos insuficientes"

    if rsi:
        if rsi > 70:
            senal_rsi = "sobrecomprado"
        elif rsi < 30:
            senal_rsi = "sobrevendido"
        else:
            senal_rsi = "neutral"
    else:
        senal_rsi = "N/A"

    target = info.get("precio_objetivo")
    upside = None
    if target and precio and isinstance(target, (int, float)) and isinstance(precio, (int, float)):
        upside = round((target - precio) / precio * 100, 1)

    noticias_data = run_script("fetch_news.py", ticker, "--limit", "10", "--days", "90")

    run_script("chart_generator.py", ticker, "--period", args.period, "--type", "candlestick")

    resultado = {
        "ticker": ticker,
        "nombre": info.get("nombre", ticker),
        "precio_actual": precio,
        "variacion_dia": data.get("variacion_dia", 0),
        "tendencia": tendencia,
        "tecnico": {
            "ma20": ma20,
            "ma50": ma50,
            "ma200": ma200,
            "rsi": rsi,
            "senal_ma": senal_ma,
            "senal_rsi": senal_rsi,
            "soporte": soporte,
            "resistencia": resistencia,
        },
        "valuacion": {
            "pe_trailing": info.get("pe_trailing"),
            "pe_forward": info.get("pe_forward"),
            "precio_objetivo": target,
            "upside_pct": upside,
            "recomendacion": info.get("recomendacion"),
            "num_analistas": info.get("num_analistas"),
        },
        "salud": {
            "margen_bruto": info.get("margen_bruto"),
            "margen_neto": info.get("margen_neto"),
            "roe": info.get("roe"),
            "deuda_capital": info.get("deuda_capital"),
            "crecimiento_ingresos": info.get("crecimiento_ingresos"),
            "crecimiento_ganancias": info.get("crecimiento_ganancias"),
            "beta": info.get("beta"),
            "52w_max": info.get("52w_max"),
            "52w_min": info.get("52w_min"),
        },
        "sector": info.get("sector"),
        "industria": info.get("industria"),
        "noticias": noticias_data,
        "grafico": f"jarvis/charts/{ticker}_{args.period}_candlestick.html",
    }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
