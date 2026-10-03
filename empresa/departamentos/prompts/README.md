# Ingeniería de Prompts — Plan del departamento

_Agente: Mini-Jarvis Prompts · Abierto: 03/10/2026 · Estado: **borrador v0.1** · Área: Método y Calidad_

## 1. Misión
Que **todo empiece por un buen prompt**. Cada pedido, consigna a un sub-agente, instrucción de bot (n8n/ManyChat) o brief creativo pasa por este departamento antes de ejecutarse: claro, didáctico, actualizado y con apoyo visual cuando ayuda.

## 2. Cómo trabaja (especialista)
Skill `.claude/skills/prompts/SKILL.md`. Estructura estándar de todo prompt:
1. **Rol** (quién es el especialista) · 2. **Contexto** (empresa, objetivo, datos reales) · 3. **Tarea** (verbo + entregable) · 4. **Reglas y límites** (solo lectura, no inventar cifras, políticas Meta) · 5. **Formato de salida** (informe, tabla, gráficos) · 6. **Ejemplos** · 7. **Criterio de «terminado»**.
- Didáctico: explica el porqué de cada instrucción; usa esquemas y ejemplos buenos/malos.
- Actualizado: revisa el modelo y las prácticas vigentes antes de reescribir un prompt de producción (consulta de documentación oficial).
- Versionado: cada prompt de producción vive en `datos/biblioteca/` con versión, fecha, autor y resultado de pruebas.
- Se prueba con 3–5 casos reales antes de darlo por bueno (incluido un caso límite).

## 3. Entregables
Prompt de departamento · prompt del bot (ManyChat/n8n) · brief creativo · plantilla de consigna a sub-agentes · guía visual «cómo pedirle cosas a Jarvis» (esquema + ejemplos).

## 4. Informe
Estado de la biblioteca de prompts: cantidad por departamento (torta), versión y resultados de pruebas (tabla), mejoras pendientes. Sin métricas de uso reales, el informe muestra cobertura y pendientes.

## 5. Hoja de ruta
| Fase | Objetivo | Entregables |
|---|---|---|
| 0 | Método y plantilla | Skill + plantilla maestra |
| 1 | Prompts de Publicidad y ManyChat | Prompt de informe semanal y de auditoría de conversaciones |
| 2 | Auditoría del prompt del bot en n8n | Informe con mejoras (tras recibir el export) |
| 3 | Biblioteca para todos los departamentos | Un prompt maestro por depto |
