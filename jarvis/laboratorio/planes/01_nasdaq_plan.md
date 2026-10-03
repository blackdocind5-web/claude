# Plan de pruebas — Estrategia 01 (cruce de EMAs) en Nasdaq

**Objetivo:** saber si el cruce EMA 9/21 con filtro EMA 200 tiene borde en Nasdaq, con costos, y en qué
timeframe y horario funciona. Es la primera estrategia del laboratorio; sirve también para ensayar el método.

## Instrumento
- Preferido para empezar: **CFD US100** (permite tamaños fraccionarios, el sizing del script funciona tal cual).
- Alternativa: futuros **MNQ1!** (micro, USD 2 por punto). Con **NQ1!** (USD 20 por punto) el tamaño mínimo es 1 contrato:
  con capital chico el riesgo del 1% no se puede respetar y el backtest miente.
- Confirmar con el broker real: spread, comisión y horario. Los costos del script (0,01% y 2 ticks) son un supuesto inicial.

## Sesiones que importan en Nasdaq (hora de Nueva York)
| Franja | Horario | Por qué |
|---|---|---|
| Premercado | 04:00–09:30 | Liquidez baja, movimientos por noticias |
| Apertura | 09:30–10:30 | Mayor volumen y volatilidad del día |
| Mediodía | 11:30–14:00 | Suele ser lateral, el cruce de EMAs sufre |
| Cierre | 15:00–16:00 | Vuelve el volumen |

## Matriz de pruebas (completar `resultados.csv` en cada una)
Mismo período en todas. Anotar en cada fila el período y los costos usados.

| # | Timeframe | Filtro horario | Variante | Estado |
|---|---|---|---|---|
| 1 | M15 | Sin filtro | Base (9/21/200, 1,5 ATR, R:R 1,5) | pendiente |
| 2 | M15 | 09:30–16:00 | Base | pendiente |
| 3 | M5 | 09:30–16:00 | Base | pendiente |
| 4 | H1 | Sin filtro | Base | pendiente |
| 5 | M15 | 09:30–11:30 | Solo apertura | pendiente |
| 6 | M15 | 09:30–16:00 | Solo largos (Nasdaq tiene sesgo alcista de largo plazo) | pendiente |
| 7 | M15 | 09:30–16:00 | Costos ×2 | pendiente |

Regla: antes de mirar los resultados de 2 a 7, anotar qué esperamos de cada una. Si el resultado cambia nuestra
idea, anotar por qué (evita ajustar a posteriori).

## Qué mirar en el gráfico (para ir viendo juntos)
- Operaciones que entran tarde, cuando el movimiento ya se agotó.
- Stops que se tocan y luego el precio sigue a favor (stop demasiado justo).
- Cruces falsos en rangos del mediodía.
- Cómo se comporta alrededor de soportes y resistencias claras (máximo/mínimo del día anterior, premercado).

## Ideas para formular juntos (cada una se vuelve ficha y se testea)
Se completan con lo que vayas viendo en vivo. Candidatas iniciales:
- Rebote o ruptura en máximo y mínimo del día anterior.
- Zonas de acumulación: rangos laterales de baja volatilidad antes de una expansión.
- Áreas entre el precio y las EMAs 9 y 20 (la idea de ayer): necesito que me expliques cómo la definías para codificarla igual.

## Convención de capturas
Guardar en `bitacora/capturas/` como `AAAA-MM-DD_activo_TF_tema.png`, por ejemplo `2026-10-03_US100_M15_cruce-falso.png`,
y referenciarlas en la bitácora del día.
