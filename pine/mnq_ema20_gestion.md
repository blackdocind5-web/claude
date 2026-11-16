# MNQ · EMA20 · Gestión del día · versión 2 (datos MNQ reales)

Estrategia: `pine/mnq_ema20_tendencia.pine` (Pine v6, gráfico de 1 minuto, MNQ).
Periodo analizado: 01/12/2023 a 13/11/2026 (2,95 años, 756 días). Corrida sin rango de apertura, RR 2,0, BE a 1R, hasta las 11:00, con el código que agota el retroceso al entrar.
Todos los resultados son **brutos** (los CSV traen comisión 0) salvo donde se indica «neto».

> **Corrección.** La versión anterior de este documento usaba como «validación» dos CSV de dic-2023 a dic-2024 que **no eran de MNQ**: sus precios no caen en la cuadrícula de 0,25 puntos del MNQ (solo el 18% lo hace) y cada punto valía 1 USD en vez de 2, como en un CFD. Esos números y las conclusiones que dependían de ellos se retiran: la «ganancia de +61,1 R en validación», la «ventaja de operar sin rango en validación» y las cifras de caída, rachas y costos de esa versión. Esta versión usa solo la corrida MNQ del 01/12/2023 al 13/11/2026.

## 1. Veredicto

- La estrategia muestra una esperanza pequeña y positiva (+0,04 a +0,06 R por operación) que **no se distingue del azar** en 35 meses de MNQ: t entre 1,7 y 2,0 y el intervalo del R total incluye el 0.
- **«Primer TP o 3 SL» ya no es la gestión ganadora.** En dic-2023 a dic-2024 dio +15,4 R, frente a +58,3 R sin gestión. En 2025-2026 dio +74,7 R. Su efecto cambia de signo entre periodos.
- La gestión más estable y con mejor control del riesgo es **«máximo 3 operaciones por día»**. Es un control de riesgo, no una ventaja demostrada: se eligió mirando estos mismos datos entre 14 reglas, y la mejor regla del conjunto tiene p = 0,38 al corregir por haber probado varias.
- Con costos reales de 2 a 3 USD por contrato, el resultado neto es pequeño (+48 a +18 R en 35 meses con esta gestión).

## 2. Qué cambió en el código

1. **Gestión del día programada** (grupo 8 de los ajustes). Comprobación: con la gestión activada, TradingView da 1.652 operaciones; aplicar la misma regla sobre el CSV sin gestión de la misma corrida da exactamente las mismas 1.652 (+90,18 R). La programación coincide con la simulación.
2. **Un retroceso se agota cuando se entra en él.** Para volver a entrar hace falta una vela en contra nueva. Efecto medido en MNQ 2025-nov 2026 (único tramo donde se puede comparar la versión anterior con la nueva en el mismo instrumento): sin gestión pasa de 1.697 a 1.679 operaciones (+45,0 a +49,0 R); con gestión da exactamente lo mismo (1.073 operaciones, +74,7 R), porque casi todas las entradas que desaparecen eran reentradas después de un TP, que la gestión ya bloqueaba.

## 3. Reglas de la gestión del día (interruptores)

| Interruptor | Valor para «máximo 3 por día» |
|---|---|
| Gestión del día | Activada |
| Parar el día tras el primer TP | Desactivado |
| Máximo de SL seguidos | 0 (sin límite) |
| El BE cuenta como… | Neutro |
| Máximo de operaciones por día | 3 |
| Parar al llegar a +X R | 0 (apagado) |

Resto de la configuración: rango de apertura desactivado, RR 2,0, BE activado a 1R, SL máximo 100 puntos, entradas hasta las 11:00, cierre forzado a las 16:00, riesgo 1% sin interés compuesto.

El freno solo impide abrir entradas nuevas. Con 3 operaciones como máximo, el peor día posible es de unos −3 R (o −3,05 R con deslizamiento).

## 4. Resultados (MNQ, 01/12/2023 a 13/11/2026)

| | Sin gestión | **Máx. 3 por día** | Primer TP o 3 SL |
|---|---|---|---|
| Operaciones | 2.507 | 1.979 | 1.652 |
| TP / SL / BE | 668 / 1.230 / 603 | 537 / 967 / 470 | 452 / 815 / 381 |
| **Win rate** (TP sobre operaciones) | 26,7% | **27,1%** | 27,4% |
| Win rate sin contar BE | 35,2% | 35,7% | 35,7% |
| **R bruto total** | +107,3 | **+108,6** | +90,2 |
| R dic-2023 a dic-2024 | +58,3 | +53,3 | +15,4 |
| R 2025 a nov-2026 | +49,0 | +55,3 | +74,7 |
| Esperanza por operación | +0,043 R | +0,055 R | +0,055 R |
| t-stat (por días) | 1,73 | 1,99 | 1,82 |
| IC 95% del R total | −11 a +229 | −2 a +214 | −8 a +190 |
| Factor de beneficio | 1,09 | 1,11 | 1,11 |
| **Caída máxima** | 35,5 R | **26,9 R** | 39,5 R |
| Caída a planificar (p95) | 75 R | 61 R | 61 R |
| Peor / mejor día | −7,95 / +8,94 R | −3,00 / +6,00 R | −3,00 / +2,00 R |
| Días positivos / negativos | 49% / 47% | 50% / 45% | 57% / 38% |
| Meses positivos | 61% (22 de 36) | **72% (26 de 36)** | 69% (25 de 36) |
| Peor / mejor mes | −16,9 / +19,9 R | −14,9 / +24,9 R | −18,9 / +16,8 R |
| **Racha máxima de SL seguidos** | 9 | **10** | 10 |
| Racha máxima de operaciones sin TP | 21 | 20 | 19 |
| Máx. días negativos seguidos | 12 | 7 | 6 |

Por año con «máx. 3 por día»: 2023 (solo diciembre) −10,0 R · 2024 +63,3 R · 2025 +22,3 R · 2026 (hasta el 13/11) +32,9 R.

### 4.1 Rentabilidad en % con «máx. 3 por día» (sin interés compuesto)

| Riesgo por R | Bruto total (por año) | Neto con 2 USD por contrato (por año) | Caída máx. histórica | Caída a planificar (p95) | Peor día |
|---|---|---|---|---|---|
| 1,00% | +108,6% (+37%/año) | +48,3% (+16%/año) | −26,9% | −61% | −3,0% |
| 0,50% | +54,3% (+18%/año) | +24,2% (+8%/año) | −13,4% | −31% | −1,5% |
| 0,25% | +27,1% (+9%/año) | +12,1% (+4%/año) | −6,7% | −15% | −0,75% |

La caída «a planificar» sale de remuestrear los días 3.000 veces (percentil 95). La caída real fue más benigna que ese valor.

## 5. Costos

| Costo ida y vuelta por contrato | Sin gestión | Máx. 3 por día | Primer TP o 3 SL |
|---|---|---|---|
| 0 USD | +107,3 | +108,6 | +90,2 |
| 1 USD | +69,5 | +78,5 | +65,0 |
| 2 USD | +31,7 | +48,3 | +39,9 |
| 3 USD | −6,1 | +18,2 | +14,7 |
| **Punto de equilibrio** | 2,84 USD | 3,60 USD | 3,59 USD |

Con el SL mediano de 37 puntos, 2 USD por contrato cuestan 0,03 R por operación. Comisión y slippage reales (incluidos los de los stops y los BE) hay que medirlos en tu cuenta.

## 6. Lo que ya no se afirma

- Que el rango de apertura perjudique. La evidencia de 2025-2026 (con rango −32,5 R frente a sin rango, intervalo de −72 a +7) es débil, y la de 2023-2024 era de otro instrumento. Falta una corrida de MNQ con rango.
- Que cortar a las 10:30 o a las 11:00 cambie algo. Sin gestión: dic-2023 a dic-2024 dio +36,1 R con corte a las 10:30 y +58,3 R a las 11:00; 2025-2026 dio +67,2 R y +49,0 R. Sin patrón estable.
- Que la gestión del día agregue rentabilidad. Contra el azar, la regla «primer TP o 3 SL» dio p = 0,95 en 2023-2024 y p = 0,04 en 2025-2026.

## 7. Consideraciones

1. **Tamaño**: con 1 millón de capital se usan cientos de contratos. Ajusta al capital real de la cuenta y revisa el máximo de contratos de la firma.
2. **Reglas de Lucid Trading** (tipo de drawdown, pérdida diaria, consistencia, contratos): no evaluadas.
3. **Días de cierre anticipado** (por ejemplo el 19/06/2026): el cierre forzado de las 16:00 puede no ejecutarse. Cierra a mano esos días.
4. **Fills ideales** en el backtest (stops, BE y TP al precio exacto). Los reales traerán slippage.

## 8. Próximos pasos

1. Corrida de **MNQ con rango activado**, del 01/12/2023 al 13/11/2026, sin gestión y con «máx. 3 por día», para decidir con datos reales si el rango se usa.
2. Prueba fuera de tiempo: el mismo código sobre NAS100 (CFD) de 2021 a nov-2023, sin gestión. Es otro instrumento, pero otro periodo.
3. Demo de 4 a 8 semanas con los costos reales de tu cuenta.
