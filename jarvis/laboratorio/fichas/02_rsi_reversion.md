# Ficha 02_rsi_reversion

**02 - Reversión por RSI a favor de la tendencia**

| Campo | Detalle |
|---|---|
| Tipo | Reversión |
| Archivo Pine | `estrategias/02_rsi_reversion.pine` |
| Timeframe sugerido | M15 / H1 |
| Mercados a probar | Índices, acciones líquidas, oro |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
Dentro de una tendencia, los retrocesos extremos del RSI tienden a revertir hacia la tendencia.

## Reglas
- **Señal**: Compra cuando el RSI sale de sobreventa en tendencia alcista (y vende al revés).
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Tendencias muy fuertes: el RSI queda en sobreventa y sigue cayendo.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
