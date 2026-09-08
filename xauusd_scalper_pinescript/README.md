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
- [x] **Fase 3 (parte 1) — motor MEC**: bandera unificada `mecListo`
  (BOS→arma inmediato si no hay búsqueda pendiente; CHoCH→resetea y
  arranca Quiebre→Pullback→Continuación en M1 con validación 0,01%,
  nivel fijo desde que arranca el pullback, reinicio ante CHoCH
  contrario). Señal "en bruto" (`mecBuyBruto`/`mecSellBruto`) para
  validar el motor antes de sumar SL/TP.
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
  reales de Fabián) se retiraron del dibujo por completo -- generaban
  demasiada información en pantalla y no aportan nada una vez que el
  clasificador ya está validado. Las etiquetas de Alto/Bajo M3 y
  quiebre/cambio de estructura quedaron con su toggle apagado por defecto
  (grupo "Estructura M3"). Lo único que se dibuja de fábrica es el **cartel
  de señal MEC BUY/SELL**: un label estilo "nube" gris con la ficha completa
  de la operación (Estructura M3, Posicionamiento, Ejecución, Fecha, Hora de
  entrada) -- "Resultado" y "Hora de salida" se suman cuando exista el
  simulador de SL/TP. El cálculo interno (M3, envolvente, Start) sigue
  corriendo siempre igual -- el motor MEC lo necesita -- solo se apagó el
  DIBUJO intermedio. Esto además libera casi todo el cupo compartido de 500
  labels de TradingView para las señales de entrada, que son las únicas que
  importan para operar y las que más historial necesitan.

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
