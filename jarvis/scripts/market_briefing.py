import json
import sys
import yfinance as yf
from datetime import datetime


INDICES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
}

SECTORES = {
    "Tecnología": "XLK",
    "Salud": "XLV",
    "Financiero": "XLF",
    "Consumo Discrecional": "XLY",
    "Consumo Básico": "XLP",
    "Energía": "XLE",
    "Materiales": "XLB",
    "Industriales": "XLI",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Comunicaciones": "XLC",
}

MACRO = {
    "Oro": "GLD",
    "Petróleo": "USO",
    "Dólar Index": "UUP",
    "Bonos 20Y": "TLT",
    "Bitcoin": "BTC-USD",
    "Yield 10Y": "^TNX",
    "Yield 2Y": "^IRX",
}


def get_variacion(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if len(hist) < 2:
            return None, None
        precio = round(hist["Close"].iloc[-1], 2)
        variacion = round(
            (hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
            / hist["Close"].iloc[-2] * 100, 2
        )
        return precio, variacion
    except Exception:
        return None, None


if __name__ == "__main__":
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    indices = {}
    for nombre, ticker in INDICES.items():
        precio, var = get_variacion(ticker)
        indices[nombre] = {"precio": precio, "variacion": var}

    sectores = {}
    for nombre, ticker in SECTORES.items():
        precio, var = get_variacion(ticker)
        sectores[nombre] = {"precio": precio, "variacion": var}

    macro = {}
    for nombre, ticker in MACRO.items():
        precio, var = get_variacion(ticker)
        macro[nombre] = {"precio": precio, "variacion": var}

    vix = indices.get("VIX", {}).get("precio")
    if vix:
        if vix < 15:
            vix_senal = "baja volatilidad — mercado confiado"
        elif vix < 25:
            vix_senal = "volatilidad moderada — precaución"
        elif vix < 35:
            vix_senal = "alta volatilidad — miedo en el mercado"
        else:
            vix_senal = "volatilidad extrema — pánico"
    else:
        vix_senal = "N/A"

    sectores_con_var = {k: v for k, v in sectores.items() if v["variacion"] is not None}
    mejor_sector = max(sectores_con_var, key=lambda k: sectores_con_var[k]["variacion"]) if sectores_con_var else None
    peor_sector = min(sectores_con_var, key=lambda k: sectores_con_var[k]["variacion"]) if sectores_con_var else None

    yield_10y = macro.get("Yield 10Y", {}).get("precio")
    yield_2y = macro.get("Yield 2Y", {}).get("precio")
    if yield_10y and yield_2y:
        spread = round(yield_10y - yield_2y, 2)
        curva_invertida = spread < 0
    else:
        spread = None
        curva_invertida = None

    sp500_var = indices.get("S&P 500", {}).get("variacion")
    if sp500_var is not None:
        if sp500_var > 1:
            sentimiento = "alcista fuerte"
        elif sp500_var > 0:
            sentimiento = "levemente alcista"
        elif sp500_var > -1:
            sentimiento = "levemente bajista"
        else:
            sentimiento = "bajista fuerte"
    else:
        sentimiento = "neutral"

    resultado = {
        "fecha": fecha,
        "sentimiento_general": sentimiento,
        "indices": indices,
        "sectores": sectores,
        "mejor_sector": mejor_sector,
        "peor_sector": peor_sector,
        "macro": macro,
        "vix": {
            "valor": vix,
            "interpretacion": vix_senal,
        },
        "yield_curve": {
            "yield_10y": yield_10y,
            "yield_2y": yield_2y,
            "spread": spread,
            "invertida": curva_invertida,
        },
    }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
