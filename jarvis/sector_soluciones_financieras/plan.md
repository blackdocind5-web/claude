# Plan del Sector Soluciones Financieras

_Última actualización: 02/10/2026 — Estado: **borrador v0.1**, en construcción con el usuario._

## 1. Misión

Administrar, controlar y hacer crecer el patrimonio del usuario combinando dos frentes:
la gestión de sus finanzas personales e inversiones de mediano/largo plazo, y la operatoria
de trading de corto plazo a cargo de Fabi. Todo medido, registrado y reportado a la Dirección (Jarvis).

## 2. Qué hacemos

### Área 1 — Finanzas personales e Investigación
- Seguimiento del portfolio de inversión con P&L en tiempo real (`portfolio_tracker.py`).
- Investigación de empresas, sectores y macro (`analyze_company.py`, `deep_research.py`, `fetch_news.py`).
- Briefing diario de mercado (`market_briefing.py`) y scanner de oportunidades (`scan_opportunities.py`).
- Reportes HTML y envío por email (`report_builder.py`, `send_email.py`).
- _A definir:_ presupuesto personal, ingresos/gastos, fondo de emergencia, metas de ahorro.

### Área 2 — Trading (Fabi)
- _A definir con el usuario:_ mercados, instrumentos, estilo (intradía / swing), capital asignado.
- Registro de cada operación (diario de trading).
- Control de reglas de riesgo y métricas de desempeño.

## 3. Qué necesitamos (pendientes de arranque)

| # | Necesidad | Área | Estado |
|---|---|---|---|
| 1 | Completar onboarding del usuario (`jarvis/data/profile.json`): perfil, riesgo, horizonte | Finanzas | ⏳ Pendiente |
| 2 | Cargar posiciones actuales (`active_positions.json`) | Finanzas | ⏳ Pendiente |
| 3 | Definir capital asignado a trading y reglas de riesgo de Fabi | Trading | ⏳ Pendiente |
| 4 | Definir mercados/instrumentos y broker de Fabi | Trading | ⏳ Pendiente |
| 5 | Diario de trading (formato de registro de operaciones) | Trading | ⏳ Pendiente |
| 6 | Definir KPIs del sector y metas mensuales | Ambas | ⏳ Pendiente |
| 7 | Configurar `.env` (email, Alpha Vantage) para reportes y noticias | Ambas | ⏳ Pendiente |
| 8 | Cargar ideas del usuario en `ideas.md` | Ambas | ⏳ Pendiente |

## 4. Ritmo de control

| Control | Cuándo | Contenido mínimo | Plantilla |
|---|---|---|---|
| Diario | Cierre de cada día hábil | Mercado, portfolio, operaciones de Fabi, alertas | `controles/plantilla_diaria.md` |
| Semanal | Viernes / domingo | Rendimiento semanal, cumplimiento de reglas, avances del plan | `controles/plantilla_semanal.md` |
| Mensual | Primer día hábil del mes | Resultados vs. metas, patrimonio, lecciones, ajustes | `controles/plantilla_mensual.md` |

## 5. Hoja de ruta

| Fase | Objetivo | Entregables |
|---|---|---|
| **Fase 0 — Oficina** ✅ | Estructura del sector | Organigrama, plan, plantillas, bitácora, banco de ideas |
| **Fase 1 — Datos base** | Perfil y portfolio cargados; reglas de Fabi definidas | profile.json, active_positions.json, ficha de trading completa |
| **Fase 2 — Operación** | Controles diarios/semanales en marcha | Primeros controles completados, diario de trading activo |
| **Fase 3 — Automatización** | Reportes automáticos | Reporte diario programado + consolidado semanal a Jarvis |
| **Fase 4 — Ideas** | Implementar las ideas aprobadas del usuario | Según `ideas.md` |
