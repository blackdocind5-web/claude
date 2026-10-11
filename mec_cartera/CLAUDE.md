# Cartera Esencial (Pre NY + NY)

- `base.py`: carga la gestión ganadora de Pre NY (XAUUSD E, EURUSD ES, GBPUSD S, BTCUSD E) y de NY (S&P 500 09:00 E y BTCUSD NY 09:00 ES, días sin noticia ni FOMC), todo sin viernes. `filtrar()` aplica en orden cronológico el freno semanal −3R y reglas de corte por ganancia (objetivo semanal, mensual, diario, por activo y candado), medidas en R realizados; `metricas()` usa `hibrida.simular`.
- `python analisis.py` → `datos_cartera.json`; `python build_cartera.py` → `Cartera_Esencial.html`.
- Artefacto: https://claude.ai/artifact/QqkUDoxF56pqEu1eChS1wx
- Primer resultado (09/10/2026): sale BTCUSD NY; Pre NY + S&P 500 NY con candado semanal (+2R → 0R).
- Recomendación vigente (09/10/2026, tras EURUSD/GBPUSD NY y la prueba de robustez de `../mec_ny`): **operar solo Pre NY, sin candado**. El aporte del S&P 500 es frágil (de lunes a jueves +8,9R en 191 operaciones; baja la caída en 19% de los escenarios remuestreados). El candado no mejora los dos años en Pre NY sola (12 variantes en `estabilidad.pre`); único freno: −3R semanal. S&P 500 en observación (reevaluar si sostiene ≥ +0,10R por operación de lunes a jueves).
- `analisis.py` lee `../mec_ny/datos_ny.json` (correr antes `analisis_ny.py`). Objetivos fijos en el promedio cortan las semanas que pagan (en Pre NY el 20% de las mejores semanas aporta ~79% del R).
- Enero sin operar (decisión de Fabián, 10/10/2026): `base.MESES_FUERA = {1}`. Cartera recomendada sin enero: +83,7% anual, caída −11,9% (2025 +77,3% / 2026 +60,5%). Revisar con enero de 2027.
- Cartera real (11/10/2026): XAUUSD E + EURUSD ES + GBPUSD S, neta de costos de Multibank (`analisis.real()`, usa `../mec_diario/costos.py`): +34,7% anual, caída −16,0% (2025 +23,3% / 2026 +35,4%). BTCUSD sale (CFD con 50 USD de spread: −0,40R por operación). El resto del artefacto (Pareto, NY, reglas) es sin costos y lo dice.
