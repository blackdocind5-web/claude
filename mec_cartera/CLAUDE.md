# Cartera Esencial (Pre NY + NY)

- `base.py`: carga la gestión ganadora de Pre NY (XAUUSD E, EURUSD ES, GBPUSD S, BTCUSD E) y de NY (S&P 500 09:00 E y BTCUSD NY 09:00 ES, días sin noticia ni FOMC), todo sin viernes. `filtrar()` aplica en orden cronológico el freno semanal −3R y reglas de corte por ganancia (objetivo semanal, mensual, diario, por activo y candado), medidas en R realizados; `metricas()` usa `hibrida.simular`.
- `python analisis.py` → `datos_cartera.json`; `python build_cartera.py` → `Cartera_Esencial.html`.
- Artefacto: https://claude.ai/artifact/QqkUDoxF56pqEu1eChS1wx
- Resultado (09/10/2026): sale BTCUSD NY; cartera esencial = 4 activos de Pre NY + S&P 500 NY, con candado semanal (si la semana llega a +2R y vuelve a 0R, se deja de operar hasta el lunes). Objetivos fijos en el promedio cortan las semanas que pagan (el 20% de las mejores semanas aporta ~81% del R).
