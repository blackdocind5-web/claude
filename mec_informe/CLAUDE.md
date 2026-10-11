# Informe "Backtest 2026" (para Diego)

- Resume las cuatro etapas: 1) XAUUSD Backtest, 2) Escalera de riesgo, 3) Gestión híbrida (4 activos, con enero), 4) Cartera esencial: ruta teoría (+83,7%, 4 activos sin costos) → sin BTCUSD (+48,1%) → cartera real neta de costos de Multibank (+34,7%, XAUUSD, EURUSD, GBPUSD, sin enero). Lee `real` de `../mec_cartera/datos_cartera.json`.
- `python informe.py` → `datos_informe.json` (lee `../mec_analisis/datos.json`, `../mec_hibrida/datos_hibrida.json`, `../mec_ny/datos_ny.json`, `../mec_cartera/datos_cartera.json`; recalcula la escalera y las curvas con los datos vigentes); `python build_informe.py` → `Backtest_2026.html`.
- Artefacto: https://claude.ai/artifact/Mb9SoYoYJcARLopmkD2cUQ
- Referencias de mercado (S&P 500 y oro, comprar y mantener): series armadas con los precios de entrada y salida de las exportaciones de TradingView (`precio()` en `informe.py`), porque este entorno no tiene acceso a fuentes de precios en internet. S&P 500 sin dividendos.
- Estética inspirada en la guía de marca que pasó Fabián (violeta #6149DA, fondo violeta muy oscuro, celeste #50ACEA, verde #3EDB9C, naranja #F4AA44, SF Pro + tipografía redondeada para números, sin mayúsculas, sin textos rojos). Sin logo ni nombre de la marca.
- Cifras de la cartera recomendada: las de `mec_cartera` (+76,9%); Gestión híbrida y Sesión NY muestran +76,0% (651 operaciones contra 650; misma cartera, distinto script).
