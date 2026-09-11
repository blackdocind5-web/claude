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
- [x] **Fase 3 (parte 1) — umbral de quiebre a 0,005% (09/09)**: `UMBRAL_QUIEBRE`
  pasa a ser un input configurable, default 0,005% (la mitad del 0,01%
  original). Fabián mide este volumen con la herramienta "rango de precios"
  de TradingView, que redondea a 2 decimales -- un volumen real de 0,00742%
  ya le aparece como "0,01%" en pantalla, indistinguible de un 0,01000%
  exacto. Bajar el umbral a la mitad cubre todo lo que esa herramienta
  redondearía hacia "0,01%". Caso real que lo motivó: BUY 02/09 07:12,
  volumen real 0,00742% (nivel 4.315,905 -> cierre 4.316,225).
- [x] **Fase 3 (parte 1) — reset solo ante CHoCH real (09/09)**: antes,
  CUALQUIER quiebre válido (CHoCH o BOS) reseteaba `mecListo` y
  `huboPullbackEnBusqueda` desde cero. En una tendencia sana con varios BOS
  seguidos (normal, sin cambio real de estructura) eso tiraba abajo
  `mecListo` una y otra vez, dejando el motor "esperando Continuación" casi
  toda la sesión en vez de sostenerse listo. Ahora el reset completo ocurre
  SOLO cuando `esCambioEstructuraAlto`/`esCambioEstructuraBajo` es true (la
  tendencia efectivamente cambia); un BOS o un Alto/Bajo M3 nuevo en la
  misma dirección ya no resetean nada -- el nivel se sigue extendiendo solo,
  vela a vela. Caso real que lo destapó: BUY 03/09 20:55, pullback largo y
  mixto con varios BOS internos sin cambio de tendencia real.
- [x] **Fase 3 (parte 1) — colchón de 4 velas en el reset (10/09)**: el
  reset de `extremoQuiebre` toma el máximo/mínimo de las últimas 4 velas M1
  (esta + 3 para atrás), no solo la vela actual. La estructura M3 agrupa de
  a 3 minutos y el código recién "reconoce" un quiebre hasta 3 velas M1
  después de que ocurrió de verdad (cuando el gráfico M1 llega al siguiente
  bloque de 3 minutos) -- sin este colchón, `extremoQuiebre` arrancaba con
  el mínimo/máximo de la vela donde el código RECONOCE el quiebre (tarde),
  no de la vela que lo originó, dando un nivel mucho más fácil de superar y
  señales falsas. Caso real que lo destapó: SELL 07/09 20:47 -- el quiebre
  real fue en la vela de las 20:43 (mínimo 4.418,830), el código recién lo
  reconoció en la de las 20:45 (mínimo 4.420,620), y la vela de las 20:47
  superaba ese segundo nivel sin superar el real.
- [x] **Fase 3 (parte 1) — techo de 40% en el Doji (10/09)**: la rama Doji
  del clasificador de envolvente (Sección 3) no tenía techo en `nivelOpen` --
  aceptaba cualquier valor por encima de la banda de Martillo (40%-50%)
  mientras el cierre llegara a 90%/85%, sin importar cuán grande fuera la
  mecha en contra antes de la apertura. Eso permitía que una vela con más de
  la mitad del rango como mecha en contra (la MISMA forma que la Sección 4
  reconoce como vela de indecisión/pinbar) pasara como envolvente Doji
  decisiva. Ahora Doji exige `nivelOpen < 40%-TOLERANCIA_CUERPO` -- por
  encima de eso la vela ya no es ningún tipo de envolvente, sea cual sea el
  cierre. Caso real que lo destapó: SELL 10/09 08:30 (Pre-NY), nivelOpen
  64,96%, cierre 91,62% (pasaba la regla vieja del 90%) con un cuerpo real
  de apenas 26,66% -- Fabián la identificó a mano como pinbar bajista, vela
  de indecisión de un patrón Start confirmado recién en la vela siguiente
  (08:31, envolvente Estándar con cuerpo 95,61%, pullback en 08:29).
- [x] **Fase 3 (parte 1) — líneas M3 limitadas a la sesión operativa (10/09)**:
  el motor interno de estructura M3 (`altoM3Activo`/`bajoM3Activo`, detección
  de quiebres, `tendencia`) sigue corriendo las 24hs -- el MEC lo necesita
  para no perder el hilo fuera de sesión. Lo que cambió es el DIBUJO de las
  líneas (`line.new()`), que es lo que consume el cupo compartido de 500
  líneas de TradingView (el mismo límite ya mitigado antes para labels).
  Nuevo input `limitarLineasASesion` (default activado): las líneas de
  estructura M3 solo se dibujan durante Pre-NY/Asia, que ocupan ~17% del
  día -- esto multiplica por ~6 el historial visible de líneas antes de que
  empiecen a borrarse las más viejas. El interruptor queda disponible para
  apagarlo puntualmente si hace falta ver la estructura completa fuera de
  esas horas para depurar un caso. Motivado por: Fabián detectó que las
  líneas de la sesión de Asia del 07/09 ya no se veían (el histórico visible
  llegaba solo hasta 08/09 12:15h) justo en medio de la depuración del caso
  SELL 07/09 20:47.
- [x] **Fase 3 (parte 1) — reconocimiento M3 duplicado (10/09)**: con una
  etiqueta de debug temporal (`mostrarDebugM3`) se detectó que el mismo
  pivote (Alto M3 de 07:03) quedaba reconocido DOS VECES -- `ta.change(t3)`
  disparándose más de una vez para la misma vela M3 ya cerrada. Se agrega
  `ultimoT0Procesado` (guarda la apertura de la última vela M3 realmente
  procesada e ignora cualquier disparo repetido para esa misma vela) --
  confirmado con Fabián que el duplicado desapareció. Ojo con `na` en Pine:
  la primera versión de esta guardia comparaba `t3[1] != ultimoT0Procesado`
  directo, y como `ultimoT0Procesado` arranca en `na`, esa comparación daba
  `false` siempre (comparar contra `na` con `!=` no da `true` en Pine) --
  el reconocimiento de estructura M3 quedó completamente apagado (sin
  Altos/Bajos ni señales) hasta agregar el chequeo explícito
  `na(ultimoT0Procesado)`.
- [ ] **Fase 3 (parte 1) — pendiente, en pausa: línea continua M1 con nivel
  viejo en un CHoCH puntual (10/09)**: caso real: CHoCH alcista 10/09 07:25
  (Pre-NY), la línea continua en M1 quedó en 4.385,890 (ancla 07:12) en vez
  del Alto M3 correcto, 4.384,490 (ancla 07:18, tras el flip
  alcista→bajista de la vela de 07:21) -- en el gráfico M3 nativo el nivel
  se vio siempre bien. Con la etiqueta de debug se confirmó que el motor
  reconoce el pivote correcto (4.384,49 @ 07:18) una sola vez y sin
  duplicados -- el problema está puntualmente en el dibujo de la línea
  continua, no en el cálculo del nivel: `tendencia`, `quiebreAlto` y el MEC
  usan `altoM3Activo`, que a esta altura del rastreo manual del código
  parece quedar en el valor correcto. Se probaron dos causas (repintado
  intradía con `barstate.isconfirmed`, reconocimiento duplicado) sin
  resultado sobre este síntoma puntual. Fabián decidió pausar esta
  investigación (10/09) para no perder más tiempo en un tema visual que no
  parece afectar las señales de entrada -- retomar más adelante si hace
  falta. La etiqueta `mostrarDebugM3` queda en el código (apagada por
  defecto) para cuando se retome.
- [x] **Fase 3 (parte 1) — cierre de la fase (10/09)**: tres ajustes finales
  antes de pasar a la parte 2:
  - Se retiró la herramienta de debug temporal (`mostrarDebugM3` y sus
    etiquetas) que sirvió para encontrar el reconocimiento M3 duplicado.
  - **Sesión NY (09-11 EST, Lunes a Viernes)** agregada como tercera sesión
    operativa, con el mismo tratamiento que Pre-NY y Asia: sombreado de
    fondo, estructura M3 (Altos/Bajos, líneas) y señal final BUY/SELL.
    Sombreado en escala de grises distinta por sesión para diferenciarlas
    de un vistazo -- Pre-NY más clara (`#cccccc`), NY intermedia
    (`#b3b3b3`), Asia más oscura (`#999999`), todas a 78% de transparencia
    (antes 85%, para que el gris más claro no se pierda contra el fondo
    blanco del gráfico).
  - **Colchón de 15 minutos antes de Pre-NY (06:45) y de Asia (19:45)**:
    la estructura M3 (Altos/Bajos, líneas) ya se dibuja desde ese
    horario, no recién con la apertura -- Fabián hace un análisis previo a
    cada sesión y quiere ver la estructura armada de antemano para
    anticiparse. Solo afecta el DIBUJO de las líneas, no la sesión
    operativa en sí (sombreado, señal BUY/SELL), que sigue arrancando a la
    hora real de cada sesión. NY no lleva colchón propio: arranca justo
    donde termina Pre-NY, sin hueco que anticipar.
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
  defecto, sombreado de las tres sesiones (Pre-NY, NY y Asia) en escala de
  grises por defecto -- antes eran azul/naranja. Desde el 10/09 cada sesión
  tiene su propio tono de gris (Pre-NY más clara, NY intermedia, Asia más
  oscura) para diferenciarlas de un vistazo.
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
  (Pre-NY, NY y Asia llevan cada una su propio contador).
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
