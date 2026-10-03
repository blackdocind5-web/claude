# Bitácora de la empresa

Registro de todo lo que se decide y se conversa. Se actualiza en cada sesión. Formato de fechas: DD/MM/YYYY.

## 30/09/2026

**Contexto**
- Se trabaja con Meta Ads para promocionar cirugías (cirujanos plásticos). Se usa ManyChat.
- El usuario quiere analizar las métricas de publicidad de la última semana y compararlas con los mejores cirujanos de Brasil, Argentina, Chile, Colombia, Miami, París y Turquía.
- Enfoque pedido: publicista con especialidad en neuromarketing y cierre de ventas. Mejorar por segmentación (gustos, calidad del lead) y por lo que mejor anduvo en la última semana.

**Decisiones**
- Se arma una estructura de departamentos, cada uno con su mini-agente ("mini-Jarvis") y su informe diario. Ver `organigrama.json`.
- Cada mañana se empieza con `/manana`: estructura, pendientes y informes del día.
- Todo lo hablado desde ahora se guarda en esta bitácora.

**Límites detectados**
- Las sesiones en la nube no acceden a Chrome ni a Meta Ads Manager. Para leer las métricas hace falta una sesión Local en la Mac (Claude in Chrome) o exportar el .csv de Ads Manager.
- No existía un organigrama previo en el sistema. Este es el primero.

**Pendiente**
- Nombre de la empresa, cirujanos o clínicas que se atienden, procedimientos a promocionar.
- Export de Ads Manager (últimos 7 días, vista Anuncios).
- Confirmar qué departamentos faltan o sobran.

### Ajustes de la tarde (30/09/2026)
- Organigrama rediseñado: el usuario (CEO) arriba, Jarvis Central como asistente de dirección, barras que bajan a tres áreas y cajas apiladas por departamento. Paleta sobria en azul acero y grises.
- El usuario quiere ir construyendo los departamentos de a poco.
- Pregunta abierta resuelta: los "mini-Jarvis" son roles definidos en archivos, no bots que corren solos. Ver explicación en la sesión.
- Copia abrible del organigrama: `empresa/organigrama.html`.

### Estado de accesos (30/09/2026)
- El usuario indicó que dio acceso a ManyChat, Meta y n8n. Verificado en esta sesión en la nube: **no hay conexión** a ninguno de los tres.
- Conectores activos hoy: Gmail y Google Calendar. Canva está instalado pero necesita reconectarse.
- En el registro de conectores existen n8n, Supermetrics (incluye Facebook Ads) y Adspirer (incluye Meta Ads), sin instalar. ManyChat no aparece en el registro.
- Caminos posibles: (1) instalar conectores en claude.ai, (2) sesión Local en la Mac con Claude in Chrome para Meta y ManyChat, (3) export manual de Ads Manager.
- Regla: no pasar contraseñas ni tokens por el chat.

## 03/10/2026

**Ideas sueltas del CEO en este mensaje** (ver `ideas.md` #1–11)
- Leer toda la sincronización (ramas con organigrama, sector financiero, auditoría ManyChat/Meta Ads) y abrir oficina.
- Cada mensaje del CEO empieza con la lista de ideas sueltas; cada depto con skill y forma de trabajo de especialista.
- Dirección recopila bitácoras; informes de equipo nivel accionistas, con gráficos aunque haya una sola conversación.
- Nuevo sector de Ingeniería de Prompts (todo empieza por ahí). Empezar por Marketing y Publicidad y sumar ManyChat.

**Hecho hoy**
- Se unificó en esta rama lo disperso: organigrama/agentes (30/09), sector Soluciones Financieras + Bot Oro (02–03/10), plan de auditoría y Meta Ads (sleepy-bohr).
- Se creó `empresa/PROTOCOLO.md`, `informe.py` (informes con gráficos SVG), `consolidar.py` (Dirección) y `abrir_oficina.py`.
- Oficinas abiertas: Dirección, Ingeniería de Prompts, Publicidad y Meta Ads, ManyChat y Captación. Skills y agentes por departamento.

**Pendiente de la sesión del 30/09 que sigue abierto**
- Export de Ads Manager (últimos 7 días), nombre de la empresa/clínica, conexión a ManyChat/n8n/Meta (la nube no los ve).
- Ramas sueltas con perfil de Diego (onboarding) y trabajo de trading (Pine, mec_filtros) sin integrar a `main`.

### Aclaración (03/10/2026, tarde)
- El CEO preguntó por qué los informes del día no estaban en las bitácoras. Hallazgos: (1) mis dos informes (`marketing_arranque` y `direccion_consolidado`) existían como archivos pero no estaban anotados en ninguna bitácora → corregido y automatizado (`informe.py` registra solo; regla de cierre en PROTOCOLO §4). (2) Los informes que pidió en las otras sesiones del día (Meta Ads, auditoría ManyChat, supervisión) no están en este repo: viven en `diegodarpa-netizen/jarvis` (carpeta `oficina/sectores/`), al que esta sesión no tiene acceso. Esta estructura `empresa/` duplica lo que ya existe allá; pendiente decidir cuál es la fuente de verdad.
