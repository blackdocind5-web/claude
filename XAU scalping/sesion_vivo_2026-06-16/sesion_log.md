# Sesión en Vivo — XAUUSD — Martes 16 Jun 2026

**Trader:** Fabian (humano, opera manualmente) + análisis Claude
**Instrumento:** Gold Spot / U.S. Dollar (XAUUSD OANDA)
**Indicador Fabian:** XAU VIVO v2 (privado, sin código fuente — usuario tiene copia en Drive propia para referencia futura)
**Indicador nuestro:** XAU_estrategia_Scalping.pine (MEC/MER) — único Pine Script que tenemos en el repo
**Sesión NY:** 09:01 - 10:59 EDT (UTC-4)

---

## Resumen rápido al iniciar

Se repasó lo aprendido la semana pasada (11-12 jun): fix de líneas m3, `use_limite=false`, pre-señales, bug de ping-pong de estructura, resultado del viernes (nuestro código 2TP vs Fabian 2SL pero cerró semana en +1.35R). Se agregó toggle `use_session` y fix de display "NO-sesion".

Se pasó el código completo actualizado al usuario para cargar en TradingView.

---

## Screenshots y análisis del día

### 09:09 EDT — Vela gigante roja post-apertura

**Contexto:** Rally fuerte de ~4,341 a ~4,353 entre 08:00-09:00. Justo al abrir sesión NY (09:00), vela roja gigante: cae de ~4,353 a ~4,347, sigue bajando hasta ~4,344 a las 09:09.

**Hallazgo clave:** Ningún indicador marcó SELL en esa vela. Tabla mostraba desacuerdo estructural:
- Nuestro "Estructura m3" = ALCISTA (todavía no actualizado)
- Fabian "Dir MR" = BAJISTA (ya había cambiado)

**Hipótesis de la discrepancia:**
1. Lag estructural de M3 — `last_m3_low` solo se actualiza cuando CIERRA una vela M3 (cada 3 min). Si la caída ocurrió dentro de una vela M3 sin cerrar, nuestro nivel de referencia estaba desactualizado.
2. El bajo m3 vigente podía estar más abajo de lo que la vela alcanzó (no se rompió aún según nuestra referencia).
3. Cuerpo insuficiente para `entry_bear` en esa vela específica.

---

### 09:19 EDT — Comparación M1 vs M3 (martillo de Fabian)

**Captura 1 (M1):** Estructura ya BAJISTA (cambió). Zona rosa/teal con niveles Fibonacci (0.25, 0.382, 0.5, 0.618, 0.75) dibujados sobre la caída.

**Captura 2 (M3):** Aparece label "✓E.MARTILLO" (Fabian) justo después de la caída grande, con tabla mostrando "E.Martillo: SELL".

**Pregunta del usuario:** ¿Por qué aparece martillo en M3 pero no en M1?

**Respuesta:** La vela M3 es una agregación de 3 velas M1. Su forma (mecha/cuerpo) es una propiedad EMERGENTE de la combinación — open de la primera M1, low mínimo de las 3, close de la última M1. Ninguna vela M1 individual tenía proporción de martillo; el martillo solo existe al agregar.

**Por diseño**, nuestro código nunca evalúa forma de vela en M3 — solo usa M3 para niveles estructurales (`m3_high_price`/`m3_low_price`). La clasificación de patrones (`mart_bull`, `env_bear`, etc.) corre exclusivamente sobre M1, igual que el modelo original de Fabian descrito el día 1 ("MEC BUY: cuando precio supera con cuerpo la línea punteada en m1").

---

### Repaso vela por vela M1 (08:00-09:19) — entradas reales vs pre-señales

**Nuestro código:**
- `~SELL` (pre-señal) ~08:08 y ~08:20 — no entrada real
- `~BUY` (pre-señal) ~08:30 — no entrada real
- **Cero entradas reales durante todo el rally** (08:00-09:00)

**Fabian:**
- 2 entradas BUY por E.Martillo (~08:32 y ~08:38), ambas con TP marcado ("-0.02 TP" x2) — **2 trades ganadores que nosotros no tomamos**

**Hipótesis de por qué solo pre-señal:**
La vela de ~08:30 tenía cuerpo 75-84% (activó `~BUY`, no `BUY` real). Para entrada real necesitaba:
- Envolvente (`env_bull`): cuerpo ≥85% — no llegó
- Martillo (`mart_bull`): cuerpo 50-85% **+ mecha inferior >30%** — sospecha de que nuestro umbral de mecha es más estricto que el de Fabian

**Pendiente:** Verificar con OHLC exacto de esa vela si `lpct > 0.30` fue el bloqueador real (usuario debe confirmar valores).

---

### 09:28 EDT — Identificación de las dos estrategias activas

**Aclaración importante:** Solo "XAU Scalp" es nuestro (código propio, controlado). "XAU VIVO v2" es el indicador privado de Fabian — nunca tuvimos su código fuente, solo análisis visual.

**Resultado positivo:** Nuestro código disparó una entrada REAL esta vez — **"SELL — MEC ENV SELL"** alrededor de las 09:15-09:18, capturando la continuación bajista después del ChOC. Bien identificado el movimiento de continuación.

**Balance del día hasta este punto:**
| | Fabian (XAU VIVO v2) | Nuestro (XAU Scalp) |
|---|---|---|
| Rally 08:00-09:00 | 2 BUY por martillo (ganadores) | Solo pre-señales, 0 entradas |
| Caída 09:00-09:19 | (sin confirmar) | MEC ENV SELL (en curso) |

---

## Aprendizajes del día

1. **Discrepancia de estructura M3 vs M1 en spikes rápidos** — nuestro sistema puede tardar hasta una vela M3 completa (~3 min) en reflejar un cambio de estructura que Fabian ya detectó. Pendiente de investigar si esto es un lag real o solo diferencia de criterio.

2. **Patrones de vela son timeframe-dependientes** — un martillo en M3 no implica que exista una vela M1 con esa forma. Es una propiedad emergente de la agregación. Confirma que nuestro diseño (M3 = solo estructura, M1 = solo patrones) es correcto y coherente con el modelo original de Fabian.

3. **Posible umbral de mecha demasiado estricto en martillo** — Fabian capturó 2 entradas que nosotros solo pre-señalamos. La sospecha es el filtro `lpct > 0.30` en `mart_bull`/`mart_bear`. Falta confirmar con datos OHLC exactos.

4. **MEC ENV SELL funcionó bien en la continuación** — después de perder las entradas alcistas del rally, nuestro código sí capturó correctamente la continuación bajista posterior al ChOC.

5. **XAU VIVO v2 sigue siendo una caja negra** — el usuario tiene una copia propia guardada en Drive por si en el futuro sirve de referencia, pero seguimos sin código fuente. Cualquier "combinación" futura de estrategias requeriría portar reglas observadas manualmente, no fusión directa de código.

---

### ~09:35 EDT — Fabian deja de responder, usuario opera solo. Búsqueda de RR en PDFs

**Contexto:** Fabian no respondió más mensajes. Usuario sigue operando solo (en venta abierta desde ~09:15-09:18). Pidió revisar los PDFs subidos (Plan Operativo, Plan Técnico, Apariencia del Indicador) en busca de información sobre el RR.

**Hallazgo principal — RR confirmado:** Última página del Plan Técnico dice explícitamente **"RR 1 : 0.9"** — coincide exactamente con nuestro `rr_tp = 0.9`. Sin inconsistencia.

**Otros hallazgos del Plan Técnico (no leído hasta hoy, 31 páginas):**
- **SL:** último bajo m3 (compras) / último alto m3 (ventas) — igual que nuestro código. Si supera 20.000 pips → reduce 40%. Misma estructura que nuestro umbral de 200pts.
- **Regla de "único nivel m3 opuesto" en MER** (pág. 26-27): al ejecutar, solo puede existir UN alto m3 (ventas) o UN bajo m3 (compras) opuesto a la entrada. Si hay dos niveles m3 opuestos visibles (típico en rebotes rápidos post-spike), la ejecución se invalida — salvo que estén a ≤0.01% de distancia, en cuyo caso se extiende el SL al primer nivel y se ejecuta. **Esto es la defensa explícita de Fabian contra el escenario que nosotros llamamos "ping-pong de estructura".** No tenemos esta validación en el código.
- **MER es "solo primer toque"** (pág. 24-25): la vela de entrada debe ser la PRIMERA que toca el nivel m3 de línea continua (el ChOC). Si esa primera vela no cumple parámetros de envolvente/martillo/doji, no hay entrada — no es válido esperar una envolvente posterior.
- **MEC requiere patrón completo Quiebre-Pullback-Continuación** (pág. 19-20) cuando viene de un cambio de estructura, no solo `market_struct` en la dirección correcta.
- **Concepto nuevo "Hedge Position"** (pág. 16): si estando en una operación aparece un patrón de entrada válido en dirección contraria antes de tocar SL/TP, Fabian abre la segunda operación y cierra automáticamente la primera (cobertura). No implementado en nuestro código.
- Plan Operativo (ya leído antes): regla de 3 escenarios de stop diario (1 TP / 1 SL+1TP / 2 SL) y ventanas de no-trading por noticias.

**Pendiente:** Plan Técnico es ahora una referencia completa de las reglas de Fabian — releer con calma fuera de sesión en vivo para auditar nuestro código regla por regla.

---

### ~09:45 EDT — Cambios al código a partir de los hallazgos del Plan Técnico

**Aclaración:** el Plan Técnico se leyó completo (31 páginas, en dos tandas por límite de herramienta) antes de reportar el RR. La comparación regla por regla del documento contra el código sí encontró una inconsistencia real que se corrigió:

1. **Fix martillo:** `lpct > 0.30` / `upct > 0.30` era un umbral inventado por nosotros, no está en el Plan Técnico. La regla real de Fabian es cuerpo 50-85% + mecha A FAVOR de la entrada reducida (mismo umbral que envolvente, <15%) — la mecha opuesta no lleva % fijo. Cambiado a `upct < (1.0 - body_min)` (bull) / `lpct < (1.0 - body_min)` (bear). **Esto probablemente explica las 2 entradas de martillo perdidas en el rally de las 08:30 de hoy.**
2. **Líneas m3 dinámicas:** ahora el estilo (punteada/continua) depende del rol vigente según `market_struct` — punteada = nivel tendencial, continua = nivel de reversión/ChOC — igual que el Plan Técnico pág.3-4. Antes alto m3 siempre era punteado y bajo m3 siempre continuo, sin importar la estructura.
3. **Etiqueta numérica en cada línea m3** (precio al final de la línea) — pendiente desde sesiones anteriores, implementado.
4. **Texto "CAMBIO DE ESTRUCTURA ALCISTA/BAJISTA"** en el ChOC — pendiente desde sesiones anteriores, implementado.

**No tocado (ambigüedad real en el documento):** la "vela envolvente doji" del Plan Técnico (pág.8-9) tiene un umbral de 15%/85% descrito en texto que admite más de una lectura razonable. Se dejó nuestra definición de "doji" actual sin cambios para no meter un bug nuevo en código que se está usando en vivo ahora mismo — queda pendiente validarlo comparando señales reales.

**No hacía falta tocar:**
- Regla de "único nivel m3 opuesto" en MER — ya estaba implementada (`mer_sl_long`/`mer_sl_short` devuelven `na` y bloquean el trade si hay dos niveles válidos no cercanos).
- "Hedge Position" (cobertura) — ya ocurre sola por el comportamiento nativo de `strategy.entry` en Pine sin pyramiding (al entrar en dirección contraria revierte la posición).

---

### ~09:50 EDT — Comparación de capturas (Fabian vs nuestro) y nueva directiva

**Contexto:** Usuario compartió dos capturas (su gráfico con la toma de decisión de Fabian vs el nuestro) pidiendo comparación completa: decisión, altos/bajos m3, tipo de entrada, velas.

**Hallazgos de la comparación:**
- **Patrón exclusivo nuestro:** la pre-señal (`~SELL`/`~BUY`, cuerpo 75-85%) no existe en el indicador de Fabian — es una capa de aviso que agregamos nosotros, sin equivalente en su sistema.
- **Niveles m3 ligeramente distintos:** nuestro último alto/bajo m3 vs el de Fabian no coincidían exactamente (~4341 vs ~4342.5 aprox.) — probablemente por timing de cierre de vela M3 o por la regla de "variante fractal extendido" del Plan Técnico (pág.2-3, nivel real puede estar en una vela adyacente con mecha más extrema) que no tenemos implementada.
- **Modelo de entrada distinto en el mismo movimiento:** donde nuestro código marcó MEC, el criterio de Fabian correspondía más a MER (entrada en el mismo bar del ChOC) — confirma que el timing de `market_struct` puede estar corriendo del lado nuestro antes de tiempo (mismo tema que el ping-pong de estructura ya documentado).
- **Balance aproximado al momento de la comparación:** Fabian alrededor de +0.94R en la sesión.

**Conclusión del usuario:** decidió que, en lugar de seguir comparando y reconciliando diferencia por diferencia, el código debe replicar EXACTAMENTE la operativa de Fabian — sus reglas están respaldadas por 8 meses de backtesting propio, así que se tratan como autoridad ("palabra santa"). Objetivo explícito: acercar nuestra rentabilidad a la de él (+1.35R semanal, semana 9-13 jun).

**Cambios implementados a partir de esta directiva:**
1. **`use_limite` activado por defecto** (`true`) — el día ahora se detiene igual que Fabian: 1 TP, o 1 SL+1TP, o 2 SL. Antes estaba desactivado a propósito solo para poder comparar señales sin cortar el día.
2. **Nuevo módulo `use_news_block`** (manual) — releído el Plan Operativo completo (3 páginas) para extraer las reglas exactas de noticias: alto impacto = ventana -10min/+3min (no abrir ni cerrar), medio impacto = ventana -3min/+3min (solo bloquea aperturas nuevas, una operación abierta se puede sostener), orador de impacto medio con hora programada = tratar como alto impacto, 5 eventos de no-sostener-operación-abierta (Federal Funds Rate & Statement, NFP, CPI y/y, FOMC Minutes, Advance GDP q/q). Como TradingView/Pine no tiene feed nativo de calendario económico, se implementó como dos inputs de texto (`sess_news_high`, `sess_news_med`, formato `HHMM-HHMM`) que el usuario debe llenar antes de cada sesión con las ventanas ya calculadas del día. `can_trade` ahora exige `not in_news_block`; la tabla muestra "NO-noticia" cuando aplica.

**No tocado todavía:** la "variante fractal extendido" de los niveles m3 (pendiente, ver hallazgo de comparación arriba) y el lag estructural M3 vs M1 en spikes — quedan en la lista de correcciones pendientes.

---

### ~14:53 EDT — Corrección: `use_limite` se revierte a desactivado, se agrega cooldown post-spike

**Contexto:** el usuario aclaró la directiva anterior: replicar la operativa de Fabian línea por línea, EXCEPTO el límite diario de entradas — porque en sesión en vivo queremos ver TODAS las señales del día para comparar, no que el código se quede mudo el resto de la sesión después del primer TP/SL.

**Releídos `sesion_vivo_2026-06-11` y `sesion_vivo_2026-06-12` completos** para confirmar el motivo original: en ambas sesiones pasadas se aprendió (dos veces, de forma independiente) que activar `use_limite` corta toda señal posterior y arruina la comparación visual con Fabian — no es una regla de Fabian que debamos imitar, es una limitación de nuestra herramienta de comparación. El cambio de las 09:45 (activar `use_limite=true`) se revierte: vuelve a `false` por defecto.

**Cooldown post-spike implementado** (pendiente desde 11-jun y 12-jun, marcado [PRIORITARIO] en ambas sesiones): nuevo `use_cooldown` + `spike_size` (10pts default) + `cooldown_bars` (15 default). Cualquier vela M1 con rango ≥`spike_size` marca `last_spike_bar`; `can_trade` se bloquea durante las siguientes `cooldown_bars` velas. Replica la paciencia de Fabian tras noticias ("Fabian espera ~15-20 minutos" — confirmado en ambas sesiones pasadas) y de paso mitiga parte del ping-pong de estructura, porque los niveles m3 espurios del rebote post-spike se forman justo en esa ventana. Tabla muestra "NO-cooldown" cuando aplica.

**Se mantiene sin cambios:** `use_news_block` (no es un corte de día completo, son ventanas acotadas de pocos minutos — no entra en conflicto con "ver todo el día").

---

## Correcciones pendientes (acumulado)

1. **[PRIORITARIO]** Ping-pong de estructura — lado MER **ya resuelto** (`mer_sl_long`/`mer_sl_short` bloquean si hay dos niveles m3 opuestos no cercanos). Lado MEC/`market_struct` mitigado parcialmente por el cooldown post-spike de hoy, pero sigue pendiente extender la idea de "nivel único" directamente a `market_struct`.
2. ~~Cooldown post-spike~~ — **resuelto 16-jun**: `use_cooldown`/`spike_size`/`cooldown_bars` implementados, bloquean `can_trade` por N velas tras un spike.
3. ~~Revisar umbral mecha en martillo (`lpct`/`upct` > 0.30)~~ — **resuelto 16-jun**: era un umbral inventado, no estaba en el Plan Técnico; corregido a mecha-a-favor reducida.
4. Investigar lag estructural M3 vs reacción más rápida de Fabian en spikes — sigue pendiente, sin cambios hoy.
5. ~~Evaluar regla MER "solo primer toque"~~ — **confirmado ya implementado**: `choc_bull`/`choc_bear` son pulsos de un solo bar, no es posible esperar una envolvente posterior.
6. ~~Evaluar "Hedge Position"~~ — **confirmado que ya ocurre solo** por el netting nativo de `strategy.entry` en Pine sin pyramiding.
7. ~~Etiqueta numérica en líneas m3~~ — hecho 16-jun.
8. ~~Texto "Cambio de estructura" en chart~~ — hecho 16-jun.
9. **[NUEVO]** "Variante fractal extendido" de niveles m3 (Plan Técnico pág.2-3): a veces el nivel real no está en la mecha de las dos velas que definen el par, sino en una vela adyacente del mismo movimiento con mecha más extrema. Gap confirmado al comparar capturas hoy (~4341 vs ~4342.5). No implementado — ambigüedad real de cómo delimitar el "fractal" algorítmicamente sin riesgo de repintado/inestabilidad.
10. Validar en vivo el umbral exacto de "vela envolvente doji" del Plan Técnico (texto ambiguo, no traducido a código).
11. **[NUEVO]** Antes de cada sesión, si hay noticias USD en el calendario de Forex Factory durante la ventana NY, llenar `sess_news_high`/`sess_news_med` con las ventanas ya calculadas (ver módulo `use_news_block`, añadido hoy).

---

## Estado del código al momento de este log

**Archivo:** `XAU_estrategia_Scalping.pine`
**Branch:** `claude/trading-strategy-inconsistencies-w9S9b`
**Último cambio:** `use_limite` revertido a `false` (excepción explícita a la directiva "replicar exactamente a Fabian" — ver sesión 14:53) + nuevo módulo `use_cooldown` (post-spike) + `use_news_block` (bloqueo manual de noticias vía `sess_news_high`/`sess_news_med`) ambos siguen activados

**Sesión en curso** — se continúa actualizando este log a medida que avanza el día.
