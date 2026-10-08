# Sesión NY (09:00-11:00 hora de Nueva York)

Segunda franja del sistema MEC. Activos a estudiar: S&P 500, US100, Dow Jones (US30) y quizás BTCUSD, con dos exportaciones por activo (desde 09:00 y desde 09:30, ambas hasta 11:00), patrones Envolvente, START y Envolvente + START, 2025-2026.

## Calendario (`calendario_ny.csv`, generado con `python generar_calendario_ny.py`)
- SIN_OPERAR: feriados bancarios y receso de Pre NY, discursos de Pre NY y discursos de la ventana NY (`fuentes/discursos_ny_2025_2026.csv`).
- ANALIZAR_NOTICIA: NFP, CPI USD y GBP, PPI, PIB final (sin operar en Pre NY). No se excluyen de entrada: analizar si conviene operar NY esos días.
- ANALIZAR_FOMC: Federal Funds Rate / FOMC Statement, Economic Projections y Meeting Minutes (14:00). Analizar si conviene operar.
- BLOQUEO_NOTICIA 09:50-10:03: ISM Manufacturing PMI, JOLTS, CB Consumer Confidence (pendiente la captura) y Core PCE de las 10:00.
- No se copian las reglas de Pre NY fuera de la ventana NY (BCE solo entrada 07:00-08:00, ADP 08:15, Core PCE 08:30).
- No usar `mec_filtros/filtrar_trades.py` con este calendario (no conoce las reglas ANALIZAR_*); el calendario de Pre NY no cambia.
