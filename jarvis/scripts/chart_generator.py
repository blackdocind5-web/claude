import argparse
import sys
from pathlib import Path

try:
    import plotly.graph_objects as go
    import yfinance as yf
except ImportError as e:
    print(f"Error: {e}. Instalá con: pip install plotly yfinance", file=sys.stderr)
    sys.exit(1)


def generate_chart(ticker, period="1y", chart_type="candlestick"):
    stock = yf.Ticker(ticker.upper())
    hist = stock.history(period=period)

    if hist.empty:
        print(f"Error: no hay datos para {ticker}", file=sys.stderr)
        sys.exit(1)

    fig = go.Figure()

    if chart_type == "candlestick":
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist["Open"],
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"],
            name=ticker.upper(),
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ))
    elif chart_type == "area":
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            fill="tozeroy",
            name=ticker.upper(),
            line=dict(color="#2196F3", width=2),
        ))
    else:
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            name=ticker.upper(),
            line=dict(color="#2196F3", width=2),
        ))

    if len(hist) >= 20:
        ma20 = hist["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=hist.index, y=ma20, name="MA20",
            line=dict(color="#FF9800", width=1.5, dash="dot")
        ))
    if len(hist) >= 50:
        ma50 = hist["Close"].rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=hist.index, y=ma50, name="MA50",
            line=dict(color="#9C27B0", width=1.5, dash="dot")
        ))

    precio_actual = round(hist["Close"].iloc[-1], 2)

    fig.update_layout(
        title=f"{ticker.upper()} — ${precio_actual:,.2f} | {period.upper()}",
        xaxis_title="Fecha",
        yaxis_title="Precio (USD)",
        template="plotly_dark",
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        font=dict(family="Arial", size=13),
    )

    charts_dir = Path("jarvis/charts")
    charts_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{ticker.upper()}_{period}_{chart_type}.html"
    output_path = charts_dir / filename
    fig.write_html(str(output_path))

    return str(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar gráfico interactivo Plotly")
    parser.add_argument("ticker")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--type", choices=["candlestick", "line", "area"],
                        default="candlestick", dest="chart_type")
    args = parser.parse_args()

    path = generate_chart(args.ticker, args.period, args.chart_type)
    print(f"Gráfico generado: {path}")
