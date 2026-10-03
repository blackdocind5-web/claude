# Ficha 04_breakout_donchian

**04 - Ruptura de canal Donchian**

| Campo | Detalle |
|---|---|
| Tipo | Ruptura |
| Archivo Pine | `estrategias/04_breakout_donchian.pine` |
| Timeframe sugerido | M15 / H1 / H4 |
| Mercados a probar | Oro, Nasdaq, BTC |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
Romper el máximo/mínimo reciente indica momentum que continúa; pocas ganancias grandes pagan muchas pérdidas chicas.

## Reglas
- **Señal**: Entra en la ruptura del máximo/mínimo de las últimas N velas (momentum / breakout).
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Rangos con falsas rupturas; acierto bajo (esperable).

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
