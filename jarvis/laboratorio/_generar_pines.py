#!/usr/bin/env python3
"""Genera el paquete de estrategias Pine v5 (un .pine por estrategia).

Todas comparten el MISMO bloque de riesgo, costos y filtro horario, para que
la comparación en el Strategy Tester sea justa: lo único que cambia entre
archivos es la señal de entrada.

Uso:  python jarvis/laboratorio/_generar_pines.py
"""
from pathlib import Path

SALIDA = Path(__file__).parent / "estrategias"

CABECERA = """//@version=5
// ============================================================================
// {nombre}
// {descripcion}
// Timeframe sugerido: {tf}
//
// Paquete de prueba Jarvis -- modelo de riesgo idéntico en todas las
// estrategias (riesgo fijo en % del equity, stop por ATR, TP por R:R) para
// poder compararlas de igual a igual. Sin garantías: es una herramienta de
// investigación, no una recomendación de inversión.
// ============================================================================
strategy("{titulo}", shorttitle="{corto}", overlay=true,
     initial_capital=10000, pyramiding=1, calc_on_every_tick=false,
     process_orders_on_close=false, margin_long=0, margin_short=0,
     commission_type=strategy.commission.percent, commission_value=0.01,
     slippage=2)

// --- Gestión de riesgo (común a todo el paquete) ----------------------------
grpR = "Gestión de riesgo"
riesgoPct = input.float(1.0, "Riesgo por operación (% del equity)", minval=0.1, step=0.1, group=grpR)
atrLen    = input.int(14, "ATR período", minval=1, group=grpR)
slMult    = input.float(1.5, "Stop = ATR ×", minval=0.1, step=0.1, group=grpR)
rr        = input.float(1.5, "Ratio R:R (TP = distancia del stop × R:R)", minval=0.1, step=0.1, group=grpR)
permitirLargos = input.bool(true, "Permitir largos", group=grpR)
permitirCortos = input.bool(true, "Permitir cortos", group=grpR)

// --- Filtro horario (común) --------------------------------------------------
grpS = "Filtro horario"
usarSesion = input.bool(false, "Operar solo dentro de la sesión", group=grpS)
sesion     = input.session("0700-1100", "Sesión (hora de Nueva York)", group=grpS)
enSesionNY = not na(time(timeframe.period, sesion, "America/New_York"))
dentroSesion = not usarSesion or enSesionNY

atr = ta.atr(atrLen)

// --- Parámetros propios de la estrategia -------------------------------------
{inputs}

// --- Señales ----------------------------------------------------------------
{calculo}

// --- Ejecución (idéntica en todo el paquete) ------------------------------------
sinPosicion = strategy.position_size == 0
if senalLarga and sinPosicion and dentroSesion and permitirLargos and not na(atr)
    distancia = atr * slMult
    cantidad = (strategy.equity * riesgoPct / 100) / distancia
    if cantidad > 0
        strategy.entry("Largo", strategy.long, qty=cantidad)
        strategy.exit("Largo SL/TP", "Largo", stop=close - distancia, limit=close + distancia * rr)

if senalCorta and sinPosicion and dentroSesion and permitirCortos and not na(atr)
    distancia = atr * slMult
    cantidad = (strategy.equity * riesgoPct / 100) / distancia
    if cantidad > 0
        strategy.entry("Corto", strategy.short, qty=cantidad)
        strategy.exit("Corto SL/TP", "Corto", stop=close + distancia, limit=close - distancia * rr)

// --- Visualización ---------------------------------------------------------------
{plots}
"""

ESTRATEGIAS = [
    {
        "id": "01_cruce_ema",
        "nombre": "01 - Cruce de EMAs con filtro de tendencia",
        "corto": "TV01 Cruce EMA",
        "descripcion": "Cruce de EMA rápida/lenta a favor de la EMA de tendencia (seguimiento de tendencia).",
        "tf": "M15 / H1",
        "inputs": """grpE = "Cruce de EMAs"
emaRapidaLen = input.int(9, "EMA rápida", minval=1, group=grpE)
emaLentaLen  = input.int(21, "EMA lenta", minval=2, group=grpE)
emaTendLen   = input.int(200, "EMA de tendencia", minval=2, group=grpE)""",
        "calculo": """emaRapida = ta.ema(close, emaRapidaLen)
emaLenta  = ta.ema(close, emaLentaLen)
emaTend   = ta.ema(close, emaTendLen)
senalLarga = ta.crossover(emaRapida, emaLenta) and close > emaTend
senalCorta = ta.crossunder(emaRapida, emaLenta) and close < emaTend""",
        "plots": """plot(emaRapida, "EMA rápida", color=color.new(color.blue, 0))
plot(emaLenta, "EMA lenta", color=color.new(color.orange, 0))
plot(emaTend, "EMA tendencia", color=color.new(color.gray, 0), linewidth=2)""",
    },
    {
        "id": "02_rsi_reversion",
        "nombre": "02 - Reversión por RSI a favor de la tendencia",
        "corto": "TV02 RSI",
        "descripcion": "Compra cuando el RSI sale de sobreventa en tendencia alcista (y vende al revés).",
        "tf": "M15 / H1",
        "inputs": """grpE = "RSI"
rsiLen     = input.int(14, "RSI período", minval=2, group=grpE)
rsiSobreV  = input.int(30, "Nivel de sobreventa", minval=1, maxval=50, group=grpE)
rsiSobreC  = input.int(70, "Nivel de sobrecompra", minval=50, maxval=99, group=grpE)
emaTendLen = input.int(200, "EMA de tendencia", minval=2, group=grpE)""",
        "calculo": """rsi     = ta.rsi(close, rsiLen)
emaTend = ta.ema(close, emaTendLen)
senalLarga = ta.crossover(rsi, rsiSobreV) and close > emaTend
senalCorta = ta.crossunder(rsi, rsiSobreC) and close < emaTend""",
        "plots": """plot(emaTend, "EMA tendencia", color=color.new(color.gray, 0), linewidth=2)""",
    },
    {
        "id": "03_bollinger_reversion",
        "nombre": "03 - Reversión en Bandas de Bollinger",
        "corto": "TV03 Bollinger",
        "descripcion": "Entra cuando el precio vuelve a entrar a la banda tras cerrar fuera de ella (reversión a la media).",
        "tf": "M5 / M15",
        "inputs": """grpE = "Bandas de Bollinger"
bbLen  = input.int(20, "Período", minval=2, group=grpE)
bbMult = input.float(2.0, "Desvíos", minval=0.5, step=0.1, group=grpE)""",
        "calculo": """[bbMedia, bbSup, bbInf] = ta.bb(close, bbLen, bbMult)
senalLarga = close[1] < bbInf[1] and close > bbInf
senalCorta = close[1] > bbSup[1] and close < bbSup""",
        "plots": """plot(bbMedia, "Media", color=color.new(color.gray, 0))
plot(bbSup, "Banda superior", color=color.new(color.red, 0))
plot(bbInf, "Banda inferior", color=color.new(color.green, 0))""",
    },
    {
        "id": "04_breakout_donchian",
        "nombre": "04 - Ruptura de canal Donchian",
        "corto": "TV04 Donchian",
        "descripcion": "Entra en la ruptura del máximo/mínimo de las últimas N velas (momentum / breakout).",
        "tf": "M15 / H1 / H4",
        "inputs": """grpE = "Canal Donchian"
donLen = input.int(20, "Velas del canal", minval=2, group=grpE)""",
        "calculo": """donAlto = ta.highest(high, donLen)[1]
donBajo = ta.lowest(low, donLen)[1]
senalLarga = close > donAlto
senalCorta = close < donBajo""",
        "plots": """plot(donAlto, "Máximo del canal", color=color.new(color.green, 0))
plot(donBajo, "Mínimo del canal", color=color.new(color.red, 0))""",
    },
    {
        "id": "05_supertrend",
        "nombre": "05 - Supertrend",
        "corto": "TV05 Supertrend",
        "descripcion": "Entra en cada cambio de dirección del Supertrend (seguimiento de tendencia).",
        "tf": "M15 / H1",
        "inputs": """grpE = "Supertrend"
stFactor = input.float(3.0, "Factor", minval=0.5, step=0.1, group=grpE)
stLen    = input.int(10, "ATR período", minval=1, group=grpE)""",
        "calculo": """[stValor, stDir] = ta.supertrend(stFactor, stLen)
senalLarga = ta.change(stDir) < 0
senalCorta = ta.change(stDir) > 0""",
        "plots": """plot(stValor, "Supertrend", color=stDir < 0 ? color.green : color.red, linewidth=2)""",
    },
    {
        "id": "06_macd_tendencia",
        "nombre": "06 - Cruce MACD a favor de la tendencia",
        "corto": "TV06 MACD",
        "descripcion": "Cruce de la línea MACD con su señal, solo a favor de la EMA de tendencia.",
        "tf": "M15 / H1",
        "inputs": """grpE = "MACD"
macdRapida = input.int(12, "EMA rápida", minval=1, group=grpE)
macdLenta  = input.int(26, "EMA lenta", minval=2, group=grpE)
macdSenal  = input.int(9, "Señal", minval=1, group=grpE)
emaTendLen = input.int(200, "EMA de tendencia", minval=2, group=grpE)""",
        "calculo": """[macdLinea, macdSen, macdHist] = ta.macd(close, macdRapida, macdLenta, macdSenal)
emaTend = ta.ema(close, emaTendLen)
senalLarga = ta.crossover(macdLinea, macdSen) and close > emaTend
senalCorta = ta.crossunder(macdLinea, macdSen) and close < emaTend""",
        "plots": """plot(emaTend, "EMA tendencia", color=color.new(color.gray, 0), linewidth=2)""",
    },
    {
        "id": "07_rango_apertura",
        "nombre": "07 - Ruptura del rango de apertura (Opening Range)",
        "corto": "TV07 ORB",
        "descripcion": "Marca el rango de los primeros minutos de la sesión y opera la ruptura (una operación por día).",
        "tf": "M1 / M5",
        "inputs": """grpE = "Rango de apertura"
tzOR       = input.string("America/New_York", "Zona horaria", group=grpE)
rangoOR    = input.session("0800-0830", "Ventana que define el rango", group=grpE)
ventanaOp  = input.session("0830-1100", "Ventana para operar la ruptura", group=grpE)""",
        "calculo": """inOR = not na(time(timeframe.period, rangoOR, tzOR))
inOp = not na(time(timeframe.period, ventanaOp, tzOR))
var float orAlto = na
var float orBajo = na
var bool operoHoy = false
if inOR and not inOR[1]
    orAlto := high
    orBajo := low
    operoHoy := false
else if inOR
    orAlto := math.max(orAlto, high)
    orBajo := math.min(orBajo, low)
senalLarga = inOp and not operoHoy and not na(orAlto) and close > orAlto
senalCorta = inOp and not operoHoy and not na(orBajo) and close < orBajo
if (senalLarga or senalCorta) and strategy.position_size == 0
    operoHoy := true""",
        "plots": """plot(inOp ? orAlto : na, "Máximo del rango", color=color.new(color.green, 0), style=plot.style_linebr)
plot(inOp ? orBajo : na, "Mínimo del rango", color=color.new(color.red, 0), style=plot.style_linebr)
bgcolor(inOR ? color.new(color.gray, 85) : na)""",
    },
    {
        "id": "08_pullback_ema",
        "nombre": "08 - Pullback a la EMA en tendencia",
        "corto": "TV08 Pullback",
        "descripcion": "En tendencia (EMA50 vs EMA200) entra cuando el precio recupera la EMA20 tras un retroceso.",
        "tf": "M5 / M15",
        "inputs": """grpE = "Pullback a EMA"
emaPullLen = input.int(20, "EMA de pullback", minval=1, group=grpE)
emaMediaLen = input.int(50, "EMA media", minval=2, group=grpE)
emaTendLen  = input.int(200, "EMA de tendencia", minval=3, group=grpE)""",
        "calculo": """emaPull  = ta.ema(close, emaPullLen)
emaMedia = ta.ema(close, emaMediaLen)
emaTend  = ta.ema(close, emaTendLen)
senalLarga = emaMedia > emaTend and close[1] < emaPull[1] and close > emaPull
senalCorta = emaMedia < emaTend and close[1] > emaPull[1] and close < emaPull""",
        "plots": """plot(emaPull, "EMA pullback", color=color.new(color.blue, 0))
plot(emaMedia, "EMA media", color=color.new(color.orange, 0))
plot(emaTend, "EMA tendencia", color=color.new(color.gray, 0), linewidth=2)""",
    },
]

# Metadatos para las fichas del laboratorio (hipótesis y mercados donde tiene sentido probarla)
META = {
    "01_cruce_ema": ("Tendencia", "Las tendencias sostenidas dejan más ganancia que las pérdidas de los falsos cruces; la EMA200 filtra el contra-tendencia.", "Oro, índices, forex mayor", "Mercados laterales: muchos cruces falsos (whipsaw) y pérdidas seguidas."),
    "02_rsi_reversion": ("Reversión", "Dentro de una tendencia, los retrocesos extremos del RSI tienden a revertir hacia la tendencia.", "Índices, acciones líquidas, oro", "Tendencias muy fuertes: el RSI queda en sobreventa y sigue cayendo."),
    "03_bollinger_reversion": ("Reversión", "El precio que cierra fuera de la banda y vuelve a entrar tiende a regresar a la media.", "Forex mayor, oro en rango", "Rupturas con volatilidad creciente: la banda se expande y el precio la recorre."),
    "04_breakout_donchian": ("Ruptura", "Romper el máximo/mínimo reciente indica momentum que continúa; pocas ganancias grandes pagan muchas pérdidas chicas.", "Oro, Nasdaq, BTC", "Rangos con falsas rupturas; acierto bajo (esperable)."),
    "05_supertrend": ("Tendencia", "El cambio de dirección del Supertrend captura el inicio de tendencias sostenidas por volatilidad (ATR).", "Oro, índices, BTC", "Mercados laterales: señales contrarias consecutivas."),
    "06_macd_tendencia": ("Tendencia", "El cruce del MACD a favor de la EMA200 filtra señales contra-tendencia y mejora el acierto del cruce simple.", "Oro, índices, forex mayor", "Mercados laterales; señal más lenta que el cruce de EMAs."),
    "07_rango_apertura": ("Ruptura / sesión", "El rango de los primeros minutos de la sesión marca el sesgo del día; su ruptura tiene continuación.", "Oro, índices (sesión NY)", "Días sin catalizador: rango chico con ruptura falsa. Depende de la hora elegida."),
    "08_pullback_ema": ("Tendencia", "Entrar en el retroceso a una EMA corta dentro de tendencia da mejor precio y stop más corto que entrar en la ruptura.", "Oro, índices, forex mayor", "Cambios de tendencia: el pullback se convierte en reversión."),
}

FICHA = """# Ficha {id}

**{nombre}**

| Campo | Detalle |
|---|---|
| Tipo | {tipo} |
| Archivo Pine | `estrategias/{id}.pine` |
| Timeframe sugerido | {tf} |
| Mercados a probar | {mercados} |
| Creada | {fecha} |
| Estado | ver `CATALOGO.md` |

## Hipótesis
{hipotesis}

## Reglas
- **Señal**: {descripcion}
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
{falla}

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
"""

CATALOGO_ENCABEZADO = """# Catálogo de estrategias del laboratorio

Una fila por estrategia. **Es la única fuente de verdad del estado.** Etapas (ver `GUIA.md`):
`0 Idea` -> `1 Ficha` -> `2 Codificada` -> `3 Backtest` -> `4 Robustez` -> `5 Paper` -> `6 Real` | `Descartada`

| ID | Estrategia | Tipo | Timeframe | Estado | Última actualización | Nota |
|---|---|---|---|---|---|---|
"""


def main():
    from datetime import date
    hoy = date.today().strftime("%d/%m/%Y")
    SALIDA.mkdir(parents=True, exist_ok=True)
    FICHAS = SALIDA.parent / "fichas"
    FICHAS.mkdir(exist_ok=True)
    filas = []
    for e in ESTRATEGIAS:
        titulo = f"Jarvis | {e['nombre']}"
        codigo = CABECERA.format(
            nombre=e["nombre"], descripcion=e["descripcion"], tf=e["tf"],
            titulo=titulo, corto=e["corto"], inputs=e["inputs"],
            calculo=e["calculo"], plots=e["plots"],
        )
        (SALIDA / f"{e['id']}.pine").write_text(codigo, encoding="utf-8")
        print("generado:", f"{e['id']}.pine")

        tipo, hipotesis, mercados, falla = META[e["id"]]
        ficha = FICHAS / f"{e['id']}.md"
        if not ficha.exists():  # no pisar fichas que ya tienen aprendizajes anotados
            ficha.write_text(FICHA.format(id=e["id"], nombre=e["nombre"], tipo=tipo, tf=e["tf"],
                                          mercados=mercados, fecha=hoy, hipotesis=hipotesis,
                                          descripcion=e["descripcion"], falla=falla), encoding="utf-8")
            print("ficha nueva:", ficha.name)
        filas.append(f"| {e['id'][:2]} | [{e['nombre'][5:]}](fichas/{e['id']}.md) | {tipo} | {e['tf']} | 2 Codificada | {hoy} | Sin backtest |")

    catalogo = SALIDA.parent / "CATALOGO.md"
    if not catalogo.exists():  # el catálogo se edita a mano una vez creado
        catalogo.write_text(CATALOGO_ENCABEZADO + "\n".join(filas) + "\n", encoding="utf-8")
        print("catálogo creado")


if __name__ == "__main__":
    main()
