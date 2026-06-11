# Sesión en Vivo — XAUUSD — Jueves 11 Jun 2026

**Trader:** Fabian (humano) + análisis Claude
**Instrumento:** Gold Spot / U.S. Dollar (XAUUSD OANDA)
**Indicador Fabian:** XAU VIVO v2
**Indicador nuestro:** XAU_estrategia_Scalping.pine (MEC/MER)
**Sesión NY:** 09:01 - 10:59 EDT (UTC-4)

---

## Screenshots y análisis del día

### 08:48 EDT — Primera captura

**Archivo:** screenshot_0848.png
**Estado del mercado:**
- Estructura M3: ALCISTA
- Sesión NY: aún no abierta (abre a las 09:01)
- Precio: 4,075.735
- Posición Fabian: LONG @ 4,075.315
- Tipo de entrada: E.Martillo (martillo alcista)
- GB High: 4,073.9
- GB Low: 4,057.55
- SL hoy: 4/2 (pendiente confirmar qué significa el formato)
- TP hoy: 3/2

**Observaciones:**
- La última vela (08:48) es bajista — pullback desde el spike de 08:45
- El nivel GB High 4,073.9 actúa como soporte
- Indicador marca "CONTACTO" cuando precio toca nivel m3 (señal MER)
- "E.Martillo" confirma tipo de vela de entrada = martillo

---

### 08:57 EDT — Gráfico M3 (Fabian)

**Archivo:** screenshot_0857_m3.png
**Timeframe:** 3 minutos
**Precio:** 4,079.115

**Estructura visible en M3:**
- Estructura: ALCISTA ✓
- Línea continua (bajo m3 actual): ~4,057-4,058 → nuevo bajo formado, nivel trasladado
- Líneas punteadas (altos m3): ~4,074 y ~4,082-4,085
- Precio consolidando entre 4,077-4,081 tras gran rally desde 4,057

**Lógica de Fabian explicada:**
- MEC BUY: cuando precio supera con cuerpo la línea punteada (alto m3) en m1
- MER SELL: cuando precio rompe la línea continua (bajo m3) → ChOC bajista

**Observaciones:**
- El gran rally de 08:30-08:45 superó varios altos m3 (potenciales MEC BUY en m1)
- El nuevo bajo m3 en 4,057 es el SL natural para cualquier BUY activo
- Actualmente en fase de consolidación post-rally

---

### 09:15 EDT — Gráfico M3 (Fabian) — CAMBIO DE ESTRUCTURA

**Archivo:** screenshot_0915_m3.png
**Timeframe:** 3 minutos
**Precio:** 4,074.745

**Anotación de Fabian dentro de la imagen:**
> "Cambio de estructura a bajista"

---

**Comparación con screenshot anterior (08:57 → 09:15):**

| Dato | 08:57 | 09:15 |
|---|---|---|
| Precio | 4,079.115 | 4,074.745 |
| Estructura m3 | ALCISTA | **BAJISTA** |
| Alto m3 ref SL | ~4,074 / ~4,082-4,085 | ~4,085-4,086 (último formado) |
| Bajo m3 | ~4,057 | movido más arriba (nuevo par) |
| Acción | Consolidando | ChOC bajista confirmado |

---

**¿Qué pasó entre 08:57 y 09:15? — Análisis vela a vela (estimado m3):**

1. **08:57-09:00** — Tras rally hasta ~4,086, precio consolida en zona 4,079-4,081. Se forman altos m3 nuevos en ~4,085-4,086. Se empieza a generar un bajo m3 más alto (durante el pullback post-rally).

2. **09:00-09:03** — Aparece una vela bajista (negra/blanca según convención OANDA). El mercado empieza a devolver el rally. Esta vela forma parte del par bajista-alcista que define un nuevo bajo m3 a nivel más alto que 4,057.

3. **09:03-09:09** — Dos velas blancas (alcistas) de recuperación. En el chart de Fabian se ven dos velas recuperando hacia ~4,077-4,079. Estas velas son el PULLBACK que podría preparar el patrón MEC.

4. **09:09-09:15** — Vela NEGRA grande. Esta vela bajista:
   - Tiene cuerpo amplio (potencial envolvente)
   - Cierra con cuerpo **POR DEBAJO** del bajo m3 más reciente formado durante el pullback
   - Esto es el **ChOC bajista** → `market_struct = -1`
   - Precio cae a 4,074.745

---

**¿Cuál fue exactamente el ChOC?**

La vela bajista grande alrededor de 09:12-09:15 cerró con cuerpo por debajo del bajo m3 que se había formado durante la consolidación post-rally (ese bajo estaba entre ~4,075-4,077, NO en 4,057). 

Esto es clave: el bajo m3 que se rompió NO es el de 4,057 del rally previo. Durante la consolidación post-rally (4,079-4,086), se formó un **nuevo bajo m3 más alto** (par de velas bajista→alcista que fijó mínimo alrededor de 4,075-4,077). La vela de 09:15 rompió ESE nivel más reciente → ChOC bajista.

---

**Niveles clave post-ChOC bajista:**

- **Alto m3 (SL referencia para SELL):** ~4,085-4,086 (último formado durante rally)
- **Precio actual:** 4,074.745
- **Distancia SL estimada:** ~11 puntos → dentro del límite de 200 pts ✓
- **TP estimado (RR 1:0.9):** 4,074.745 - (11 × 0.9) = ~4,064.85

---

**¿Hay setup MEC SELL activo ahora mismo (09:15)?**

Condición necesaria: `market_struct == -1` ✓ (acaba de cambiar)

Para MEC ENV SELL necesitamos:
- `pb_to_bear` = vela anterior alcista (blanca) ✓ (las dos velas de recuperación 09:06-09:12)
- `entry_bear` = vela bajista tipo envolvente/martillo/doji
- `cont_bear_env` = close actual < low de la vela alcista anterior

**POSIBLE:** Si la vela bajista grande de 09:15 cerró por debajo del low de la vela alcista previa → hay un MEC ENV SELL activo en nuestra estrategia.

Sin embargo, esta misma vela también es el **ChOC** → en ese caso también se activaría MER SELL si es la primera vela que toca el nivel m3.

**Para MEC START SELL necesitamos:**
- `pb2_to_bear` = vela [-2] alcista ✓
- `indecion_bear` = vela [-1] bajista con cuerpo ≤ 50% del rango ✓ (la 2da vela de recuperación podría ser indecisión)
- `entry_bear` = vela [0] bajista envolvente ✓
- `cont_bear_start` = close < min(low[-1], low[-2]) ✓

→ Si se cumplen estas condiciones: **MEC START SELL también activo**

---

**Lo que debería marcar nuestro código (XAU Scalp):**

Si el código está correcto debería mostrar una etiqueta **"SELL"** en la vela de las 09:15 porque:
1. `market_struct` acaba de cambiar a -1 en esa vela (ChOC)
2. La secuencia previa tiene pullback alcista + vela envolvente bajista
3. `cont_bear_env` se cumple si close < low del pullback

**Diferencia con XAU VIVO v2 de Fabian:**
- Fabian marcó explícitamente "Cambio de estructura a bajista" con anotación visual
- Nuestro código debería capturar esto automáticamente mediante `choc_bear` y el background color rojo claro
- Fabian busca MEC SELL activamente después de este punto

---

## Aprendizajes del día

1. **El ChOC no siempre rompe el mínimo más lejano:** La estructura cambió al romper el bajo m3 formado DURANTE la consolidación post-rally (~4,075-4,077), no el bajo de 4,057 del inicio del rally. Esto significa que los bajo m3 se actualizan continuamente.

2. **Secuencia MEC SELL típica:** Rally → Consolidación → Pullback (2 velas blancas) → Envolvente bajista que rompe hacia abajo = MEC SELL. Esto coincide exactamente con lo que pasó en 09:15.

3. **ChOC y MEC pueden coincidir:** La misma vela que produce el ChOC bajista puede también ser la entrada MEC SELL si la secuencia previa era pullback-indecisión. Nuestro código los separa en mer_sell y mec_sell pero en la práctica pueden dispararse simultáneamente.

4. **GB High/Low de Fabian vs nuestros alto/bajo m3:** Los niveles "GB High" y "GB Low" en el indicador de Fabian parecen equivaler a nuestros `last_m3_high` y `last_m3_low`. Confirmar con más screenshots.

---

## Diferencias detectadas entre XAU VIVO v2 y nuestro código

1. **Anotaciones visuales:** XAU VIVO v2 muestra texto "Cambio de estructura a bajista" en el gráfico. Nuestro código usa solo un `bgcolor` rojo claro para indicar ChOC.
2. **Niveles GB High/Low:** Fabian muestra los niveles con líneas etiquetadas. Nuestro código usa `plot(last_m3_high)` y `plot(last_m3_low)` como steplines sin etiqueta de precio.
3. **Tipo de entrada:** Fabian muestra "E.Martillo", "E.Envolvente" en la etiqueta. Nuestro código usa "MEC ENV", "MEC START", "MER".

---

## Correcciones pendientes al código

1. **Verificar:** ¿El código dispara SELL correctamente en el ChOC de 09:15? Necesitamos el screenshot de XAU Scalp en ese momento para comparar.
2. **Considerar:** Agregar texto del tipo de vela de entrada a la etiqueta (martillo/envolvente/doji) para igualar la info de Fabian.
3. **Considerar:** Mostrar el precio del nivel m3 en la línea (label al final de la stepline).
