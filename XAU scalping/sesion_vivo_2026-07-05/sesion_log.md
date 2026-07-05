# Sesión en vivo — 5 julio 2026

## Estado inicial del sistema
- Código: commit 70aba50 (fix línea m3 sólida post-ChOC)
- `use_limite = false` ✅
- `use_news_block = true` ✅
- `use_cooldown = true` ✅
- `show_debug = true` (temporal) ✅
- Rama: `claude/trading-strategy-inconsistencies-w9S9b`

---

## Comparación de capturas: Fabian (OANDA izquierda) vs nuestro código (TradingView derecha)

### Resumen de diferencias
| Momento | Fabian (OANDA) | Nuestro código (TradingView) |
|---|---|---|
| ~09:05 | Sin señal | **MEC ENV SELL** (señal fantasma) |
| ~09:15 | **MER BUY** (entrada real, ChOC alcista) | Sin señal MER |
| ~09:20 | Sin señal nueva | **MEC ENV BUY** (señal tardía, modelo incorrecto) |

### Detalle de cada diferencia

#### 1. MEC ENV SELL a ~09:05 — señal que Fabian NO tomó

Nuestro código disparó `mec_sell` en una vela que completaba un patrón MEC ENV bajista (pullback alcista + vela envolvente bajista que rompe el mínimo del pullback). Fabian no tomó esa señal. Causas posibles:

- **Bloqueo por cooldown:** si hubo un spike al open (~09:00–09:01), Fabian esperaría ~15-20 min — nuestro cooldown hace lo mismo para MEC, pero si la vela fue anterior al último `last_spike_bar`, no lo bloquea.
- **Estructura m3 no confirmada aún:** posible que la estructura bajista estuviera en período de consolidación / niveles m3 recientes.
- **Discrecional de Fabian:** el Plan Operativo menciona contexto de primer pullback del día — Fabian puede omitir señales con estructura muy fresca.

**Impacto:** señal que nuestro código muestra pero Fabian no operó. No es un bug de código (la lógica MEC ENV es correcta), es contexto discretional. A documentar para análisis futuro.

#### 2. MER BUY a ~09:15 — entrada de Fabian que NOSOTROS NO VIMOS

Esta es la discrepancia principal del día.

##### Contexto de estructura
- Estructura previa: BAJISTA (`market_struct = -1`)
- Vela ~09:15: cerró con **cuerpo por encima del último alto m3** con ≥0.01% de quiebre → `choc_bull = true`
- Este bar es el ChOC alcista → Fabian entra por **MER BUY** (primera vela en contacto con el nivel m3)

##### Por qué nuestro código NO disparó MER BUY
`mer_buy` requiere: `can_trade AND can_long AND use_mer AND choc_bull AND entry_bull AND not na(mer_sl_long)`

El `choc_bull` estaba activo. El problema fue `entry_bull = false` — la vela de ese bar no calificaba como envolvente, martillo, ni doji según nuestros umbrales numéricos.

##### Análisis Gann de la vela del ChOC

La **Cuadrícula de Gann** del Plan Técnico es una herramienta visual de TradingView (no teoría de Gann). Se aplica a cada vela para medir las proporciones cuerpo/mecha contra niveles horizontales fijos:

| Tipo de vela | Niveles Gann configurados | Criterio |
|---|---|---|
| Envolvente estándar | 0 / 0.85 / 1 | Cuerpo ≥85%, mecha opuesta pequeña |
| Envolvente martillo | 0 / 0.50 / 0.85 / 1 | Cuerpo 50–85%, mecha a favor <15% |
| Envolvente doji | 0 / 0.15 / 0.85 / 1 | Ambas mechas ≥15%, cuerpo cercano a 15% |
| Indecisión (START) | 0 / 0.25 / 0.50 / 0.75 | Cuerpo ≤50% |

Aplicando Gann a la vela del ChOC (~09:15):
- El cuerpo estaba por debajo del 50% del rango total de la vela
- La mecha inferior (a favor de alcista, el low) era pronunciada
- La mecha superior (opuesta al alcista, el high) también era moderada
- Clasificación visual de Fabian: **vela válida para MER** (posiblemente doji o pequeño martillo)
- Clasificación de nuestro código: `bpct < mart_min (0.50)` Y `bpct < 0.15` → ni doji ni martillo → `entry_bull = false`

##### Hipótesis: umbral doji demasiado restrictivo en el borde bajo

En Plan Técnico (pág. 7-8) la "vela envolvente doji" se describe como cuerpo **cercano al 15%** con **ambas mechas pronunciadas y similares**. Nuestra implementación actual:

```pine
doji_bull = use_doji and close > open and bpct >= 0.15 and bpct < mart_min and lpct >= 0.15 and upct >= 0.15
```

El límite inferior `bpct >= 0.15` podría estar excluyendo velas con `bpct` entre 0.05 y 0.15 que Fabian visualmente sí clasifica como doji (cuerpo pequeño pero no exactamente en 15%). El documento dice "cercano al 15%" — no "exactamente ≥15%".

**Hipótesis alternativa:** la vela tenía `bpct` entre 0.05–0.15, ambas mechas pronunciadas → Fabian la ve como doji válida → nuestro código la rechaza por `bpct < 0.15`.

#### 3. MEC ENV BUY a ~09:20 — señal tardía con modelo incorrecto

Cinco velas después del ChOC, nuestro código disparó `mec_buy` (MEC ENV): hubo un pullback bajista y luego una vela envolvente alcista que superó el máximo del pullback. La señal es técnicamente válida según nuestra lógica MEC, pero:
- Fabian ya había entrado 5 velas antes por MER
- El modelo se etiquetó como "MEC ENV BUY" cuando el movimiento real era la continuación del MER de Fabian

---

## Hallazgos del Plan Técnico (lectura completa 31 páginas, 5-jul-2026)

### Confirmados (ya en código)
- RR 1:0.9 ✅ (confirmado explícito última página)
- Regla "nivel único" MER (pág. 26-27) ✅ — niveles m3 lejanos → SL al más extremo, entra igual
- Cooldown solo en MEC, no en MER ✅ (fix 16-jun confirmado por Plan Técnico)
- Hedge Position ✅ (netting automático de Pine, sin pyramiding)
- MER "solo primera vela" (pág. 24): nuestra implementación es correcta — si el ChOC bar no califica → NO hay MER tardío ✅

### Pendiente de implementar / verificar

#### [PENDIENTE] Umbral doji: revisar borde inferior

**Descripción:** Plan Técnico describe "vela envolvente doji" con cuerpo "cercano al 15%". Nuestro código requiere `bpct >= 0.15`. Una vela con cuerpo 8–14% y ambas mechas pronunciadas podría calificar visualmente para Fabian pero nuestro código la rechaza.

**Propuesta:** bajar umbral a `bpct >= 0.05` (o incluso `bpct >= 0.0` con `upct >= 0.15 and lpct >= 0.15`). Pendiente confirmación en vivo con replay.

#### [PENDIENTE] Regla MER pág. 28: quiebre del último m3 tendencial

El Plan Técnico (pág. 28) dice: "El último m3 traspasado en la estructura tendencial anterior al ChOC debe ser superado con cuerpo ≥0.01%. Si no → el ChOC es válido para cambio de estructura m3 PERO NO válido para tomar entrada MER."

Esta regla **no está implementada**. Actualmente `choc_bull/bear` solo verifica que el cuerpo supere el nivel m3 con ≥0.01%, pero no verifica que ese nivel haya sido el "último traspasado en la estructura tendencial anterior". 

Ejemplo: en una estructura bajista, puede haber varios altos m3 formados durante la bajada. El ChOC ocurre cuando se rompe el último (`last_m3_high`). Pág. 28 requiere además que `last_m3_high` haya sido "traspasado" durante la estructura tendencial bajista previa — es decir, que el precio haya pasado por encima de él antes (formando la bajada), NO que sea un alto m3 nuevo recién formado en el rebote.

**Impacto potencial:** podría explicar señales MER que nuestro código no ve (o dispara de más). Análisis más profundo necesario antes de implementar.

#### [YA IMPLEMENTADO] Línea m3 sólida post-ChOC
Fix de esta sesión: la línea m3 verde ahora permanece SOLID durante `m3_line_len` bars tras el ChOC bajista (y lo mismo para línea roja post-ChOC alcista), en vez de pasarse a punteada inmediatamente cuando `market_struct` cambia.

---

## PDFs de Fabian — actualizados esta sesión

- `docs/Plan_Tecnico.pdf` reemplazado — ahora es la versión **completa de 31 páginas** (9.2MB, subido 5-jul-2026). La versión anterior era solo 1 página (captura de pantalla del viewport macOS Quartz).
- `docs/Plan_Operativo.pdf` — 1 página (pendiente reemplazar con versión completa)
- `docs/Apariencia_Indicador.pdf` — 2 páginas (spec visual confirmada = nuestro código ✅)

---

## Pendientes abiertos

| Prioridad | Ítem |
|---|---|
| ALTA | Verificar en replay con debug table si vela ChOC ~09:15 tiene `bpct < 0.15` — confirmar hipótesis doji |
| ALTA | Estudiar regla MER pág. 28 (último m3 tendencial) — definir si y cómo implementar |
| MEDIA | Quitar tabla debug (`show_debug`) una vez diagnosticado el doji |
| MEDIA | Plan_Operativo.pdf — pedir versión completa a Fabian |
| BAJA | Verificar contador TP/SL día (timing issue con `strategy.netprofit`) |
| BAJA | Validar umbral doji en vivo antes de cambiar el threshold |

---

## Commits de esta sesión
- PDF Plan_Tecnico.pdf completo (31 pág, 9.2MB) guardado en `docs/`
- Log de sesión `sesion_vivo_2026-07-05/sesion_log.md`
