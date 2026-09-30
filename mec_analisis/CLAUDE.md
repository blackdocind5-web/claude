# Análisis de backtests del sistema MEC (XAUUSD, Pre NY)

Criterios que pidió Fabián para cada análisis de un CSV de TradingView. Aplicarlos siempre.

## Flujo
1. Filtrar cada CSV con `../mec_filtros/filtrar_trades.py` y trabajar solo con `<nombre>_validos.csv`.
2. `python metricas.py` (modelos definidos en `MODELOS`: combinado, envolvente, start) → `datos.json`.
   Variantes de gestión: `python variante.py` (después de `metricas.py`) agrega `<modelo>_v` y la comparación a `datos.json`; se ven en la pestaña "Gestión: variante SL/TP" y con el selector de versión de cada informe. El Reset no se toca nunca: es parte fundamental del sistema.
3. `python build.py` arma `XAUUSD_Backtest_2026.html` desde `plantilla.html` + `comparativa.js` + `datos.json`.
4. Publicar en el mismo enlace de siempre: https://claude.ai/artifact/8vaF1wPne8ThugaGpN1BjE (título "XAUUSD | Backtest 2026"; pestañas "Sistema MEC (Envolvente + START)", "Envolvente | Backtest 2026", "START | Backtest 2026" y "Comparativa y recomendación").
5. Entregar todo por el chat (enlace a la presentación y archivos). Fabián no tiene acceso a GitHub.
6. La comparativa final es un análisis imparcial de consultor: qué modelo operar, horario, días, gestión, calendario y tamaño de riesgo, siempre advirtiendo sobre sobreoptimización y validación fuera de muestra.

## Convenciones
- Capital inicial 1.000 USD, riesgo 1% por operación. **1R = 1 TP = 0,9% del capital** antes de la operación (un SL completo ≈ −1,11R).
- Siempre mostrar **tres R**: R total, R promedio por operación y **R promedio por semana** (R total / semanas del período).
- Las entradas a las **09:00–09:01 son válidas** (Fabián las está probando). No marcarlas como error: mostrar su resultado por separado (win rate, R, detalle) para decidir más adelante si conviene mantenerlas.
- Patrones temporales: win rate y % ganado por día (lunes a viernes) y por franja de entrada (07:00–07:59, 08:00–08:59, 09:00+); mejor mes, mejor semana, duración promedio.
- Operaciones excluidas: analizarlas por tipo de evento (NFP, CPI USD, CPI GBP, BCE, ADP, discursos, feriados EE. UU., Reino Unido, Europa continental) con recomendación. Advertir siempre que las muestras por evento son chicas y que habilitar un evento solo por su resultado es sobreoptimizar.
- Idioma español, números con coma decimal y punto de miles, fechas DD/MM/AAAA, horario de Nueva York.
