# Catálogo de estrategias del laboratorio

Una fila por estrategia. **Es la única fuente de verdad del estado.** Etapas (ver `GUIA.md`):
`0 Idea` -> `1 Ficha` -> `2 Codificada` -> `3 Backtest` -> `4 Robustez` -> `5 Paper` -> `6 Real` | `Descartada`

| ID | Estrategia | Tipo | Timeframe | Estado | Última actualización | Nota |
|---|---|---|---|---|---|---|
| 01 | [Cruce de EMAs con filtro de tendencia](fichas/01_cruce_ema.md) | Tendencia | M15 / H1 | 2 Codificada | 03/10/2026 | Sin backtest |
| 02 | [Reversión por RSI a favor de la tendencia](fichas/02_rsi_reversion.md) | Reversión | M15 / H1 | 2 Codificada | 03/10/2026 | Sin backtest |
| 03 | [Reversión en Bandas de Bollinger](fichas/03_bollinger_reversion.md) | Reversión | M5 / M15 | 2 Codificada | 03/10/2026 | Sin backtest |
| 04 | [Ruptura de canal Donchian](fichas/04_breakout_donchian.md) | Ruptura | M15 / H1 / H4 | 2 Codificada | 03/10/2026 | Sin backtest |
| 05 | [Supertrend](fichas/05_supertrend.md) | Tendencia | M15 / H1 | 2 Codificada | 03/10/2026 | Sin backtest |
| 06 | [Cruce MACD a favor de la tendencia](fichas/06_macd_tendencia.md) | Tendencia | M15 / H1 | 2 Codificada | 03/10/2026 | Sin backtest |
| 07 | [Ruptura del rango de apertura (Opening Range)](fichas/07_rango_apertura.md) | Ruptura / sesión | M1 / M5 | 2 Codificada | 03/10/2026 | Sin backtest |
| 08 | [Pullback a la EMA en tendencia](fichas/08_pullback_ema.md) | Tendencia | M5 / M15 | 2 Codificada | 03/10/2026 | Sin backtest |
| F1 | Fabi MEC (scalper XAUUSD) — código en rama `claude/jarvis-initial-inquiry-xp7les`, carpeta `xauusd_scalper_pinescript/` | Estructura M3 / patrones de vela | M1 | 3 Backtest | 03/10/2026 | +32,99% y PF 1,48 SIN costos (26/01–18/09/2026); falta validar con costos y con el motor M3 nuevo |
