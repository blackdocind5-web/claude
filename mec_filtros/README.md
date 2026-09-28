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
| ⛔ **No operar** (`SIN_OPERAR`) | Se descarta **cualquier** operación cuya entrada caiga ese día. | Feriados bancarios de EE. UU., Reino Unido, Alemania, Francia e Italia (incluido el feriado parcial de Italia) · NFP (USD) · CPI (USD) · CPI (GBP) · Discursos del presidente de EE. UU. o del presidente de la Fed **dentro de 07:00–09:00** |
| ⚠️ **Solo entradas en ventana** (`SOLO_ENTRADA`) | Solo vale una operación con **entrada** dentro de la ventana (07:00–07:59). La salida no importa: si queda abierta, sigue hasta su SL o TP. | BCE: Main Refinancing Rate, Monetary Policy Statement, ECB Press Conference (EUR) |
| ⏸️ **Sin abrir ni cerrar** (`BLOQUEO_NOTICIA`) | Se descarta la operación si su **entrada o su salida** caen dentro del bloqueo (10 min antes a 3 min después del dato, extremos incluidos). Una operación abierta antes y cerrada después del bloqueo es válida. | ADP Non-Farm Employment Change (USD, 08:15 → bloqueo 08:05–08:18) |

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

## Calendario 2026 (58 días · 59 eventos: 44 ⛔ · 6 ⚠️ · 9 ⏸️)

### Enero

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/01/2026 | Jue | ⛔ No operar | EUR | Feriado bancario Francia e Italia (Año Nuevo) |
| 06/01/2026 | Mar | ⛔ No operar | EUR | Feriado bancario Italia (Epifanía) |
| 07/01/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 09/01/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 13/01/2026 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 19/01/2026 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Martin Luther King Jr.) |
| 21/01/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |

### Febrero

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 04/02/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/02/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 11/02/2026 | Mié | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 13/02/2026 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 16/02/2026 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Presidents' Day) |
| 18/02/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |

### Marzo

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 04/03/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 06/03/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 11/03/2026 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 19/03/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 25/03/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |

### Abril

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/04/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 03/04/2026 | Vie | ⛔ No operar | USD/GBP/EUR | NFP + Feriado bancario Reino Unido y Alemania (Viernes Santo) |
| 06/04/2026 | Lun | ⛔ No operar | GBP/EUR | Feriado bancario Reino Unido, Alemania, Francia e Italia (Lunes de Pascua) |
| 10/04/2026 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 21/04/2026 | Mar | ⛔ No operar | USD | Discurso de Trump (presidente de EE. UU.) dentro de Pre NY |
| 22/04/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 30/04/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |

### Mayo

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/05/2026 | Vie | ⛔ No operar | EUR | Feriado bancario Alemania, Francia e Italia (Día del Trabajo) |
| 04/05/2026 | Lun | ⛔ No operar | GBP | Feriado bancario Reino Unido (May Day) |
| 06/05/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 08/05/2026 | Vie | ⛔ No operar | USD/EUR | NFP + Feriado bancario Francia (Día de la Victoria) |
| 12/05/2026 | Mar | ⛔ No operar | USD | CPI m/m (USD) |
| 14/05/2026 | Jue | ⛔ No operar | EUR | Feriado bancario Alemania y Francia (Ascensión) |
| 20/05/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 25/05/2026 | Lun | ⛔ No operar | USD/GBP/EUR | Feriado bancario EE. UU. (Memorial Day), Reino Unido (Spring Bank Holiday), Alemania y Francia (Lunes de Pentecostés) |

### Junio

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/06/2026 | Mar | ⛔ No operar | EUR | Feriado bancario Italia (Día de la República) |
| 03/06/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 05/06/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 10/06/2026 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 11/06/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 17/06/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 19/06/2026 | Vie | ⛔ No operar | USD | Feriado bancario EE. UU. (Juneteenth) |
| 29/06/2026 | Lun | ⛔ No operar | EUR | Feriado bancario parcial Italia (San Pedro y San Pablo, solo algunos bancos) |

### Julio

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 01/07/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 01/07/2026 | Mié | ⛔ No operar | USD | Discurso de Warsh (presidente de la Fed) dentro de Pre NY |
| 02/07/2026 | Jue | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 03/07/2026 | Vie | ⛔ No operar | USD | Feriado bancario EE. UU. (Día de la Independencia, observado) |
| 14/07/2026 | Mar | ⛔ No operar | USD/EUR | CPI USD + Feriado bancario Francia (Día Nacional) |
| 22/07/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 23/07/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |

### Agosto

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 05/08/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 07/08/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 12/08/2026 | Mié | ⛔ No operar | USD | CPI m/m (USD) |
| 19/08/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
| 31/08/2026 | Lun | ⛔ No operar | GBP | Feriado bancario Reino Unido (Summer Bank Holiday) |

### Septiembre

| Fecha | Día | Regla | Divisa | Evento |
|---|---|---|---|---|
| 02/09/2026 | Mié | ⏸️ Sin abrir ni cerrar 08:05–08:18 | USD | ADP Non-Farm Employment Change (dato 08:15) |
| 04/09/2026 | Vie | ⛔ No operar | USD | NFP - Non-Farm Payrolls (USD) |
| 07/09/2026 | Lun | ⛔ No operar | USD | Feriado bancario EE. UU. (Labor Day) |
| 10/09/2026 | Jue | ⚠️ Solo entradas 07:00–08:00 | EUR | BCE: Main Refinancing Rate + Monetary Policy Statement + ECB Press Conference |
| 11/09/2026 | Vie | ⛔ No operar | USD | CPI m/m (USD) |
| 16/09/2026 | Mié | ⛔ No operar | GBP | CPI y/y (GBP) |
