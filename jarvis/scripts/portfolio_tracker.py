import json
import sys
import yfinance as yf
from datetime import datetime
from pathlib import Path


def get_precio(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty:
            return None, None
        precio = round(hist["Close"].iloc[-1], 2)
        var = round(
            (hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
            / hist["Close"].iloc[-2] * 100, 2
        ) if len(hist) > 1 else 0
        return precio, var
    except Exception:
        return None, None


if __name__ == "__main__":
    positions_path = Path("jarvis/portfolio/active_positions.json")
    try:
        with open(positions_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: active_positions.json no encontrado", file=sys.stderr)
        sys.exit(1)

    positions = data.get("positions", [])
    if not positions:
        print(json.dumps({
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "mensaje": "No hay posiciones en cartera.",
            "posiciones": [],
            "resumen": None,
        }, ensure_ascii=False, indent=2))
        sys.exit(0)

    total_invertido = 0
    total_actual = 0
    resultados = []

    for pos in positions:
        ticker = pos.get("ticker", "").upper()
        qty = pos.get("quantity", 0)
        buy_price = pos.get("avg_buy_price", 0)

        precio_actual, variacion_dia = get_precio(ticker)
        if precio_actual is None:
            precio_actual = buy_price
            variacion_dia = 0

        invertido = round(qty * buy_price, 2)
        valor_actual = round(qty * precio_actual, 2)
        pnl = round(valor_actual - invertido, 2)
        pnl_pct = round((pnl / invertido) * 100, 2) if invertido else 0

        total_invertido += invertido
        total_actual += valor_actual

        resultados.append({
            "ticker": ticker,
            "cantidad": qty,
            "precio_compra": buy_price,
            "precio_actual": precio_actual,
            "variacion_dia_pct": variacion_dia,
            "invertido": invertido,
            "valor_actual": valor_actual,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "tipo": pos.get("type", "stock"),
            "notas": pos.get("notes", ""),
        })

    pnl_total = round(total_actual - total_invertido, 2)
    pnl_total_pct = round((pnl_total / total_invertido) * 100, 2) if total_invertido else 0

    mejor = max(resultados, key=lambda x: x["pnl_pct"]) if resultados else None
    peor = min(resultados, key=lambda x: x["pnl_pct"]) if resultados else None

    resultado = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "posiciones": resultados,
        "resumen": {
            "total_invertido": round(total_invertido, 2),
            "valor_actual": round(total_actual, 2),
            "pnl_total": pnl_total,
            "pnl_total_pct": pnl_total_pct,
            "num_posiciones": len(resultados),
            "mejor_posicion": {"ticker": mejor["ticker"], "pnl_pct": mejor["pnl_pct"]} if mejor else None,
            "peor_posicion": {"ticker": peor["ticker"], "pnl_pct": peor["pnl_pct"]} if peor else None,
        },
    }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
