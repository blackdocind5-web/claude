# Estrategia FVG · especificación v1 (para NQ)

Gráfico de 1 minuto, hora de Nueva York (NY). Mismo código válido para MNQ, NQ y NAS100; el backtest profundo se hará solo en **NQ** (1 punto = 20 USD, tick 0,25, contratos enteros).
Todo lo de abajo se explica para **ventas**; las compras son el espejo exacto. «Puntos» y «pips» se tratan como puntos de precio.

## 1. Parámetros editables

| Parámetro | Por defecto |
|---|---|
| Inicio y fin del rango de apertura | 09:00 a 09:30 |
| Hora límite (quiebre, pasos, FVG, vencimiento de órdenes) | 11:00 |
| Cierre forzado | 16:00 |
| Quiebre mínimo del rango (cierre fuera del borde) | 5 puntos |
| Cuerpo mínimo de la vela 2 del FVG | 30 puntos |
| Tamaño mínimo de la zona del FVG | 12 puntos |
| Margen del SL sobre su nivel base | 5 puntos |
| SL máximo | 140 puntos |
| RR mínimo hasta el extremo del movimiento (solo modelo 1) | 0,9 |
| RR del TP | 2,0 |
| BE | activado, a 1R |
| Filtro EMA20 · filtro VWAP | ambos apagados |
| Riesgo por operación | 1% del capital inicial, sin interés compuesto |
| Interruptor por modelo (1 y 2) | ambos activados |

## 2. Definiciones comunes

**Rango de apertura.** Máximo y mínimo, con mechas, de las velas que abren entre 09:00 y 09:30. Contorno negro, sin relleno.

**Quiebre válido.** Una vela con el color de la dirección (bajista abajo, alcista arriba), que abre desde las 09:30 y antes de la hora límite, y **cierra** fuera del rango por al menos 5 puntos. Una mecha sin cierre fuera no cuenta. Un cierre fuera por menos de 5 puntos no cuenta ni apaga nada. El lado superior y el inferior se evalúan por separado, cada uno con su primer quiebre válido del día.

**FVG bajista.** Tres velas consecutivas (1, 2 y 3) con hueco real entre la mecha inferior de la vela 1 y la mecha superior de la vela 3: máximo(3) < mínimo(1). La zona va de máximo(3) a mínimo(1) y su tamaño es mínimo(1) − máximo(3). Se confirma al cierre de la vela 3. La vela 2 tiene siempre el color de la dirección y un cuerpo (|cierre − apertura|) de al menos 30 puntos.

**SL (ventas).** Nivel base + 5 puntos:
- Si la vela 1 tiene el color de la vela 2: el máximo de la primera vela de la racha ininterrumpida de velas bajistas que contiene la vela 2.
- Si la vela 1 es de otro color: el alto M1 vigente que la incluye. Un alto M1 es una vela alcista seguida de una bajista, con el mayor de los dos máximos, mecha incluida. La vela 3 no influye.
- **Tope:** si la distancia entrada–nivel base + 5 supera 140 pero la distancia al nivel base no, el SL va en el nivel base, sin los 5 puntos. Si la distancia al nivel base supera 140, el FVG se descarta directamente (sin probar el 50% del modelo 1).

**Entrada.** Orden límite en el borde del FVG por el que el precio retrocede (ventas: borde inferior; compras: borde superior). Se ejecuta en cuanto el precio toca el nivel. **TP:** RR × riesgo. **BE:** al tocar 1R el SL pasa a la entrada desde la vela siguiente.

**Una operación abierta a la vez.** Si el nuevo FVG del **lado contrario** se activa con una operación abierta, esta se cierra de inmediato al precio de entrada de la nueva orden. Si la operación abierta es del **mismo lado** y de otro modelo, no se cierra: la orden nueva no se abre, ese FVG se pierde y no consume la operación de ese lado en el día.

## 3. Modelo 1 · FVG en rango

1. **Quiebre válido** del lado (primer quiebre del día).
2. **FVG principal.** Sea X la vela del quiebre.
   - **Caso A:** X es la vela 2. La vela 1 es X−1 (de cualquier color) y la vela 3 es X+1 (de cualquier color).
   - **Caso B:** X es la vela 1, y la vela 2 es X+1 con el mismo color que X. La vela 3 es X+2 (de cualquier color).

   Al cierre de X+1 se prueba A. Si no hay hueco pero X+1 tiene el color de la dirección, se espera a X+2 y se prueba B. **Sin FVG principal, el modelo 1 de ese lado queda apagado el resto del día.**
3. **Filtros** (cada uno descarta solo ese FVG): cuerpo de la vela 2 ≥ 30; zona ≥ 12; **contacto con el rango** (la zona está dentro del rango, o toca o cruza un extremo); SL ≤ 140. En el caso B el hueco queda fuera del rango, así que ese FVG se descarta y se pasa al siguiente.
4. **FVG alternativos.** Si se descarta el FVG principal, se prueban los anteriores del mismo movimiento (la racha ininterrumpida de velas del color de la dirección que contiene la vela de quiebre; ninguna vela contraria entre el FVG y la vela de quiebre). El orden es el que el precio toca primero al retroceder. Todos pasan los mismos filtros. No se buscan FVG formados después. Si no queda ninguno, el lado queda apagado el resto del día.
5. **RR mínimo.** Al tocar el borde se mide: recorrido de la entrada hasta el extremo del movimiento (el mínimo más bajo, con mecha, desde la vela de quiebre incluida hasta la vela **anterior** a la del toque) dividido por la distancia al SL. Si es ≥ 0,9 se ejecuta. Si no, la entrada pasa al 50% del FVG con el mismo SL y se vuelve a medir. Si tampoco llega, se descarta ese FVG.
6. **Orden pendiente.** Una a la vez. Vence a la hora límite. La cancela un FVG confirmado del lado contrario (el modelo 1 de ese lado queda apagado el resto del día) o el paso 3 del modelo 2 del mismo lado.
7. **Límite:** una operación por lado en el día.

## 4. Modelo 2 · FVG en tendencia

**Pasos por lado.**
1. **Quiebre válido** del rango, el mismo del modelo 1.
2. **Retroceso:** una vela de color contrario después de la vela de quiebre.
3. **Impulso:** una vela con el color de la dirección cierra con cuerpo más allá de la **referencia**.

**Referencia.** El punto bajo M1 más bajo confirmado desde el quiebre, incluido el del retroceso. Un punto bajo M1 es una vela bajista seguida de una alcista, con el mínimo de ambas, mecha incluida. En compras es el alto M1 más alto. Solo la desplaza un punto M1 confirmado más extremo que el actual. Los puntos M1 menos extremos de una consolidación no la cambian.

**Impulso y FVG.**
- En una racha continua, cada vela que cierra más allá de la referencia cuenta como impulso, sin exigir un retroceso nuevo.
- Un intento fallido es una vela que hace un mínimo más bajo sin cerrar por debajo de la referencia. Solo la desplaza si luego una vela alcista forma un nuevo punto bajo M1 más bajo.
- La vela que rompe la referencia es la 1, 2 o 3 del FVG. Si es la 1 o la 3, debe ser del color de la vela 2.
- Rigen los filtros del modelo 1 (cuerpo de la vela 2 ≥ 30, zona ≥ 12, colocación del SL, tope de 140). **No rigen** el contacto con el rango, el RR mínimo ni el 50%.
- Si el impulso no genera un FVG válido, se descarta ese impulso y se espera el siguiente. El modelo sigue vivo el resto del día.
- Una orden pendiente se reemplaza por la del último impulso válido con FVG. Vence a la hora límite.

**Cambio de dirección.** Cuando el lado contrario confirma su paso 3 o un FVG, se cancela la orden pendiente de este lado porque la dirección cambió. El modelo 2 de este lado **no** queda descartado el resto del día: queda en espera de realinearse. La realineación ocurre cuando una vela con el color de este lado cierra con cuerpo más allá del último M1 creado antes del cambio. Después se repiten los pasos 2 y 3 (retroceso e impulso más allá de la referencia confirmada desde la realineación) con un FVG válido. En el ejemplo de tus imágenes: el paso 3 bajista a las 09:40 → el cambio a alcista a las 09:58 → la vela bajista de las 10:20 que cierra por debajo del bajo M1 → retroceso → impulso con FVG → venta.

**Con el modelo 1.** Al confirmarse el paso 3, el modelo 1 de ese lado se descarta: se cancelan sus pendientes y no abre nuevas. Una operación ya ejecutada sigue abierta. Si el modelo 1 apagó el lado por falta de FVG principal, el modelo 2 sigue activo.

**Límite:** una operación por lado en el día para este modelo.

## 5. Reglas globales

- **Sin gestión del día.** Los límites de «una operación por lado y modelo» ya acotan las operaciones: como máximo 4 en el día.
- **Etiqueta de entrada:** solo «BUY» o «SELL», sin el modelo.
- **Visual:** contorno negro del rango, rectángulo gris del FVG, líneas de SL, BE y TP.
- **Filtros EMA20 y VWAP** (apagados por defecto): una compra solo vale con la entrada por encima de la EMA20 y del VWAP, y una venta por debajo. El VWAP usa hlc3 y se reinicia a las 18:00 NY.
- **Backtest:** las órdenes límite se llenan al tocar el nivel, con las velas de menor temporalidad (bar magnifier). Los costos se configuran en Propiedades de TradingView.

## 6. Pendiente de confirmar

1. **Nivel de realineación.** Entiendo que es la referencia vigente (el bajo M1 más bajo) cuando se confirmó el cambio de dirección. ¿O es el último bajo M1 formado antes del paso 3 contrario?
2. **Alcance.** La suspensión y realineación aplican solo al modelo 2. Si el cambio de dirección cancela una pendiente del modelo 1, ese lado queda apagado el resto del día, como acordamos.
3. **Qué dispara el cambio de dirección.** ¿Solo el paso 3 del modelo 2 contrario, o también un FVG del modelo 1 contrario?
