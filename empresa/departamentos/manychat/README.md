# ManyChat y Captación — Plan del departamento

_Agente: Mini-Jarvis ManyChat · Abierto: 03/10/2026 · Estado: **borrador v0.1** · Sector: Marketing y Publicidad_

## 1. Misión
Ser el departamento que **explica cómo rindió la publicidad desde adentro de las conversaciones**: qué anuncios traen leads que responden, califican, agendan y compran, y dónde se pierden. Es la mitad que le falta a Publicidad: Meta dice cuánto costó el mensaje; ManyChat dice si valió la pena. También audita el bot (flujos, mensajes, remarketing) junto con n8n.

## 2. Cómo trabaja (especialista)
Skill `.claude/skills/manychat/SKILL.md`. Rol: especialista en automatización conversacional y cierre por chat.
- Clasifica cada conversación por **fuente** (anuncio, orgánico, link en bio, remarketing, referido), canal (Instagram/WhatsApp/Messenger) y tratamiento (estética / implantes / otros).
- Ficha por conversación: fuente, hora de entrada, tiempo de 1.ª respuesta, descubrimiento, momento del precio, objeciones, CTA, resultado, error y severidad.
- Catálogo de errores ya detectados: cierre de sí/no, precio temprano, «recargo», promesa de resultado, sin seguimiento, duplicados, nombre «Saira».
- Neuromarketing aplicado al chat: fricción, prueba social, reciprocidad, anclaje, aversión a la pérdida, compromiso/coherencia, urgencia real.
- **Solo lectura**: nada se modifica en ManyChat/n8n sin aprobación expresa. Pacientes anonimizados salvo autorización.

## 3. Informe «Cómo anduvo la publicidad» (objetivo del departamento)
Embudo por **fuente/anuncio**: leads → respondidos → calificados → precio enviado → turno → asistió → cerró.
Gráficos: embudo (barras horizontales), leads por fuente (torta), errores por severidad (barras), tiempo de 1.ª respuesta por franja horaria (línea), leads fuera de horario (torta).
Tabla clave: **anuncio → conversaciones → calificados → turnos** (se une con Publicidad por el ID del anuncio de «click to WhatsApp/Instagram»; a verificar qué campo expone el export de ManyChat).
Cierre: top 5 hallazgos, quick wins de la semana 1 y cambios estructurales.

## 4. Fuentes de datos
| Fuente | Estado | Cómo se conecta |
|---|---|---|
| Export de contactos (CSV: etiquetas, fuente, fechas) | Pendiente | Exportar desde ManyChat a `datos/` |
| Conversaciones (muestra lo más grande posible) | Pendiente | Export o sesión local con Chrome |
| Flujos y campos personalizados | Pendiente | Capturas o export |
| n8n: workflows JSON (sin credenciales) + ejecuciones con error | Pendiente | Export desde n8n |
| ManyChat no figura en el registro de conectores | Bloqueada | Chrome local o export manual |

## 5. KPIs
Leads por fuente · Tiempo de 1.ª respuesta · % calificados · % con turno · % asistencia · % cierre · Leads fuera de horario sin atender · Errores por severidad · Duplicados.

## 6. Hoja de ruta (de `auditoria/PLAN_AUDITORIA.md`)
| Fase | Objetivo | Entregables |
|---|---|---|
| 0 — Acceso y datos | Conseguir exports y definir semana a auditar | Datos en `datos/` |
| 2 — Auditoría ManyChat | Fuentes, embudo, lectura de conversaciones, catálogo de errores | Informe de la semana |
| 3 — Bot en n8n | Inventario de workflows, prompt del agente, fallos | Informe técnico |
| 4 — Agenda de estética punta a punta | 5–10 conversaciones que terminaron en turno | Veredicto y mejoras |
| 5 — Remarketing y leads sin etiqueta | Segmentar y reactivar | Segmentos + mensajes de prueba |
| 6 — Informe final | Hallazgos, quick wins, tablero de KPIs | Informe accionistas |

## 7. Preguntas abiertas
Semana exacta a auditar · dónde vive n8n · plataformas que entran · meta numérica de turnos · si los nombres de pacientes se pueden ver o se anonimizan.
