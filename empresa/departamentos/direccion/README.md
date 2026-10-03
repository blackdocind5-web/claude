# Dirección — Plan del departamento

_Agente: Jarvis Central · Abierto: 03/10/2026 · Estado: **activo**_

## 1. Misión
Asistente de dirección del CEO: abre cada mañana con el estado de la empresa, **recopila las bitácoras de todos los grupos** y arma el informe completo, prioriza decisiones y vigila que cada departamento cumpla el protocolo.

## 2. Cómo trabaja
Skill `.claude/skills/direccion/SKILL.md`. Al recibir cada mensaje aplica `PROTOCOLO.md` §1 (lista de ideas sueltas). Cada día: `/manana` → `consolidar.py` → briefing (5 cifras, 3 alertas, 3 decisiones).

## 3. Informe consolidado
`python empresa/scripts/consolidar.py` lee estado, tareas, ideas y bitácora de cada oficina y genera el HTML nivel accionistas en `empresa/informes/`.

## 4. Hoja de ruta
| Fase | Objetivo |
|---|---|
| 0 ✅ | Protocolo, consolidador y oficinas de Dirección, Prompts, Publicidad, ManyChat |
| 1 | Oficinas de Ventas, Inteligencia, Creativos |
| 2 | Datos, Compliance, Redes, Finanzas integrada |
| 3 | Rutinas programadas diarias con envío por email |
