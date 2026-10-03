---
description: Abre la oficina de un departamento (carpeta, plan, skill, agente) y arma su plan con el CEO
---

Abrí la oficina del departamento indicado en $ARGUMENTS:

1. Aplicá `empresa/PROTOCOLO.md` §1: listá las ideas sueltas del pedido.
2. Ejecutá `python empresa/scripts/abrir_oficina.py <id> "<Nombre>" "<Agente>"`.
3. Escribí el plan (`README.md`), la skill `.claude/skills/<id>/SKILL.md` y el agente `.claude/agents/<id>.md` con el método de un especialista de ese sector.
4. Agregalo a `empresa/organigrama.json` y regenerá el HTML con `python empresa/scripts/actualizar_organigrama.py`.
5. Anotá en `empresa/bitacora.md` y mostrá al CEO el plan con las preguntas abiertas.
