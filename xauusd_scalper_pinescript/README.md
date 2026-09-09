# Indicador XAUUSD Scalper — Fabián

Indicador de TradingView (Pine Script v5) para automatizar el análisis de la
estrategia discrecional scalper de Fabián en XAUUSD (Oro/USD), dejando la
ejecución manual en MT5.

## Plan de fases

Se construye por fases para poder validar cada capa de lógica contra los
gráficos reales antes de apilar la siguiente. Cada fase es un archivo `.pine`
independiente hasta que todo esté validado; el resultado final se consolida
en un único indicador.

- [x] **Fase 1 — `fase1_estructura_m3.pine`**: estructura de mercado M3
  (altos/bajos por patrón de 2 velas, líneas punteada/continua, BOS/CHoCH) +
  sombreado de sesiones operativas (Pre-NY 07-09 EST y Asia 20-22 EST,
  Lunes a Jueves).
- [x] **Fase 2a — `fase2a_patron_envolvente.pine`**: clasificador de vela
  envolvente en M1 (estándar / martillo / doji, BUY y SELL) + contexto de
  pullback (vela anterior de color contrario). Fórmulas validadas letra por
  letra contra velas reales de Fabián (03/09).
- [x] **Fase 2b — `fase2b_patron_start.pine`**: patrón Start (vela de
  indecisión doji/pinbar + envolvente de continuación), pullback previo,
  invalidación de 3ª vela consecutiva del mismo color. La vela de
  indecisión usa el mismo marco direccional (0=contra, 1=favor) que la
  envolvente, confirmado por Fabián.
- [x] **Base consolidada — `fase3_base_consolidada.pine`**: une Fase 1
  (sesiones + estructura M3) y Fase 2 (envolvente + Start) en un solo
  script — reemplaza a los 3 archivos anteriores, que se mantienen solo de
  referencia. Punto de partida de la Fase 3.
- [x] **Fase 3 (parte 1) — motor MEC**: bandera `mecListo` (ya hubo una
  Continuación confirmada desde el último reset) + regla "todos los niveles
  a la izquierda" (confirmada por Fabián el 09/09): `extremoQuiebre` se
  extiende con la mecha de TODA vela M1 sin importar si `mecListo` ya está
  en true, y cada entrada puntual (no solo la Continuación original) tiene
  que volver a superar el nivel vigente con 0,01% por sí misma -- una
  reentrada no hereda gratis la validación de una vela anterior. Reset ante
  cualquier quiebreAlto/quiebreBajo (CHoCH o BOS, sin exigir 0,01% en el
  arranque, solo en cada intento de superar el nivel) o ante un Alto/Bajo M3
  nuevo. Señal "en bruto" (`mecBuyBruto`/`mecSellBruto`) para validar el
  motor antes de sumar SL/TP.
- [x] **Fase 3 (parte 1) — margen de estimación visual (09/09)**: los cortes
  de 85%/90% de cuerpo del clasificador de envolvente (Sección 3) y de la
  vela de indecisión del patrón Start (Sección 4) se relajan con
  `TOLERANCIA_CUERPO` (input, default 1 punto porcentual). Motivo: Fabián
  mide el volumen a ojo con una grilla de Gann dibujada a mano, sin
  decimales -- exigirle al código una precisión matemática perfecta sobre
  un corte que él mismo definió visualmente es más estricto que el propio
  método que se está formalizando. Caso real que lo motivó: vela de 30/08
  20:35, cuerpo 84,60%, confirmada por Fabián como Estándar válida.
- [x] **Fase 3 (parte 1) — banda de Martillo (09/09)**: Martillo exige un
  cuerpo CHICO (tal como lo indica su nombre): el nivel del lado de la
  apertura tiene que caer en la banda angosta 40%-50% (antes era cualquier
  punto >=50%). Un nivelOpen por encima de esa banda (cuerpo más grande)
  pasa a evaluarse como envolvente Doji en su lugar.
- [x] **Fase 3 (parte 1) — ramas del Doji corregidas (09/09)**: estaban
  INVERTIDAS desde la Fase 2a. nivelOpen >= 15% (el open queda más lejos del
  extremo) exige el cierre más estricto (90%); nivelOpen < 15% (open ya casi
  en el extremo) se conforma con 85%. Caso real que lo destapó: SELL 31/08
  08:25, nivelOpen 24,80% exigía cierre >=90%, cerró en 86,64% -- inválida
  (el motor la había marcado válida con la fórmula vieja).
- [ ] **Fase 3 (parte 2)**: SL/TP, filtro de sesión sobre la señal final,
  "una señal por vela hasta invalidarse", señal visual BUY/SELL (globo +
  ficha de la operación), alertas push.
- [ ] **Fase 4**: gestión de salida (SL en último alto/bajo M3 con reducción
  del 40% si supera 20.000 pips, TP en RR 1:0,9), Hedge Position.
- [ ] **Fase 5**: límite diario (1 TP / 1 SL+1 TP / 2 SL) y flexibilización
  del 85% atada al PnL semanal simulado — ambos por simulación interna del
  indicador, ya que Pine Script no tiene acceso a la cuenta real de MT5.
- [ ] **Fase 6**: filtro de noticias — solo recordatorio visual (Pine Script
  no puede leer Forex Factory en vivo), sin bloqueo automático de señales.

## Decisiones de diseño (confirmadas con Fabián)

- **Estética minimalista, solo la señal final**: los triángulos/etiquetas de
  debug de envolvente candidata y patrón Start (útiles en su momento para
  validar el volumen de cada vela letra por letra contra los gráficos
  reales de Fabián), y las etiquetas de Alto/Bajo M3 y quiebre/cambio de
  estructura, se retiraron del dibujo por completo -- generaban demasiada
  información en pantalla y no aportan nada una vez que el clasificador ya
  está validado. Lo único que se dibuja de fábrica es el **cartel de señal
  BUY/SELL**: un label estilo "nube" gris claro con texto blanco en
  mayúsculas, sin datos adicionales (la "ficha de la operación" -- Estructura
  M3, Posicionamiento, Ejecución, etc. -- fue solo contexto para desarrollar
  el motor, nunca parte del diseño final del cartel). El cálculo interno (M3,
  envolvente, Start) sigue corriendo siempre igual -- el motor MEC lo
  necesita -- solo se apagó el DIBUJO intermedio. Esto además libera casi
  todo el cupo compartido de 500 labels de TradingView para las señales de
  entrada, que son las únicas que importan para operar y las que más
  historial necesitan.
- **Paleta sobria**: línea M3 continua (cambio de estructura) en negro por
  defecto, sombreado de ambas sesiones (Pre-NY y Asia) en gris claro por
  defecto -- antes eran azul/naranja.
- **Cartel BUY/SELL no repinta**: se dibuja solo con `barstate.isconfirmed`,
  es decir únicamente en el cierre real y confirmado de la vela M1 de
  entrada, nunca en un tick intermedio mientras la vela todavía se está
  formando. El patrón envolvente/Start se define con el open/close/high/low
  FINAL de la vela, así que no hay forma honesta de confirmarlo antes de
  ese cierre -- sin este freno, un tick intermedio que luzca momentáneamente
  válido podía dejar una etiqueta fantasma si el precio se revertía antes de
  que cerrara el minuto. El panel de estado ("No Entry" / "Waiting for MEC" /
  "MEC ready") sigue siendo el anticipo legítimo: "MEC ready" significa que
  la próxima vela que cierre como envolvente o Start válida dispara la señal
  de inmediato, sin necesidad de un quiebre nuevo.
- **Panel de estado en inglés y reducido a 2 celdas**: "Tendencia: Alcista/
  Bajista" pasó a "Uptrend (BUY)" / "Downtrend (SELL)"; "no armado" /
  "esperando continuación" / "MEC: listo" pasaron a "No Entry" / "Waiting for
  MEC" / "MEC ready". La celda del medio (sesión activa / fuera de sesión)
  se eliminó -- el sombreado de fondo de cada sesión ya cumple esa función,
  mostrarlo dos veces era redundante.

- El indicador corre sobre el gráfico **M1** (donde se ejecuta) y trae la
  estructura M3 por detrás con `request.security()`.
- Límite diario y flexibilización del 85%: **automatizados por simulación**
  (el script seguí precio a precio si el SL o TP teórico de cada señal se
  tocó primero, ya que no hay forma de leer los fills reales de MT5).
- Conteo de "primer/segundo trade" para la flexibilización: **por sesión**
  (Pre-NY y Asia llevan cada una su propio contador).
- Filtro de noticias: **solo recordatorio visual**, sin bloqueo automático
  (Forex Factory no es accesible en vivo desde Pine Script).

## Notas de la Fase 1

- La detección de alto/bajo M3 usa un modelo de "tramos" (rachas de velas
  M3 del mismo lado, doji tolerado como continuación): el nivel se forma en
  el límite entre dos tramos opuestos y toma el extremo de todo el tramo de
  cada lado, sea la mecha relevante hacia atrás o hacia adelante en el
  tiempo. Validado contra 2 ejemplos reales de Fabián (uno de cada
  dirección) el 03/09.

## Cómo probar la Fase 1

1. Abrir XAUUSD en TradingView, timeframe **1 minuto**.
2. Pine Editor → pegar el contenido de `fase1_estructura_m3.pine` → Add to
   chart.
3. Comparar contra tus marcados manuales: los altos/bajos M3, el cambio de
   línea punteada→continua en los cambios de estructura, y el sombreado de
   las sesiones Pre-NY / Asia.
