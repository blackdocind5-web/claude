# Estrategia FVG · NQ · análisis de las 6 corridas · versión 1

Estrategia: `pine/nq_fvg.pine`. NQ, gráfico de 1 minuto, 03/01/2025 a 23/11/2026 (1,89 años, 23 meses). RR 2, SL máx. 140, hasta las 11:00, ambos modelos activos, riesgo 1% del capital inicial (10.000 USD sobre 1 millón), sin interés compuesto.
Resultados **brutos** (los CSV traen comisión 0). **R** es el R real de cada operación: PyG ÷ (contratos × 20 USD × distancia al SL). Difiere un poco del R nominal (PyG ÷ 10.000) porque los contratos son enteros: el riesgo real medio es de 9.320 USD, no 10.000.
Gráfico: `pine/fvg_analisis_curvas.png`.

## 0. Qué se analizó y qué no

| Corrida | Filtro | BE | Operaciones |
|---|---|---|---|
| 1 | ninguno | 1R | 242 |
| 2 | ninguno | no | 242 |
| 3 | EMA20 | 1R | 220 |
| 4 | EMA20 | no | 220 |
| 5 | VWAP | 1R | 219 |
| 6 | VWAP | no | 219 |

1. **Cada archivo trae el mismo conjunto de entradas con y sin BE** (242, 220 y 219 coincidentes en hora, dirección y precio). Eso permite comparar el BE operación por operación, sin ruido de muestra.
2. **El CSV no dice de qué modelo es cada operación.** La columna «Señal» solo trae BUY o SELL. **No se puede responder con estos archivos si el modelo 1 o el 2 es más ganador.** En la sección 5 está lo que sí se puede decir y el cambio de código que lo resuelve.
3. En 10 u 11 operaciones por corrida (cierre forzado a las 16:00 sin tocar SL ni TP) no hay distancia al SL en ningún archivo. Usé el SL estimado con los contratos (error de unos ±5% en esas operaciones).
4. Máximo 2 operaciones por día en todo el periodo (186 días con 1 y 28 con 2 en las corridas 1 y 2). Ninguna operación se solapa con otra y ninguna se cerró por inversión de lado.
5. No hay costos en los archivos. La sección 9 muestra el R neto con costos.

## 1. Veredicto

- **BE: apagado.** Sin BE gana +10,5 / +10,5 / +11,5 R más que con BE en las tres parejas (mismas entradas), en 2025 y en 2026 y en 14 o 15 de los 23 meses. El intervalo incluye el cero (−12 a +33 R), así que es una tendencia consistente pero no una prueba.
- **Filtros: VWAP sí, EMA20 no.** El filtro EMA20 descarta 25 operaciones que sumaban +14,0 R (esperanza +0,56 R) y resta 11 R. El VWAP descarta 28 que sumaban −1,0 R y suma +3,8 R. Ninguna diferencia es significativa (VWAP − sin filtro: −11 a +18 R). VWAP no daña y baja la caída máxima de 13,0 a 9,1 R; EMA20 es la peor de las tres, con y sin BE.
- **Combinación más ganadora de las 6: VWAP activo, sin BE.** +28,9 R, 219 operaciones, esperanza +0,132 R, caída máx. 9,1 R, 57% de meses positivos, positiva en 2025 (+7,3) y en 2026 (+21,6). Frente a «sin filtro, sin BE» (+25,2 R) la diferencia es ruido.
- **Horario: 11:05 no aporta.** Las entradas después de las 10:15 suman +0,5 R en 52 operaciones (VWAP, sin BE). Cortar a las 10:30 conserva el resultado (+28,2 R frente a +28,9 R) en las corridas sin BE y mejora +10 R en las corridas con BE. Cortar a las 09:45 o a las 10:00 no es estable (sección 6).
- **Límites diarios: no hacen falta.** La estrategia ya opera 1 o 2 veces por día. Limitarla a 1 resta entre 0 y 5,6 R. Parar tras un SL ahorra 1 a 3 R en 12 a 19 días: ruido.
- **Pareto: hay concentración, pero no es una ley demostrable.** El tramo 09:30–09:45 (32 a 36% de las operaciones) produce el 95% del R neto (corrida 2) y el 87% (corrida 6). Es el hallazgo más llamativo y también el menos fiable: p = 0,06 a 0,08 sin corregir y entre 0,3 y 0,4 corrigiendo por las cinco ventanas horarias probadas.
- **No hay ventaja estadística demostrada en ninguna corrida.** El mejor t es 1,37 (p = 0,09). Más de la mitad del R sale de un solo mes: **noviembre de 2026 aporta +14,5 R de los +25,2** (corrida 2). Sin él, +10,7 R en 22 meses; sin las 10 mejores operaciones, +5,2 R.
- **Frente a las estrategias anteriores: no es superadora en retorno** (13 a 15 R por año frente a ~29 R por año de la EMA20 en NQ en el mismo periodo). Es mejor en esperanza por operación y en robustez a costos, y opera 5 veces menos. Ver sección 10.

## 2. Las 6 corridas

| Métrica | 1 · sin filtro, BE | 2 · sin filtro, sin BE | 3 · EMA20, BE | 4 · EMA20, sin BE | 5 · VWAP, BE | **6 · VWAP, sin BE** |
|---|---|---|---|---|---|---|
| Operaciones (días) | 242 (214) | 242 (214) | 220 (197) | 220 (197) | 219 (197) | **219 (197)** |
| TP / SL / BE / cierre forzado | 61 / 109 / 69 / 3 | 84 / 148 / 0 / 10 | 51 / 100 / 66 / 3 | 73 / 137 / 0 / 10 | 55 / 95 / 65 / 4 | **77 / 131 / 0 / 11** |
| Win rate (TP sobre operaciones) | 25,2% | 34,7% | 23,2% | 33,2% | 25,1% | **35,2%** |
| **R bruto** | +14,7 | +25,2 | +3,7 | +14,2 | +17,5 | **+28,9** |
| IC 95% del R (bootstrap por días) | −22,7 a +53,4 | −18,8 a +70,5 | −30,6 a +38,9 | −26,9 a +56,2 | −17,8 a +54,0 | **−13,7 a +72,8** |
| Esperanza por operación | +0,061 | +0,104 | +0,017 | +0,064 | +0,080 | **+0,132** |
| t-stat · prueba de signos (p) | 0,78 · 0,22 | 1,14 · 0,14 | 0,21 · 0,42 | 0,68 · 0,25 | 0,98 · 0,17 | **1,37 · 0,09** |
| Factor de beneficio | 1,13 | 1,17 | 1,04 | 1,10 | 1,18 | **1,22** |
| Caída máxima (R) | 15,0 | 13,0 | 17,0 | 15,0 | 11,0 | **9,1** |
| Peor / mejor día (R) | −2,0 / +4,0 | −2,0 / +4,0 | −2,0 / +4,0 | −2,0 / +4,0 | −2,0 / +4,0 | −2,0 / +4,0 |
| Racha máx. de SL seguidos | 6 | 8 | 6 | 8 | 6 | 8 |
| Meses positivos (de 23) | 43% | 52% | 35% | 48% | 52% | **57%** |
| R 2025 / 2026 | −1,1 / +15,8 | +7,3 / +17,8 | −4,1 / +7,8 | +2,3 / +11,8 | −2,1 / +19,6 | **+7,3 / +21,6** |
| Neto USD (sobre 1 millón) | +137.080 | +233.030 | +35.980 | +131.755 | +160.835 | **+267.040** |
| Caída máx. en USD | 136.510 | 116.775 | 155.380 | 135.645 | 101.305 | **86.400** |
| Costo de equilibrio (puntos) | 3,6 | 6,1 | 1,0 | 3,8 | 4,8 | **7,9** |

El mejor día es +4 R en todas; el peor es −2 R (dos SL el mismo día). Hay operaciones en 197 a 214 de unos 475 días hábiles: opera casi 1 de cada 2 días (unas 10 operaciones al mes).

## 3. BE a 1R: apagado

Diferencia de R (sin BE menos con BE) con las mismas entradas:

| Pareja | ΔR | IC 95% (por días) | 2025 / 2026 | Meses a favor de «sin BE» |
|---|---|---|---|---|
| Sin filtro | +10,5 | −12,1 a +33,4 | +8,4 / +2,0 | 14 de 23 |
| EMA20 | +10,5 | −11,7 a +33,2 | +6,4 / +4,0 | 14 de 23 |
| VWAP | +11,5 | −9,9 a +34,3 | +9,4 / +2,0 | 15 de 23 |

Por qué: de las 69 operaciones que el BE sacó en cero (corrida 1), sin BE 23 habrían llegado al TP (+46 R), 39 habrían terminado en SL (−39 R) y 7 habrían cerrado a las 16:00. El BE a 1R regala más de lo que protege. Tampoco baja la caída máxima (15,0 R con BE y 13,0 R sin él).

Con RR 2 y sin BE, el win rate de equilibrio es 33,3%. El real es 34,7% a 35,2%: el margen es delgado y por eso depende tanto de un puñado de operaciones.

## 4. Filtros

| Comparación (sin BE) | Operaciones descartadas | R de las descartadas | ΔR | IC 95% |
|---|---|---|---|---|
| EMA20 − sin filtro | 25 (+3 de otro FVG) | +14,0 | −11,0 | −27,0 a +3,0 |
| VWAP − sin filtro | 28 (+5 de otro FVG) | −1,0 | +3,8 | −11,0 a +17,8 |
| VWAP − EMA20 | | | +14,8 | −4,0 a +34,2 |

Con BE el patrón es el mismo (EMA20 −11,0 R, VWAP +2,8 R). El EMA20 es el filtro que quita operaciones buenas (12 compras +3,0 R y 13 ventas +11,0 R). El VWAP quita 13 compras (−4,0 R) y 15 ventas (+3,0 R): casi neutro.

Mi lectura: **EMA20 desactivado**. VWAP activado es razonable porque no pierde R y suaviza la curva, pero su ventaja sobre no filtrar no se puede distinguir del azar.

## 5. Modelo de entrada: no se puede medir con estos archivos

- La columna «Señal» no distingue el modelo 1 del 2. Lo que se puede aproximar: el modelo 2 necesita quiebre, retroceso, impulso y FVG, así que en los primeros minutos casi todo es modelo 1. El tramo 09:30–09:45 es mayormente modelo 1, pero no exclusivamente, así que no es una medición.
- **Cambio de código (ya hecho en `nq_fvg.pine`)**: la señal de entrada ahora es «BUY M1», «BUY M2», «SELL M1» o «SELL M2». No cambia ninguna operación ni la etiqueta del gráfico. Con un solo CSV nuevo de la corrida 6 (VWAP, sin BE) puedo medir cada modelo por separado.

## 6. Horario

R por hora de entrada (R de cada tramo; n entre paréntesis):

| Tramo | Corrida 2 (sin filtro, sin BE) | Corrida 6 (VWAP, sin BE) | Corrida 1 (sin filtro, BE) | Corrida 5 (VWAP, BE) |
|---|---|---|---|---|
| 09:30–09:45 | +24,0 (87) | +25,0 (71) | +15,0 (87) | +17,0 (71) |
| 09:45–10:00 | −11,3 (67) | −11,3 (58) | +1,2 (67) | +0,2 (58) |
| 10:00–10:15 | +11,7 (38) | +14,7 (38) | +4,0 (38) | +6,0 (38) |
| 10:15–10:30 | +0,8 (22) | −0,2 (23) | +5,0 (22) | +4,0 (23) |
| 10:30–11:05 | 0,0 (28) | +0,8 (29) | −10,5 (28) | −9,7 (29) |

R acumulado si solo se acepta la entrada antes de la hora indicada:

| Corte | Corrida 2 | Corrida 6 | Corrida 1 | Corrida 5 |
|---|---|---|---|---|
| 09:45 | +24,0 (87) | +25,0 (71) | +15,0 | +17,0 |
| 10:00 | +12,7 (154) | +13,7 (129) | +16,2 | +17,2 |
| 10:15 | +24,4 (192) | +28,4 (167) | +20,2 | +23,2 |
| **10:30** | **+25,2 (214)** | **+28,2 (190)** | **+25,2** | **+27,2** |
| 10:45 | +27,6 (229) | +30,6 (205) | +20,2 | +22,2 |
| 11:05 (todo) | +25,2 (242) | +28,9 (219) | +14,7 | +17,5 |

- **El corte de las 10:30 es el único que no pierde R en las 4 corridas** (iguala el total sin BE y lo mejora con BE). Quita el 12–13% de las operaciones.
- **El tramo 09:30–09:45 es el único que es positivo en las 4 corridas y en los dos años** (corrida 6: +11,0 en 2025 y +14,0 en 2026). Con 5 tramos y 2 años, si cada signo fuera una moneda, la probabilidad de que algún tramo salga positivo en ambos años es de ~75%, así que no lo uso como regla.
- **El tramo 09:45–10:00 pierde 11 R sin BE** (p = 0,02 a 0,03 de que un subconjunto aleatorio del mismo tamaño sea tan malo, sin corregir) y por eso cortar a las 10:00 es peor que cortar a las 10:15. Es un hueco aislado, no una tendencia.
- Con BE, el tramo 10:30–11:05 pierde 10 R (win rate de 10%). Sin BE es neutro. Otra razón para apagar el BE.

## 7. Límites diarios

La estrategia es de 1 o 2 operaciones por día (máximo 4 por diseño, 2 observadas):

| | Corrida 2 | Corrida 6 | Corrida 1 | Corrida 5 |
|---|---|---|---|---|
| Solo la 1.ª del día | +21,4 | +23,3 | +14,7 | +13,5 |
| Todas (máx. 2) | +25,2 | +28,9 | +14,7 | +17,5 |
| Días con 2 operaciones | 28 | 22 | 28 | 22 |
| 2.ª tras SL de la 1.ª | −2,9 (19 días) | −2,0 (14) | −3,0 (16) | −1,0 (12) |
| 2.ª tras TP de la 1.ª | +6,7 (9 días) | +7,7 (8) | +4,0 (8) | +5,0 (7) |

Un tope de 1 por día resta entre 0 y 5,6 R (3,8 y 5,6 R sin BE). Parar tras un SL ahorra 1 a 3 R, con 12 a 19 días: no se distingue del azar. «Parar tras TP» no aplica (la 2.ª tras TP rindió +4 a +8 R en 7 a 9 días). **No agregaría ningún límite diario.**

## 8. Pareto

- **Operaciones**: el 20% mejor (48 de 242) suma +96,0 R, el 55% del bruto ganador (+173,8 R). Con pagos de +2 R y −1 R la concentración es mecánica: no hay un 80/20 escondido.
- **Fragilidad**: sin las 3 mejores operaciones, +19,2 R; sin las 5, +15,2; sin las 10, +5,2 (corrida 2). Con VWAP: +23,0 / +19,0 / +9,0.
- **Tiempo**: dos tramos del calendario concentran el resultado: noviembre-diciembre de 2025 (+13,4 R) y noviembre de 2026 (+14,5 R). Enero a octubre de 2025 sumó −6,1 R y enero a octubre de 2026 +3,3 R (corrida 2). Julio a octubre de 2026 (4 meses) suma −9,0 R. Que ambos meses fuertes sean noviembres no es una conclusión: son dos observaciones.
- **Horario**: la versión «20% del esfuerzo, 80% del resultado» sí aparece (09:30–09:45), pero ver sección 6.
- **Mensual** (corrida 2): sin el mejor mes, +10,7 R; los 3 mejores meses suman +27,9 R, el 111% del neto.

La curva (`pine/fvg_analisis_curvas.png`) muestra lo mismo: 2025 es plana o negativa hasta noviembre, 2026 sube hasta julio, cae de julio a octubre y se recupera en noviembre.

## 9. Costos

R neto según el costo por operación (comisión + spread + deslizamiento), en puntos de NQ, ida y vuelta, por contrato (1 punto = 20 USD):

| Corrida | 0 pt | 0,5 pt | 1,0 pt | 1,5 pt | 2,0 pt | 3,0 pt | Equilibrio |
|---|---|---|---|---|---|---|---|
| 2 · sin filtro, sin BE | +25,2 | +23,1 | +21,0 | +19,0 | +16,9 | +12,8 | 6,1 pt |
| **6 · VWAP, sin BE** | **+28,9** | +27,1 | **+25,3** | +23,5 | +21,6 | +18,0 | **7,9 pt** |
| 1 · sin filtro, BE | +14,7 | +12,6 | +10,6 | +8,5 | +6,5 | +2,4 | 3,6 pt |
| 5 · VWAP, BE | +17,5 | +15,7 | +13,8 | +12,0 | +10,2 | +6,5 | 4,8 pt |
| 4 · EMA20, sin BE | +14,2 | +12,3 | +10,5 | +8,6 | +6,8 | +3,0 | 3,8 pt |
| 3 · EMA20, BE | +3,7 | +1,8 | 0,0 | −1,9 | −3,7 | −7,4 | 1,0 pt |

Los costos pesan poco: se opera poco y el SL medio es de 68 puntos (mediana 64, rango 25 a 143). Con 1 punto de costo la corrida 6 sigue en +25,3 R. Los costos no son el problema de esta estrategia. La pregunta abierta es si hay ventaja: el t es de 1,4 aun sin costos.

## 10. Comparación con las estrategias anteriores

Las cifras de la EMA20 salen de `pine/mnq_ema20_gestion.md` (rango OFF, RR 2, BE a 1R, SL máx. 100, hasta las 11:00, máx. 3 por día; 01/12/2023 a 13/11/2026, 2,95 años). Para que el periodo sea comparable uso los R de 2025 y 2026 (1,87 años) de esa tabla.
**No tengo cifras de las estrategias de XAUUSD** (no quedaron registradas en el repositorio y no hay CSV de ellas en esta sesión). Si me pasas sus CSV, las agrego con el mismo método.

| Métrica | **FVG · NQ · VWAP, sin BE** (corrida 6) | **FVG · NQ · sin filtro, sin BE** (corrida 2) | EMA20 · NQ | EMA20 · MNQ | EMA20 · NAS100 (CFD) |
|---|---|---|---|---|---|
| Periodo | 03/01/2025 a 23/11/2026 | igual | 01/12/2023 a 13/11/2026 | igual | igual |
| Operaciones (por año) | 219 (116) | 242 (128) | 1.982 (672) | 1.979 (671) | 1.988 (674) |
| Win rate (TP sobre operaciones) | 35,2% | 34,7% | 27,8% | 27,1% | 27,4% |
| R bruto total | +28,9 | +25,2 | +122,7 | +108,6 | +118,0 |
| **R por año, mismo periodo** (entre paréntesis el total de 2025 + 2026) | **+15,3** | **+13,3** | **+29,4** (+54,9) | **+29,5** (+55,2) | **+25,0** (+46,8) |
| R por año, periodo completo de cada una | +15,3 | +13,3 | +41,6 | +36,8 | +40,0 |
| Esperanza por operación | **+0,132 R** | +0,104 R | +0,062 R | +0,055 R | +0,059 R |
| t-stat · años | 1,37 · 1,9 | 1,14 · 1,9 | 2,34 · 2,95 | 1,99 · 2,95 | 2,14 · 2,95 |
| Caída máx. (R) | **9,1** | 13,0 | 18,9 | 26,9 | 22,0 |
| R por año ÷ caída máx. (periodo completo) | 1,7 | 1,0 | 2,2 | 1,4 | 1,8 |
| Peor día | **−2,0 R** | −2,0 R | −3,0 R | −3,0 R | −3,2 R |
| Meses positivos | 57% | 52% | 67% | 72% | 61% |
| R neto con 1 pt de costo (por año) | +25,3 (+13,4) | +21,0 (+11,1) | +63,6 (+21,6) | +48,3 (+16,4) | +55,5 (+18,8) |
| Costo de equilibrio | **7,9 pt** | 6,1 pt | 2,07 pt | 1,80 pt | 1,89 pt |
| Fuera de tiempo | no hay | no hay | NAS100 2021–23: +35,1 R, t = 0,76 | — | — |
| Mejor mes sobre el total | 33% (+9,5 R) | 58% (+14,5 R) | — | — | — |

**Lectura**

- **Retorno: la EMA20 gana.** En el mismo periodo rinde ~29 R por año frente a 13 a 15 R de la FVG, es decir, el doble. Con 1 punto de costo la diferencia se acorta (FVG +13,4 R por año; EMA20 en NQ +21,6 R por año, medido en su periodo completo).
- **Calidad por operación: la FVG gana.** La esperanza es el doble (+0,13 frente a +0,06 R) y el costo de equilibrio es de 6 a 8 puntos frente a 1,8 a 2,1. Es una estrategia más barata de operar, con 5 veces menos operaciones.
- **Riesgo: empate técnico.** Caída máx. y peor día más bajos en la FVG, pero con la mitad del retorno; el cociente R por año ÷ caída es de 1,0 a 1,7 frente a 1,4 a 2,2.
- **Evidencia: ninguna está demostrada.** La EMA20 tiene t = 2,3 en 2,95 años, pero en 2021–2023 (NAS100) bajó a 0,76. La FVG tiene t = 1,1 a 1,4 en 1,9 años y no tiene un periodo fuera de tiempo.
- **¿Superadora? No, no todavía.** No supera a la EMA20 en R por año. Es, en cambio, una estrategia distinta (pocas operaciones, SL grandes, entradas límite en el hueco) que podría complementarla. No sé si sus resultados se correlacionan: eso requiere los CSV de ambas en el mismo periodo.

## 11. Lo que no está probado

1. **El tamaño de la muestra:** 242 operaciones en 1,9 años. Hace falta ampliar el periodo. Correr desde 01/12/2023, como se hizo con la EMA20, permite comparar ambas en las mismas fechas.
2. **Hay una elección dentro de la muestra.** Las 6 corridas se miraron sobre los mismos datos; la elección de «VWAP, sin BE, 10:30» sale de ellos. La prueba real es un periodo posterior o anterior que no se haya mirado.
3. **Los modelos 1 y 2 no se separaron** (sección 5).
4. **Reglas de Lucid Trading:** no se evaluaron (tipo de drawdown, pérdida diaria, contratos, consistencia).
5. **Fills ideales:** las órdenes límite se llenan al tocar el nivel; en la práctica, parte de los toques no se ejecuta. Los costos de 0 en el CSV no incluyen comisión ni deslizamiento.
6. **Noviembre de 2026** es un mes incompleto y concentra más de la mitad del R de la corrida 2.

## 12. Próximos pasos

1. **Un CSV nuevo de la corrida 6** (VWAP activado, sin BE, resto igual) con el código actualizado: la señal trae el modelo y se puede medir cada uno.
2. **Mismo CSV con el periodo ampliado hacia atrás (01/12/2023 a 31/12/2024)** para tener un periodo fuera de la muestra y compararlo con la EMA20 en las mismas fechas.
3. **No tocar parámetros** (BE, RR, hora, filtro) hasta tener esos dos resultados. Si el modelo 2 resultara negativo en el periodo nuevo, se evalúa apagarlo; si no, no hay nada que ajustar.
4. **Demo de 4 a 8 semanas** con VWAP, sin BE, hasta las 10:30 o las 11:00, para medir comisión, spread y deslizamiento reales de NQ.
