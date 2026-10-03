# Ficha 08_pullback_ema

**08 - Pullback a la EMA en tendencia**

| Campo | Detalle |
|---|---|
| Tipo | Tendencia |
| Archivo Pine | `estrategias/08_pullback_ema.pine` |
| Timeframe sugerido | M5 / M15 |
| Mercados a probar | Oro, índices, forex mayor |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
Entrar en el retroceso a una EMA corta dentro de tendencia da mejor precio y stop más corto que entrar en la ruptura.

## Reglas
- **Señal**: En tendencia (EMA50 vs EMA200) entra cuando el precio recupera la EMA20 tras un retroceso.
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Cambios de tendencia: el pullback se convierte en reversión.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
