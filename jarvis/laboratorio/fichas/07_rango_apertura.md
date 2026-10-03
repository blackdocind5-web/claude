# Ficha 07_rango_apertura

**07 - Ruptura del rango de apertura (Opening Range)**

| Campo | Detalle |
|---|---|
| Tipo | Ruptura / sesión |
| Archivo Pine | `estrategias/07_rango_apertura.pine` |
| Timeframe sugerido | M1 / M5 |
| Mercados a probar | Oro, índices (sesión NY) |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
El rango de los primeros minutos de la sesión marca el sesgo del día; su ruptura tiene continuación.

## Reglas
- **Señal**: Marca el rango de los primeros minutos de la sesión y opera la ruptura (una operación por día).
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Días sin catalizador: rango chico con ruptura falsa. Depende de la hora elegida.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
