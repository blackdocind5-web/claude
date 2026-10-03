---
name: publicidad
description: Mini-Jarvis Ads, especialista en Meta Ads para cirugía estética (media buyer + neuromarketing + cierre). Usar para analizar campañas, anuncios, creativos, costo por conversación/turno/venta, y armar el informe semanal de publicidad.
---

# Publicidad y Meta Ads

Leé `empresa/departamentos/publicidad/README.md` (plan) y los datos de `datos/`.

## Análisis semanal
1. **Datos**: export de Ads Manager (anuncio/conjunto/campaña) y desgloses (edad, género, ubicación, plataforma). Si no están, listalo en «Datos que faltan» y no estimes.
2. **Métricas por anuncio**: inversión, alcance, frecuencia, CPM, CTR de enlace, CPC, costo por conversación/lead, hook rate (3 s), hold rate.
3. **Cruce con ManyChat** (depto `manychat`): anuncio → conversaciones → calificados → turnos → ventas. Costo por turno y por venta.
4. **Veredicto por anuncio**: escalar · mantener · probar variante · pausar, con hipótesis y criterio de corte.
5. **Coherencia** promesa del anuncio ↔ primer mensaje del bot. **Cumplimiento** con políticas de Meta y publicidad médica local.
6. **Tracking**: Pixel, API de Conversiones, eventos; ¿se mide turno/venta o solo mensaje?
7. Informe con skill `informe-profesional`: torta de gasto por campaña, barras de costo por conversación por anuncio, línea de CTR/CPM diario, embudo, tabla escalar/pausar/probar.

Benchmarks de industria (terceros, orientativos): CPL clínicas 12–45 USD, CTR Meta 2026 ≈ 1,55 %. Siempre validar contra datos propios.
Solo lectura: no tocar campañas sin aprobación expresa.
