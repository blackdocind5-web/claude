---
name: informe-profesional
description: Genera el informe de un departamento a nivel accionistas (portada, KPIs, resumen ejecutivo, tortas, barras, líneas, tablas, decisiones, datos que faltan). Usar para cualquier informe, auditoría o reporte de departamento, aunque haya una sola conversación como fuente.
---

# Informe profesional

1. Reuní los datos **reales** (bitácora del depto, `estado.json`, tareas, ideas, exports en `datos/`). No inventes cifras.
2. Escribí un spec JSON (formato en `empresa/scripts/ejemplo_spec.json`) y generá el HTML:
   `python empresa/scripts/informe.py <spec.json> --salida empresa/departamentos/<id>/informes/AAAA-MM-DD_<id>.html`
3. Estructura obligatoria: portada · 3–5 KPIs · resumen ejecutivo (≤5 líneas) · secciones con gráficos y tablas · decisiones del CEO · próximos pasos (responsable + prioridad) · **datos que faltan** · fuentes con fecha.
4. Gráficos: `torta` (partes de un total, ≤6 porciones), `barras` / `barras_h` (comparar magnitudes o rankear), `linea` (evolución en el tiempo). Un mensaje por gráfico, título que diga la conclusión, fuente al pie. Sin doble eje.
5. Aunque haya una sola conversación: graficá lo que sí es real (avance del plan, fuentes conectadas vs pendientes, tareas por estado, ideas, distribución de errores hallados).
6. Abrí el HTML en el navegador y revisalo (textos cortados, etiquetas pisadas). Mencioná la ruta al usuario.
7. Idioma: español neutro, fechas DD/MM/YYYY, números 1.250,50.
