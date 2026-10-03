---
description: Arranque del día de la empresa: estructura, pendientes e informes por departamento
---

Empezá el día de la empresa, en español:

0. Aplicá `empresa/PROTOCOLO.md` (lista de ideas sueltas de lo que escriba el CEO).
1. Leé `empresa/PROTOCOLO.md`, `empresa/organigrama.json` y `empresa/bitacora.md`.
2. Mostrá el organigrama resumido con el estado de cada departamento (activo, por conectar, planificado).
3. Listá los pendientes abiertos de la bitácora.
4. Por cada departamento activo o con datos disponibles en `empresa/datos/`, pedile a su agente (carpeta `.claude/agents/`) el informe del día y guardalo en `empresa/informes/`.
5. Ejecutá `python empresa/scripts/consolidar.py` (Dirección recopila las bitácoras) y abrí el informe.
6. Cerrá con un briefing de Dirección: 5 cifras clave, 3 alertas y 3 decisiones pendientes.
7. Agregá una entrada con la fecha de hoy a `empresa/bitacora.md`.
