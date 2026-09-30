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
