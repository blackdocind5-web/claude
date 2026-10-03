# Ficha 01_cruce_ema

**01 - Cruce de EMAs con filtro de tendencia**

| Campo | Detalle |
|---|---|
| Tipo | Tendencia |
| Archivo Pine | `estrategias/01_cruce_ema.pine` |
| Timeframe sugerido | M15 / H1 |
| Mercados a probar | Oro, índices, forex mayor |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
Las tendencias sostenidas dejan más ganancia que las pérdidas de los falsos cruces; la EMA200 filtra el contra-tendencia.

## Reglas
- **Señal**: Cruce de EMA rápida/lenta a favor de la EMA de tendencia (seguimiento de tendencia).
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Mercados laterales: muchos cruces falsos (whipsaw) y pérdidas seguidas.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
