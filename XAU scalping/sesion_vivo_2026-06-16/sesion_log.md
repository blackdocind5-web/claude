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

## Correcciones pendientes (acumulado)

1. **[PRIORITARIO]** Fix ping-pong de estructura (pendiente desde 11-12 jun) — **ahora con solución concreta de Fabian**: invalidar ejecución MER si hay dos niveles m3 opuestos visibles, salvo que estén a ≤0.01% de distancia (ver hallazgo de hoy en Plan Técnico pág. 26-27)
2. **[PRIORITARIO]** Cooldown post-spike (pendiente desde 12 jun)
3. **[NUEVO]** Revisar si `lpct > 0.30` / `upct > 0.30` en martillo es demasiado estricto vs criterio de Fabian — necesita datos OHLC de vela específica para confirmar
4. **[NUEVO]** Investigar lag estructural M3 vs reacción más rápida de Fabian en spikes — posible necesidad de detectar quiebres usando M1 en vez de esperar cierre de M3
5. **[NUEVO]** Evaluar implementar regla MER "solo primer toque" (no esperar envolvente posterior)
6. **[NUEVO]** Evaluar implementar "Hedge Position" (cobertura automática al aparecer señal contraria en operación abierta)
7. Etiqueta numérica en líneas m3 (pendiente)
8. Texto "Cambio de estructura" en chart (pendiente)

---

## Estado del código al momento de este log

**Archivo:** `XAU_estrategia_Scalping.pine`
**Branch:** `claude/trading-strategy-inconsistencies-w9S9b`
**Último cambio:** `use_session` toggle + fix display "NO-sesion"

**Sesión en curso** — se continúa actualizando este log a medida que avanza el día.
