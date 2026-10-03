#!/usr/bin/env python3
"""Dirección (Jarvis Central): consolida las bitácoras y el estado de todos los departamentos.

Lee, por departamento:  estado.json · tareas.md · ideas.md · bitacora.md
Genera un spec y el informe HTML consolidado (nivel accionistas) en empresa/informes/.

Uso:
    python empresa/scripts/consolidar.py                 # informe de hoy
    python empresa/scripts/consolidar.py --fecha 03/10/2026
Solo usa datos reales de los archivos: si algo falta, lo reporta como pendiente.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import informe  # noqa: E402

ESTADOS_TAREA = {"⏳": "Pendiente", "🚧": "En curso", "✔️": "Hecha", "⛔": "Bloqueada"}
ESTADOS_IDEA = {"💡": "Nueva", "🔍": "En evaluación", "✅": "Aprobada", "🚧": "En implementación", "✔️": "Hecha", "❌": "Descartada"}
ETIQ_DEPTO = {"activo": "Activo", "por_conectar": "Por conectar", "planificado": "Planificado", "en_construccion": "En construcción"}


def deptos():
    """(id, carpeta) de cada departamento con oficina abierta."""
    res = []
    base = RAIZ / "empresa" / "departamentos"
    for d in sorted(base.iterdir()) if base.exists() else []:
        if d.is_dir() and (d / "estado.json").exists():
            res.append((d.name, d))
    fin = RAIZ / "jarvis" / "sector_soluciones_financieras"
    if fin.exists():
        res.append(("finanzas", fin))
    return res


def contar(archivo, mapa):
    cuenta = {v: 0 for v in mapa.values()}
    if not archivo.exists():
        return cuenta
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        if not linea.startswith("|") or linea.startswith("|---") or linea.startswith("| #"):
            continue
        for emoji, nombre in mapa.items():
            if emoji in linea:
                cuenta[nombre] += 1
                break
    return cuenta


def ultima_entrada(bitacora):
    """Último encabezado de fecha de la bitácora (DD/MM/YYYY) y su primer texto."""
    if not bitacora.exists():
        return None, None
    fecha, texto = None, None
    for linea in bitacora.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{2}/\d{2}/\d{4})\s*\|(.*)", linea)  # bitácora en formato tabla (más reciente arriba)
        if m:
            cols = [x.strip() for x in m.group(2).split("|") if x.strip()]
            return m.group(1), (cols[1] if len(cols) > 1 else None)
        m = re.match(r"^#{2,3}\s+.*?(\d{2}/\d{2}/\d{4})", linea)
        if m:
            fecha, texto = m.group(1), None
        elif fecha and texto is None and linea.strip().startswith(("-", "*")):
            texto = linea.strip("-* ").strip()
    return fecha, texto


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fecha", default=datetime.now().strftime("%d/%m/%Y"))
    a = ap.parse_args()

    filas, estados, tareas_dep, tareas_tot, ideas_tot, fuentes_tot = [], {}, [], {}, {}, {"Conectada": 0, "Pendiente": 0, "Bloqueada": 0}
    sin_bitacora, pendientes = [], []
    for did, carpeta in deptos():
        est = json.loads((carpeta / "estado.json").read_text(encoding="utf-8"))
        nombre = est.get("nombre") or est.get("sector") or did
        estado = est.get("estado_depto") or est.get("estado") or "en_construccion"
        if estado not in ETIQ_DEPTO:  # el sector financiero guarda texto libre en áreas
            estado = "activo" if did == "finanzas" else "en_construccion"
        estados[ETIQ_DEPTO[estado]] = estados.get(ETIQ_DEPTO[estado], 0) + 1
        t = contar(carpeta / "tareas.md", ESTADOS_TAREA)
        i = contar(carpeta / "ideas.md", ESTADOS_IDEA)
        for k, v in t.items():
            tareas_tot[k] = tareas_tot.get(k, 0) + v
        for k, v in i.items():
            ideas_tot[k] = ideas_tot.get(k, 0) + v
        abiertas = t["Pendiente"] + t["En curso"] + t["Bloqueada"]
        tareas_dep.append({"etiqueta": nombre, "valor": abiertas})
        for f in est.get("fuentes", []):
            s = {"conectada": "Conectada", "bloqueada": "Bloqueada"}.get(f.get("estado"), "Pendiente")
            fuentes_tot[s] += 1
            if s != "Conectada":
                pendientes.append(f'{nombre}: conectar «{f.get("nombre")}» ({s.lower()})')
        fecha_b, ult = ultima_entrada(carpeta / "bitacora.md")
        if not fecha_b:
            sin_bitacora.append(nombre)
        filas.append([nombre, est.get("agente", est.get("reporta_a", "—")), ETIQ_DEPTO[estado],
                      str(est["fase"] if "fase" in est else est.get("fase_actual", "—"))[:22], f"{abiertas}", f"{sum(i.values())}", fecha_b or "sin registro",
                      (ult[:90] + "…" if ult and len(ult) > 90 else ult) or "—"])

    n = len(filas)
    spec = {
        "titulo": "Informe consolidado de Dirección",
        "subtitulo": "Estado de todos los departamentos a partir de sus bitácoras, tareas e ideas",
        "departamento": "Dirección — Jarvis Central",
        "fecha": a.fecha,
        "autor": "Jarvis Central",
        "kpis": [
            {"label": "Departamentos con oficina abierta", "valor": str(n)},
            {"label": "Tareas abiertas", "valor": str(tareas_tot.get("Pendiente", 0) + tareas_tot.get("En curso", 0) + tareas_tot.get("Bloqueada", 0)),
             "detalle": f'{tareas_tot.get("Bloqueada", 0)} bloqueadas'},
            {"label": "Ideas en el banco", "valor": str(sum(ideas_tot.values())), "detalle": f'{ideas_tot.get("Nueva", 0)} nuevas'},
            {"label": "Fuentes de datos conectadas", "valor": f'{fuentes_tot["Conectada"]} de {sum(fuentes_tot.values())}'},
        ],
        "resumen_ejecutivo": [
            f"Hay {n} departamentos con oficina abierta. {sin_bitacora and 'Sin bitácora al día: ' + ', '.join(sin_bitacora) + '.' or 'Todos tienen bitácora.'}",
            f"Fuentes de datos: {fuentes_tot['Conectada']} conectadas, {fuentes_tot['Pendiente']} pendientes, {fuentes_tot['Bloqueada']} bloqueadas. "
            "Hasta conectarlas, los informes de rendimiento reportan el dato como pendiente en vez de estimarlo.",
        ],
        "secciones": [
            {"titulo": "Estado de los departamentos",
             "graficos": [
                 {"tipo": "torta", "titulo": "Departamentos por estado", "unidad": " deptos.",
                  "datos": [{"etiqueta": k, "valor": v} for k, v in estados.items()]},
                 {"tipo": "barras_h", "titulo": "Tareas abiertas por departamento",
                  "datos": tareas_dep, "fuente": "tareas.md de cada departamento"},
             ],
             "tabla": {"columnas": ["Departamento", "Agente", "Estado", "Fase", "Tareas abiertas", "Ideas", "Última bitácora", "Último registro"],
                       "filas": filas}},
            {"titulo": "Trabajo y creatividad",
             "graficos": [
                 {"tipo": "torta", "titulo": "Tareas por estado", "datos": [{"etiqueta": k, "valor": v} for k, v in tareas_tot.items() if v]},
                 {"tipo": "torta", "titulo": "Banco de ideas por estado", "datos": [{"etiqueta": k, "valor": v} for k, v in ideas_tot.items() if v]},
             ]},
            {"titulo": "Conexión de datos",
             "graficos": [{"tipo": "torta", "titulo": "Fuentes de datos", "datos": [{"etiqueta": k, "valor": v} for k, v in fuentes_tot.items() if v]}]},
        ],
        "pendientes_datos": pendientes or ["Sin pendientes de conexión registrados."],
        "proximos_pasos": ["Revisar los departamentos en estado «Por conectar» y elegir la vía de acceso a sus datos.",
                           "Completar la bitácora de los departamentos sin registro."],
        "fuentes": ["empresa/departamentos/*/estado.json, tareas.md, ideas.md, bitacora.md", "jarvis/sector_soluciones_financieras/*"],
    }
    dest = RAIZ / "empresa" / "informes"
    dest.mkdir(parents=True, exist_ok=True)
    iso = datetime.strptime(a.fecha, "%d/%m/%Y").strftime("%Y-%m-%d")
    (dest / f"{iso}_direccion_consolidado.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    out = dest / f"{iso}_direccion_consolidado.html"
    out.write_text(informe.construir(spec), encoding="utf-8")
    print(f"Informe consolidado: {out}")


if __name__ == "__main__":
    main()
