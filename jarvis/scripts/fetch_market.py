import argparse
import json
import sys
import yfinance as yf
from datetime import datetime


def fetch_market(ticker, period="6mo", show_info=False, no_history=False):
    stock = yf.Ticker(ticker.upper())
    result = {"ticker": ticker.upper()}

    if show_info:
        try:
            info = stock.info
            result["info"] = {
                "nombre": info.get("longName") or info.get("shortName", ticker.upper()),
                "sector": info.get("sector", "N/A"),
                "industria": info.get("industry", "N/A"),
                "precio_actual": info.get("currentPrice") or info.get("regularMarketPrice"),
                "pe_trailing": info.get("trailingPE"),
                "pe_forward": info.get("forwardPE"),
                "precio_objetivo": info.get("targetMeanPrice"),
                "recomendacion": info.get("recommendationKey", "N/A"),
                "num_analistas": info.get("numberOfAnalystOpinions"),
                "market_cap": info.get("marketCap"),
                "dividendo": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52w_max": info.get("fiftyTwoWeekHigh"),
                "52w_min": info.get("fiftyTwoWeekLow"),
                "margen_bruto": info.get("grossMargins"),
                "margen_neto": info.get("profitMargins"),
                "roe": info.get("returnOnEquity"),
                "deuda_capital": info.get("debtToEquity"),
                "crecimiento_ingresos": info.get("revenueGrowth"),
                "crecimiento_ganancias": info.get("earningsGrowth"),
            }
        except Exception as e:
            result["info_error"] = str(e)

    if not no_history:
        try:
            hist = stock.history(period=period)
            if not hist.empty:
                result["historia"] = {
                    "fechas": [d.strftime("%d/%m/%Y") for d in hist.index],
                    "apertura": [round(v, 2) for v in hist["Open"]],
                    "maximo": [round(v, 2) for v in hist["High"]],
                    "minimo": [round(v, 2) for v in hist["Low"]],
                    "cierre": [round(v, 2) for v in hist["Close"]],
                    "volumen": [int(v) for v in hist["Volume"]],
                }
                result["precio_actual"] = round(hist["Close"].iloc[-1], 2)
                if len(hist) > 1:
                    result["variacion_dia"] = round(
                        (hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                        / hist["Close"].iloc[-2] * 100, 2,
                    )
                else:
                    result["variacion_dia"] = 0
        except Exception as e:
            result["historia_error"] = str(e)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obtener datos de mercado via Yahoo Finance")
    parser.add_argument("ticker", help="Símbolo del ticker (ej: AAPL, NVDA, BTC-USD)")
    parser.add_argument("--period", default="6mo",
                        help="Período: 1d 5d 1mo 3mo 6mo 1y 2y 5y (default: 6mo)")
    parser.add_argument("--info", action="store_true", help="Incluir info y fundamentals")
    parser.add_argument("--no-history", action="store_true", help="Omitir historial de precios")
    args = parser.parse_args()

    data = fetch_market(args.ticker, args.period, args.info, args.no_history)
    print(json.dumps(data, ensure_ascii=False, indent=2))
