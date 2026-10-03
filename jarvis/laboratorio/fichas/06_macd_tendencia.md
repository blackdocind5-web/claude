# Ficha 06_macd_tendencia

**06 - Cruce MACD a favor de la tendencia**

| Campo | Detalle |
|---|---|
| Tipo | Tendencia |
| Archivo Pine | `estrategias/06_macd_tendencia.pine` |
| Timeframe sugerido | M15 / H1 |
| Mercados a probar | Oro, índices, forex mayor |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
El cruce del MACD a favor de la EMA200 filtra señales contra-tendencia y mejora el acierto del cruce simple.

## Reglas
- **Señal**: Cruce de la línea MACD con su señal, solo a favor de la EMA de tendencia.
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Mercados laterales; señal más lenta que el cruce de EMAs.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
