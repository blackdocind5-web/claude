# Proyecto Meta Ads — Diagnóstico, benchmark internacional y campañas

Estado: PLAN (sin datos propios todavía). Solo lectura hasta aprobar cambios.
Depende de: PLAN_AUDITORIA.md (Fases 2 y 5 aportan el dato de calidad del lead y la etapa del embudo).

## Fase A — Diagnóstico de lo nuestro (última semana)
Datos necesarios: export de Ads Manager (nivel campaña / conjunto / anuncio / creativo), desglose por edad, género, ubicación, plataforma y dispositivo.
- [ ] Métricas por anuncio: inversión, alcance, frecuencia, CPM, CTR (enlace), CPC, costo por conversación iniciada, costo por lead, hook rate (3 s) y hold rate en video.
- [ ] Cruce con ManyChat: cada anuncio → conversaciones → calificados → turnos → asistencias → ventas. Costo por turno y por venta (no solo por lead).
- [ ] Calidad del lead por anuncio/segmento: % que responde, que pide precio y desaparece, que agenda.
- [ ] Qué anduvo mejor y peor de la semana, con hipótesis de por qué.
- [ ] Coherencia promesa del anuncio ↔ primer mensaje del bot (mismo tratamiento, mismo tono, sin promesas de resultado).
- [ ] Revisión de cumplimiento: políticas de Meta para salud/antes y después, publicidad médica local.
- [ ] Tracking: Pixel, API de Conversiones, eventos, atribución; ¿se mide turno/venta o solo mensaje?

## Fase B — Benchmark de competencia (7 mercados)
Mercados: Brasil, Argentina, Chile, Colombia, Miami, París, Turquía.
Fuente: Biblioteca de Anuncios de Meta (pública), web y redes de las clínicas/cirujanos. Solo información pública. Analizamos patrones, no copiamos creativos.
Por mercado, 5–8 referentes (por reputación, volumen de anuncios activos y antigüedad de los anuncios: un anuncio que lleva meses activo suele ser rentable).
Ficha por anuncio/competidor:
- [ ] Tratamiento y público objetivo
- [ ] Formato (video, carrusel, antes/después, testimonio, reel del cirujano, UGC)
- [ ] Hook de los primeros 3 segundos y promesa central
- [ ] Gatillos de neuromarketing: prueba social, autoridad, reciprocidad, escasez, anclaje, aversión a la pérdida, identidad/pertenencia
- [ ] Oferta y CTA (valoración gratis, WhatsApp, formulario, financiación)
- [ ] Idioma, tono y estética; nivel de "lujo" percibido
- [ ] Destino (WhatsApp, landing, Instagram) y fricción
- [ ] Antigüedad del anuncio y cantidad de variantes (proxy de lo que funciona)
Síntesis: patrones ganadores por mercado, diferencias culturales (Brasil: cuerpo y resultados visibles; Miami: lujo y turismo médico; Turquía: paquete todo incluido y precio; París: discreción y autoridad médica), y huecos que nosotros podemos ocupar.

## Fase C — Segmentación por gustos y calidad
- [ ] Mapa de audiencias actuales vs. potenciales: edad, zona, intereses (estética, bienestar, moda, maternidad, etc.), comportamiento.
- [ ] Públicos de calidad: lookalikes de pacientes que compraron (no de todos los leads), clientes por ticket, recurrentes.
- [ ] Exclusiones: leads que nunca califican, curiosos de precio, ya pacientes.
- [ ] Segmentos por motivación (no solo demografía): "quiero verme natural", "recuperación rápida", "miedo a que salga mal", "precio/financiación".
- [ ] Un mensaje y un creativo por segmento.

## Fase D — Propuesta de campañas
Estructura (a validar con datos):
1. Captación fría por tratamiento (estética / implantes), 3–5 creativos por ángulo.
2. Remarketing a quienes vieron video, interactuaron o escribieron y no agendaron (conecta con el lote de leads sin etiqueta).
3. Reactivación de base antigua.
4. Posventa y referidos (prueba social de pacientes reales con consentimiento).
Por campaña: objetivo, público, creativos, hipótesis, presupuesto, KPI de éxito (costo por turno), criterio de corte y calendario de pruebas A/B (una variable por vez).

## Fase E — Medición y mejora continua
- [ ] Tablero semanal: gasto → conversaciones → turnos → ventas, por campaña y segmento.
- [ ] Reunión semanal de decisión: qué se escala, se pausa o se prueba.
- [ ] Benchmarks de referencia de la industria para contrastar (ver fuentes).

## Referencias iniciales (industria, no datos propios)
- CPL de clínicas estéticas: 12–45 USD; médicos y cirujanos ~32 USD por lead (campañas de leads). CTR promedio Meta 2026 ~1,55%. ROI típico ~3,6x y 7x+ en los mejores.
- La API de Conversiones bien implementada puede bajar el costo por consulta entre 20% y 35% el primer mes.
- Fuentes: https://www.get-ryze.ai/es/blog/meta-ads-cost-benchmarks-by-industry-2026 · https://almcorp.com/facebook-ads-benchmarks-2026-ctr-cpc-cpl/ · https://www.prospyrmed.com/blog/post/paid-ad-roi-benchmarks-aesthetic-clinics · https://aestheticpatientacquisition.com/blog/meta-ads-for-plastic-surgeons
- Son cifras de terceros, orientativas; se validan contra nuestros números reales.

## Qué falta para empezar
1. Acceso de lectura a Ads Manager (Chrome local) o export CSV de la última semana.
2. Presupuesto diario/mensual y objetivo (turnos/semana, costo máximo por turno).
3. Tratamientos prioritarios y margen de cada uno.
4. Ciudad/país donde atendemos y si recibimos turismo médico.
5. Lista de competidores que ya conocen, por país.
6. Aprobación para consultar la Biblioteca de Anuncios de Meta.
