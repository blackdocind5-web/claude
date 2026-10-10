# Investigación: objetivo diario + escalera sobre la cartera recomendada (Pre NY, m1)

- `diario.py`: simulador con escalera de cartera (base × 2^k, tope), objetivo diario en % del capital del día y freno semanal en %. El control (fijo 1%, freno 2,7%) reproduce la cartera: +77% anual, −11,9%.
- `grilla.py` → `grilla.json` (180 variantes); `mc.py` → `mc.json` (1.000 simulaciones por variante elegida).
- Resultado (10/10/2026): el objetivo diario resta rendimiento y no sube los días positivos; la escalera sube los días positivos (60% → 73% histórico, 57% → 65% en simulaciones) pero queda dominada por el riesgo fijo equivalente (más caída en el peor 5% por el mismo rendimiento). Propuestas de Fabián: A (0,5% tope 3, objetivo 0,45%) peor que la actual; B (1% tope 3, objetivo 0,9%) 37% de probabilidad de caída de 30%. Tope máximo razonable con 4 activos: 2. No se modificó ningún artefacto.
