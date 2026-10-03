# Plan de auditoría integral — ManyChat + n8n + Marketing + Ventas

Estado: PLAN (sin datos aún). Duración estimada: 2+ semanas, por fases.
Regla: nada se modifica en ManyChat/n8n/Meta sin aprobación expresa. Solo lectura hasta la Fase 6.

## Fase 0 — Acceso y datos (bloqueante)
- [ ] Definir vía de acceso: Claude in Chrome / app de escritorio (local) o export de datos.
- [ ] Export de ManyChat: contactos (CSV con etiquetas, fuente, fechas), conversaciones, flujos, campos personalizados.
- [ ] Export de n8n: workflows en JSON (sin credenciales) + historial de ejecuciones con errores.
- [ ] Organigrama actual (aunque sea informal).
- [ ] Acordar rango de fechas de la semana a auditar.

## Fase 1 — Organigrama y sectores
- [ ] Mapa de sectores: Marketing/Pauta, Captación (bot), Closers/Recepción, Agenda, Clínica (estética/implantes), Posventa, Administración/Cobranza, Legal/Publicidad médica.
- [ ] Por sector: responsable, objetivo, KPI, herramienta, qué recibe y qué entrega al siguiente sector.
- [ ] Puntos de traspaso (bot → humano, humano → agenda, agenda → clínica) y dónde se pierden leads.
- [ ] Definir cómo "activar" cada sector: checklist, SLA y reporte semanal.

## Fase 2 — Auditoría de ManyChat (la más larga)
2.1 Fuentes de los mensajes: anuncio (Meta Ads), orgánico, Instagram/Facebook/WhatsApp, link en bio, campaña de remarketing, referido. Tabla fuente → volumen → calificación → turnos → ventas.
2.2 Volumen y embudo de la semana: leads, respondidos, calificados, con precio enviado, con turno, asistieron, cerraron.
2.3 Lectura de conversaciones (muestra lo más grande posible, todas si el export lo permite), clasificadas por tratamiento: estética, implantes, otros.
2.4 Ficha por conversación: fuente, hora de entrada, tiempo de 1.ª respuesta, descubrimiento, momento del precio, objeciones, CTA, resultado, error detectado, severidad.
2.5 Catálogo de errores (ya detectados: cierre de sí/no, precio temprano, "recargo", promesa de resultado, sin seguimiento, duplicados, nombre "Saira") + los nuevos.
2.6 Horarios: leads fuera de horario y cómo se atienden.

## Fase 3 — Auditoría del bot en n8n
- [ ] Inventario de workflows, triggers, nodos, credenciales (solo nombres), dependencias.
- [ ] Prompt/instrucciones del agente: identidad, tono, reglas de precio, reglas médicas, escalamiento a humano.
- [ ] Memoria/contexto, manejo de "después te escribo", duplicados, reintentos, timeouts.
- [ ] Ejecuciones fallidas, latencia, mensajes duplicados (causa raíz).
- [ ] Integración de agenda (disponibilidad, confirmación, recordatorios, cancelaciones).
- [ ] Riesgos: datos personales, publicidad médica, alucinaciones de precios/promociones.

## Fase 4 — Caso especial: agenda de estética de punta a punta
- [ ] Transcripción completa de 5–10 conversaciones que terminaron en turno.
- [ ] Evaluar: saludo, descubrimiento, valor antes de precio, elección de horario, confirmación, recordatorio, datos pedidos, tiempo total.
- [ ] Neuromarketing: fricción/carga cognitiva, prueba social, reciprocidad, anclaje, aversión a la pérdida (encuadre de pago), compromiso y coherencia, urgencia real.
- [ ] Gustos y motivaciones de la población objetivo (edad, zona, tratamientos más pedidos, lenguaje que usan).
- [ ] Veredicto: ¿fue perfecta? Mejoras priorizadas.

## Fase 5 — Remarketing y leads sin etiqueta
- [ ] Segmentar los lotes de primeros leads sin etiqueta: cantidad, antigüedad, última interacción, fuente.
- [ ] Revisar la campaña actual: mensaje, horario, frecuencia, respuesta, bajas, riesgo de ventana de 24 h / políticas de Meta y WhatsApp.
- [ ] Propuesta de etiquetado retroactivo y segmentos (interés, tratamiento, etapa).
- [ ] Mensajes de reactivación alternativos para testear.

## Fase 6 — Informe final y plan de implementación
- [ ] Informe completo: hallazgos por sector, errores por severidad, impacto estimado en turnos.
- [ ] Quick wins (semana 1) vs. cambios estructurales.
- [ ] Reescritura de mensajes, prompt del bot, secuencias de seguimiento 24/48 h.
- [ ] Tablero de KPIs semanales.

## Fase 7 — Siguiente etapa: Meta Ads
Con el embudo auditado: revisar cuentas, campañas, creativos, públicos, costo por lead/turno/venta y alinear el mensaje del anuncio con el del bot.

## Paralelización
- Hilo A (n8n): Fases 3 y parte de 4, en cuanto haya JSON de workflows.
- Hilo B (ManyChat): Fases 2, 4 y 5, el más largo.
- Hilo C: organigrama (Fase 1), en paralelo desde ya.

## Preguntas abiertas para el dueño
1. ¿Cómo accedemos a los datos (Chrome local o exports)?
2. ¿Qué semana exacta auditamos?
3. ¿Quién es quién en el organigrama?
4. ¿Dónde vive n8n (cloud o propio) y hay export de workflows?
5. ¿Qué plataformas entran (Instagram, WhatsApp, Messenger)?
6. ¿Cuál es la meta numérica (turnos/semana, costo por turno)?
7. ¿Los nombres de pacientes se pueden ver/tratar o se anonimizan?
