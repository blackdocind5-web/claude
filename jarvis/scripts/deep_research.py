import argparse
import json
import sys


TEMPLATES = {
    "company": [
        "{subject} latest news earnings revenue 2025 2026",
        "{subject} analyst price target upgrade downgrade rating",
        "{subject} CEO guidance outlook quarterly results",
        "{subject} competitive threats risks opportunities",
        "{subject} institutional investors insider trading SEC filing",
    ],
    "macro": [
        "{subject} latest update Federal Reserve 2025 2026",
        "{subject} impact on stock market S&P 500 investors",
        "{subject} economic data analysis forecast",
        "{subject} central bank policy rate decision",
    ],
    "sector": [
        "{subject} sector ETF performance analysis 2025 2026",
        "{subject} top stocks opportunities momentum",
        "{subject} sector outlook analysts forecast",
        "{subject} trends disruption innovation leaders",
    ],
    "news": [
        "{subject} latest news analysis financial impact",
        "{subject} market reaction stocks affected",
        "{subject} analyst reaction investor sentiment",
        "{subject} timeline developments 2025 2026",
    ],
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar queries para deep research web")
    parser.add_argument("--ticker", help="Ticker de empresa (para --type company)")
    parser.add_argument("--topic", help="Tema de investigación")
    parser.add_argument("--type", choices=["company", "macro", "sector", "news"],
                        default="company")
    args = parser.parse_args()

    if args.type == "company" and args.ticker:
        subject = args.ticker.upper()
    elif args.topic:
        subject = args.topic
    else:
        print("Error: especificá --ticker o --topic", file=sys.stderr)
        sys.exit(1)

    queries = [q.format(subject=subject) for q in TEMPLATES[args.type]]

    resultado = {
        "tipo": args.type,
        "sujeto": subject,
        "instruccion": (
            "Ejecutá cada query con WebSearch y sintetizá los resultados. "
            "Filtrá ruido, identificá el impacto (alcista/bajista/neutro) "
            "y dá una conclusión accionable con fecha de cada fuente."
        ),
        "queries": queries,
    }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
