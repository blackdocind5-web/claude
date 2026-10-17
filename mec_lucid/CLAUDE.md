# Lucid Trading 25K Flex · MNQ (investigación, 17/10/2026)

- Fase 1 (evaluación): +1.250 USD, pérdida máxima 1.000 USD trailing de fin de día, consistencia 50% (mejor día ≤ 50% de la ganancia). Fase 2 (fondeo): +1.000 USD, 5 días de al menos +100 USD. Fase 3: retiros (mínimo 500 USD; hay que llegar a +1.000 porque retienen 500).
- `datos/FASE_1-MNQ_<trimestre>_<año>_<09.30h|09.45h>_SL_<pts>_TP_<pts>.csv`: 14 exportaciones (1 contrato, 2 USD por punto), una operación por día.
- `fase1.py` (lectura, calendario NY de `../mec_ny/calendario_ny.csv`, contratos = piso(1.000 / (SL × 2)), máx. 20 micros); `estudio.py` → `estudio.json`; `evaluacion.py` simula la evaluación empezando en cada día (MLL trailing, consistencia, comisión por contrato).
- Hallazgos: 09:30 y 09:45 tienen el mismo win rate (63,4%, equilibrio 58,8% con RR 0,7), pero 09:45 tiene 24 operaciones con gaps (pérdidas de hasta 1,8× el stop) y peor 2026. Mejor: 09:30 sin feriados/receso/discursos ni noticias de las 08:30: pasa 61,8% de las evaluaciones (2025 62,3% / 2026 60,4%), mediana 2 días. Arriesgar menos no sube la probabilidad de pasar y tarda mucho más.
