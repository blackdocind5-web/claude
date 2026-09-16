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
  investigación (10/09) para no perder más tiempo en un tema que en ese
  momento parecía solo visual.
- [x] **RESUELTO (11/09) -- reconocimiento M3 con "replay" de velas
  salteadas**: al agregar el SL/TP (Fase 3 parte 2, más abajo), Fabián
  encontró dos casos reales donde el Alto/Bajo M3 activo quedaba en un
  valor VIEJO varias velas M1 de más de lo esperado -- BUY 11/09 09:28 (NY):
  `bajoM3Activo` debía actualizarse a 4.380,605 (par bajista/alcista
  09:21/09:24) al llegar a la vela de las 09:27, pero siguió en el valor
  anterior (4.381,420, par 09:15/09:18) hasta la vela de las 09:29 -- 2
  velas M1 de atraso. SELL 09/09 08:25 (Pre-NY): mismo patrón, con un Alto
  M3 viejo (confirmado a las 08:12, nivel 4.404,845) en vez del correcto
  (confirmado a las 08:24, nivel 4.400,375).
  Con `mostrarDebugM3` (un `plot()` del valor EXACTO de
  `altoM3Activo`/`bajoM3Activo` en cada vela, leíble en la Ventana de
  Datos) se probó primero si la guardia anti-duplicados (`ultimoT0Procesado`)
  era la causa -- **descartado**: desactivándola temporalmente el atraso
  persistió igual. Los dos casos reales tampoco muestran un sesgo "seguro"
  consistente (en uno el nivel viejo daba un SL más ajustado que el
  correcto, en el otro uno más amplio), así que no alcanzaba con un parche
  tipo "usar siempre el nivel más lejano".
  La causa real: el código asumía que `t3[1]` siempre trae la vela M3
  inmediatamente siguiente a la última procesada, pero `request.security()`
  a veces tarda más de una vela M1 en reflejar el cierre real de una vela
  M3, dejando una vela intermedia sin procesar. Fix: el reconocimiento
  (Sección 2) ahora se separó en una función (`procesarVelaM3`) y revisa
  `t3[3]`, `t3[2]` y `t3[1]` en orden cronológico en cada `nuevaVelaM3` --
  cualquier vela M3 más nueva que la última procesada (`ultimoT0Procesado`)
  se corre por el motor antes de seguir, así ninguna vela queda salteada
  sin importar cuántas velas M1 tarde en aparecer.
  **SUPERADO (11/09, ver entrada más abajo)**: Fabián confirmó con los dos
  mismos casos reales que el atraso persistía igual -- el lag de
  `request.security()` era mayor de lo que un lookback de 3 velas M3 podía
  cubrir. Se reemplazó este enfoque por completo (dejar de usar
  `request.security()` para esto).
- [x] **RESUELTO (11/09) -- `procesarVelaM3` no compilaba: "Cannot modify
  global variable 'curDir' in function" (y ~19 errores más iguales)**: al
  pegar el fix anterior en el editor de Pine, TradingView lo rechazó. Causa:
  asumí (mal, sin compilarlo) que una función `=>` puede reasignar variables
  del scope global con `:=` -- Pine v5 no lo permite para tipos simples
  (int/float/string/bool), aunque sean `var`. La función original escribía
  directo sobre `curDir`/`curHigh`/`curLow`/`prevDir`/`prevHigh`/`prevLow` y
  eso es justamente lo prohibido. Fix: `procesarVelaM3` ahora es una función
  pura -- recibe el estado actual como parámetros (`dirIn`, `highIn`, etc.) y
  **devuelve** el estado nuevo (`dirOut`, `highOut`, etc.) en la tupla de
  salida, junto con lo que ya devolvía antes (esAlto/esBajo/niveles/inicios).
  Quien llama a la función (scope global, en el bloque de reconocimiento con
  `t3[3]`/`t3[2]`/`t3[1]`) es quien hace `curDir := ...` etc. con cada
  resultado, y encadena ese estado a la siguiente llamada dentro de la misma
  vela M1 (para que el replay de varias velas M3 salteadas siga funcionando
  igual que antes). Ningún cambio de lógica del motor de tramos -- mismo
  comportamiento, ahora en una forma que sí compila.
- [x] **RESUELTO (11/09) -- se abandonó `request.security()` para la
  estructura M3: se arma a mano con `timeframe.change("3")`**: Fabián
  confirmó con los dos mismos casos reales (BUY 11/09 09:28 NY, SELL 09/09
  08:25 Pre-NY) que el fix de "replay" (revisar `t3[3]`/`t3[2]`/`t3[1]`)
  seguía sin alcanzar -- el atraso real fue mayor a los 3 períodos M3 que
  ese lookback cubría (en el caso BUY, `bajoM3Activo` recién se actualizó al
  valor correcto 06 velas M1 después de formado el pivote real). Esto
  descartó cualquier arreglo basado en "mirar más para atrás": el lag de
  `request.security()` en este timeframe no-estándar no tiene un techo fijo
  conocido.
  Causa real, ahora sí de fondo: usar un timeframe secundario vía
  `request.security()` depende de que TradingView decida CUÁNDO exponer los
  datos de esa serie -- y esa decisión no es instantánea ni tiene un lag
  máximo garantizado para timeframes no-estándar como "3".
  Fix definitivo: se eliminó `request.security()` por completo de la
  Sección 2. La vela M3 ahora se arma A MANO, acumulando open/high/low/close
  directamente de las velas M1 del propio gráfico (`m3Open`/`m3High`/
  `m3Low`/`m3Close`/`m3OpenTime`, todas `var`), y se detecta el cierre de
  cada período de 3 minutos con `timeframe.change("3")` -- función nativa de
  Pine para justamente este caso (saber cuándo arrancó un período de un
  timeframe mayor a partir del timeframe actual, sin repintado). La vela M3
  queda cerrada y procesada en el MISMO instante en que el M1 entra al
  siguiente bloque de 3 minutos: cero lag adicional más allá del mínimo
  inevitable (que cierren las 3 velas M1 que la componen), y cero
  dependencia de la lógica interna de `request.security()`. También se pudo
  eliminar la guardia anti-duplicados/replay (`ultimoT0Procesado`): con este
  método cada vela M3 se procesa exactamente una vez, nunca dos, nunca
  salteada. `procesarVelaM3` (el motor de tramos en sí) no cambió su lógica,
  solo de dónde recibe cada vela. **Confirmado por Fabián (14/09)**: con
  este fix el `DEBUG` de `altoM3Activo`/`bajoM3Activo` ya se actualiza al
  valor correcto en el momento correcto, sin lag -- los dos casos reales
  quedan resueltos.
- [x] **RESUELTO (14/09) -- `quiebreAlto`/`quiebreBajo` (CHoCH/BOS) se
  confirmaban con cualquier toque mínimo, sin el mismo umbral que exige el
  MEC para validar una entrada**: encontrado por Fabián revisando las
  etiquetas de SL/TP -- una START BUY el 08/09 09:54 (Pre-NY) resultó
  inválida. El Alto M3 en 4.402,92 tuvo un primer toque débil que NO lo
  superaba con el volumen mínimo exigido (`UMBRAL_QUIEBRE`), pero
  `quiebreAlto` (que hasta ahora era `ta.crossover(close, altoM3Activo)`,
  SIN margen) ya lo daba por roto ahí mismo -- cortaba la línea, cambiaba
  `tendencia` a "alcista" y dejaba el motor MEC creyendo que el CHoCH ya
  estaba confirmado. De ahí en más, el primer pullback + continuación con
  margen (que sí exige el MEC en Sección 6) se cumplió ANTES de las 09:54,
  así que la vela de las 09:54 -- que en realidad era la que recién
  confirmaba el quiebre real del nivel -- disparó la señal directo, sin
  exigirle su propio pullback + continuación nuevos (los que le
  corresponden a un CHoCH recién confirmado). El nivel debía seguir
  extendiéndose a la derecha (línea sin cortar) hasta esa vela.
  Fix: `quiebreAlto`/`quiebreBajo` ahora exigen el mismo `UMBRAL_QUIEBRE`
  que ya usaba el MEC para validar una Continuación puntual (movido de la
  Sección 6 a la Sección 2, mismo valor y mismo grupo "Modelo MEC" en el
  panel -- solo cambió DÓNDE se declara en el código, corre antes). Ya no
  hace falta `ta.crossover` (semántica de cruce entre esta vela y la
  anterior): como `altoM3Activo`/`bajoM3Activo` pasan a `na` en la MISMA
  vela en que se confirma el quiebre, el chequeo simple "nivel + margen, y
  que siga sin estar en na" ya se comporta como "solo la primera vez que se
  cumple", sin repetirse en las velas siguientes. **Confirmado por Fabián
  (14/09)**: "ya quedó corregido, todo perfecto".
- [x] **Fase 3 (parte 2) — límite de operativa diaria, un trade a la vez,
  Hedge Position (14/09)**: nueva Sección 6C. Esto resuelve de paso la pieza
  pendiente "una señal por vela hasta invalidarse" -- ya no hace falta un
  mecanismo aparte, queda cubierta por esta regla más general. Reglas
  confirmadas por Fabián (su propio resumen: "UN SOLO TRADE ABIERTO A LA VEZ,
  NO SE DEBE TOMAR DOS OPERACIONES EN SIMULTÁNEO/PARALELO"):
  - Por SESIÓN (Pre-NY, NY, Asia -- cada una con su propio contador, no
    comparten límite entre sí) hay como máximo 2 señales. La sesión queda
    cerrada (cero señales más, aunque aparezca un setup válido) apenas se da
    uno de estos 3 escenarios: a) la 1ª señal llega a su TP, b) la 1ª llega a
    su SL y la 2ª (última) llega a su TP, c) la 1ª llega a su SL y la 2ª
    también llega a su SL.
  - Una 2ª señal en el MISMO sentido que la 1ª solo puede aparecer después de
    que la 1ª ya llegó a su SL (mientras sigue abierta, nada la invalida).
  - Una señal en sentido CONTRARIO (Hedge Position) SÍ puede dispararse en
    paralelo, con el trade original todavía abierto (sin llegar a SL ni TP) --
    pero en ese mismo instante el trade original se da por cerrado, para
    sostener la regla de "un solo trade a la vez" (la 2ª reemplaza a la 1ª,
    nunca coexisten).
  Implementación: `senalesSesion` (contador 0-2, se resetea al arrancar cada
  sesión -- flanco ascendente de `enPreNY`/`enNY`/`enAsia`), `sesionCerrada`,
  y `tradeAbiertoDir`/`SL`/`TP` (estado del trade abierto ahora mismo, si
  hay). En cada vela, si hay un trade abierto se chequea si `high`/`low`
  tocó su SL o su TP (sin esperar `barstate.isconfirmed` -- una orden real en
  MT5 no espera a que cierre la vela M1 para saltar) y se actualiza el
  estado según corresponda. `puedeGenerarBuy`/`puedeGenerarSell` combinan
  todo eso para filtrar `mecBuySenal`/`mecSellSenal` en
  `mecBuySenalFinal`/`mecSellSenalFinal` (lo que realmente dibuja el
  cartel), y `esHedgeBuy`/`esHedgeSell` agregan "(HEDGE)" al texto cuando
  corresponde. Panel de estado (Sección 7) ampliado con una fila que muestra
  señales usadas sobre 2 y si hay trade abierto (y en qué dirección), para
  verificar en vivo antes de seguir con la ficha final.
  Pendiente: que Fabián confirme en vivo (o con casos reales) que el límite
  de 2 señales, el cierre de sesión en los 3 escenarios, y el Hedge Position
  cerrando el trade original funcionan como se describió.
- [x] **Fase 3 (parte 2) — 3ª señal para el caso aislado de dos Hedge
  seguidos (14/09)**: Fabián pidió habilitar una 3ª señal (siempre la
  última) para dos escenarios reales que a veces se dan, con una lectura en
  común una vez reconstruidos: en ambos, la señal 2 y la señal 3 son DOS
  HEDGES SEGUIDOS -- la 2ª cierra a la 1ª por Hedge Position, y mientras la
  2ª sigue abierta (sin tocar ni SL ni TP), la 3ª la cierra también por
  Hedge. Lo único que cambia entre sus dos escenarios es si la 1ª terminó en
  pérdida o en ganancia/breakeven al momento de ser hedgeada -- no afecta la
  regla en sí, la excepción no depende de eso.
  Implementación: nueva `var bool tradeAbiertoEsHedge` -- registra si el
  trade abierto ahora mismo fue él mismo abierto por Hedge (se guarda con
  `esHedgeBuy`/`esHedgeSell` en el mismo momento en que se abre cada trade).
  `tercerHedgeBuy`/`tercerHedgeSell` habilitan la excepción exactamente
  cuando `senalesSesion == 2` (nunca más, así nunca hay una 4ª señal) Y el
  trade abierto es el contrario Y fue él mismo un Hedge Y la sesión todavía
  no está cerrada (`sesionCerrada` sigue en false -- ninguno de los 3
  escenarios de cierre se dio todavía). `puedeGenerarBuy`/`puedeGenerarSell`
  ahora combinan la regla normal (tope de 2) con esta excepción vía `or`.
  Panel de estado simplificado (ya no fuerza "/2" fijo, engañoso en este
  caso) -- ahora muestra la cantidad de señales usadas y si el trade abierto
  es un Hedge. **Confirmado por Fabián (14/09)**: "visualicé el nuevo código
  en TradingView y está perfecto".
- [x] **Fase 3 (parte 2) — alertas de TradingView (14/09)**: nueva Sección
  6D. Se usa `alert()`, no `alertcondition()` -- `alertcondition()` solo
  admite mensajes estáticos, sin poder meter el precio de entrada/SL/TP REAL
  de esa señal puntual dentro del texto. Para recibirlas, Fabián crea UNA
  sola alerta sobre el indicador con condición "Any alert() function call"
  -- dispara tanto para BUY como para SELL, cada una con su propio texto
  (ej.: "XAUUSD Scalper -- BUY (HEDGE) | Sesión: NY | Entrada: 4.123,456 |
  SL: 4.120,000 | TP: 4.125,000"), incluye sesión vigente, si es Hedge, y
  entrada/SL/TP. Nuevo input `activarAlertas` (default true, grupo
  "Alertas"). `alert.freq_once_per_bar_close` refuerza lo que ya hace
  `barstate.isconfirmed` -- nunca dispara en un tick intermedio.
  De paso, se separó en tres partes independientes lo que hasta ahora corría
  todo junto bajo `mostrarSenalMEC`: apagar el cartel visual también
  apagaba la actualización del estado de la sesión (Sección 6C) -- un bug
  latente nunca reportado (Fabián siempre lo deja activado) pero real. Ahora
  el estado de la sesión se actualiza siempre que la señal es real, el
  cartel se dibuja solo si `mostrarSenalMEC`, y la alerta solo si
  `activarAlertas` -- ninguno depende de otro. Pendiente: que Fabián
  configure la alerta en TradingView y confirme que el texto le llega
  completo y a tiempo.

## Multi-activo (14/09)

Fabián empezó a probar el indicador en otros mercados (AUDUSD, EURUSD,
BTC). El motor de estructura/patrones/MEC es 100% por porcentaje (nunca
ticks/pips fijos), pensado desde el principio para ser
instrumento-agnóstico -- pero algunos parámetros (umbrales, horarios de
sesión) fueron calibrados específicamente con casos reales de oro. Se
separan los hallazgos en dos categorías: **bug real** (error de lógica que
también podría afectar a XAUUSD sin que se haya detectado todavía -- se
corrige en el código, beneficia a todos los activos) vs. **descalibración**
(el código funciona como se diseñó, pero un valor por defecto no encaja con
este activo -- se resuelve ajustando el input en ese gráfico puntual, sin
tocar los defaults ya validados en oro).

- [x] **RESUELTO (14/09) -- `esMartilloIndBuy`/`esMartilloIndSell` no
  reconocían una segunda forma de vela decisiva, dejándola pasar como
  "indecisión" válida (BUG REAL, no descalibración)**: caso real BUY AUDUSD
  10/09 20:43h inválido -- Fabián identificó que la vela de indecisión
  (20:42h: apertura 0,71605, máximo 0,71614, mínimo 0,71604, cierre 0,71610)
  cumple los parámetros de lo que él llama "Vela Envolvente Martillo": nivel
  de apertura (D=BUY) = 10% (<15%), nivel de cierre = 60% (>50%) -- una
  mecha chica del lado de la apertura pero un cuerpo que ya superó la mitad
  del rango, ya decisiva, no indecisa. El código solo reconocía la forma
  CLÁSICA de Martillo (apertura en la banda 40%-50%, cierre >=85%), así que
  esta forma asimétrica se colaba como indecisión válida y habilitaba un
  Start inválido. Fix: `esMartilloIndBuy`/`esMartilloIndSell` (Sección 4)
  ahora reconocen dos formas -- la clásica (sin cambios) O la asimétrica
  (apertura <15%, cierre >50%-margen). Cálculo 100% por porcentaje: corrige
  por igual en cualquier instrumento, oro incluido -- no se tocó la Sección
  3 (clasificador de la vela de ENTRADA/confirmación), que es lógica
  distinta ya validada con casos de oro. **Confirmado por Fabián (14/09)**:
  "quedó perfecto y nada en el oro se alteró" -- además, un error que había
  visto por separado en EURUSD se corrigió solo, probablemente por este
  mismo fix (misma lógica de indecisión/Martillo).

- [x] **RESUELTO (14/09) -- `pullbackStartBuy`/`pullbackStartSell` y
  `pullbackEnvolventeBuy`/`pullbackEnvolventeSell` excluían una vela de
  cuerpo CERO (BUG REAL, no descalibración)**: caso real SELL BTCUSD 09/09
  20:20h -- el indicador NO marcó la señal (patrón Start válido a ojo). La
  vela de pullback (20:18h) abrió y cerró exactamente en 78,242 (cuerpo
  cero, doji perfecto). El chequeo `close[2] > open[2]` (estricto) nunca se
  cumple cuando `close[2] == open[2]` exacto -- una vela sin cuerpo no es "a
  favor" de ninguna dirección, así que tampoco debería quedar excluida de
  contar como pullback. TradingView ya la pinta como vela válida (mecha sin
  cuerpo) aunque no tenga cuerpo. Fix: los 4 chequeos de pullback
  (`pullbackStartBuy`/`Sell` en Sección 4, `pullbackEnvolventeBuy`/`Sell` en
  Sección 3) pasan de `</` >` estrictos a `<=`/`>=` -- cambio puramente
  aditivo (solo agrega el caso borde `open==close`, nunca saca un caso que
  ya calificaba), así que no puede romper ningún caso de oro ya validado.
  Pendiente: que Fabián confirme que este mismo caso de BTC ya se reconoce.

- [x] **Cartel sin "(HEDGE)" (14/09)**: a pedido de Fabián, el cartel visual
  BUY/SELL vuelve a decir siempre lo mismo (solo "BUY" o "SELL"), sea o no
  Hedge Position -- "simple y minimalista", como el diseño original. El tag
  "(HEDGE)" queda solo en el texto de la alerta (Sección 6D), que es
  informativo y no forma parte del cartel.

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
- [x] **Fase 3 (parte 2) — cálculo de SL/TP (11/09)**: primera pieza de la
  parte 2 (orden elegido por Fabián: SL/TP primero, es la base para el resto).
  - **SL**: distancia entre la entrada (cierre de la vela de señal) y el
    último Alto/Bajo M3 ACTIVO -- resistencia sin romper para un SELL
    (`altoM3Activo`), soporte sin romper para un BUY (`bajoM3Activo`); si no
    hay uno activo (caso borde, recién roto) usa el último quebrado
    (`ultimoAltoQuebrado`/`ultimoBajoQuebrado`, variables nuevas que sí
    persisten entre velas, a diferencia de `nivelQuebradoAlto`/`Bajo` que se
    resetean en la vela siguiente).
  - Si esa distancia cruda supera un umbral (`UMBRAL_SL_PCT`, default 0,46%
    **del precio de entrada, no ticks fijos**) se reduce multiplicándola por
    `REDUCCION_SL` (default 0,60 = reduce un 40%). El umbral va en
    porcentaje -- a pedido de Fabián -- para que el mismo indicador sirva en
    cualquier instrumento (oro, índices, forex, cripto) sin tocar código; su
    plan es reutilizar este motor en S&P 500, Nasdaq, Dow Jones, GBPUSD,
    EURUSD y Bitcoin.
  - **TP** = `RR_TP` (default 0,90) × la distancia FINAL del SL (ya reducida
    si correspondía), en la dirección favorable.
  - Validado letra por letra contra la operación real de Fabián del 23/08
    20:24h (Asia, SELL): entrada 4.612,435, Alto M3 4.640,935 -> distancia
    cruda 28,500 (0,6179% del precio, supera el umbral 0,46%) -> distancia
    final 28,500×0,6 = 17,100 -> SL calculado 4.629,535 (real: 4.629,515) y
    TP calculado 4.597,045 (real: 4.597,145) -- diferencia mínima por
    redondeo de Fabián, fórmula confirmada tal cual.
  - Por ahora se muestra con etiquetas chicas de verificación
    (`mostrarSLTP`) junto al cartel BUY/SELL existente, sin tocar ese cartel
    -- la "ficha de la operación" enriquecida queda para más adelante en
    esta misma parte 2.
  - Pendiente en esta parte 2: filtro de sesión sobre la señal final (ya
    existe vía `enSesionOperativa`, revisar si hace falta algo más), "una
    señal por vela hasta invalidarse", cartel final enriquecido (ficha de la
    operación), alertas push.
- [x] **Candidato a cambio de estructura "bloqueado" (línea continua fija)
  (15/09)**: bug real en la Sección 2 (estructura M3), presente desde
  siempre, no relacionado con el margen de `UMBRAL_QUIEBRE` agregado el
  14/09. Hasta ahora, `altoM3Activo`/`bajoM3Activo` se reemplazaban por
  CUALQUIER pivote nuevo del mismo tipo (`esAltoM3`/`esBajoM3`) apenas se
  formaba, sin chequear si el nivel anterior ya se había roto. El nivel del
  lado OPUESTO a la `tendencia` vigente (el candidato a CHoCH, "línea
  continua" en la jerga de Fabián) tiene que ser UNO SOLO y quedar fijo
  hasta que se resuelva -- confirmado por Fabián.
  - Caso real que lo destapó: SELL 14/09 20:04 (Asia) que no disparó pese a
    ser una envolvente evidente en vivo. La estructura ya era bajista desde
    mucho antes de las 19:54 (confirmado por Fabián contra un gráfico M3
    más amplio, y contra una versión anterior del indicador que sí
    reconocía el CHoCH correcto). El verdadero cambio de estructura era el
    Bajo M3 de las 19:36-19:42 (nivel 4.288,230, formado tras el quiebre
    alcista del Alto M3 de 19:21-19:24 en la vela M1 de 19:31) -- pero el
    panel DEBUG mostró que `bajoM3Activo` ya había cambiado a 4.287,365 para
    las 19:51, antes de que 4.288,230 tuviera oportunidad de romperse. La
    vela M1 de las 19:53 (cierre 4.287,820) sí rompía 4.288,230 con margen
    de sobra (nivel con `UMBRAL_QUIEBRE` ≈4.288.015,6) -- confirmando que el
    margen NO era el problema, el código simplemente ya no vigilaba el
    nivel correcto.
  - Fix: dos flags nuevos, `altoM3Bloqueado`/`bajoM3Bloqueado`. Mientras
    `tendencia` es "alcista", el lado bajo es el candidato a CHoCH y queda
    bloqueado apenas se fija el primer Bajo M3 tras el último reseteo -- los
    Bajos M3 que se formen después se grafican punteados (informativos) pero
    NO reemplazan al candidato activo. El bloqueo se libera solo ante los
    dos eventos que señaló Fabián: (1) el candidato se rompe con volumen
    válido -- confirma el CHoCH, o (2) se rompe antes un Alto M3 a favor de
    la tendencia alcista vigente (un BOS) -- demuestra que el retroceso que
    generó el candidato fue falso, se descarta y se vuelve a buscar uno
    nuevo. Simétrico para el lado alto cuando `tendencia` es "bajista".
  - No toca la fórmula de `quiebreAlto`/`quiebreBajo` (margen de
    `UMBRAL_QUIEBRE`, validado el 14/09 contra el caso de AUDUSD START BUY
    08/09 09:54) -- ambos fixes son independientes y no se pisan entre sí.
- [x] **SL/TP vuelve a usar el pivote M3 más reciente, no el candidato
  bloqueado (15/09)**: efecto colateral del fix anterior, detectado por
  Fabián al probar el mismo código en vivo. `altoM3Activo`/`bajoM3Activo`
  cumplían dos roles a la vez: (1) el candidato bloqueado a cambio de
  estructura (recién corregido) y (2) la referencia de SL/TP en la Sección
  6B ("el último Alto/Bajo M3 activo"). Al bloquear el candidato para el rol
  (1), el rol (2) quedó congelado en el mismo nivel viejo sin querer.
  - Caso real que lo destapó: SELL 14/09 20:24 -- el SL se armó contra el
    Alto M3 de ~19:00 (4.297,53, el candidato bloqueado, tendencia ya era
    bajista desde antes) en vez del Alto M3 real más cercano a la entrada
    (4.289,225, formado ~20:00) -- un SL bastante más lejos del que
    corresponde.
  - Fix: dos variables nuevas, `altoM3Reciente`/`bajoM3Reciente`, que
    siempre seguen al ÚLTIMO pivote M3 formado (esté o no bloqueado el
    candidato de estructura) -- son las que ahora usa el SL/TP (Sección 6B)
    en vez de `altoM3Activo`/`bajoM3Activo`. La lógica de estructura/CHoCH
    (Sección 2) no cambia, sigue usando el candidato bloqueado. Agregadas
    también al panel DEBUG (`mostrarDebugM3`) para verificar en la Ventana
    de Datos.
- [x] **El margen de UMBRAL_QUIEBRE solo aplica al CHoCH, no al BOS (15/09)**:
  matiz que faltaba en el fix del candidato bloqueado. Un CHoCH (cambio de
  tendencia) necesita la confirmación fuerte del margen -- fue justamente el
  caso de AUDUSD que motivó agregarlo el 14/09. Pero un BOS (la tendencia
  vigente simplemente continúa) es un estándar mucho más bajo: alcanza con
  que el precio supere el nivel, aunque sea solo con mecha o con un cuerpo
  menor al margen -- confirmado por Fabián.
  - Caso real que lo destapó: PRE-NY 15/09 en vivo -- el candidato bajo
    bloqueado en 4.278,725 (bajo M3 de las 07:06) debió haber sido
    reemplazado por el bajo M3 más reciente (4.282,460, formado a las 07:54)
    apenas se confirmó un BOS alcista entre esas dos velas (un alto M3
    superado, aunque sea débil) -- pero el toque real fue más débil que el
    margen exigido y el código no lo reconoció, así que el candidato bloqueado
    quedó pegado al nivel viejo hasta su quiebre real, mucho más tarde.
  - Fix: `quiebreAlto`/`quiebreBajo` ahora distinguen el caso -- exigen el
    margen de `UMBRAL_QUIEBRE` SOLO cuando el quiebre implicaría un CHoCH
    (`tendencia` es la opuesta al lado evaluado); si `tendencia` ya es ese
    mismo lado (BOS) o está "indefinida" (arranque), alcanza con que la
    mecha (`high`/`low`) supere el nivel, sin margen. No toca la Sección 6
    (MEC), que sigue con su propia validación de entrada por `UMBRAL_QUIEBRE`
    tal cual estaba.
- [x] **Candidato bloqueado v2: comparación directa en vez de detectar el BOS
  (15/09, hack de Fabián)**: el fix anterior (liberar el candidato bloqueado
  ante un BOS detectado vía `quiebreAlto`/`quiebreBajo`) resultó frágil en la
  práctica -- un BOS real puede no llegar a tocar ni con mecha el Alto/Bajo
  M3 vigente en ese momento (el precio simplemente no vuelve a acercarse a
  ese nivel específico antes de formar el siguiente pivote), así que el
  evento de invalidación muchas veces no se disparaba aunque el candidato SÍ
  debía trasladarse.
  - Caso real que lo destapó: PRE-NY 15/09 en vivo (mismo día, segunda
    vuelta) -- el candidato bajo bloqueado pasó correctamente de 4.278,725 a
    4.281,460 (sí hubo un BOS detectado ahí) pero se quedó pegado en
    4.281,460 en vez de seguir a 4.282,460 (bajo M3 de las 07:51-07:54, más
    reciente y más alto) porque no se detectó ningún `quiebreAlto` entre
    medio.
  - Fix (hack de Fabián): en vez de depender de detectar un quiebre
    intermedio, comparar DIRECTAMENTE el nivel del pivote nuevo contra el
    candidato bloqueado vigente. Regla: "el nivel de línea continua (CHoCH)
    siempre debe ser el más cercano al precio actual del mercado" -- mientras
    `tendencia` es "alcista", un Bajo M3 nuevo reemplaza al candidato
    bloqueado SI Y SOLO SI es más alto que el actual (un higher low real,
    más favorable/cercano al precio); si es igual o más bajo, no lo
    reemplaza. Simétrico para el lado alto cuando `tendencia` es "bajista"
    (reemplaza solo si es más bajo). Esto también reconcilia limpiamente el
    caso original del SELL 14/09 20:04: los Bajos M3 posteriores a 4.288,230
    (4.287,365 y 4.287,360) eran MÁS BAJOS -- por esta regla nunca lo hubieran
    reemplazado, tal como correspondía.
  - El único evento que sigue liberando el bloqueo por completo (para que el
    primer pivote de la tendencia siguiente arranque una búsqueda nueva, no
    herede el último valor) es el CHoCH real -- el reseteo de
    `bajoM3Bloqueado`/`altoM3Bloqueado` en los bloques `quiebreAlto`/
    `quiebreBajo` ahora está condicionado a `esCambioEstructuraAlto`/`Bajo`,
    ya no se dispara ante cualquier BOS.
  - Confirmado con Fabián que este cambio NO afecta la validación de entrada
    del MEC (Sección 6): `superaNivelAhora` calcula su propio margen contra
    `extremoQuiebre`, un mecanismo totalmente independiente de
    `quiebreAlto`/`quiebreBajo` (Sección 2) -- exige el 0,01%/0,005% completo
    en cada entrada puntual, sin excepción, tal como estaba.
- [x] **Fase 4 (concepto original)**: gestión de salida (SL en último
  alto/bajo M3 con reducción, TP en RR configurable), Hedge Position -- ya
  implementado dentro de la Fase 3 parte 2 (Sección 6B/6C del indicador),
  adelantado respecto al plan original.
- [x] **Fase 5 (concepto original)**: límite diario (2 señales por sesión,
  3 en el caso aislado de Hedge encadenado) -- también adelantado dentro de
  la Fase 3 parte 2 (Sección 6C). La flexibilización del 85% atada al PnL
  semanal simulado sigue pendiente.
- [ ] **Fase 6**: filtro de noticias — solo recordatorio visual (Pine Script
  no puede leer Forex Factory en vivo), sin bloqueo automático de señales.
- [x] **Fase 4 (backtesting) — `fase4_strategy_backtest.pine` (15/09)**:
  versión `strategy()` del indicador para poder correr el backtest nativo
  de TradingView (pestaña "Strategy Tester") en cualquier instrumento
  (arrancando por oro, luego EURUSD, GBPUSD, Nasdaq, S&P 500, BTC, AUDUSD),
  no solo mirar señales en vivo.
  - Archivo NUEVO y separado del indicador -- Pine no permite que un mismo
    script sea `indicator()` y `strategy()` a la vez. Las Secciones 1 a 6B
    (sesiones, estructura M3, envolvente/Start, MEC, SL/TP) son una copia
    literal de las mismas secciones del indicador ya validado, sin tocar
    una coma. Lo nuevo es la Sección 6C (ejecución real con
    `strategy.entry()`/`strategy.exit()` en vez del cartel/bookkeeping
    simulado) y la Sección 7 (tabla de métricas en el gráfico).
  - **Tamaño de posición**: riesgo fijo en % del equity por operación
    (`RIESGO_PCT`, confirmado por Fabián) -- `qty = (equity × riesgo%) /
    distancia al SL`, recalculado en cada entrada.
  - **Costos**: arranca en cero (comisión y slippage en 0, a pedido de
    Fabián, para ver primero el potencial "puro") -- se ajustan sin tocar
    código desde Propiedades de la estrategia en TradingView.
  - **Regla del trade que se arrastra entre sesiones** (confirmada por
    Fabián, 15/09): si al terminar una sesión un trade sigue abierto y la
    estructura (`tendencia`) favorece su dirección, se deja correr hasta
    SL, TP o un CHoCH real en contra; si la estructura está en contra, se
    cierra ya. Mientras corre así "de arrastre", la sesión siguiente opera
    como si no existiera -- cuenta sus propias señales desde cero y puede
    abrir su propio trade en paralelo, **en el mismo sentido** (BUY+BUY o
    SELL+SELL). Si la sesión nueva genera señal en sentido **contrario** al
    trade arrastrado, es un Hedge Position entre sesiones (cierra primero
    el arrastrado, recién después abre el nuevo) -- confirmado por Fabián.
  - **Restricción técnica resuelta**: el motor de estrategias de Pine
    mantiene una única posición neta por símbolo -- no hay forma nativa de
    sostener un BUY y un SELL abiertos a la vez (a diferencia de una cuenta
    de hedging en MT5). Solución: cada sesión opera bajo su propio id de
    entrada ("PreNY"/"NY"/"Asia"/"WallStreet") con `pyramiding=4`, permitiendo
    múltiples posiciones abiertas EN EL MISMO SENTIDO; el Hedge Position
    entre sesiones (arriba) es lo que evita que el motor llegue a necesitar
    sostener sentidos opuestos de verdad.
  - `procesarSesionTrade()`: función pura (mismo patrón que
    `procesarVelaM3()` de la Sección 2) que corre el límite diario/Hedge/
    arrastre de UNA sesión -- se llama 4 veces (Pre-NY, NY, Asia, Wall
    Street), cada una con su propio estado, nunca comparten contador ni
    trade entre sí.
  - Pendiente de validar: correr primero en oro (mismo período ya validado
    en vivo con el indicador) y confirmar que las entradas/salidas
    coinciden con lo que el indicador mostró, antes de confiar en los
    resultados de otros activos.
- [x] **Fase 4 (backtesting) — filtros de sesión/día + sesión Wall Street
  (16/09)**: a pedido de Fabián, para poder experimentar con distintas
  combinaciones de franja horaria/sesión/día por activo al backtestear.
  - **Sesión nueva "Wall Street"** (09:30-11:00 EST): pensada para
    backtestear índices (Nasdaq, S&P 500, Dow Jones). A diferencia de
    Pre-NY/NY/Asia (mutuamente excluyentes), esta se SUPERPONE con la
    sesión NY (09:00-11:00 EST) -- si se habilitan las dos a la vez,
    ambas reaccionan a las mismas señales durante el solapamiento
    (09:30-11:00), duplicando entradas/riesgo en esa franja. Para
    índices: Wall Street habilitada, NY deshabilitada.
  - **Toggle on/off por sesión** (`habilitarPreNY`/`habilitarNY`/
    `habilitarAsia`/`habilitarWallStreet`, grupo de inputs "Backtest —
    Filtros de sesión y día"): solo afecta si esa sesión puede abrir
    operaciones NUEVAS -- `procesarSesionTrade()` recibe un nuevo
    parámetro `habilitadaEjecucion` que se usa únicamente en la regla 5
    (señal nueva); el monitoreo de SL/TP y el arrastre de un trade ya
    abierto (reglas 2-4) siguen corriendo siempre, incluso con la sesión
    deshabilitada, para no romper un arrastre en curso.
  - **Toggle on/off por día de la semana** (Domingo a Viernes,
    `diaHabilitado`, usando `dayofweek(time, "America/New_York")`) --
    inicialmente Domingo quedó sin toggle (siempre habilitado), pero
    Fabián pidió agregarlo también como día desactivable el mismo 16/09,
    así que quedaron los 6 días (Domingo a Viernes) con su propio
    `habilitarX`, ninguno forzado. Se aplica como filtro adicional en
    `mecBuyGate`/`mecSellGate`, junto a `barstate.isconfirmed`.
  - **Hedge Position entre sesiones generalizado a 4 sesiones**: la lógica
    pasó de 3 condiciones manuales por par de sesiones a 4 condiciones (una
    por sesión objetivo), cada una evaluando si CUALQUIERA de las otras 3
    acaba de abrir en sentido contrario -- evita que el número de
    condiciones escale por combinación de pares al sumar sesiones.
  - Panel de estado (Sección 7): fila nueva para Wall Street, tabla de 6 a
    7 filas.
  - `pyramiding` sube de 3 a 4 en la declaración `strategy()` para permitir
    que las 4 sesiones tengan una posición abierta en el mismo sentido a
    la vez.

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
