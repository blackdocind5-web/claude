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
| Límite diario | **DESACTIVADO** (`use_limite = false`) — NUNCA activar en sesión en vivo |

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

### [PRIORITARIO] Cooldown post-spike
El código entra inmediatamente después de velas gigantes (noticias). Fabian espera ~15-20 minutos.

**Implementación propuesta:**
```pine
spike_size   = input.float(10.0, "Tamaño mínimo spike (pts)")
cooldown_bars = input.int(15,   "Velas de espera post-spike")
var int last_spike_bar = na
if (high - low) >= spike_size
    last_spike_bar := bar_index
in_cooldown = not na(last_spike_bar) and (bar_index - last_spike_bar) < cooldown_bars
// agregar: and not in_cooldown a can_trade
```

### Pendientes menores
- ~~Etiqueta numérica al final de cada línea m3~~ — hecho 16-jun (`lbl_m3_high`/`lbl_m3_low`)
- ~~Texto "Cambio de estructura" en chart cuando ocurre ChOC~~ — hecho 16-jun
- Verificar contador TP/SL día (lógica con `strategy.netprofit` puede tener timing issues)
- Validar en vivo el umbral exacto de "vela envolvente doji" del Plan Técnico (texto ambiguo, no traducido a código)

## Documentos de Fabian (no son parte del repo, en uploads de la sesión)
- **Plan Operativo** — horario, reglas de noticias (Forex Factory, ventanas por impacto), 3 escenarios de stop diario (1 TP / 1 SL+1TP / 2 SL)
- **Plan Técnico** (31 págs) — la referencia más completa: estructura m3 (incl. variantes de fractal extendido), líneas punteadas (tendencial) vs continuas (reversión/ChOC), los 3 tipos de vela envolvente con sus % exactos, patrón START (morning/evening star), MEC (2 escenarios + 4 sub-tipos), MER (cambio de estructura + regla de "único nivel m3 opuesto" + "solo primer toque"), concepto **Hedge Position** (cobertura: si aparece señal contraria en operación abierta, se abre y se cierra la primera — esto YA pasa solo con el código actual gracias al netting nativo de `strategy.entry` en Pine, sin pyramiding), SL (último m3 ± reducción 40% si >20.000 pips), **RR 1:0.9 confirmado explícito en la última página**
- **Apariencia del Indicador** — spec visual de las etiquetas BUY/SELL, ejemplos reales de trades

## Sesiones grabadas
- `sesion_vivo_2026-06-11/sesion_log.md` — primera sesión en vivo, muchos bugs corregidos
- `sesion_vivo_2026-06-12/sesion_log.md` — trampa doble post-Michigan, nuestro código 2TP vs Fabian 2SL
- `sesion_vivo_2026-06-16/sesion_log.md` — lag estructural M3, fix umbral martillo, hallazgos de los PDFs de Fabian (RR, Hedge Position, regla de nivel único m3)

## Resultado semanal Fabian (semana 9-13 Jun 2026)
- **+1.35R** al cierre del viernes

## Reglas de sesión en vivo
1. Leer el log de la última sesión antes de empezar
2. Verificar que `use_limite = false`
3. Verificar que hay UNA sola instancia del indicador cargada
4. Rama de trabajo: `claude/trading-strategy-inconsistencies-w9S9b`
5. Guardar capturas y análisis en `sesion_vivo_YYYY-MM-DD/sesion_log.md`
6. Commit + push al final de cada sesión

## Cómo arrancar sesión
El usuario dice: **"hola Jarvis, sesión en vivo"** o **"estamos en vivo"**
→ Leer este archivo + último sesion_log + código actual → responder con estado del sistema listo para operar.
