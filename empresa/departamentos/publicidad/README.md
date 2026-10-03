# Publicidad y Meta Ads — Plan del departamento

_Agente: Mini-Jarvis Ads · Abierto: 03/10/2026 · Estado: **borrador v0.1** · Sector: Marketing y Publicidad_

## 1. Misión
Medir qué anuncios, conjuntos y campañas rinden, detectar fugas de presupuesto y decidir qué **pausar, escalar o duplicar**, midiendo hasta el turno y la venta (no solo el lead). Promociona cirugías con cirujanos plásticos; el destino es ManyChat/WhatsApp.

## 2. Cómo trabaja (especialista)
Skill `.claude/skills/publicidad/SKILL.md`. Rol: media buyer senior con neuromarketing y cierre de ventas.
- Siempre cruza **anuncio → conversación → calificado → turno → venta** con el depto ManyChat. El costo por lead solo es un dato intermedio.
- Una variable por test A/B. Un anuncio con meses activo en la competencia suele ser rentable (proxy).
- Cumplimiento primero: políticas de Meta para salud/estética y publicidad médica local.
- Hipótesis siempre explícitas: «creemos que X porque Y; lo confirma/descarta Z».

## 3. Fuentes de datos
| Fuente | Estado | Cómo se conecta |
|---|---|---|
| Export de Ads Manager (.csv, vista Anuncios, 7 días) | Pendiente | Exportar y dejar en `empresa/departamentos/publicidad/datos/` |
| Desglose por edad, género, ubicación, plataforma, dispositivo | Pendiente | Mismo export con desgloses |
| Sesión Local con Claude in Chrome (Mac) | Pendiente | Sesión local; la nube no accede |
| Conector Supermetrics / Adspirer (Meta Ads) | Sin instalar | Instalar en claude.ai → conectores |
| Biblioteca de anuncios de Meta (competencia) | Pendiente | Pública; requiere aprobación del CEO (lo ejecuta Inteligencia) |

## 4. KPIs
Gasto diario · Alcance · Frecuencia · CPM · CTR de enlace · CPC · Costo por conversación · Costo por lead · Hook rate (3 s) y hold rate · **Costo por turno · Costo por venta**.
Referencias de industria (terceros, orientativas, se validan con datos propios): CPL clínicas estéticas 12–45 USD; CTR promedio Meta 2026 ≈ 1,55 %.

## 5. Informes
- **Diario**: 24 h y 7 días; mejor y peor anuncio; alertas de fuga (frecuencia alta, CTR en caída, gasto sin conversaciones).
- **Semanal (accionistas)**: embudo completo, gasto por campaña (torta), ranking de anuncios (barras), tendencia de CPM/CTR (línea), qué se escala/pausa/prueba, calendario de tests.
- Se genera con `informe.py` (skill `informe-profesional`). Sin datos reales, el informe muestra avance del plan y **Datos que faltan**.

## 6. Hoja de ruta (de `auditoria/PROYECTO_META_ADS.md`)
| Fase | Objetivo | Entregables |
|---|---|---|
| A — Diagnóstico propio (última semana) | Qué anduvo mejor y peor y por qué | Tabla por anuncio, cruce con ManyChat, coherencia anuncio↔bot, cumplimiento, tracking (Pixel/API de Conversiones) |
| B — Benchmark 7 mercados | Patrones ganadores (BR, AR, CL, CO, Miami, París, Turquía) | Fichas por anuncio — lo ejecuta Inteligencia Competitiva |
| C — Segmentación | Públicos por motivación y calidad | Mapa de audiencias, lookalikes de compradores, exclusiones |
| D — Campañas | Frío por tratamiento, remarketing, reactivación, posventa/referidos | Plan por campaña con KPI de corte y calendario A/B |
| E — Medición | Tablero semanal y reunión de decisión | Escalar / pausar / probar |

## 7. Preguntas abiertas
1. Nombre de la clínica/agencia, cirujanos y procedimientos prioritarios con su margen.
2. Presupuesto diario/mensual y meta (turnos/semana, costo máximo por turno).
3. País/ciudad de atención y si hay turismo médico.
4. Vía de acceso a los datos: export, Chrome local o conector.
5. ¿Hay Pixel y API de Conversiones activos?
