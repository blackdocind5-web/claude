# XAUUSD · Swing trading · plan de trabajo

Estrategia: `pine/xauusd_swing.pine` (Pine v6, gráfico D1). Es una **hipótesis a probar**, no un sistema validado.

## 1. Qué es realista (aritmética, no opinión)

Esperanza por operación = `win rate × (RR + 1) − 1`. Win rate necesario para ganar +0,2 R por operación:

| RR | Win rate de equilibrio | Win rate para +0,2 R |
|---|---|---|
| 1:1 | 50 % | 60 % |
| 1:2 | 33 % | 40 % |
| 1:3 | 25 % | 30 % |

- Con RR ≥ 1:2, un win rate de **35–45 %** ya es un resultado muy bueno. Un 60 % o más con RR 1:2 en un sistema simple casi siempre indica sobreajuste o un error (mirar el futuro).
- «Alto acierto» y «RR asimétrico» compiten: lo normal es elegir uno. Para este objetivo (pocas operaciones, RR ≥ 1:2) se prioriza el RR.

## 2. Reglas (todas se evalúan al cierre de la vela diaria, 17:00 NY)

| Regla | Valor por defecto |
|---|---|
| Tendencia | Compras si EMA50 > EMA200; ventas si EMA50 < EMA200 |
| Setup (Pullback) | En las últimas 5 velas el precio tocó la EMA20 y la vela de señal cierra del lado de la tendencia, a favor |
| Entrada | Orden stop 1 tick más allá del máximo (mínimo) de la vela de señal; vale 3 velas |
| SL | Mínimo (máximo) de las últimas 5 velas ∓ 0,5 × ATR(14). Mínimo 1 × ATR; si supera 3 × ATR no se opera |
| TP | 2 × el riesgo (probar 3) |
| Salida por tiempo | 30 velas |
| Riesgo | 1 % del capital inicial, una sola posición |
| Alternativa (modo 2) | Ruptura Donchian de 55 velas, con la misma tendencia, SL y TP |

## 3. Protocolo anti-sobreajuste (se fija antes de ver resultados)

1. **Ajuste (2005–2018).** Cuatro corridas en TradingView, nada más: Pullback RR 2, Pullback RR 3, Donchian RR 2, Donchian RR 3. Se elige **una**.
2. **Validación ciega (2019 en adelante).** La elegida, sin cambiar ningún parámetro. Se usa «Inicio / Fin del backtest» para separar los tramos.
3. **Robustez.** Se mueven EMA de pullback (15 / 20 / 25) y velas del SL (3 / 5 / 8). Se busca una meseta, no un pico.

**Criterios de aceptación** (todos deben cumplirse con el periodo completo y costos incluidos):

- Al menos 100 operaciones.
- Esperanza ≥ +0,15 R y t ≥ 2,5.
- En la validación, esperanza > 0 y al menos la mitad de la del ajuste.
- En la meseta, esperanza > 0 en al menos el 80 % de las combinaciones vecinas.
- Caída máxima ≤ 12 R, racha máxima de pérdidas ≤ 10.
- Resultado positivo en al menos el 70 % de los años.

## 4. Lo que falta medir que TradingView no modela

- **Swap (financiación nocturna).** En operaciones de semanas puede costar una fracción relevante de 1 R. Mídelo en tu plataforma antes de dar por buenos los resultados.
- **Spread y deslizamiento.** El backtest asume 0,50 USD de ida y vuelta por onza; ajústalo al de tu broker.
- **Diferencias de precio** entre el feed de TradingView y tu broker (sobre todo en los gaps de fin de semana).

## 5. Rutina diaria (poca pantalla) y paso a MT5

- Una alerta al cierre diario te dice si hay orden nueva (entrada, SL, TP, lotes). La colocas una vez; el resto del día no hay nada que hacer.
- Revisión semanal de unos 10 minutos.
- El bot de MT5 usa exactamente las mismas reglas: se ejecuta en cada vela D1 nueva, coloca la orden pendiente con vencimiento, SL y TP, y cierra por tiempo. Se hace **después** de aprobar la validación, no antes.
