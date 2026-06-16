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

## Correcciones pendientes (acumulado)

1. **[PRIORITARIO]** Fix ping-pong de estructura (pendiente desde 11-12 jun)
2. **[PRIORITARIO]** Cooldown post-spike (pendiente desde 12 jun)
3. **[NUEVO]** Revisar si `lpct > 0.30` / `upct > 0.30` en martillo es demasiado estricto vs criterio de Fabian — necesita datos OHLC de vela específica para confirmar
4. **[NUEVO]** Investigar lag estructural M3 vs reacción más rápida de Fabian en spikes — posible necesidad de detectar quiebres usando M1 en vez de esperar cierre de M3
5. Etiqueta numérica en líneas m3 (pendiente)
6. Texto "Cambio de estructura" en chart (pendiente)

---

## Estado del código al momento de este log

**Archivo:** `XAU_estrategia_Scalping.pine`
**Branch:** `claude/trading-strategy-inconsistencies-w9S9b`
**Último cambio:** `use_session` toggle + fix display "NO-sesion"

**Sesión en curso** — se continúa actualizando este log a medida que avanza el día.
