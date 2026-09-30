# Análisis de backtests del sistema MEC (XAUUSD, Pre NY)

Criterios que pidió Fabián para cada análisis de un CSV de TradingView. Aplicarlos siempre.

## Flujo
1. Filtrar con `../mec_filtros/filtrar_trades.py` y trabajar solo con `<nombre>_validos.csv`.
2. Calcular métricas (`metricas.py`, que genera `metricas.json`) y armar la presentación a partir de `plantilla.html`.
3. Entregar todo por el chat (enlace a la presentación y archivos). Fabián no tiene acceso a GitHub.

## Convenciones
- Capital inicial 1.000 USD, riesgo 1% por operación. **1R = 1 TP = 0,9% del capital** antes de la operación (un SL completo ≈ −1,11R).
- Siempre mostrar **tres R**: R total, R promedio por operación y **R promedio por semana** (R total / semanas del período).
- Las entradas a las **09:00–09:01 son válidas** (Fabián las está probando). No marcarlas como error: mostrar su resultado por separado (win rate, R, detalle) para decidir más adelante si conviene mantenerlas.
- Patrones temporales: win rate y % ganado por día (lunes a viernes) y por franja de entrada (07:00–07:59, 08:00–08:59, 09:00+); mejor mes, mejor semana, duración promedio.
- Operaciones excluidas: analizarlas por tipo de evento (NFP, CPI USD, CPI GBP, BCE, ADP, discursos, feriados EE. UU., Reino Unido, Europa continental) con recomendación. Advertir siempre que las muestras por evento son chicas y que habilitar un evento solo por su resultado es sobreoptimizar.
- Idioma español, números con coma decimal y punto de miles, fechas DD/MM/AAAA, horario de Nueva York.
