# 🏢 Oficina — Sector Soluciones Financieras

> Creada el 02/10/2026. Este directorio es la "oficina" del sector: acá vive el plan, los controles, la bitácora y las ideas. Todo lo que hagamos queda registrado acá.

## Organigrama

```
                    ┌──────────────────────────┐
                    │   DIRECCIÓN — JARVIS     │
                    │  (coordina todos los     │
                    │   sectores, fija metas)  │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │ SECTOR SOLUCIONES        │
                    │ FINANCIERAS (sub-bot)    │
                    │ Jefe de sector: este bot │
                    └──────┬────────────┬──────┘
                           │            │
         ┌─────────────────▼───┐   ┌────▼────────────────────┐
         │ ÁREA 1               │   │ ÁREA 2                  │
         │ Finanzas personales  │   │ Trading                 │
         │ e Investigación      │   │ Responsable: FABI       │
         │ Responsable: sector  │   │                         │
         └──────────────────────┘   └─────────────────────────┘
```

## Cadena de reporte

| Quién | Reporta a | Qué entrega | Frecuencia |
|---|---|---|---|
| Fabi (Trading) | Jefe de sector | Operaciones, P&L, cumplimiento de reglas | Diario / semanal / mensual |
| Área Finanzas personales | Jefe de sector | Portfolio, investigaciones, presupuesto | Diario / semanal / mensual |
| Jefe de sector | Dirección (Jarvis) | Consolidado del sector + alertas | Diario / semanal / mensual |

## Mapa de la oficina

| Archivo / carpeta | Para qué sirve |
|---|---|
| `plan.md` | Misión, qué hacemos, qué necesitamos, hoja de ruta |
| `areas/finanzas_personales.md` | Ficha del Área 1 (alcance, herramientas, KPIs) |
| `areas/trading_fabi.md` | Ficha del Área 2 — Fabi (alcance, reglas, KPIs) |
| `controles/plantilla_*.md` | Plantillas de control diario, semanal y mensual |
| `controles/diarios/` `semanales/` `mensuales/` | Controles completados (uno por fecha) |
| `bitacora.md` | Registro cronológico de todo lo que se hace en el sector |
| `ideas.md` | Banco de ideas del sector (pendientes, en evaluación, aprobadas) |
| `estado.json` | Estado del sector en formato máquina, para que Jarvis lo lea |

## Convenciones

- Controles: `controles/diarios/AAAA-MM-DD.md`, `controles/semanales/AAAA-Wnn.md`, `controles/mensuales/AAAA-MM.md`.
- Fechas en texto: DD/MM/AAAA. Montos: $1.250,50. Porcentajes con signo: +12,3%.
- Toda decisión relevante se anota en `bitacora.md` con fecha.
