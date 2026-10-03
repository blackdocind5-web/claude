# Laboratorio de Estrategias — Guía de trabajo

Departamento de investigación de estrategias de trading. Objetivo: **formular, guardar, backtestear y medir
estrategias de forma ordenada**, y quedarnos solo con las que sobreviven a pruebas serias antes de arriesgar plata.

> Regla de oro: una estrategia no es buena porque ganó en el backtest. Es buena si **sigue ganando cuando intentamos
> romperla**: con costos reales, en otros períodos, en otros activos y con parámetros movidos.

---

## 1. Qué hay en la carpeta

| Archivo / carpeta | Para qué sirve |
|---|---|
| `CATALOGO.md` | Lista de todas las estrategias y su etapa actual. **Única fuente de verdad del estado.** |
| `fichas/` | Una ficha por estrategia: hipótesis, reglas, cuándo debería fallar y aprendizajes. `_PLANTILLA.md` para las nuevas. |
| `estrategias/` | Código Pine v5 listo para pegar en TradingView (uno por estrategia). |
| `_generar_pines.py` | Genera los `.pine` con el mismo bloque de riesgo y costos. Para sumar una estrategia se agrega ahí. |
| `datos_tv/` | CSV exportados del Strategy Tester (lista de operaciones). |
| `resultados.csv` | Registro de cada backtest: una fila por corrida. |
| `ranking.py` | Ordena `resultados.csv` y marca las corridas poco confiables. |
| `metricas_trades.py` | Mide una estrategia a fondo desde el CSV exportado (esperanza en R, rachas, Monte Carlo, por hora y día). |
| `bitacora/` | Diario de sesiones de trabajo (`_PLANTILLA.md`). |

---

## 2. El embudo: de la idea al dinero real

Cada estrategia avanza de etapa **solo si cumple el criterio de pase**. Se anota en `CATALOGO.md`.

| Etapa | Qué se hace | Criterio para pasar |
|---|---|---|
| **0 Idea** | Se escribe en una línea y se asigna ID. | Tiene una hipótesis que se pueda explicar con palabras. |
| **1 Ficha** | Se completa la ficha (reglas exactas, cuándo debería fallar). | Reglas sin ambigüedad: dos personas codificarían lo mismo. |
| **2 Codificada** | Se escribe el `.pine` y se verifica que compile y que las operaciones del gráfico coincidan con las reglas. | Revisión visual de al menos 20 operaciones: entran y salen donde la ficha dice. |
| **3 Backtest** | Corrida base **con costos** (ver sección 3). | ≥ 100 operaciones, factor de ganancias ≥ 1,3, esperanza > 0,15 R, drawdown ≤ 20%. |
| **4 Robustez** | Intentamos romperla (ver sección 4). | Sigue siendo rentable en la mayoría de las pruebas. |
| **5 Paper trading** | Cuenta demo o alertas, sin dinero. Mínimo 4 semanas y 30 operaciones. | Resultados en vivo dentro de lo esperado por el backtest (no peor que el peor 5% del Monte Carlo). |
| **6 Real** | Riesgo mínimo (0,25%–0,5% por operación) las primeras 50 operaciones. | Se sube el riesgo solo si el real se parece al paper. |
| **Descartada** | Se archiva con el motivo en la ficha. | — (descartar también es resultado: evita repetir errores) |

---

## 3. Protocolo de backtest en TradingView (corrida base)

1. Abrir el activo y timeframe de la ficha. Por defecto empezamos con **XAUUSD en M15**, porque es el activo de Fabi y nos
   permite comparar contra su estrategia.
2. Pine Editor → pegar el contenido de `estrategias/NN_nombre.pine` → Add to chart.
3. Propiedades de la estrategia: capital 10.000, **comisión 0,01% y slippage 2 ticks (no dejarlos en 0)**. Ajustar a los costos reales del broker
   cuando los sepamos.
4. Fijar el **mismo período** para todas las estrategias que se comparen (anotarlo). Sugerido: 26/01/2026 a hoy, el mismo que usó Fabi.
5. Strategy Tester → anotar neto, operaciones, % de acierto, factor de ganancias, drawdown máximo.
6. Exportar la lista de operaciones (Export data) y guardarla en `datos_tv/` con el nombre
   `NN_nombre_ACTIVO_TF.csv`, por ejemplo `01_cruce_ema_XAUUSD_M15.csv`.
7. Medir a fondo:
   `python jarvis/laboratorio/metricas_trades.py jarvis/laboratorio/datos_tv/01_cruce_ema_XAUUSD_M15.csv --capital 10000 --riesgo-pct 1`
8. Agregar la fila a `resultados.csv` y ver el ranking: `python jarvis/laboratorio/ranking.py`
9. Actualizar `CATALOGO.md` y escribir el aprendizaje en la ficha (o en la bitácora del día).

---

## 4. Pruebas de robustez (etapa 4)

Una estrategia que pasa la etapa 3 todavía puede ser pura suerte. Se prueba, en este orden:

1. **Otro período**: dividir el historial en dos mitades; debe ser rentable en las dos, no solo en una.
2. **Otro activo parecido**: la misma lógica en otro instrumento (si anda en oro, ¿anda en EURUSD o Nasdaq?). Si solo anda en uno, hay que entender por qué.
3. **Otro timeframe cercano**: M15 → M5 y H1. Si desaparece, estaba ajustada a un tamaño de vela.
4. **Parámetros movidos ±20%**: EMA 21 → 17 y 25, ATR ×1,5 → 1,2 y 1,8. Si un cambio chico la rompe, es frágil. Buscamos una **meseta** de buenos resultados, no un pico aislado.
5. **Costos peores**: el doble de comisión y slippage. Si deja de ser rentable, no tiene margen.
6. **Monte Carlo** (`metricas_trades.py`): ¿qué drawdown podemos sufrir con las mismas operaciones en otro orden?
7. **Concentración**: sacar las 5 mejores operaciones. Si el resultado desaparece, dependía de golpes de suerte.

---

## 5. Qué medimos (como traders)

| Métrica | Por qué importa | Referencia |
|---|---|---|
| **Esperanza en R** | Cuánto gana en promedio cada operación en múltiplos de lo arriesgado. Es *la* métrica. | > 0,15 R después de costos |
| **Factor de ganancias** | Ganancias brutas / pérdidas brutas. | 1,3–2,5 (arriba de 3 es sospechoso) |
| **Payoff vs. acierto** | Se compara el acierto real con el acierto de equilibrio que exige el payoff. | Acierto real > equilibrio |
| **Drawdown máximo** | Lo que hay que aguantar sin abandonar. | ≤ 20% |
| **Racha perdedora máxima** | Define si podemos sostener psicológicamente el sistema. | Poder tolerar 2× la histórica |
| **Factor de recuperación** | Ganancia neta / drawdown. | > 2 |
| **Monte Carlo** | Drawdown "malo pero plausible" y riesgo de perder la mitad del capital. | Prob. de perder 50% < 5% |
| **Costos como % del R** | Cuánta ganancia se come la comisión y el slippage (crítico en scalping). | < 20% del R promedio |
| **Por sesión / hora / día** | Dónde está el borde. | **Solo informativo** con ≥ 30 operaciones por casilla |
| **Operaciones por mes** | Define cuánto tarda en validarse y cuánto se opera. | — |

**Ojo con cortar los datos en rebanadas.** Dividir el historial por hora y día de la semana produce casilleros con 3 o 5 operaciones,
y casi siempre alguno se ve espectacular por pura casualidad. Un filtro horario solo se adopta si hay una razón de mercado que lo explique
(por ejemplo, la apertura de Nueva York) y se confirma en datos que no se usaron para encontrarlo.

---

## 6. Errores que invalidan un backtest

- **Sin costos o con costos irreales**: es el error más común. Scalping sin slippage es ficción.
- **Muestra chica**: menos de 100 operaciones no prueba nada.
- **Sobreajuste**: mover parámetros hasta que la curva se vea linda. Cada combinación probada cuenta como un intento. **Llevamos registro de cuántas pruebas hicimos.**
- **Mirar el futuro (look-ahead)**: `request.security()` mal usado, usar el cierre de la vela para entrar en esa misma vela.
- **Repintado**: indicadores que cambian su señal después de cerrada la vela.
- **Elegir el período a dedo**: usar siempre el mismo período para comparar.
- **Ejecuciones imposibles**: stop y objetivo tocados en la misma vela (el orden real se desconoce; TradingView asume el peor caso solo con Bar Magnifier, que requiere plan pago).
- **Ignorar el régimen**: una estrategia de tendencia probada en un año de tendencia no demuestra nada sobre un año lateral.
- **Mezclar el resultado de la estrategia con el del activo**: comparar contra comprar y mantener.

---

## 7. Cómo trabajamos juntos en TradingView

Desde esta sesión de nube **no puedo ver ni controlar TradingView en vivo** (el entorno bloquea el sitio y no hay un navegador conectado).
La dinámica es la siguiente:

1. Yo dejo el `.pine` listo y la ficha con lo que hay que mirar.
2. Vos lo pegás en TradingView, corrés la prueba y me pasás **capturas** del gráfico y del Strategy Tester, y el **CSV exportado**.
   (Las sesiones de escritorio de Claude pueden leer capturas, como en la sesión de Fabi.)
3. Yo corro `metricas_trades.py`, interpreto como trader, anoto en la bitácora y propongo el siguiente experimento.
4. Si quieren verlo en vivo: abrir la sesión desde la **app de escritorio** con Claude in Chrome o el navegador integrado.

Cuando miremos operaciones en el gráfico, buscamos tres cosas: entradas tardías, stops demasiado justos
(el precio los toca y luego va a favor) y señales que aparecen en horarios donde la estrategia no debería operar.

---

## 8. Hoja de ruta

**Sprint 0 — Primeras mediciones (esta semana)**
- Correr las 8 estrategias del paquete en XAUUSD M15, mismo período, con costos.
- Cargar resultados y mirar el ranking. Esperamos que la mayoría no pase la etapa 3: es normal.

**Sprint 1 — Robustez de las 2 o 3 mejores**
- Pruebas de la sección 4 y descarte de las que no resisten.

**Sprint 2 — Estrategia de Fabi con costos**
- Volver a correr la estrategia de Fabi con comisión y slippage reales y compararla con las del paquete en igualdad de condiciones.
- Pendiente aparte: su backtest M3 hoy no muestra operaciones (ver la sesión de Fabi).

**Sprint 3 — Más activos y más ideas**
- Probar las finalistas en EURUSD, Nasdaq y BTC. Sumar estrategias nuevas (squeeze de volatilidad, VWAP, ruptura de rango asiático, estrategias de scripts públicos de TradingView).

**Cómo sumar una estrategia nueva**
1. Copiar `fichas/_PLANTILLA.md` y completarla.
2. Agregarla a `ESTRATEGIAS` y `META` en `_generar_pines.py` y correr `python jarvis/laboratorio/_generar_pines.py` (no pisa fichas existentes).
3. Agregar la fila a `CATALOGO.md`.

---

## 9. Reglas del laboratorio

1. Toda idea queda guardada, funcione o no. Las descartadas se archivan con el motivo.
2. Nada pasa de etapa sin cumplir el criterio, aunque "se vea bien".
3. Siempre con costos. Siempre el mismo período al comparar.
4. Se anota cada prueba: lo que no se registra no existió.
5. Antes de modificar una estrategia que ya falló, se escribe la razón de mercado del cambio. Cambios sin razón son sobreajuste.
6. Esto es investigación, no asesoramiento financiero. Ninguna estrategia pasa a dinero real sin paper trading previo.
