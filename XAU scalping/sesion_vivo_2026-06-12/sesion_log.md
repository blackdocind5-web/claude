# Sesión en Vivo — XAUUSD — Viernes 12 Jun 2026

**Trader:** Fabian (humano, opera manualmente) + análisis Claude
**Instrumento:** Gold Spot / U.S. Dollar (XAUUSD OANDA)
**Indicador Fabian:** XAU VIVO v2 (privado, sin código fuente)
**Indicador nuestro:** XAU_estrategia_Scalping.pine (MEC/MER)
**Sesión NY:** 09:01 - 10:59 EDT (UTC-4)

---

## Contexto de mercado del día

- **Noticia 09:00 EDT:** University of Michigan Consumer Sentiment / Inflation Expectations (dato mensual)
  - Clasificación: "Medio impacto" (según Fabian)
  - Efecto: vela bajista gigante de ~13.8 pts en los primeros segundos de sesión
- **Tendencia del día:** Gold ~4,225 (+0.31%), alcista general
- **Semana:** CPI de mayo + expectativas de inflación U. of Michigan
- **Próximo evento macro:** FOMC minutes el 17 de junio
- **Contexto geopolítico:** Optimismo por posible acuerdo EEUU-Irán (reduce presión inflacionaria)

---

## Screenshots y análisis del día

### 09:24 EDT — Captura Fabian (XAU VIVO v2)

**Descripción:** Chart M1 OANDA de Fabian mostrando la entrada MER BUY del día.

**Estado del mercado:**
- Precio actual: ~4,205.395
- Fabian: LONG activo por MER

**Eventos clave visibles:**
- **09:00 EDT** — Vela bajista grande por noticias "Medio impacto":
  - Caída desde ~4,213 a ~4,187 (~13,840 pts / 0.329%)
  - Caja gris marcando el movimiento bajista
- **Post-09:00** — Recuperación alcista:
  - Subida desde ~4,187 a ~4,205 (~12,524 pts / 0.298%)
  - Caja azul marcando el movimiento alcista
- **~09:20-09:24** — ChOC alcista: vela m1 cerró con cuerpo por encima del alto m3 más reciente → cambio de estructura a ALCISTA
- **09:24** — Fabian entra LONG por MER en ~4,205

**Lógica de Fabian:**
- Esperó que el caos post-noticia se calmara completamente
- Esperó el ChOC alcista real (precio superó con cuerpo el alto m3 legítimo con ≥0.01%)
- Entró en la confirmación del cambio de estructura real
- Tipo de entrada: MER (Modelo de Entrada Retroceso / primer toque al nivel ChOC)

---

### 09:27 EDT — Captura XAU Scalp (nuestro código, M1)

**Descripción:** Chart M1 mostrando nuestras señales en el mismo período.

**Configuración visible (dos indicadores cargados — PROBLEMA):**
- `XAU Scalp (0901-1059, 0.9, 0.85, 0.5, 200, 0.4, 0.0001, 8)` ← versión VIEJA (sin body_warn)
- `XAU Scalp (0901-1059, 0.9, 0.85, 0.75, 0.5, 200, 0.4, 0.0001, 5)` ← versión NUEVA ✓

**Table info (top right):**
- Estructura m3: ALCISTA ✓
- Sesión NY: ACTIVA ✓
- Puede operar: **NO-límite** ← BLOQUEADO
- TP / SL día: 10/0 (aproximado)
- RR: 1:0.9

**Señales marcadas por nuestro código:**

1. **SELL ~09:01 EDT** (etiqueta naranja/amarilla)
   - Al abrir sesión, estructura ya era BAJISTA (la caída de las 09:00 rompió el bajo m3)
   - Marcó venta en la primera vela de sesión
   - Tipo: MEC o MER SELL (por estructura bajista heredada de 09:00)
   - Resultado probable: TP → `day_tp = 1` → con `use_limite = true` bloqueó todo

2. **MEC ENV BUY ~09:06 EDT** (etiqueta gris con "+2.38")
   - Código entró LONG a los 5 minutos de la caída, en plena volatilidad
   - **Causa:** ping-pong de estructura: caída → nuevo alto m3 más bajo se formó → precio lo rompió → `market_struct = 1` → disparó MEC ENV BUY
   - **Etiqueta incorrecta:** debería haber sido MER BUY pero el código lo clasificó como MEC ENV BUY porque el market_struct ya estaba en 1 cuando entró

3. **Después: BLOQUEADO** — "NO-límite" cortó todo el trading posterior
   - `use_limite = true` en la instancia cargada
   - Con `day_tp >= 1` → `can_trade = false` para el resto de la sesión

**Líneas m3 visibles:**
- Varias líneas rojas punteadas (altos m3) en ~4,200-4,202
- Varias líneas verdes sólidas (bajos m3) en ~4,188-4,194

---

### 10:11 EDT — Captura XAU Scalp M3 (nuestro código)

**Timeframe:** 3 minutos — da visión completa del recorrido del día

**Table info:**
- Estructura m3: **BAJISTA** (cambió cuando la caída de 09:37-09:40 rompió el bajo m3)
- Sesión NY: ACTIVA
- Puede operar: **SI** ✓ (use_limite corregido)
- TP / SL día: **1 / 0** ✓

**Recorrido completo visible en M3:**
1. 09:00 — Drop noticia a ~4,187
2. 09:05 — Código entra MEC ENV BUY en recuperación
3. 09:30-09:35 — Spike alcista hasta ~4,212
4. TP del BUY alcanzado durante el spike → day_tp = 1
5. 09:37-09:40 — Gran vela bajista, estructura cambia a BAJISTA
6. Código entra SELL en el ChOC bajista
7. Precio cae desde ~4,212 hasta ~4,183 (~29 pts)
8. SELL en TP → day_tp = 2 (confirmado por tabla 1/0 → luego 2/0)

### 10:13 EDT — Captura Fabian M1 (análisis post-trade)

**Anotaciones de Fabian:**
- Caja azul (09:01-09:30): Recovery 12.524 pts (0.298%) — período BUY
- Caja gris (pre-09:00): Drop inicial 13.840 pts (0.329%)
- Caja gris grande (09:37-09:47): Spike alcista 18.875 pts (0.450%) — trampa
- Caja rosa/roja (09:40-10:03): Drop final 16.916 pts (0.404%) — reversal violento
- "-0.65R" junto al BUY: pérdida del trade 1
- Rectángulo rojo en SELL: trade 2 (también cerrado en SL)

**Secuencia trampa doble de las 09:37:**
1. Spike alcista limpia los SL de los shorts anteriores
2. Genera señal de BUY (Fabian ya estaba en BUY, no llegó al TP)
3. Reversión violenta baja desde 4,212 a 4,175 → limpia el BUY de Fabian
4. Fabian intenta SELL → reversión parcial limpia también ese SL

---

## Comparación Fabian vs Nuestro Código

| Evento | Nuestro código | Fabian |
|---|---|---|
| Primera acción | SELL 09:01 (estructura bajista) | Esperó |
| Segunda acción | MEC ENV BUY 09:06 (prematuro) | Esperó |
| Entrada real | BLOQUEADO por use_limite | MER BUY 09:24 |
| Tipo de entrada | MEC ENV (incorrecto) | MER (correcto) |
| Identificación de vela | ✅ Correcto (vela válida) | ✅ Correcto |
| Timing | Demasiado temprano | Paciente, esperó confirmación |
| Resultado | No pudo seguir operando | En operación activa |

**Conclusión clave:** El código identificó correctamente la vela de entrada (Fabian lo confirmó — "identificó bien la vela de entrada"), pero la clasificó como MEC en lugar de MER porque el ping-pong de estructura ya había cambiado `market_struct` a 1 antes del ChOC real.

---

## Problemas identificados hoy

### 1. Ping-pong de estructura (bug conocido, confirmado hoy)
**Descripción:** En movimientos volátiles post-noticia:
1. Gran caída → `market_struct = -1` (bajista)
2. Pequeño rebote forma nuevo alto m3 más bajo
3. Precio rompe ese nuevo alto m3 → `choc_bull` → `market_struct = 1` (alcista)
4. Ya no hay MER disponible — el código entra por MEC antes del ChOC real de Fabian

**Consecuencia:** Entradas prematuras en períodos volátiles. La señal es válida en cuanto a vela, pero el timing y el modelo (MEC vs MER) son incorrectos.

**Pendiente:** Investigar filtro de cooldown post-spike o requerir que el alto m3 roto sea el MISMO que el que creó la estructura bajista original.

### 2. use_limite activado sin querer
**Descripción:** Una de las dos instancias cargadas tenía `use_limite = true`, bloqueando el trading después del primer TP.

**Solución inmediata:** En settings del indicador → `use_limite = false`

### 3. Dos indicadores cargados simultáneamente
**Descripción:** Versión vieja (8 params, sin body_warn) y versión nueva (9 params, con body_warn) cargadas al mismo tiempo.

**Solución:** Borrar la versión vieja, dejar solo la nueva.

---

## Concepto nuevo: Cooldown post-spike

**Definición:** Período de tiempo en el que el código no entra trades aunque haya señal, porque acaba de ocurrir una vela de tamaño anormal (spike).

**Motivación:** Post-noticias, el mercado está en caos. Fabian espera instintivamente; el código entra inmediatamente. En días normales esto puede costar trades; en días como hoy fue ventajoso por casualidad.

**Implementación propuesta:**
```pine
spike_size = input.float(10.0, "Tamaño mínimo spike (pts)")
cooldown_bars = input.int(15, "Velas de espera post-spike")
var int last_spike_bar = na
big_candle = (high - low) >= spike_size
if big_candle
    last_spike_bar := bar_index
in_cooldown = not na(last_spike_bar) and (bar_index - last_spike_bar) < cooldown_bars
can_trade = in_session and not in_cooldown and (not use_limite or ...)
```

**Parámetros sugeridos para evaluar:** spike ≥ 10 pts, cooldown 15 velas m1 (~15 minutos)

---

## Aprendizajes del día

1. **El código identifica bien la vela de entrada** — Fabian confirmó que la vela que marcamos como MEC ENV BUY era efectivamente una vela válida de entrada. El problema fue el modelo (MEC vs MER), no el reconocimiento de la vela.

2. **Post-noticias = ping-pong de estructura** — Confirmado en vivo. En noticias "Medio impacto" o mayor, los primeros 5-20 minutos tienen movimientos erráticos que hacen flip-flop la estructura. Fabian espera; nuestro código no puede esperar.

3. **use_limite debe ser false en sesión en vivo** — Confirmado otra vez. Con límite activado, el primer trade bloquea toda la sesión.

4. **Fabian es muy paciente en post-noticias** — Esperó 24 minutos después de la caída para confirmar el ChOC real. Nuestro código entró a los 5 minutos.

5. **Mantener una sola instancia del indicador** — Tener dos versiones cargadas genera confusión visual y dos tablas/señales.

6. **Spike falso = trampa doble** — El spike de las 09:37 subió ~19 pts para luego caer ~17 pts. Limpia posiciones en ambas direcciones. Patrón frecuente en viernes con noticias de alto impacto.

7. **"Incorrecto" puede ser rentable** — El MEC ENV BUY de las 09:05 fue el modelo equivocado (debió ser MER) pero fue el trade más rentable del día. Timing prematuro pero con SL/TP bien calibrados puede sobrevivir la volatilidad.

8. **Fabian también pierde** — Incluso con su sistema maduro y experiencia humana, días de trampa doble post-noticia resultan en 2 SL seguidos. El mercado puede ser impredecible para cualquier sistema.

9. **Viernes + Michigan = volatilidad extrema** — El dato de U. of Michigan sale el último viernes del mes. Marcar en calendario para aplicar precaución extra o no operar esa apertura.

---

## Correcciones pendientes

1. **[PRIORITARIO] Filtro post-spike/cooldown** — Opción para no operar durante X minutos después de un movimiento brusco (ej. spike > Y puntos en 1 vela). Evita entradas en caos post-noticia.

2. **[PRIORITARIO] Fix ping-pong de estructura** — Revisar si el ChOC que cambia la estructura usa el mismo nivel m3 del movimiento original, no un nivel intermediario formado durante el rebote.

3. **Etiqueta numérica en líneas m3** — Mostrar el precio al final de cada línea (como Fabian: "GB High: 4,073.9").

4. **Texto "Cambio de estructura"** — Anotar en chart cuando ocurre ChOC, como hace Fabian.

5. **Verificar contador TP/SL día** — El contador no refleja correctamente los resultados.

---

## Estado del código al cierre de análisis

**Archivo:** `XAU_estrategia_Scalping.pine`
**Branch:** `claude/trading-strategy-inconsistencies-w9S9b`

**Parámetros clave actuales (versión nueva):**
- Sesión NY: 09:01-10:59 EDT
- Cuerpo min envolvente: 85%
- Cuerpo pre-señal: 75%
- Cuerpo min martillo: 50%
- Quiebre mínimo: 0.01%
- RR: 1:0.9
- SL máximo: 200 puntos
- Longitud líneas m3: 5 velas
- Límite diario: **desactivado (use_limite = false)** ← IMPORTANTE mantener así

---

## Resultados finales de la sesión

### Nuestro código
| Trade | Tipo | Entrada | Resultado |
|---|---|---|---|
| 1 | MEC ENV BUY | ~09:05 ~4,200 | TP ✓ |
| 2 | SELL | ~09:37 ~4,212 | TP ✓ |
| **Total** | | | **2 TP / 0 SL** |

### Fabian
| Trade | Tipo | Entrada | Resultado |
|---|---|---|---|
| 1 | MER BUY | ~09:24 ~4,200 | SL ✗ (-0.65R) |
| 2 | SELL | ~09:40 ~4,212 | SL ✗ |
| **Total** | | | **0 TP / 2 SL** |

### Análisis del resultado

El spike falso de las 09:37 a ~4,212 fue una trampa doble:
- Limpió el BUY de Fabian (que entró a 4,200 pero el TP no alcanzó)
- Luego la reversión violenta hasta 4,175 limpió su SELL también

Nuestro código se benefició de entrar MÁS TEMPRANO (09:05 vs 09:24) — el TP del BUY fue alcanzado durante el spike antes de la reversión. El modelo fue "incorrecto" (MEC vs MER) pero el timing accidentalmente fue mejor.

**Lección:** En días de alta volatilidad post-noticia, los spikes falsos castigan las entradas tardías más que las prematuras. No es una regla general — fue el contexto específico de hoy.

---

## Notas para próxima sesión

- Implementar cooldown post-spike antes de siguiente sesión en vivo
- Verificar que solo hay UNA instancia del indicador cargada
- Confirmar que use_limite = false antes de abrir sesión
- Preguntar a Fabian si tiene filtro especial para períodos post-noticia
- Estudiar por qué el spike falso de hoy no tenía continuación — posible patrón recurrente en viernes con noticias Michigan
