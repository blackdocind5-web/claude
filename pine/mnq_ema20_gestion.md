# EMA20 · MNQ, NQ y NAS100 · análisis completo y gestión recomendada · versión 4

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
- **Gestión: «máximo 3 operaciones por día», sin parar tras TP y sin tope de SL.** Con el rango OFF baja la caída en los 3 instrumentos (−8,7 / −11,6 / −10,5 R) sin restar R (+1,3 / +2,6 / +11,1 R) y limita el peor día a unos −3 R. «Primer TP o 3 SL» se descarta.
- **Instrumento: no hay uno con ventaja demostrable.** Con la configuración recomendada, en 35 meses: NQ +122,7 R, NAS100 +118,0 R, MNQ +108,6 R. Las diferencias (de −5 a +14 R) tienen intervalos de unos ±70 R y los meses se reparten 21 a 15 (NAS100 contra MNQ), es decir, un empate.
- **La estrategia no tiene ventaja fuera de tiempo demostrada.** En NAS100 de marzo 2021 a noviembre 2023 dio +35,1 R (t = 0,76; 2021 en 0 R). Sin 2024 (el mejor año), el t en 5,7 años baja a 1,26.

## 2. Qué hay en las pruebas

| Instrumento | Rango ON, sin gestión | Rango OFF, sin gestión | Rango ON, 1.er TP o 3 SL | Rango OFF, 1.er TP o 3 SL |
|---|---|---|---|---|
| MNQ | archivo | archivo | simulado | archivo |
| NQ | archivo | archivo | archivo | archivo |
| NAS100 | archivo | archivo | archivo | archivo |

Además, NAS100 de 01/03/2021 a 30/11/2023 con rango OFF y «máx. 3 por día» activo (prueba fuera de tiempo). Los archivos «rango OFF, gestión desactivada» de NQ y NAS100 confirman la coherencia: el recorte «1.er TP o 3 SL» del archivo sin gestión coincide con el archivo con gestión (1.648 de 1.648 y 1.689 de 1.689 operaciones).

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

### 4.1 Configuración recomendada en los tres (rango OFF, RR 2, BE a 1R, SL máx. 100, hasta las 11:00, máx. 3 por día), 01/12/2023 a 13/11/2026

| Métrica | MNQ | NQ | NAS100 (CFD) |
|---|---|---|---|
| Operaciones | 1.979 | 1.982 | 1.988 |
| Win rate (TP sobre operaciones) | 27,1% | 27,8% | 27,4% |
| **R bruto** | **+108,6** | **+122,7** | **+118,0** |
| Esperanza por operación | +0,055 R | +0,062 R | +0,059 R |
| t-stat · IC 95% del R | 1,99 · +5 a +218 | 2,34 · +21 a +228 | 2,14 · +12 a +228 |
| Factor de beneficio | 1,11 | 1,13 | 1,12 |
| Caída máx. | 26,9 R | 18,9 R | 22,0 R |
| Peor día | −3,0 R | −3,0 R | −3,2 R |
| Racha máx. de SL seguidos | 10 | 11 | 10 |
| Meses positivos | 72% | 67% | 61% |
| R 2023-24 / 2025 / 2026 | +53,3 / +22,3 / +32,9 | +67,9 / +30,0 / +24,9 | +71,2 / +43,3 / +3,5 |
| Costo de equilibrio | 1,80 pt | 2,07 pt | 1,89 pt |
| R neto con 1 punto de costo | +48,3 | +63,6 | +55,5 |

Diferencias pareadas por día: NAS100 − MNQ +9,4 R (IC −65 a +82); NQ − MNQ +14,1 R (IC −44 a +72); NAS100 − NQ −4,7 R (IC −75 a +63). NAS100 gana en 21 de los 36 meses frente a MNQ y en 18 frente a NQ. La correlación de los R diarios es de 0,77 a 0,85.

Por año, NAS100 supera a MNQ en 2023-24 (+17,8 R) y en 2025 (+21,0 R) pero queda por debajo en 2026 (−29,4 R, IC −66 a +7): +3,5 R frente a +32,9 R.

### 4.2 ¿Se parecen las operaciones?

NAS100 y MNQ comparten el 75% de las operaciones (misma hora y dirección). En las 1.488 comunes, el 96% termina con el mismo resultado (TP, SL o BE) y el R tiene correlación de 0,95. Las exclusivas de cada uno rinden parecido: 491 operaciones solo de MNQ (+34,6 R, +0,071 por operación) y 500 solo de NAS100 (+33,2 R, +0,066). La ventaja nominal de NAS100 sobre MNQ (+9,4 R) sale de las comunes (+10,8 R): son diferencias de precio entre las series, no de ventaja.

### 4.3 Prueba fuera de tiempo: NAS100, 01/03/2021 a 30/11/2023 (rango OFF, máx. 3 por día)

| | Valor |
|---|---|
| Operaciones · días | 1.407 · 701 |
| Win rate (TP sobre operaciones) | 26,1% (34,3% sin contar BE) |
| R bruto · esperanza por operación | +35,1 · +0,025 R |
| t-stat · IC 95% del R | 0,76 · −57 a +128 (prueba de signos p = 0,23) |
| Caída máx. · peor día | 27,2 R · −3,0 R |
| Racha de SL seguidos · días negativos seguidos | 8 · 5 |
| Meses positivos | 48% |
| Por año | 2021: 0,0 R (409 operaciones) · 2022: +24,5 R (538) · 2023 hasta noviembre: +10,7 R (460) |
| Costo de equilibrio | 0,67 pt (con 0,5 pt: +8,8 R; con 1 pt: −17,5 R) |

Todo NAS100, 5,7 años (01/03/2021 a 13/11/2026): +153,2 R, esperanza +0,045 R, t = 2,13, caída máx. 27,2 R, equilibrio 1,33 pt (con 1 pt: +38,0 R). Por año: 2021 0,0 · 2022 +24,5 · 2023 +9,7 · 2024 **+72,2** · 2025 +43,3 · 2026 +3,5 R. Sin 2024: +81,0 R y t = 1,26 (MNQ sin 2024: +45,3 R, t = 1,04).

El periodo 2021-2023 fue positivo pero débil. Solo NAS100 tiene datos de esa época, así que no se puede decir si la debilidad es del instrumento o del periodo.

### 4.4 Qué instrumento usar para las señales

No hay base estadística para elegir. Si quieres una sola gráfica maestra:
- **Gráfica de futuros (MNQ o NQ).** Es el instrumento de la cuenta de fondeo, y la ejecución coincide con las señales. NQ salió nominalmente mejor (t = 2,34 y caída de 18,9 R) y es el mismo mercado que MNQ, pero la diferencia de +14 R con MNQ está dentro del ruido: desempate práctico, no evidencia.
- **NAS100 CFD** para la cuenta de CFD, con sus propias señales. Copiar las señales de futuros al CFD (o al revés) es razonable: el 96% de las operaciones comunes termina igual, pero un 25% de las operaciones no coincide entre gráficas. Los niveles se trasladan por distancias en puntos, no por precio (los precios de cada gráfico difieren).
- **Tamaño:** MNQ para cuentas pequeñas (1 contrato de NQ arriesga unos 737 USD con el SL mediano; con 0,5% de riesgo hace falta una cuenta de ≥ 147.000 USD).

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
- **Con el rango OFF, en los tres instrumentos** (corridas sin gestión de NQ y NAS100 recibidas): «máx. 3» pasa de 35,5 a 26,9 R de caída en MNQ, de 30,5 a 18,9 R en NQ y de 32,5 a 22,0 R en NAS100, con R +1,3 / +2,6 / +11,1 y peor día de −3 R frente a −7,6 a −8,0 R.
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
| t-stat · IC 95% del R total | 1,99 · +5 a +218 |
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

1. **No hay ventaja fuera de tiempo demostrada.** La configuración se eligió mirando diciembre 2023 a noviembre 2026. En 2021-2023 (solo NAS100) dio +35,1 R, t = 0,76. El resultado de 2024 pesa casi la mitad del total.
2. **Sin ventaja neta demostrada**: t neto de 0,5 a 1,3 con un punto de costo; en NAS100 2021-2023 el equilibrio es 0,67 puntos.
3. No se evaluaron las reglas de Lucid Trading (tipo de drawdown, pérdida diaria, consistencia, contratos).
4. Fills ideales en el backtest, y días de cierre anticipado sin cierre forzado (por ejemplo el 19/06/2026).
5. NQ y NAS100 con «máx. 3» no se probaron con la gestión del día encendida en los archivos del periodo 2023-2026 (se aplicó por simulación, que es exacta). Solo el archivo de 2021-2023 trae el tope activo.

## 10. Próximos pasos

1. **Demo de 4 a 8 semanas** con la configuración recomendada y los costos reales de cada cuenta (MNQ y CFD).
2. Medir comisión, spread y slippage reales. Con NAS100 el equilibrio histórico va de 0,7 a 1,9 puntos según el periodo.
3. Si quieres más evidencia fuera de tiempo, probar otros mercados o periodos (por ejemplo NAS100 antes de 2021 si hay datos de 1 minuto) con la misma configuración, sin cambiar nada.
