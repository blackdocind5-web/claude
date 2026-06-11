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
    return sum(precios[-periodo:]) / periodo


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


def score_ticker(ticker):
    data = run_script("fetch_market.py", ticker, "--period", "6mo", "--info")
    if not data:
        return None

    info = data.get("info", {})
    historia = data.get("historia", {})
    cierres = historia.get("cierre", [])
    precio = data.get("precio_actual")

    if not precio or not cierres:
        return None

    score = 50
    senales = []

    ma20 = calcular_ma(cierres, 20)
    ma50 = calcular_ma(cierres, 50)
    rsi = calcular_rsi(cierres)

    if ma20 and precio > ma20:
        score += 10
        senales.append("precio > MA20")
    if ma50 and precio > ma50:
        score += 10
        senales.append("precio > MA50")
    if rsi and 30 < rsi < 70:
        score += 5
        senales.append(f"RSI neutro ({rsi})")
    elif rsi and rsi < 35:
        score += 15
        senales.append(f"RSI sobrevendido ({rsi}) — oportunidad")

    target = info.get("precio_objetivo")
    upside = None
    if target and isinstance(target, (int, float)):
        upside = round((target - precio) / precio * 100, 1)
        if upside > 20:
            score += 15
            senales.append(f"upside {upside}% vs target analistas")
        elif upside > 10:
            score += 8
            senales.append(f"upside {upside}% vs target analistas")

    if len(cierres) >= 5:
        momentum_5d = round((cierres[-1] - cierres[-5]) / cierres[-5] * 100, 1)
        if 0 < momentum_5d < 5:
            score += 5
            senales.append(f"momentum +{momentum_5d}% (5d)")

    return {
        "ticker": ticker,
        "nombre": info.get("nombre", ticker),
        "precio": precio,
        "variacion_dia": data.get("variacion_dia", 0),
        "score": min(score, 100),
        "senales": senales,
        "upside_pct": upside,
        "recomendacion": info.get("recomendacion"),
        "sector": info.get("sector"),
        "rsi": rsi,
        "pe_forward": info.get("pe_forward"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scanner de oportunidades")
    parser.add_argument("--list", default="tech", dest="lista",
                        help="Lista: tech, etfs, latam, macro, custom")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    watchlist_path = Path("jarvis/portfolio/watchlist.json")
    try:
        with open(watchlist_path) as f:
            watchlist = json.load(f)
    except FileNotFoundError:
        print("Error: watchlist.json no encontrado", file=sys.stderr)
        sys.exit(1)

    tickers = watchlist.get("lists", {}).get(args.lista, [])
    if not tickers:
        print(f"Error: lista '{args.lista}' vacía o no encontrada", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Escaneando {len(tickers)} tickers en lista '{args.lista}'...", file=sys.stderr)

    resultados = []
    for ticker in tickers:
        print(f"  -> {ticker}", file=sys.stderr)
        r = score_ticker(ticker)
        if r:
            resultados.append(r)

    resultados.sort(key=lambda x: x["score"], reverse=True)

    print(json.dumps({
        "lista": args.lista,
        "total_escaneados": len(resultados),
        "top": resultados[:args.top],
    }, ensure_ascii=False, indent=2))
