# Informe "NY SYSTEM" (capital propio, para la cartera con Diego)

- NY SYSTEM = estrategia antes llamada KALA (XAUUSD, sesión NY, RR 1:1, 2.ª operación solo tras SL). Datos: `../mec_lucid/kala/XAU_ATR.csv` (139 ops, 08/01/2025–26/10/2026), cargados con `motor.kala()`.
- Costo Multibank XAUUSD 0,05 USD/oz → 0,05/dist en R (≈0,006R). 1.000 USD, interés compuesto. Perfiles 0,5% / 1% / 1,5% / 2%.
- Filtro sugerido: no operar días de CPI EE. UU. ni NFP (132 ops, R/op +0,37). La regla del Nasdaq (Rascacielos) empeora (anual 1% 22,1% vs 31,0%). FOMC/minutas salen 14:00, después de la operación.
- Resultado 1% con filtro: anual +31,0%, caída 3,1%, Calmar 10,1; oro +25,3% (caída 25,5%), Nasdaq +19,6% (caída 29,8%). Correlación mensual −0,18 con oro, −0,29 con Nasdaq.
- Alerta: R/op 2025 +0,48 → 2026 +0,27 (con filtro). Falta validar 2023–2024. Capital mínimo por lote 0,01 (stop típico 9,4 USD): 0,5% necesita ~1.900–3.000 USD.
- `python analisis.py` → `datos_nysystem.json`; `python build_nysystem.py` → `NY_SYSTEM.html`. Artefacto: https://claude.ai/artifact/9phMWjHoW9L8xAEiecXTmT
- Informe cronológico: la próxima etapa es sumar la estrategia del Nasdaq (MNQ) y medir diversificación.
- Consulta 03/11/2026 (`lotes_mica.py`, no cambia el informe). Lotes con 1.000 USD (mín. 1 oz, redondeo hacia abajo, siempre se abre): 1% → riesgo real mediana 0,79%, máx 2,30%, 7,6% de ops >1,25%; 1,5% → mediana 1,23%, máx 2,07%, 0,8% de ops excedidas (CAGR 41,9%, MDD 4,1%). Riesgo mínimo práctico con 1.000 USD: 1,5% (efectivo ~1,25%).
- NY SYSTEM + Mica (1R y 0,5R, filtro CPI/NFP, cortes 10:00–11:00): Mica sola es débil (1R antes de 10:00 +0,106 t 1,9; 2025 +0,03); 10:00–10:14 negativa en ambos años. Sumada a NY 1%: CAGR 55,5% pero MDD 11,0% (Calmar 5,1 vs 10,1). Mica gana en días con NY (WR 79,6%, +0,59R) y pierde en los demás (−0,16, t −2,3), pero entra ~11 min ANTES que NY (108 de 110): no se puede usar como filtro (mira el futuro). Es duplicar la misma apuesta; NY solo a 3,5% da CAGR 149% con MDD 10,7%. Veredicto: no sumar Mica.
