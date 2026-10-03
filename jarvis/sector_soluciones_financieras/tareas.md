# Tareas del sector

Estados: ⏳ Pendiente · 🚧 En curso · ✔️ Hecha · ⛔ Bloqueada

| # | Fecha alta | Tarea | Área | Responsable | Estado | Notas |
|---|---|---|---|---|---|---|
| 1 | 03/10/2026 | Crear Bot Oro (réplica Python de la estrategia XAU MEC/MER) | Trading | Jarvis | ✔️ Hecha | `jarvis/scripts/bot_oro.py` + agente `.claude/agents/bot-oro.md` |
| 2 | 03/10/2026 | Exportar velas M1 de XAUUSD (OANDA) desde TradingView y correr el Bot Oro | Trading | Diego | ⏳ | Yahoo y TradingView bloqueados desde el entorno: hace falta el CSV |
| 3 | 03/10/2026 | Validar el Bot Oro contra el Pine en TradingView (mismas señales, mismo día) | Trading | Jarvis + Diego | ⏳ | Usar una sesión ya grabada (11/06, 12/06, 16/06 o 05/07) |
| 4 | 03/10/2026 | Probar hipótesis doji <15% con `--doji-min 0.05` y comparar con Fabi | Trading | Jarvis | ⏳ | Discrepancia MER del 05/07/2026 ~09:15 |
| 5 | 03/10/2026 | Revisar `max_sl_pts = 200`: el Pine compara precio (USD), el Plan habla de 20.000 pips | Trading | Jarvis | ⏳ | Posible unidad mal traducida |
| 6 | 03/10/2026 | Adaptar estrategia a futuros MGC (horario CME, tick 0,10, $10/pto) | Futuros | Jarvis | ⏳ | Después de validar #3 |
| 7 | 03/10/2026 | Investigar PrimeroTrader a fondo (página completa) | Futuros | Jarvis | ⛔ | Habilitar `primerotrader.com` en la red del entorno |
| 8 | 03/10/2026 | Confirmar Instagram de Edgar Cruz | Futuros | Diego | ⏳ | Pasar el usuario exacto |
| 9 | 03/10/2026 | Traer 1–3 estrategias de Polo AI para backtest | Futuros | Diego | ⏳ | |
| 10 | 03/10/2026 | Unificar perfil de Diego en `main` (hoy está en ramas sueltas) | Sector | Jarvis | ⏳ | Evita que Jarvis vuelva a pedir onboarding |
