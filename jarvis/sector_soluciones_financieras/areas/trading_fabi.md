# Área 2 — Trading

**Responsable:** Fabi
**Reporta a:** Jefe del sector Soluciones Financieras

## Alcance (a completar con el usuario)
| Campo | Valor |
|---|---|
| Capital asignado | _a definir_ |
| Broker / plataforma | OANDA (gráfico) + TradingView (indicador) |
| Mercados / instrumentos | XAUUSD (oro spot). Próximo paso: futuros MGC (ver Área 3) |
| Estilo | Scalping intradía, M1 (entradas) + M3 (estructura), modelos MEC / MER |
| Horario operativo | Sesión NY 09:01–10:59 (hora de Nueva York) |
| Reglas de la estrategia | RR 1:0,9 · ventanas de noticias USD · cooldown post-spike (ver rama `claude/trading-strategy-inconsistencies-w9S9b`) |

## Reglas de riesgo (propuesta inicial — a validar)
| Regla | Propuesta |
|---|---|
| Riesgo máximo por operación | 1% del capital de trading |
| Pérdida máxima diaria | 3% → se corta la operatoria del día |
| Pérdida máxima mensual (drawdown) | 10% → revisión obligatoria con el sector |
| Stop loss | Obligatorio en toda operación, definido antes de entrar |
| Relación riesgo/beneficio mínima | 1:2 |

## Diario de trading (formato de registro)
| Fecha | Ticker | Dirección | Entrada | Stop | Objetivo | Salida | Tamaño | P&L $ | P&L R | Setup | ¿Respetó reglas? | Nota |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## KPIs
- P&L neto (diario / semanal / mensual)
- Win rate y R promedio (expectativa por operación)
- Profit factor
- Máximo drawdown
- % de operaciones que respetaron las reglas

## 🤖 Bot Oro (desde 03/10/2026)
Réplica en Python de la estrategia XAU Scalping MEC/MER del Pine v5.

| Qué | Dónde |
|---|---|
| Script | `jarvis/scripts/bot_oro.py` |
| Agente | `.claude/agents/bot-oro.md` |
| Reportes | `trading/oro/reportes/AAAA-MM-DD_bot_oro.md` |

Entrega: operaciones, win rate, resultado en R y en USD por contrato (MGC/GC), resultado por modelo,
y **diagnóstico de cada ChOC en sesión sin MER** (la discrepancia abierta con Fabi).

```bash
python jarvis/scripts/bot_oro.py --csv XAUUSD_M1.csv --guardar
python jarvis/scripts/bot_oro.py --csv XAUUSD_M1.csv --doji-min 0.05   # hipótesis doji
```
