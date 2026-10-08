# Sesión NY (09:00-11:00 hora de Nueva York)

Segunda franja del sistema MEC. Activos a estudiar: S&P 500, US100, Dow Jones (US30) y quizás BTCUSD, con dos exportaciones por activo (desde 09:00 y desde 09:30, ambas hasta 11:00), patrones Envolvente, START y Envolvente + START, 2025-2026.

## Calendario (`calendario_ny.csv`, generado con `python generar_calendario_ny.py`)
- SIN_OPERAR: feriados bancarios y receso de Pre NY y discursos de la ventana 09:00-11:00 (`fuentes/discursos_ny_2025_2026.csv`, incluidos los de las 11:00). Los discursos de Pre NY no cuentan.
- ANALIZAR_NOTICIA: NFP, CPI USD y GBP, PPI, PIB final (sin operar en Pre NY). No se excluyen de entrada: analizar si conviene operar NY esos días.
- ANALIZAR_FOMC: Federal Funds Rate / FOMC Statement, Economic Projections y Meeting Minutes (14:00). Analizar si conviene operar.
- BLOQUEO_NOTICIA 09:50-10:03: ISM Manufacturing PMI, JOLTS, CB Consumer Confidence y Core PCE de las 10:00.
- No se copian las reglas de Pre NY fuera de la ventana NY (BCE solo entrada 07:00-08:00, ADP 08:15, Core PCE 08:30).
- No usar `mec_filtros/filtrar_trades.py` con este calendario (no conoce las reglas ANALIZAR_*); el calendario de Pre NY no cambia.

## Datos y análisis
- `datos/<ACTIVO>_m1_<0900|0930>_2025-2026_<Envolvente|START|Envolvente_y_START>.csv`.
- `ny.py`: lectura, calendario NY, límite de dos pérdidas por sesión y normalización del riesgo: con 1.000 USD y lote mínimo 0,1 el riesgo real de los índices no es 1%; cada operación se lleva a riesgo exacto de 1% (salida de la estrategia: SL -1, TP +0,9; otras salidas: riesgo estimado con el tamaño).
- `python analisis_ny.py` → `datos_ny.json`; `python build_ny.py` → `Sesion_NY.html` (estilos y gráficos tomados de `../mec_analisis/plantilla.html` y `../mec_hibrida/plantilla_hibrida.html`).
- Artefacto: https://claude.ai/artifact/36fNt6b53uAQhLSiGLdvF2
