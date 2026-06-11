import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_sentiment_label(score):
    if score >= 0.35:
        return "Alcista"
    elif score >= 0.15:
        return "Levemente alcista"
    elif score > -0.15:
        return "Neutral"
    elif score > -0.35:
        return "Levemente bajista"
    else:
        return "Bajista"


def fetch_alpha_vantage(ticker, limit=15, days=90):
    api_key = os.getenv("ALPHA_VANTAGE_KEY", "").strip()
    if not api_key:
        return None

    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y%m%dT0000")

    if ticker.upper() == "MARKET":
        topics = "economy_macro,finance,earnings,ipo"
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=NEWS_SENTIMENT&topics={topics}"
            f"&apikey={api_key}&limit={limit}&time_from={date_from}&sort=LATEST"
        )
    else:
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=NEWS_SENTIMENT&tickers={ticker.upper()}"
            f"&apikey={api_key}&limit={limit}&time_from={date_from}&sort=LATEST"
        )

    try:
        response = requests.get(url, timeout=15)
        data = response.json()
    except Exception:
        return None

    if "feed" not in data:
        return None

    noticias = []
    for item in data["feed"][:limit]:
        score = float(item.get("overall_sentiment_score", 0))
        raw_date = item.get("time_published", "")
        try:
            fecha = datetime.strptime(raw_date[:8], "%Y%m%d").strftime("%d/%m/%Y")
        except Exception:
            fecha = "[fecha no disponible]"

        noticias.append({
            "fecha": fecha,
            "titulo": item.get("title", ""),
            "fuente": item.get("source", ""),
            "url": item.get("url", ""),
            "sentiment": get_sentiment_label(score),
            "sentiment_score": round(score, 3),
            "resumen": item.get("summary", "")[:300],
        })

    return noticias


def fetch_yahoo_news(ticker):
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker.upper())
        news = stock.news or []
        noticias = []
        for item in news[:15]:
            ts = item.get("providerPublishTime")
            fecha = datetime.fromtimestamp(ts).strftime("%d/%m/%Y") if ts else "[fecha no disponible]"
            noticias.append({
                "fecha": fecha,
                "titulo": item.get("title", ""),
                "fuente": item.get("publisher", "Yahoo Finance"),
                "url": item.get("link", ""),
                "sentiment": "Neutral",
                "sentiment_score": 0.0,
                "resumen": "",
            })
        return noticias
    except Exception:
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obtener noticias con sentimiento")
    parser.add_argument("ticker", help="Ticker o MARKET")
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--days", type=int, default=90)
    args = parser.parse_args()

    noticias = fetch_alpha_vantage(args.ticker, args.limit, args.days)
    fuente_usada = "Alpha Vantage"

    if not noticias:
        print("[INFO] Alpha Vantage no disponible — usando Yahoo Finance.", file=sys.stderr)
        noticias = fetch_yahoo_news(args.ticker)
        fuente_usada = "Yahoo Finance"

    alcistas = sum(1 for n in noticias if n["sentiment"] == "Alcista")
    lev_alcistas = sum(1 for n in noticias if n["sentiment"] == "Levemente alcista")
    neutrales = sum(1 for n in noticias if n["sentiment"] == "Neutral")
    lev_bajistas = sum(1 for n in noticias if n["sentiment"] == "Levemente bajista")
    bajistas = sum(1 for n in noticias if n["sentiment"] == "Bajista")

    resultado = {
        "ticker": args.ticker.upper(),
        "fuente": fuente_usada,
        "total": len(noticias),
        "resumen_sentimiento": {
            "alcistas": alcistas,
            "lev_alcistas": lev_alcistas,
            "neutrales": neutrales,
            "lev_bajistas": lev_bajistas,
            "bajistas": bajistas,
        },
        "noticias": noticias,
    }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
