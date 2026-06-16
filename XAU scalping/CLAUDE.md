# XAU Scalping — Contexto del proyecto

## Quién somos
- **Fabian** — trader humano, opera manualmente con su indicador privado "XAU VIVO v2". No maneja código.
- **Claude (Jarvis)** — desarrolla y mantiene el código Pine Script. Análisis en tiempo real durante sesiones en vivo.
- **Comparación siempre visual** — los charts de Fabian vs los nuestros en TradingView.

## Instrumento
- Gold Spot / U.S. Dollar (XAUUSD OANDA)
- Sesión NY: 09:01 - 10:59 EDT (UTC-4)
- Timeframes: M1 (entradas) + M3 (estructura)

## Convención OANDA de velas
- **Vela negra (rellena)** = ALCISTA (close > open)
- **Vela blanca (hueca)** = BAJISTA (close < open)
- Opuesto a la convención estándar de TradingView

## Archivo principal
`XAU scalping/XAU_estrategia_Scalping.pine` — estrategia Pine Script v5

## Parámetros actuales del código
| Parámetro | Valor |
|---|---|
| Sesión NY | 09:01-10:59 EDT |
| Cuerpo min envolvente | 85% |
| Cuerpo pre-señal (~) | 75% |
| Cuerpo min martillo | 50% |
| Quiebre mínimo | 0.01% (`min_brk = 0.0001`) |
| RR | 1:0.9 |
| SL máximo | 200 puntos |
| Longitud líneas m3 | 5 velas |
| Límite diario | **DESACTIVADO** (`use_limite = false`) — NUNCA activar en sesión en vivo: confirmado dos veces (11-jun, 12-jun) que cortar el día nos ciega para el resto de la comparación. Excepción explícita a la directiva 16-jun de replicar a Fabian: queremos ver TODAS las señales del día |
| Bloqueo por noticias | **ACTIVADO** (`use_news_block = true`, desde 16-jun) — manual, ver sección abajo |
| Cooldown post-spike | **ACTIVADO** (`use_cooldown = true`, desde 16-jun) — 15 velas tras spike ≥10pts, **solo bloquea MEC** (ajuste 16-jun tarde), ver sección abajo |
| Tabla debug | **ACTIVADA** (`show_debug = true`, desde 16-jun tarde) — temporal, ver sección abajo |

## Lógica del sistema

### Estructura m3
- **Alto m3** = max(high, high[1]) cuando par vela bajista+alcista en M3
- **Bajo m3** = min(low, low[1]) cuando par vela alcista+bajista en M3
- **ChOC alcista** = vela m1 cierra con cuerpo por encima del último alto m3 con ≥0.01% de quiebre, estando en estructura bajista
- **ChOC bajista** = vela m1 cierra con cuerpo por debajo del último bajo m3 con ≥0.01% de quiebre, estando en estructura alcista

### Tipos de entrada (velas m1)
- **Envolvente**: cuerpo ≥ 85% del rango total, mecha opuesta reducida
- **Martillo**: cuerpo 50-85%, mecha A FAVOR de la entrada reducida (<15%) — la mecha opuesta no tiene % fijo, es lo que sobra. (Fix 16-jun: antes exigíamos mecha opuesta >30%, umbral inventado que no está en el Plan Técnico de Fabian y bloqueaba entradas válidas — ver sesión 16-jun)
- **Doji**: cuerpo 15-50%, ambas mechas ≥15% — aproximación nuestra a la "vela de indecisión" de Fabian; el Plan Técnico tiene una "vela envolvente doji" con un umbral distinto y ambiguo en el texto (15%/85%) que NO se tradujo al código por falta de certeza — pendiente de validar en vivo
- **Pre-señal (~BUY/~SELL)**: cuerpo 75-85% — avisa sin entrar operación

### Modelos
- **MEC (Continuación)**: pullback + vela de entrada que supera el máximo/mínimo del pullback. Requiere `market_struct` en la dirección del trade.
- **MER (Retroceso/ChOC)**: primera vela válida EN el mismo bar del ChOC. `choc_bull` + `entry_bull` = `mer_buy`.

## Bugs conocidos y pendientes

### [PRIORITARIO] Ping-pong de estructura
En períodos volátiles post-noticia:
1. Gran caída → `market_struct = -1`
2. Pequeño rebote forma nuevo alto m3 más bajo
3. Precio rompe ese nuevo alto m3 → `choc_bull` → `market_struct = 1` demasiado pronto
4. El código entra por MEC antes del ChOC real de Fabian

**Consecuencia:** Entra por MEC ENV cuando debería ser MER. La vela es válida pero el modelo y el timing son incorrectos.

**Solución de Fabian (encontrada 16-jun en Plan Técnico pág.26-27):** al ejecutar un MER solo puede existir UN alto/bajo m3 opuesto a la entrada. Si hay dos niveles m3 opuestos visibles, la ejecución se invalida — salvo que estén a ≤0.01% de distancia, en cuyo caso se extiende el SL al primer nivel y se ejecuta. **Esta regla YA está implementada** en `mer_sl_long`/`mer_sl_short` (bloquean el trade con `na` si hay dos niveles válidos y no están cerca). Pendiente: extender la misma idea a `market_struct`/MEC, que es donde el ping-pong real sigue ocurriendo (el market_struct cambia con solo romper el nuevo nivel, sin la validación de "nivel único").

### ~~[PRIORITARIO] Cooldown post-spike~~ — implementado 16-jun, ajustado 16-jun tarde
El código entraba inmediatamente después de velas gigantes (noticias). Fabian espera ~15-20 minutos. Implementado como `use_cooldown`/`spike_size`/`cooldown_bars`: cualquier vela con rango ≥`spike_size` (10pts default) marca `last_spike_bar`, y `cooldown_bars` (15 default) velas siguientes quedan bloqueadas.

**Ajuste (16-jun tarde):** el cooldown ya NO bloquea `can_trade` en general — solo bloquea `mec_buy`/`mec_sell` (`not in_cooldown` movido del `can_trade` compartido a las condiciones de MEC). Encontrado en vivo: un ChOC real podía ocurrir DENTRO de la ventana de cooldown (ej. spike de apertura ~09:00, ChOC bajista ~09:14, cooldown corriendo hasta ~09:15-18). Con el cooldown bloqueando todo, el MER no disparaba en el bar del ChOC; para cuando el cooldown terminaba, `market_struct` ya había cambiado, así que la primera entrada real salía como MEC ENV — exactamente el caso que Fabian señaló como "ahí tomé la entrada por MER" en una comparación de capturas. El ChOC + MER ES la señal de "el caos ya se calmó" que Fabian espera; bloquearla con un timer fijo es contraproducente. El ping-pong de estructura en MER ya está cubierto aparte por la regla de "nivel único" (`mer_sl_long`/`mer_sl_short`), así que MER no necesita la protección del cooldown. Tabla ahora muestra "SI (solo MER)" cuando el cooldown está activo pero el resto de condiciones permite operar.

### Tabla de debug temporal (`show_debug`) — añadida 16-jun tarde
El fix de cooldown (ver arriba) no resolvió un caso real visto en vivo: un ChOC bajista (~09:14) que sigue saliendo como "MEC ENV SELL" en vez de "MER SELL". Sin acceso a OHLC exacto ni al estado interno bar-por-bar, no se puede confirmar cuál de las 3 hipótesis abiertas es la causa (regla de nivel único bloqueando `mer_sl_short`, vela sin forma válida para `entry_bear`, o lag de M3) — ver `sesion_vivo_2026-06-16/sesion_log.md` (~13:50). Se agregó una segunda tabla (`dbg`, abajo a la derecha, toggle `show_debug`) que muestra en vivo por cada vela: ChOC del bar, forma de vela (bull/bear), niveles m3 (last/prev), `mer_sl_long`/`mer_sl_short` (valor o NA), `can_long`/`can_short`, y el resultado final de `mer_buy`/`mer_sell` y `mec_buy`/`mec_sell`. Pensada para usarse con TradingView Replay, vela a vela, en vez de reconstruir la causa desde capturas. Es temporal — quitar una vez confirmada la causa real.

### Pendientes menores
- ~~Etiqueta numérica al final de cada línea m3~~ — hecho 16-jun (`lbl_m3_high`/`lbl_m3_low`)
- ~~Texto "Cambio de estructura" en chart cuando ocurre ChOC~~ — hecho 16-jun
- Verificar contador TP/SL día (lógica con `strategy.netprofit` puede tener timing issues)
- Validar en vivo el umbral exacto de "vela envolvente doji" del Plan Técnico (texto ambiguo, no traducido a código)

### Bloqueo por noticias (`use_news_block`) — añadido 16-jun
**Directiva del usuario:** replicar exactamente la operativa de Fabian (8 meses de backtesting propio) en vez de solo comparar — incluye respetar sus ventanas de noticias del Plan Operativo.

TradingView/Pine no tiene feed nativo de calendario económico, así que el bloqueo es **manual por inputs de texto**: `sess_news_high` y `sess_news_med` (formato `HHMM-HHMM`, separables por coma para varias ventanas el mismo día). El usuario debe calcularlas y pegarlas antes de la sesión:
- **Alto impacto (rojo, USD, Forex Factory):** ventana = 10 min antes a 3 min después del evento. No abrir NI cerrar manualmente durante la ventana (nuestro código solo bloquea aperturas nuevas — el SL/TP de una operación ya abierta sigue activo, no se desactiva).
- **Medio impacto (naranja, USD):** ventana = 3 min antes a 3 min después. Solo bloquea aperturas nuevas; una operación ya abierta puede mantenerse durante el evento.
- Si un orador de impacto medio tiene hora programada específica → tratar como alto impacto.
- 5 eventos que Fabian nunca sostiene una operación abierta a través de ellos: Federal Funds Rate & Statement, NFP, CPI y/y, FOMC Meeting Minutes, Advance GDP q/q (todos USD).
- Feriados bancarios = día no operable (no hay automatización para esto, es decisión manual de no cargar el indicador ese día).
- Se puede entrar después de la ventana al mismo precio que ofrecía la vela bloqueada, pero solo si el precio no alcanzó ya el nivel de SL durante la ventana.

`can_trade` ahora exige `not in_news_block` además de sesión y límite diario. La tabla muestra "NO-noticia" cuando el bloqueo está activo.

## Documentos de Fabian (no son parte del repo, en uploads de la sesión)
- **Plan Operativo** (releído completo 16-jun) — horario con notas DST; reglas de noticias: Forex Factory solo USD, feriados bancarios = no operable, alto impacto = ventana -10min/+3min (no abrir ni cerrar), medio impacto = ventana -3min/+3min (solo bloquea aperturas nuevas, una operación abierta se puede mantener), orador de impacto medio con hora programada = tratar como alto impacto, se puede entrar post-ventana al mismo precio si no se alcanzó el SL durante la ventana, 5 eventos de no-sostener-operación-abierta (Federal Funds Rate & Statement, NFP, CPI y/y, FOMC Minutes, Advance GDP q/q, todos USD); 3 escenarios de stop diario (1 TP / 1 SL+1TP / 2 SL)
- **Plan Técnico** (31 págs) — la referencia más completa: estructura m3 (incl. variantes de fractal extendido), líneas punteadas (tendencial) vs continuas (reversión/ChOC), los 3 tipos de vela envolvente con sus % exactos, patrón START (morning/evening star), MEC (2 escenarios + 4 sub-tipos), MER (cambio de estructura + regla de "único nivel m3 opuesto" + "solo primer toque"), concepto **Hedge Position** (cobertura: si aparece señal contraria en operación abierta, se abre y se cierra la primera — esto YA pasa solo con el código actual gracias al netting nativo de `strategy.entry` en Pine, sin pyramiding), SL (último m3 ± reducción 40% si >20.000 pips), **RR 1:0.9 confirmado explícito en la última página**
- **Apariencia del Indicador** — spec visual de las etiquetas BUY/SELL, ejemplos reales de trades

## Sesiones grabadas
- `sesion_vivo_2026-06-11/sesion_log.md` — primera sesión en vivo, muchos bugs corregidos
- `sesion_vivo_2026-06-12/sesion_log.md` — trampa doble post-Michigan, nuestro código 2TP vs Fabian 2SL
- `sesion_vivo_2026-06-16/sesion_log.md` — lag estructural M3, fix umbral martillo, hallazgos de los PDFs de Fabian (RR, Hedge Position, regla de nivel único m3)

## Resultado semanal Fabian (semana 9-13 Jun 2026)
- **+1.35R** al cierre del viernes — benchmark a alcanzar (ver directiva 16-jun abajo)

## Directiva 16-jun: replicar exactamente la operativa de Fabian (con una excepción)
El usuario pidió dejar de solo comparar señales y hacer que el código se comporte EXACTAMENTE como Fabian opera — sus reglas están validadas por 8 meses de backtesting propio, así que se tratan como autoridad. Objetivo explícito: acercarnos a su rentabilidad (+1.35R semanal).

**Excepción explícita del usuario:** el límite diario de entradas (`use_limite`) se queda DESACTIVADO. La razón es de la herramienta, no de la estrategia: en sesión en vivo queremos ver TODAS las señales del día para comparar contra Fabian vela por vela, no que el código se quede mudo el resto de la sesión después del primer TP/SL. Esto ya se había aprendido dos veces (11-jun, 12-jun) antes de la directiva del 16-jun — un primer intento de activarlo el 16-jun se revirtió por la misma razón.

Cambios SÍ aplicados por esta directiva:
- Nuevo módulo `use_news_block` (manual) para respetar las ventanas de noticias del Plan Operativo.
- Nuevo módulo `use_cooldown` (post-spike, pendiente desde 11/12-jun) para replicar la paciencia de Fabian tras velas de noticia.
- Fix de umbral de martillo (ver sección de tipos de entrada arriba).
- Cualquier futura discrepancia entre nuestro código y el comportamiento de Fabian debe resolverse a favor de Fabian, salvo (a) que el Plan Técnico/Operativo sea ambiguo (no se adivina, se deja pendiente — ver doji) o (b) que sea una regla de corte total de señales como `use_limite`, que por ahora se mantiene excluida.

## Reglas de sesión en vivo
1. Leer el log de la última sesión antes de empezar
2. Verificar `use_limite = false` (NUNCA activar), `use_news_block = true` y `use_cooldown = true`; si hay noticias USD ese día, pedir al usuario las horas para llenar `sess_news_high`/`sess_news_med` antes de operar
3. Verificar que hay UNA sola instancia del indicador cargada
4. Rama de trabajo: `claude/trading-strategy-inconsistencies-w9S9b`
5. Guardar capturas y análisis en `sesion_vivo_YYYY-MM-DD/sesion_log.md`
6. Commit + push al final de cada sesión

## Cómo arrancar sesión
El usuario dice: **"hola Jarvis, sesión en vivo"** o **"estamos en vivo"**
→ Leer este archivo + último sesion_log + código actual → responder con estado del sistema listo para operar.
