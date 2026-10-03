# Ficha 05_supertrend

**05 - Supertrend**

| Campo | Detalle |
|---|---|
| Tipo | Tendencia |
| Archivo Pine | `estrategias/05_supertrend.pine` |
| Timeframe sugerido | M15 / H1 |
| Mercados a probar | Oro, índices, BTC |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
El cambio de dirección del Supertrend captura el inicio de tendencias sostenidas por volatilidad (ATR).

## Reglas
- **Señal**: Entra en cada cambio de dirección del Supertrend (seguimiento de tendencia).
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Mercados laterales: señales contrarias consecutivas.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
