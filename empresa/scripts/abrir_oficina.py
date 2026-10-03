#!/usr/bin/env python3
"""Abre la oficina de un departamento: crea su carpeta con la estructura estándar.

Uso:
    python empresa/scripts/abrir_oficina.py <id> "<Nombre>" "<Agente>" [--fase N]

Crea en empresa/departamentos/<id>/:
    README.md (plan) · estado.json · bitacora.md · ideas.md · tareas.md · informes/ · datos/
Nunca pisa archivos existentes.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

PLAN = """# {nombre} — Plan del departamento

_Agente: {agente} · Abierto: {hoy} · Estado: **borrador v0.1**_

## 1. Misión
(Qué hace este departamento y para qué existe en la empresa.)

## 2. Cómo trabaja (especialista)
(Skill: `.claude/skills/{id}/SKILL.md` · Agente: `.claude/agents/{id}.md`.
Metodología, criterios de calidad, qué entrega y cada cuánto.)

## 3. Fuentes de datos
| Fuente | Estado | Cómo se conecta |
|---|---|---|

## 4. KPIs

## 5. Informe del departamento
Estructura según `empresa/PROTOCOLO.md` §4 (nivel accionistas, con gráficos).

## 6. Hoja de ruta
| Fase | Objetivo | Entregables |
|---|---|---|

## 7. Preguntas abiertas
"""

TAREAS = """# Tareas — {nombre}

Estados: ⏳ Pendiente · 🚧 En curso · ✔️ Hecha · ⛔ Bloqueada

| # | Fecha alta | Tarea | Responsable | Estado | Notas |
|---|---|---|---|---|---|
"""

IDEAS = """# Banco de ideas — {nombre}

Estados: 💡 Nueva · 🔍 En evaluación · ✅ Aprobada · 🚧 En implementación · ✔️ Hecha · ❌ Descartada

| # | Fecha | Idea | Propuesta por | Estado | Notas |
|---|---|---|---|---|---|
"""

BITACORA = """# Bitácora — {nombre}

Dirección consolida este archivo en el informe consolidado. Una entrada por fecha (DD/MM/YYYY).

## {hoy}
- Oficina abierta.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id")
    ap.add_argument("nombre")
    ap.add_argument("agente")
    ap.add_argument("--fase", type=int, default=1)
    a = ap.parse_args()
    hoy = datetime.now().strftime("%d/%m/%Y")
    base = RAIZ / "empresa" / "departamentos" / a.id
    (base / "informes").mkdir(parents=True, exist_ok=True)
    (base / "datos").mkdir(exist_ok=True)
    ctx = dict(id=a.id, nombre=a.nombre, agente=a.agente, hoy=hoy)
    estado = {"id": a.id, "nombre": a.nombre, "agente": a.agente, "estado": "en_construccion",
              "fase": a.fase, "actualizado": hoy, "fuentes": [], "kpis": []}
    archivos = {"README.md": PLAN.format(**ctx), "tareas.md": TAREAS.format(**ctx), "ideas.md": IDEAS.format(**ctx),
                "bitacora.md": BITACORA.format(**ctx),
                "estado.json": json.dumps(estado, ensure_ascii=False, indent=2) + "\n"}
    for nombre, contenido in archivos.items():
        p = base / nombre
        if p.exists():
            print(f"= ya existe, no se toca: {p.relative_to(RAIZ)}")
        else:
            p.write_text(contenido, encoding="utf-8")
            print(f"+ {p.relative_to(RAIZ)}")
    for sub in ("informes", "datos"):
        k = base / sub / ".gitkeep"
        if not k.exists():
            k.touch()


if __name__ == "__main__":
    main()
