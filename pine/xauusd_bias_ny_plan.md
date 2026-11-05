# XAUUSD · Bias del día + apertura NY · plan de trabajo

Estrategia: `pine/xauusd_bias_apertura_ny.pine` (Pine v6, gráfico de 1 minuto).
Estado: **hipótesis a probar, sin ningún backtest.** El entorno donde se escribió no tiene salida a los servidores de datos (HistData, Dukascopy, Yahoo) y el archivo no se pudo compilar en TradingView (solo se verificó la sintaxis).

## 1. Qué es realista (aritmética, no opinión)

Esperanza por operación: `E = win rate × (RR + 1) − 1`, en R (1R = lo arriesgado).

| RR | Win rate de equilibrio | Win rate para E = +0,2 R | Win rate para E = +0,4 R |
|---|---|---|---|
| 1:1 | 50 % | 60 % | 70 % |
| 1:2 | 33 % | 40 % | 47 % |
| 1:3 | 25 % | 30 % | 35 % |

- «Alto acierto» y «RR asimétrico» **compiten**: con RR 1:2 un 40–47 % ya es un resultado excelente. Un 60 % o más con RR ≥ 1:2 en un sistema simple casi siempre indica un error (mirar el futuro, desfase horario) o sobreajuste. Se prioriza el RR y la poca frecuencia, que es lo que pediste.
- Ejemplo ilustrativo, **no pronóstico**: 100 operaciones al año con E = +0,2 R y riesgo de 0,5 % por operación dan ≈ +10 % anual antes de costos. La vía para crecer no es un acierto altísimo, sino mantener una E positiva, pequeña y estable.
- Costos: el modelo asume 0,04 USD/oz por lado (0,08 ida y vuelta). Con un SL de ~1,5 × ATR(15m) pesan una fracción pequeña de 1 R, pero hay que medirlo con el spread real de tu cuenta.

## 2. Reglas (todo en hora de Nueva York, DST automático)

| Elemento | Regla por defecto |
|---|---|
| Jornada | 18:00 → 18:00 NY (reinicia VWAP y vela diaria) |
| Decisión y entrada | 09:30 NY, a mercado, con datos cerrados hasta las 09:29 |
| Módulo 1 · CRT (vale ×2) | Vela 1 = rango del día anterior (PDH/PDL). Si hoy barrió el PDH (≥ 0,10 × ATR) y el precio volvió a cerrar bajo el PDH → ▼. Si barrió el PDL y volvió sobre el PDL → ▲. Ambos lados o ninguno → neutro |
| Módulo 2 · Tendencia | EMA 50 vs EMA 200 en H1, solo velas cerradas |
| Módulo 3 · VWAP | Precio vs VWAP de la jornada (hlc3 × volumen de ticks) |
| Puntaje | 2×CRT + Tendencia + VWAP. Se opera si `|puntaje| ≥ 2`. Contradicción → se anula → no se opera |
| SL | 1,5 × ATR(14) de 15m (alternativa: más allá del extremo del barrido). Acotado entre 0,75 y 3 × ATR; si el necesario supera 3 × ATR, no se opera |
| TP | 2 × el riesgo (probar 3) |
| Salida por tiempo | 16:00 NY |
| Frecuencia | Máximo 1 operación por día; muchos días sin operar |
| Riesgo | 0,5 % del capital por operación (1 % solo después de validar) |

Por qué estos tres módulos: el CRT aporta un **evento** (barrido de liquidez + recuperación) con una invalidación clara; la tendencia en H1 evita operar contra el flujo; el VWAP indica qué lado controla la jornada. Que dos de tres fuentes distintas coincidan es el filtro que reduce la frecuencia.

## 3. Controles obligatorios (en el mismo script, «Modo de la estrategia»)

Con exactamente las mismas salidas se corren:
1. **Bias** (la estrategia).
2. **Control: siempre compra** a las 09:30 todos los días.
3. **Control: siempre venta**.
4. **Control: bias invertido** (los mismos días, al revés).

El oro tuvo fases de tendencia muy fuertes: «siempre compra» puede verse bien por pura suerte de periodo. Si el bias no supera a los controles y el invertido no pierde, **no hay ventaja del bias**, aunque el resultado total sea positivo.

## 4. Protocolo anti-sobreajuste (se fija antes de ver resultados)

Rejilla declarada de antemano, máximo **8 configuraciones**: puntaje mínimo {2, 3} × RR {2, 3} × modo del SL {ATR, barrido CRT}; resto de parámetros fijos. Se anota cuántas se probaron.

1. **Ajuste:** historia hasta el 31/12/2022. Se elige **una** configuración.
2. **Validación ciega:** 01/01/2023 en adelante, sin tocar ningún parámetro (en TradingView: «Inicio / Fin del backtest» en la copia de la estrategia, o cortando el CSV en Python).
3. **Robustez:** se mueven EMA rápida (30 / 50 / 100), SL (1,0 / 1,5 / 2,0 × ATR) y barrido mínimo (0 / 0,1 / 0,2 × ATR). Se busca una meseta, no un pico.

**Criterios de aceptación** (periodo completo, costos incluidos; todos deben cumplirse):

- Al menos 150 operaciones, 40 de ellas en la validación ciega.
- Esperanza ≥ +0,15 R; estadístico t ≥ 2,5 (≥ 3,0 si se probaron más de 8 configuraciones).
- **Bias supera al mejor control por ≥ 0,15 R** y el bias invertido tiene esperanza < 0.
- En la validación ciega, esperanza > 0 y al menos la mitad de la del ajuste.
- Meseta: esperanza > 0 en al menos el 80 % de las combinaciones vecinas.
- Caída máxima ≤ 10 R; racha máxima de pérdidas ≤ 8.
- Positiva en al menos el 70 % de los años.

Si no pasa, se descarta o se replantea con una hipótesis nueva; **no se retoca hasta que salga bien.**

## 5. Datos: trampas conocidas

- **HistData** ofrece barras M1 de XAUUSD en ASCII (`YYYYMMDD HHMMSS;O;H;L;C;V`). Sus marcas de tiempo van en **EST fijo (UTC−5, sin horario de verano)**, no en hora de Nueva York. Para obtener las 09:30 NY correctas todo el año: sumar 5 h para pasar a UTC y convertir a `America/New_York`. Un error aquí desplaza la entrada una hora la mitad del año y arruina el backtest.
- El volumen de las barras de HistData suele venir en 0 (verifícalo en tu archivo): el VWAP se replica con un proxy ponderado por tiempo, que no es idéntico al de TradingView (volumen de ticks del proveedor). Hay que comprobar que el bias no cambie en demasiados días entre ambos.
- Cada proveedor tiene su propio precio y sus huecos: lo que se prueba en TradingView debe confirmarse con la fuente y los costos de tu broker (Multibank).
- Antes de confiar en el motor de Python, se compara con TradingView en ~20 días concretos: mismas señales, mismas entradas, mismos resultados.

## 6. Rutina de poca pantalla

1. **09:25 NY:** llega la alerta (`alert()` de la estrategia) con bias, puntaje, PDH, PDL y ATR. Si dice «NO OPERAR», terminó tu día.
2. **09:30:** una orden a mercado con SL y TP (o la ejecuta el bot).
3. **16:00:** cierre forzado. Nada más que mirar.
4. Revisión semanal de ~10 minutos. Corte de seguridad sugerido: pausa tras −3 R en la semana y tras −6 R en el mes (para revisar, no para «recuperar»).

## 7. Camino a MT5 (después de aprobar la validación, no antes)

El EA replica el script regla por regla: se ejecuta en cada vela M1 nueva; convierte la hora del servidor a hora de NY (offset del servidor + regla de DST de EE. UU.); calcula PDH/PDL de la jornada 18:00 NY, VWAP por volumen de ticks, EMAs en H1 y ATR en M15; evalúa una sola vez a las 09:30; abre una operación con SL/TP calculados; cierra a las 16:00; guarda un registro con el puntaje de cada día. Se ejecuta primero en demo y se compara contra TradingView antes de pasar a real.

## 8. Qué falta y qué se hace en cada etapa

| Etapa | Qué se necesita | Qué se hace |
|---|---|---|
| 1 | Datos M1 de XAUUSD (CSV de HistData, o red abierta para descargarlos) | Motor de backtest en Python con la regla de arriba, costos y controles; réplica contra TradingView |
| 2 | Resultado de la etapa 1 | Ajuste → validación ciega → robustez, con el protocolo de la sección 4 |
| 3 | Una estrategia que pase | Los agentes en paralelo, cada uno con **una** pregunta acotada sobre los mismos datos: variantes de entrada (rango 5m, retroceso al VWAP), filtro de noticias, filtro de volatilidad, Monte Carlo de caída máxima y riesgo de ruina, simulación de reglas de prop firm. Un cambio solo se adopta si mejora también en la validación ciega |
| 4 | Aprobación de la etapa 2/3 | EA de MT5, demo, y luego real con riesgo reducido |
