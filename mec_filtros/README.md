# Filtros de calendario — Sistema MEC (XAUUSD, sesión Pre NY)

Calendario de días y horarios en los que el sistema **no opera** o **opera con restricciones**.
Se usa para limpiar los exports de TradingView antes de cualquier análisis.

- **Horario de referencia:** Nueva York (el mismo que usan los exports de TradingView).
- **Sesión Pre NY:** 07:00–09:00 NY.
- **Fuente:** capturas del calendario de ForexFactory y eventos informados por Fabián.
- **Fechas futuras:** Fabián las va enviando a medida que se publican en ForexFactory.

## Reglas

| Regla | Qué significa | Eventos que la activan |
|---|---|---|
| ⛔ **No operar** (`SIN_OPERAR`) | Se descarta **cualquier** operación cuya entrada caiga ese día. | Feriados bancarios de EE. UU., Reino Unido, Alemania, Francia e Italia (incluido el feriado parcial de Italia) · NFP (USD) · CPI (USD) · CPI (GBP) · PIB final trimestral (USD) · Discursos del presidente de EE. UU. o del presidente de la Fed **dentro de 07:00–09:00** |
| ⚠️ **Solo entradas en ventana** (`SOLO_ENTRADA`) | Solo vale una operación con **entrada** dentro de la ventana (07:00–07:59). La salida no importa: si queda abierta, sigue hasta su SL o TP. | BCE: Main Refinancing Rate, Monetary Policy Statement, ECB Press Conference (EUR) |
| ⏸️ **Sin abrir** (`BLOQUEO_NOTICIA`) | Se descarta la operación si su **entrada** cae dentro del bloqueo (10 min antes a 3 min después del dato, extremos incluidos). Una operación ya abierta puede cerrarse dentro del bloqueo por SL o TP automático. | ADP Non-Farm Employment Change (USD, 08:15 → bloqueo 08:05–08:18) · Core PCE Price Index m/m (USD, 08:30 → bloqueo 08:20–08:33) |

Si un día tiene varias reglas, gana ⛔ **No operar**.

**Discursos:** ForexFactory no muestra la hora en el historial, así que solo se cargan los discursos que Fabián confirma que ocurrieron dentro de la sesión Pre NY.

## Cómo se aplica

```bash
python mec_filtros/filtrar_trades.py <export_tradingview.csv>
```

Genera `<nombre>_validos.csv` (lo que se analiza) y `<nombre>_excluidos.csv` (lo descartado, con el motivo),
y muestra en pantalla cada operación excluida. El script solo aplica las filas con `estado = confirmado`.

Para agregar eventos o años nuevos: sumar filas a `calendario_AAAA.csv` (formato `DD/MM/AAAA`, separador `;`,
una fila por evento; un día puede tener varias). El script lee todos los `calendario_*.csv` de esta carpeta.

---

## Calendario 2026 (67 días · 73 eventos: 48 ⛔ · 6 ⚠️ · 19 ⏸️)

### Enero

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/01/2026 | Jue | ⛔ No operar | EUR | Feriado bancario Francia e Italia (Año Nuevo) |
| 06/01/2026 | Mar | ⛔ No operar | EUR | Feriado bancario Italia (Epifanía) |
| 07/01/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 09/01/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 13/01/2026 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 19/01/2026 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Martin Luther King Jr.) |
| 21/01/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 22/01/2026 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 22/01/2026 | Jue | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |

### Febrero

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 04/02/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/02/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 11/02/2026 | Mié | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 13/02/2026 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 16/02/2026 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Presidents' Day) |
| 18/02/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 20/02/2026 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Marzo

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 04/03/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 06/03/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 11/03/2026 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 13/03/2026 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 19/03/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 25/03/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |

### Abril

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/04/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 03/04/2026 | Vie | ⛔ No operar | USD/GBP/EUR | NFP + Feriado bancario Reino Unido y Alemania (Viernes Santo) |
| 06/04/2026 | Lun | ⛔ No operar | GBP/EUR | Feriado bancario Reino Unido, Alemania, Francia e Italia (Lunes de Pascua) |
| 09/04/2026 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 09/04/2026 | Jue | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |
| 10/04/2026 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 21/04/2026 | Mar | ⛔ No operar | USD | Discurso/entrevista de Trump (presidente de EE. UU.) a las 08:30 NY |
| 22/04/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 30/04/2026 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 30/04/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |

### Mayo

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/05/2026 | Vie | ⛔ No operar | EUR | Feriado bancario Alemania, Francia e Italia (Día del Trabajo) |
| 04/05/2026 | Lun | ⛔ No operar | GBP | Feriado bancario Reino Unido (May Day) |
| 06/05/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 08/05/2026 | Vie | ⛔ No operar | USD/EUR | NFP + Feriado bancario Francia (Día de la Victoria) |
| 12/05/2026 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 14/05/2026 | Jue | ⛔ No operar | EUR | Feriado bancario Alemania y Francia (Ascensión) |
| 20/05/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 25/05/2026 | Lun | ⛔ No operar | USD/GBP/EUR | Feriado bancario EE. UU. (Memorial Day), Reino Unido (Spring Bank Holiday), Alemania y Francia (Lunes de Pentecostés) |
| 28/05/2026 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Junio

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/06/2026 | Mar | ⛔ No operar | EUR | Feriado bancario Italia (Día de la República) |
| 03/06/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/06/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 10/06/2026 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 11/06/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 17/06/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 19/06/2026 | Vie | ⛔ No operar | USD | Feriado bancario EE. UU. (Juneteenth) |
| 25/06/2026 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 25/06/2026 | Jue | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |
| 29/06/2026 | Lun | ⛔ No operar | EUR | Feriado bancario parcial Italia (San Pedro y San Pablo, solo algunos bancos) |

### Julio

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/07/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 01/07/2026 | Mié | ⛔ No operar | USD | Discurso de Warsh (presidente de la Fed) a las 09:00 NY |
| 02/07/2026 | Jue | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 03/07/2026 | Vie | ⛔ No operar | USD | Feriado bancario EE. UU. (Día de la Independencia, observado) |
| 14/07/2026 | Mar | ⛔ No operar | USD/EUR | CPI USD + Feriado bancario Francia (Día Nacional) |
| 22/07/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 23/07/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 30/07/2026 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Agosto

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 05/08/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 07/08/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 12/08/2026 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 19/08/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 26/08/2026 | Mié | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 31/08/2026 | Lun | ⛔ No operar | GBP | Feriado bancario Reino Unido (Summer Bank Holiday) |

### Septiembre

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/09/2026 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 04/09/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 07/09/2026 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Labor Day) |
| 10/09/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 11/09/2026 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 16/09/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 30/09/2026 | Mié | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |
| 30/09/2026 | Mié | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |

## Calendario 2025 (97 días · 100 eventos: 70 ⛔ · 8 ⚠️ · 22 ⏸️)

### Enero

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/01/2025 | Mié | ⛔ No operar | USD/GBP/EUR | Feriado bancario EE. UU., Reino Unido, Alemania, Francia y Italia (Año Nuevo) |
| 06/01/2025 | Lun | ⛔ No operar | EUR | Feriado bancario Italia (Epifanía) |
| 08/01/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 10/01/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 15/01/2025 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 15/01/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 20/01/2025 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Martin Luther King Jr.) |
| 30/01/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 31/01/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Febrero

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 05/02/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 07/02/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 12/02/2025 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 17/02/2025 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Presidents' Day) |
| 19/02/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 28/02/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Marzo

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 05/03/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 06/03/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 07/03/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 12/03/2025 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 26/03/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 27/03/2025 | Jue | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |
| 28/03/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Abril

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/04/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 04/04/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 10/04/2025 | Jue | ⛔ No operar | USD | CPI m/m (USD) |
| 16/04/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 17/04/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 18/04/2025 | Vie | ⛔ No operar | GBP/EUR | Feriado bancario Reino Unido y Alemania (Viernes Santo) |
| 21/04/2025 | Lun | ⛔ No operar | GBP/EUR | Feriado bancario Reino Unido, Alemania, Francia y Italia (Lunes de Pascua) |
| 25/04/2025 | Vie | ⛔ No operar | EUR | Feriado bancario Italia (Día de la Liberación) |
| 30/04/2025 | Mié | ⏸️ Sin abrir 09:50–10:03 | USD | Core PCE Price Index m/m (dato 10:00, fuera de la sesión) |
| 30/04/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |

### Mayo

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/05/2025 | Jue | ⛔ No operar | EUR | Feriado bancario Alemania, Francia y Italia (Día del Trabajo) |
| 02/05/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 05/05/2025 | Lun | ⛔ No operar | GBP | Feriado bancario Reino Unido (May Day) |
| 08/05/2025 | Jue | ⛔ No operar | EUR | Feriado bancario Francia (Día de la Victoria) |
| 13/05/2025 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 15/05/2025 | Jue | ⛔ No operar | USD | Discurso de Powell (presidente de la Fed) a las 08:40 NY |
| 21/05/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 26/05/2025 | Lun | ⛔ No operar | USD/GBP | Feriado bancario EE. UU. y Reino Unido (Memorial Day / Spring Bank Holiday) |
| 29/05/2025 | Jue | ⛔ No operar | EUR | Feriado bancario Alemania y Francia (Ascensión) |
| 30/05/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Junio

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/06/2025 | Lun | ⛔ No operar | EUR | Feriado bancario Italia (Día de la República) |
| 04/06/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/06/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 06/06/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 09/06/2025 | Lun | ⛔ No operar | EUR | Feriado bancario Alemania y Francia (Lunes de Pentecostés) |
| 11/06/2025 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 18/06/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 19/06/2025 | Jue | ⛔ No operar | USD | Feriado bancario EE. UU. (Juneteenth) |
| 26/06/2025 | Jue | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |
| 27/06/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Julio

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/07/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 03/07/2025 | Jue | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 04/07/2025 | Vie | ⛔ No operar | USD | Feriado bancario EE. UU. (Día de la Independencia) |
| 14/07/2025 | Lun | ⛔ No operar | EUR | Feriado bancario Francia (Día Nacional) |
| 15/07/2025 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 16/07/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 22/07/2025 | Mar | ⛔ No operar | USD | Discurso de Powell (presidente de la Fed) a las 08:30 NY |
| 24/07/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 30/07/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 31/07/2025 | Jue | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Agosto

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/08/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 05/08/2025 | Mar | ⛔ No operar | USD | Discurso de Trump (presidente de EE. UU.) a las 08:00 NY |
| 12/08/2025 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 15/08/2025 | Vie | ⛔ No operar | EUR | Feriado bancario Francia y Italia (Asunción) |
| 19/08/2025 | Mar | ⛔ No operar | USD | Discurso de Trump (presidente de EE. UU.) a las 08:00 NY |
| 20/08/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 25/08/2025 | Lun | ⛔ No operar | GBP | Feriado bancario Reino Unido (Summer Bank Holiday) |
| 29/08/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Septiembre

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/09/2025 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Labor Day) |
| 04/09/2025 | Jue | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/09/2025 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 11/09/2025 | Jue | ⛔ No operar | USD | CPI m/m (USD) |
| 11/09/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 17/09/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 25/09/2025 | Jue | ⛔ No operar | USD | PIB final trimestral - Final GDP q/q (USD) |
| 26/09/2025 | Vie | ⏸️ Sin abrir 08:20–08:33 | USD | Core PCE Price Index m/m (dato 08:30) |

### Octubre

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/10/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 03/10/2025 | Vie | ⛔ No operar | EUR | Feriado bancario Alemania (Día de la Unidad) |
| 09/10/2025 | Jue | ⛔ No operar | USD | Discurso de Powell (presidente de la Fed) a las 08:30 NY |
| 13/10/2025 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Columbus Day) |
| 22/10/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 24/10/2025 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 30/10/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |

### Noviembre

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 05/11/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 11/11/2025 | Mar | ⛔ No operar | USD/EUR | Feriado bancario EE. UU. y Francia (Armisticio / Veterans Day) |
| 19/11/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 20/11/2025 | Jue | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 27/11/2025 | Jue | ⛔ No operar | USD | Feriado bancario EE. UU. (Acción de Gracias) |

### Diciembre

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 03/12/2025 | Mié | ⏸️ Sin abrir 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/12/2025 | Vie | ⏸️ Sin abrir 09:50–10:03 | USD | Core PCE Price Index m/m (dato 10:00, fuera de la sesión) |
| 08/12/2025 | Lun | ⛔ No operar | EUR | Feriado bancario Italia (Inmaculada Concepción) |
| 16/12/2025 | Mar | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 17/12/2025 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 18/12/2025 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 24/12/2025 | Mié | ⛔ No operar | EUR | Feriado bancario Alemania (Nochebuena) |
| 25/12/2025 | Jue | ⛔ No operar | USD/GBP/EUR | Feriado bancario EE. UU., Reino Unido, Alemania, Francia y Italia (Navidad) |
| 26/12/2025 | Vie | ⛔ No operar | GBP/EUR | Feriado bancario Reino Unido, Alemania y Italia (Boxing Day / San Esteban) |
| 31/12/2025 | Mié | ⛔ No operar | EUR | Feriado bancario Alemania (Fin de año) |
