# MNQ · EMA20 · Gestión recomendada: sin rango + «primer TP o 3 SL»

Estrategia: `pine/mnq_ema20_tendencia.pine` (Pine v6, gráfico de 1 minuto, MNQ).
Periodo analizado: 01/12/2023 a 13/11/2026 (2,95 años, 754 días, 1.664 operaciones).
Todos los resultados son **brutos** (los CSV traen comisión 0) salvo donde se indica «neto».

## 1. Veredicto

- Es la mejor combinación de las probadas y **sigue siendo positiva fuera de la muestra** con la que se eligió (dic-2023 a dic-2024: +61,1 R).
- Es una **candidata prometedora, no una ventaja validada**: t = 2,76 en todo el periodo (2,12 en la validación), por debajo del umbral de 3 que nos fijamos, y la ganancia neta depende mucho de los costos (punto de equilibrio: 3,66 USD por contrato ida y vuelta).
- La gestión del día **no aporta más rentabilidad**: baja la caída y limita el peor día. La rentabilidad viene de la estrategia base.

## 2. Reglas

### 2.1 Configuración de la estrategia (grupo / valor)

| Parámetro | Valor |
|---|---|
| Entradas | 09:30 a 10:59 (hora de Nueva York), hasta las 11:00 |
| Patrón | Quiebre + retroceso + continuación a la EMA20 (sin cambios) |
| Salida | RR 1:2 · break-even a 1R activado |
| SL | Swing M1, máximo 100 puntos (se reduce al extremo de la vela de entrada; si aún llega a 100, no se opera) |
| Cierre forzado | 16:00 |
| Riesgo | 1% del capital inicial por operación, sin interés compuesto, una posición a la vez |
| **Rango de apertura** | **Desactivado** (interruptor del grupo 7) |

### 2.2 Gestión del día (programada como interruptores, grupo 8 del código)

Cada día se opera con normalidad y el día **termina con lo primero que ocurra**:

1. **Un TP**: no se opera más ese día.
2. **El 3.er SL del día**: no se opera más ese día.
3. Se llega a las 10:59 (o a la hora de corte).

El **BE no cuenta como SL ni cierra el día**: se sigue operando y no reinicia el conteo de SL.

Ejemplos: TP = +2 R · BE → BE → TP = +2 R · SL → TP = +1 R · SL → BE → TP = +1 R · SL → SL → TP = 0 R · SL → BE → SL → SL = −3 R.

**El mejor día posible con esta regla es +2 R** (un TP sin SL previos, con cualquier cantidad de BE antes). El día de +1 R (un SL y luego un TP) **se cierra ahí**: la regla no sigue operando.

**¿Conviene seguir tras SL → TP?** No hay evidencia a favor. Sumando los 150 días de este tipo (sin rango, 11:00), seguir operando rindió en promedio −0,10 R por día (IC 95% de −0,34 a +0,14): 29% de esos días terminó peor que +1 R, 49% igual y 21% mejor, con un peor caso de −5 R. Tras un TP sin SL previos (+2 R) fue −0,05 R por día. Probar «parar a +2 R del día» en vez del primer TP dio +55,7 R (validación) y +47,4 R (2025-2026) frente a +61,1 y +74,7 con el primer TP, y con más caída.

### 2.3 Frenos y límites

| Freno | Valor | Efecto |
|---|---|---|
| Tope de pérdida diaria | 3 SL | Peor día histórico −3,05 R (sin la regla: −8 R) |
| Cierre por ganancia | 1.er TP | Mejor día histórico +2,02 R |
| Tope de SL por operación | 100 puntos | Evita operaciones con riesgo desmedido |
| Operaciones por día | Sin tope fijo (media 2,2) | Lo limitan el TP y los 3 SL |
| Posiciones simultáneas | 1 | — |
| Horario | 09:30 a 11:00 + cierre 16:00 | — |

## 3. Cómo terminan los días

| Final del día | % de días | Resultado del día | Operaciones (media) |
|---|---|---|---|
| TP sin SL previos | 34,1% | +2 R | 1,2 |
| TP tras 1 SL | 19,9% | +1 R | 2,4 |
| TP tras 2 SL | 8,6% | 0 R | 3,3 |
| 3 SL | 13,5% | −3 R | 3,5 |
| Llegan las 11:00 sin TP ni 3 SL | 23,9% | −1,2 R (media) | 2,3 |

## 4. Resultados

| | Validación: dic-2023 a dic-2024 | Diseño: 2025 a nov-2026 | Total |
|---|---|---|---|
| Días operados | 273 | 481 | 754 |
| Operaciones | 591 | 1.073 | 1.664 |
| TP / SL / BE | 171 / 282 / 137 | 301 / 526 / 245 | 472 / 808 / 382 |
| **Win rate** (TP sobre operaciones) | 28,9% | 28,1% | **28,4%** |
| Win rate sin contar los BE | 37,7% | 36,4% | 36,9% |
| **R bruto** | +61,1 | +74,7 | **+135,8** |
| Esperanza por operación | +0,103 R | +0,070 R | +0,082 R |
| Esperanza por día | +0,22 R | +0,16 R | +0,18 R |
| Factor de beneficio | 1,22 | 1,14 | 1,17 |
| t-stat (por días) | 2,12 | 1,87 | 2,76 |
| IC 95% del R total | +4,8 a +119,0 | −5,5 a +152,6 | +39,6 a +231,6 |
| Días positivos / negativos / neutros | 59,7 / 35,2 / 5,1% | 58,2 / 37,8 / 4,0% | 58,8 / 36,9 / 4,4% |
| Meses positivos | 10 de 13 | 16 de 23 | 26 de 36 (72%) |
| Mejor / peor mes | +21,1 / −13,0 R | +16,8 / −12,9 R | +21,1 / −13,0 R |
| **Caída máxima** (operación a operación) | 24,0 R | 16,9 R | **24,0 R** |
| Peor día | −3,05 R | −3,00 R | −3,05 R |
| **Racha máxima de SL seguidos** | 7 | 7 | **7** |
| Racha máxima de operaciones sin TP (SL o BE) | 11 | 17 | 17 |
| Racha máxima de días negativos | 5 | 5 | 5 |

Por año: 2023 (solo diciembre) −1,0 R · 2024 +62,1 R · 2025 +40,8 R · 2026 (hasta el 13/11) +33,9 R.

La caída máxima fue del 20/02/2024 al 05/04/2024, y el mayor tiempo sin nuevo máximo fue de 125 días (20/02/2024 a 24/06/2024).

### 4.1 Rentabilidad en % según el riesgo por operación (sin interés compuesto)

| Riesgo por R | Bruto total (≈ por año) | Neto con 2 USD por contrato | Caída máx. histórica | Caída máx. a planificar (p95) | Peor día |
|---|---|---|---|---|---|
| 1,00% | +135,8% (+46%/año) | +61,6% (+21%/año) | −24,0% | −50% | −3,05% |
| 0,50% | +67,9% (+23%/año) | +30,8% (+10%/año) | −12,0% | −25% | −1,52% |
| 0,25% | +34,0% (+11%/año) | +15,4% (+5%/año) | −6,0% | −12,5% | −0,76% |

La caída «a planificar» sale de remuestrear los días 4.000 veces: la mediana fue 28 R, el percentil 90 fue 43 R y el 95 fue 50 R. La caída real (24 R) fue más benigna que la mediana, así que no conviene tomarla como techo.

## 5. Costos

| Costo ida y vuelta por contrato | R neto total |
|---|---|
| 0 USD | +135,8 |
| 1 USD | +98,7 |
| 2 USD | +61,6 |
| 3 USD | +24,5 |

- **Punto de equilibrio: 3,66 USD** (2,64 en la validación, 5,34 en 2025-2026).
- El costo en R depende del SL en puntos. En 2024 el SL mediano era de 13,6 puntos (≈ 367 contratos) y 2 USD costaban 0,078 R por operación. En 2025-2026 era de 43 puntos (≈ 116 contratos) y costaban 0,026 R.
- Comisión y slippage reales (incluido el de los stops y los BE) hay que medirlos en tu cuenta antes de operar.

## 6. Por qué sin rango y por qué 11:00

- **Sin rango frente a con rango, con la misma gestión**: con rango da +57,4 R en total (sin rango +135,8), caída 31 R (sin rango 24 R) y racha de 14 SL (sin rango 7). La diferencia es −78,5 R, IC 95% de −133 a −27. En la validación sola: −45,9 R, IC de −81 a −13. Sin gestión del día, la diferencia es −41,6 R, IC de −91 a +6.
- **Corte a las 11:00 frente a las 10:30**: con la gestión, +61,1 frente a +35,9 R en la validación y +74,7 frente a +59,8 R en 2025-2026. Se queda en 11:00. El indicio de que 10:30 a 11:00 perdía no se repitió en la validación.
- **La gestión del día frente a no ponerla**: en la validación dio +61,1 R frente a +64,7 R, con caída de 24 R frente a 33 R y peor día de −3 R frente a −5 R. En 2025-2026 dio +74,7 R frente a +45,0 R. Contra el azar (permutación): p = 0,03 en 2025-2026 y p = 0,18 en la validación. Es control de riesgo; no hay prueba de que sume rentabilidad.

## 7. Consideraciones importantes

1. **Las reglas del día ya están en el código, pero no se han compilado en TradingView.** Los números salen de recortar los días de tus CSV (exacto porque se opera de a una); hay que comprobar que el backtest en TradingView da lo mismo. Configuración para reproducirlo: rango OFF · RR 2,0 · BE ON a 1R · SL máx. 100 · hasta las 11:00 · gestión del día ON · primer TP ON · 3 SL seguidos · BE neutro · máx. operaciones 0 · parar a +X R 0.
2. **La regla se eligió mirando 2025-2026**, y se probó después en 2024. Esa es la única validación independiente que existe.
3. **Rachas esperables**: 7 SL seguidos, 17 operaciones sin TP, 5 días negativos seguidos, mes de −13 R y 125 días sin nuevo máximo. Con 1% de riesgo eso son caídas de dos dígitos.
4. **Tamaño**: con 1 millón de capital llegó a 1.176 contratos en las entradas con SL corto. Hay que ajustar al capital de la cuenta, revisar el máximo de contratos de la firma y recordar que el redondeo hacia abajo reduce el riesgo real en cuentas pequeñas.
5. **Sin evaluar**: reglas de Lucid Trading (tipo de drawdown, pérdida diaria, regla de consistencia, límite de contratos). Hay que pasarlas por el reglamento antes de elegir el riesgo.
6. **Días de cierre anticipado** (por ejemplo el 19/06/2026): el cierre forzado de las 16:00 no se ejecuta si el mercado ya cerró. En una versión sin BE eso dejó una operación abierta hasta el domingo, con −2,82 R. Hay que cerrar a mano esos días.
7. **Los fills del backtest son ideales** (stops, BE y TP al precio exacto, bar magnifier). Los reales traerán slippage.

## 8. Siguientes pasos

1. Correr el backtest con la configuración de la sección 7 (punto 1) y comprobar que reproduce los números de arriba (sobre todo diciembre 2023 a diciembre 2024: +61,1 R y 591 operaciones; 2025 a nov-2026: +74,7 R y 1.073 operaciones). Pequeñas diferencias son normales si cambiaste costos.
2. Si no coincide, mandarme el CSV y las etiquetas «Fin del día» de un día concreto para ubicar la diferencia.
3. Operar en demo 4 a 8 semanas con los costos reales de tu cuenta y medir la comisión y el slippage efectivos.
4. Definir el riesgo por operación a partir de la caída máxima que permita la firma (guía: caída permitida dividida entre 50 R).
