# Sesión en Vivo — XAUUSD — Jueves 11 Jun 2026

**Trader:** Fabian (humano, opera manualmente) + análisis Claude
**Instrumento:** Gold Spot / U.S. Dollar (XAUUSD OANDA)
**Indicador Fabian:** XAU VIVO v2 (privado, sin código fuente)
**Indicador nuestro:** XAU_estrategia_Scalping.pine (MEC/MER)
**Sesión NY:** 09:01 - 10:59 EDT (UTC-4)
**Nota:** Fabian es trader humano, no maneja código. Comparación es visual entre sus charts y los nuestros.

---

## Screenshots y análisis del día

### 08:48 EDT — Primera captura (XAU VIVO v2 de Fabian)

**Estado del mercado:**
- Estructura M3: ALCISTA
- Sesión NY: aún no abierta (abre a las 09:01)
- Precio: 4,075.735
- Posición Fabian: LONG @ 4,075.315
- Tipo de entrada: E.Martillo (martillo alcista)
- GB High: 4,073.9
- GB Low: 4,057.55

**Observaciones:**
- La última vela (08:48) es bajista — pullback desde el spike de 08:45
- El nivel GB High 4,073.9 actúa como soporte
- Indicador marca "CONTACTO" cuando precio toca nivel m3 (señal MER)
- "E.Martillo" confirma tipo de vela de entrada = martillo

---

### 08:57 EDT — Gráfico M3 (Fabian)

**Timeframe:** 3 minutos
**Precio:** 4,079.115

**Estructura visible en M3:**
- Estructura: ALCISTA ✓
- Línea continua (bajo m3 actual): ~4,057-4,058
- Líneas punteadas (altos m3): ~4,074 y ~4,082-4,085
- Precio consolidando entre 4,077-4,081 tras gran rally desde 4,057

**Lógica de Fabian explicada:**
- MEC BUY: cuando precio supera con cuerpo la línea punteada (alto m3) en m1
- MER SELL: cuando precio rompe la línea continua (bajo m3) → ChOC bajista

---

### 09:15 EDT — CAMBIO DE ESTRUCTURA A BAJISTA (Fabian)

**Anotación de Fabian:** *"Cambio de estructura a bajista"*
**Precio:** 4,074.745

**Análisis:**
- La estructura cambió de ALCISTA a BAJISTA
- El ChOC bajista ocurrió cuando una vela m1 cerró por debajo del bajo m3 más reciente (NO el 4,057 del rally anterior, sino un nuevo bajo m3 formado durante la consolidación post-rally ~4,075-4,077)
- Alto m3 referencia para SELL: ~4,085-4,086

**Aprendizaje clave:** Los bajos m3 se actualizan continuamente. No rompe siempre el mínimo más lejano — rompe el ÚLTIMO bajo m3 formado, que puede ser más alto que el del inicio del movimiento.

---

### 09:30 EDT — XAU Scalp cargado (M3 y M1)

**M3:** Estructura BAJISTA ✓, señales "MEC START SELL" visible, TP/SL dia: 4/5 (alto = trades fuera de sesión)
**M1:** TP/SL dia: 7/13 (confirmó el problema de trades fuera de sesión)

**Problemas detectados y corregidos ese día:**
1. Trades disparando fuera de sesión (07:25, 08:30 en M3)
2. Líneas m3 como steplines continuas (incorrecto)
3. Líneas con `gaps_off` se recreaban cada barra (bug visual)
4. `extend.right` hacía las líneas infinitas

---

### 10:01 EDT — "Casi MER SELL" (Fabian)

**Fabian marcó una vela con rectángulo rojo mostrando niveles de cuerpo:**
- 0 = top del rango
- 0.15 = límite mecha superior martillo
- 0.5 = límite martillo
- 0.85 = límite mínimo envolvente
- 1 = bottom del rango

**La vela llegó al ~83-84% del cuerpo — NO alcanzó el 85% mínimo**
- MER SELL: NO disparó (bpct < 0.85) ✓ correcto
- MEC SELL: Tampoco disparó (mismo umbral bloqueó)

**Mensaje de Fabian (10:31 EDT):**
> "Bro por lo pronto se creo un nuevo alto"
> "Y el precio en m1 intento traspasarlo pero no lo logro"
> "Recuerda que debe pasar con cuerpo con un volumen mayor o igual a 0.01% para válida el quiebre del nivel"
> "De cumplir esas reglas en ese alto, confirmamos un cambio de comportamiento a alcista"

→ Confirma que nuestro `min_brk = 0.0001` (0.01%) está correcto y alineado con Fabian.

---

### 10:10 EDT — Entrada perdida (M1)

**El código no marcó una entrada que hubiese sido buena:**
- Después del ChOC bajista de las 10:00
- Precio bajó de ~4,088 a ~4,073 = ~15 puntos
- Nuestra entrada habría sido: Short @ ~4,082, SL ~4,092, TP ~4,073

**Por qué no se marcó:**
- El mismo umbral del 85% que bloqueó el MER (~83% cuerpo) también bloqueó el MEC ENV SELL
- Posible también: estructura ping-pongeó bajista→alcista→bajista por nuevos altos m3 formándose a niveles más bajos

**Solución implementada:** Pre-señales `~SELL`/`~BUY` (cuerpo 75-85%, naranja pequeño)

---

## Cambios al código realizados hoy

| # | Cambio | Motivo |
|---|---|---|
| 1 | `use_limite = false` por defecto | Bloqueaba trading durante sesión en vivo |
| 2 | `can_trade = in_session and (...)` | Trades disparaban 24/7 fuera de sesión |
| 3 | Reemplazar `plot(stepline)` por `line.new` | Steplines no coinciden con el diseño original ni de Fabian |
| 4 | `gaps=barmerge.gaps_on` | `gaps_off` llenaba forward y recreaba líneas cada barra |
| 5 | `x1 = bar_index - 1` (no x1==x2) | Punto en vez de línea con x1==x2 |
| 6 | `line.set_x2` cada barra, sin `extend.right` | Líneas infinitas → longitud fija configurable |
| 7 | Quitar `line.delete` | Mantener historial de niveles para analizar tendencia |
| 8 | `m3_line_len` default: 10 → 5 | Líneas seguían siendo muy largas |
| 9 | Agregar `body_warn = 0.75` + pre-señales `~BUY`/`~SELL` | Capturar entradas "casi válidas" (75-85% cuerpo) sin entrar operación |

---

## Aprendizajes del día

1. **ChOC no rompe siempre el nivel más lejano** — rompe el ÚLTIMO bajo/alto m3 formado, que se actualiza continuamente con el movimiento.

2. **gaps_off vs gaps_on** — `gaps_off` llena el valor hacia adelante en CADA barra (malo para detección puntual). `gaps_on` solo dispara cuando realmente se forma el nivel.

3. **El 85% de cuerpo es un filtro duro** — velas de 83-84% quedan afuera aunque visualmente parezcan válidas. Solución: pre-señal para avisar que nos estamos acercando.

4. **Los niveles m3 históricos importan** — ver la secuencia de altos/bajos m3 permite leer la tendencia de un vistazo. No borrar los anteriores.

5. **Fabian opera manualmente** — no tiene código. La comparación siempre es visual (sus charts vs los nuestros).

6. **Quiebre mínimo 0.01%** — Fabian confirmó que usa exactamente ese porcentaje para validar quiebre de nivel. Alineado con nuestro `min_brk = 0.0001`.

7. **Estructura puede ping-pongear** — en movimientos volátiles, el market_struct puede cambiar bajista→alcista→bajista rápidamente si se forman nuevos altos m3 a niveles más bajos que luego se rompen hacia arriba. Esto puede bloquear entradas válidas.

---

## Diferencias detectadas entre XAU VIVO v2 y nuestro código

| Característica | XAU VIVO v2 (Fabian) | XAU Scalp (nuestro) |
|---|---|---|
| Anotaciones visuales | Texto en chart ("Cambio de estructura a bajista") | Solo bgcolor rojo/verde en ChOC |
| Tipo de entrada | Muestra "E.Martillo", "E.Envolvente" | Muestra "MEC ENV", "MEC START", "MER" |
| Niveles GB | "GB High" / "GB Low" con etiqueta de precio | Líneas sin etiqueta numérica |
| Análisis % cuerpo | Rectángulo con niveles 0/0.15/0.5/0.85/1 | Sin visualización de % cuerpo |
| Pre-señal | Aparentemente sí (marca "CONTACTO") | Agregado hoy: `~BUY`/`~SELL` |
| Operación real | Fabian decide manualmente | Estrategia automática (backtesting/paper) |

---

## Correcciones pendientes para próxima sesión

1. **Investigar el ping-pong de estructura** — cuando el mercado hace ChOC bajista y luego rebota brevemente formando un nuevo alto m3 más bajo, el código puede volver a ALCISTA y bloquear SELL. Revisar si esto es correcto según las reglas de Fabian o si necesita un filtro.

2. **Etiqueta de precio en líneas m3** — agregar el valor numérico al final de cada línea como hace Fabian ("GB High: 4,073.9").

3. **Texto "Cambio de estructura"** — agregar anotación en chart cuando ocurre ChOC, como hace Fabian.

4. **Verificar contador TP/SL dia** — al final de la sesión mostraba 0/2 cuando debería haber TPs. Revisar lógica de `strategy.netprofit > strategy.netprofit[1]`.

5. **Validar pre-señales** — confirmar en próxima sesión que `~SELL`/`~BUY` aparecen en los casos correctos (75-85% cuerpo con estructura y contexto válidos).

---

## Estado del código al cierre de sesión

**Archivo:** `XAU_estrategia_Scalping.pine`
**Último commit:** Pre-señales ~BUY/~SELL + líneas m3 longitud 5 velas
**Branch:** `claude/trading-strategy-inconsistencies-w9S9b`

**Parámetros clave actuales:**
- Sesión NY: 09:01-10:59 EDT
- Cuerpo min envolvente: 85%
- Cuerpo pre-señal: 75%
- Cuerpo min martillo: 50%
- Quiebre mínimo: 0.01%
- RR: 1:0.9
- SL máximo: 200 puntos
- Longitud líneas m3: 5 velas
- Límite diario: desactivado (use_limite = false)
