# EMA20 · MNQ, NQ y NAS100 · análisis completo y gestión recomendada · versión 3

Estrategia: `pine/mnq_ema20_tendencia.pine` (Pine v6, gráfico de 1 minuto).
Periodo: 01/12/2023 a 13/11/2026 (2,95 años, ~750 días). Código con el retroceso agotado al entrar y la gestión del día en interruptores.
Resultados **brutos** (los CSV traen comisión 0) salvo donde se indica «neto». 1 R = 1% del capital inicial (10.000 USD sobre 1 millón).

## 0. Aclaraciones sobre los archivos

1. **Los CSV «MNQ 2023 a 2024» de la versión 1 eran de NAS100 (CFD).** Entre 589 y 659 de sus entradas coinciden en hora, dirección y precio exacto con tus archivos de NAS100, y ninguna con los de MNQ. Además sus precios no seguían la cuadrícula de 0,25 y cada punto valía 1 USD. Todo lo que dependía de ellos quedó retirado.
2. **Los tres archivos «máx. 3 por día» no tenían el tope activo**: tienen días con 4 a 9 operaciones (215 de 747 días en MNQ, 220 de 745 en NQ y 241 de 745 en NAS100). El interruptor general «Gestión del día: activar» estaba apagado, y eso ignora los demás. Los traté como corridas **sin gestión y con rango**, y el «máx. 3» lo apliqué por simulación, que es exacta porque se opera de a una.
3. **Coherencia verificada**: los archivos con gestión coinciden exactamente con el recorte de los archivos sin gestión (NQ con rango: 1.492 de 1.492 operaciones; NAS100 con rango: 1.544 de 1.544; MNQ sin rango, de la ronda anterior: 1.652 de 1.652).
4. **Los instrumentos no operan idéntico.** NQ y MNQ comparten el 85-86% de las operaciones (misma hora y dirección), y NAS100 el 76-79%, porque cada gráfico tiene su propia serie de precios (el MNQ y el NQ continuos tampoco coinciden al decimal). Eso es ruido de datos: de ±15 a ±30 R entre instrumentos que son el mismo mercado.

## 1. Veredicto

- **Rango de apertura: apagado.** Con el rango ON el resultado empeora en los 3 instrumentos con «1.er TP o 3 SL» (promedio −57 R, IC de +11 a +107 en sentido contrario) y en MNQ con las otras dos gestiones (intervalos que incluyen el 0). El efecto es mayor en 2024 y se mantiene en 2025 y en casi todo 2026.
- **Gestión: «máximo 3 operaciones por día», sin parar tras TP y sin tope de SL.** Es la única regla que baja la caída en las 4 corridas y en los 12 casos de corrida por periodo, y no cambia el R (de −13,5 a +13,1 R). Limita el peor día a unos −3 R.
- **«Primer TP o 3 SL» se descarta**: resta R en las 4 corridas (de −7 a −40 R) y no baja la caída de forma fiable.
- **Instrumento: no hay evidencia de que uno rinda más.** Las diferencias entre NAS100, NQ y MNQ caen dentro del ruido (intervalos de unos ±60 R) y los R diarios tienen correlación de 0,79 a 0,90. NAS100 es el mejor en una configuración y el peor en otras dos.
- **La estrategia en sí no tiene ventaja demostrada.** Con la configuración recomendada en MNQ: t = 1,99 bruto y 0,89 neto con 1 punto de costo.

## 2. Qué hay en las pruebas

| Instrumento | Rango ON, sin gestión | Rango OFF, sin gestión | Rango ON, 1.er TP o 3 SL | Rango OFF, 1.er TP o 3 SL |
|---|---|---|---|---|
| MNQ | archivo | ronda anterior | simulado | ronda anterior |
| NQ | archivo | **falta** | archivo | archivo |
| NAS100 | archivo | **falta** | archivo | archivo |

## 3. Rango de apertura: apagado

Diferencia de R (rango OFF menos rango ON), por días. Positivo = el rango perjudica.

| Comparación | ΔR | IC 95% | Por año (2023-24 / 2025 / 2026) |
|---|---|---|---|
| MNQ · primer TP o 3 SL | +54,9 | +3,8 a +107,0 | +22,4 / +19,5 / +13,1 |
| NQ · primer TP o 3 SL | +51,2 | +0,1 a +102,5 | +23,0 / +14,2 / +14,0 |
| NAS100 · primer TP o 3 SL | +65,7 | +14,6 a +119,9 | +45,0 / +18,7 / +2,1 |
| **Promedio de los 3** | **+57,3** | **+11,1 a +107,1** | |
| MNQ · sin gestión | +31,9 | −19,1 a +83,3 | +24,4 / +9,5 / −1,9 |
| MNQ · máx. 3 por día | +33,9 | −15,5 a +83,2 | +21,4 / +4,5 / +8,1 |

En MNQ el rango deja fuera 516 operaciones que sumaban +25,5 R (esperanza +0,049 R). El bloque 10:00 a 10:30 es el que más pierde (+30,9 R bloqueados). Los tres instrumentos comparten los mismos días, así que son réplicas de la misma evidencia y no tres pruebas independientes.

## 4. Instrumentos

R bruto total (esperanza por operación, t-stat), mismos ajustes y periodo:

| Configuración | MNQ | NQ | NAS100 |
|---|---|---|---|
| Rango OFF · 1.er TP o 3 SL | +90,2 (0,055 · 1,82) | +106,9 (0,065 · 2,26) | +118,4 (0,070 · 2,40) |
| Rango ON · sin gestión | +75,4 (0,035 · 1,30) | +80,9 (0,038 · 1,51) | +59,7 (0,027 · 1,01) |
| Rango ON · 1.er TP o 3 SL | +35,3 (0,023 · 0,74) | +55,7 (0,037 · 1,23) | +52,7 (0,034 · 1,10) |

Diferencias pareadas por día (rango OFF · 1.er TP o 3 SL): NQ − MNQ +16,7 R (IC −29 a +63); NAS100 − MNQ +28,2 R (IC −35 a +92); NAS100 − NQ +11,5 R (IC −48 a +68). Ninguna es significativa. En 2026 con rango OFF y 1.er TP o 3 SL, NAS100 rinde +12,9 R frente a +41,8 R en NQ y +33,9 R en MNQ.

**Qué instrumento usar es una decisión práctica:**
- **Futuros (MNQ o NQ)** si tu firma opera futuros. Según tengo entendido Lucid Trading es de futuros: confírmalo. El CFD de NAS100 no aplica ahí.
- **MNQ** para cuentas pequeñas. Con el SL mediano de 37 puntos, 1 contrato de NQ arriesga unos 737 USD. Con 0,5% de riesgo hace falta una cuenta de ≥ 147.000 USD para abrir un solo contrato; por debajo, NQ no opera o sobredimensiona. MNQ arriesga unos 73 USD por contrato.
- NQ redondea los contratos hacia abajo: el riesgo real fue en promedio el 95,8% del nominal, así que sus R brutos salen un 4% menores a igual ventaja.

## 5. Gestión del día

ΔR / Δcaída máxima (R) de cada regla frente a no gestionar, en las 4 corridas sin gestión disponibles (negativo en caída = mejor):

| Regla | MNQ rango ON | NQ rango ON | NAS100 rango ON | MNQ rango OFF |
|---|---|---|---|---|
| Máx. 2 por día | −14,1 / −14,9 | −33,7 / −2,0 | −12,4 / −13,0 | −42,1 / −12,9 |
| **Máx. 3 por día** | **−0,7 / −8,9** | **−13,5 / −5,7** | **+13,1 / −5,0** | **+1,3 / −8,7** |
| Máx. 4 por día | +12,7 / 0,0 | −8,5 / −0,9 | +32,1 / −3,0 | +22,7 / 0,0 |
| Parar tras 1.er TP | −27,2 / 0,0 | −14,8 / −3,2 | −5,1 / −13,9 | −3,3 / +3,0 |
| 1.er TP o 3 SL | −40,1 / +1,0 | −25,2 / −4,5 | −7,1 / −13,0 | −17,1 / +4,0 |
| 3 SL seguidos | −11,1 / +1,0 | −13,4 / +0,1 | +1,0 / +2,0 | −9,1 / +1,0 |
| Parar a +1 R | −10,1 / −4,0 | −12,0 / −6,5 | −10,1 / −11,0 | +6,9 / 0,0 |

- **Máx. 3** baja la caída en 4 de 4 corridas y en los 12 casos corrida por periodo (de −2 a −18 R), con peor día de −3 R frente a −6,6 a −7,9 R sin gestión.
- Bootstrap por días en MNQ rango OFF: Δcaída −9,7 R (IC −31,8 a +11,4; el 80% de las remuestras baja) y ΔR +1,3 R (IC −52 a +59). El tope de pérdida diaria es mecánico; el efecto sobre la caída es consistente pero no concluyente.
- **Máx. 4** rinde más (+14,8 R de media) pero no baja la caída (2 de 4) y el peor día llega a −4 R. Es la alternativa si priorizas rentabilidad sobre protección.
- Ninguna regla supera al azar tras corregir por haber probado varias; son controles de riesgo, no fuentes de ventaja.

**Hora de corte:** con rango OFF y 1.er TP o 3 SL, las 11:00 superan a las 10:30 en los 3 instrumentos (+17, +17 y +31 R) y las 10:00 son claramente peores. Con «máx. 3» el resultado es mixto. Se mantienen las 11:00. No se probó nada posterior.

## 6. Configuración recomendada

| Ajuste | Valor |
|---|---|
| Rango de apertura | **Desactivado** |
| RR · BE | 2,0 · activado a 1R |
| SL máximo · margen mínimo | 100 puntos · 5 puntos |
| Entradas | 09:30 a 10:59 (hora de Nueva York) |
| Cierre forzado | 16:00 |
| Riesgo | 1% (o menos, ver 7.1), sin interés compuesto |
| **Gestión del día: activar** | **Activado** (si queda apagado, ignora todo lo demás) |
| Parar tras el primer TP | Desactivado |
| Máximo de SL seguidos | 0 |
| El BE cuenta como… | Neutro |
| **Máximo de operaciones por día** | **3** |
| Parar al llegar a +X R | 0 |

## 7. Resultados de la recomendada (MNQ, rango OFF, máx. 3 por día)

| Métrica | Valor |
|---|---|
| Operaciones (días) | 1.979 (756) |
| TP / SL / BE | 537 / 967 / 470 |
| **Win rate** (TP sobre operaciones) | **27,1%** (35,7% sin contar BE) |
| **R bruto total** | **+108,6** (+36,8 por año) |
| Esperanza por operación | +0,055 R |
| t-stat · IC 95% del R total | 1,99 · +1,9 a +218 |
| Factor de beneficio | 1,11 |
| **Caída máxima** · a planificar (p95) | **26,9 R** · 61 R |
| Peor / mejor día | −3,0 / +6,0 R |
| Días positivos / negativos | 50% / 45% |
| **Racha máxima de SL seguidos** | **10** |
| Racha máxima de operaciones sin TP | 20 |
| Máx. días negativos seguidos | 7 |
| Meses positivos · peor / mejor | 72% (26 de 36) · −14,9 / +24,9 R |
| Por año | 2023 (solo diciembre) −10,0 · 2024 +63,3 · 2025 +22,3 · 2026 +32,9 R |

### 7.1 Rentabilidad en % según el riesgo por operación (sin interés compuesto)

| Riesgo por R | Bruto total (por año) | Neto con 1 punto de costo (por año) | Caída máx. histórica | Caída a planificar (p95) | Peor día |
|---|---|---|---|---|---|
| 1,00% | +108,6% (+37%) | +48,3% (+16%) | −26,9% | −61% | −3,0% |
| 0,50% | +54,3% (+18%) | +24,2% (+8%) | −13,4% | −31% | −1,5% |
| 0,25% | +27,1% (+9%) | +12,1% (+4%) | −6,7% | −15% | −0,75% |

## 8. Costos

R neto según el costo total por operación (comisión + spread + slippage), en **puntos del índice**, ida y vuelta, por contrato. 1 punto = 2 USD en MNQ, 20 USD en NQ y 1 USD por unidad en NAS100.

| Configuración | 0 pt | 0,5 pt | 1,0 pt | 1,5 pt | 2,0 pt | Equilibrio | t neto (1 pt) |
|---|---|---|---|---|---|---|---|
| MNQ · rango OFF · máx. 3 | +108,6 | +78,5 | +48,3 | +18,2 | −11,9 | 1,80 pt | 0,89 |
| MNQ · rango OFF · sin gestión | +107,3 | +69,5 | +31,7 | −6,1 | −43,9 | 1,42 pt | 0,51 |
| MNQ · rango OFF · 1.er TP o 3 SL | +90,2 | +65,0 | +39,9 | +14,7 | −10,4 | 1,79 pt | 0,79 |
| NQ · rango OFF · 1.er TP o 3 SL | +106,9 | +82,2 | +57,5 | +32,8 | +8,1 | 2,16 pt | 1,20 |
| NAS100 · rango OFF · 1.er TP o 3 SL | +118,4 | +91,6 | +64,9 | +38,2 | +11,4 | 2,21 pt | 1,30 |

Un costo de 1 punto equivale a 2 USD por contrato de MNQ. En puntos, la comisión pesa menos en NQ que en MNQ (los micros pagan una comisión proporcionalmente mayor); en NAS100 el costo real es tu spread más el slippage. Mide el tuyo antes de elegir.

## 9. Lo que no está probado

1. **No hay una prueba fuera de muestra limpia.** El rango OFF y el «máx. 3» se eligieron mirando estos mismos 35 meses.
2. **«Máx. 3» no se verificó con el rango OFF en NQ ni en NAS100** (faltan esas corridas sin gestión). Con el rango ON sí se verificó en los tres.
3. **Sin ventaja neta demostrada**: t neto de 0,5 a 1,3 con un punto de costo.
4. No se evaluaron las reglas de Lucid Trading (tipo de drawdown, pérdida diaria, consistencia, contratos).
5. Fills ideales en el backtest, y días de cierre anticipado sin cierre forzado (por ejemplo el 19/06/2026).

## 10. Próximos pasos

1. NQ y NAS100 con **rango desactivado y gestión del día desactivada** (con «Gestión del día: activar» apagado), del 01/12/2023 al 13/11/2026. Con eso se completa la tabla de la sección 2 y se confirma «máx. 3» con el rango OFF.
2. **Prueba fuera de tiempo**: la configuración recomendada en NAS100 (CFD) del 01/03/2021 al 30/11/2023, con «Gestión del día: activar» **encendido** y solo «máximo de operaciones por día = 3». NAS100 ya mostró el mismo comportamiento que los futuros, y es el único con historial anterior a diciembre de 2023.
3. Demo de 4 a 8 semanas con los costos reales de tu cuenta.
