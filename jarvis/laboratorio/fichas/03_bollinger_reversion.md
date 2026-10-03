# Ficha 03_bollinger_reversion

**03 - Reversión en Bandas de Bollinger**

| Campo | Detalle |
|---|---|
| Tipo | Reversión |
| Archivo Pine | `estrategias/03_bollinger_reversion.pine` |
| Timeframe sugerido | M5 / M15 |
| Mercados a probar | Forex mayor, oro en rango |
| Creada | 03/10/2026 |
| Estado | ver `CATALOGO.md` |

## Hipótesis
El precio que cierra fuera de la banda y vuelve a entrar tiende a regresar a la media.

## Reglas
- **Señal**: Entra cuando el precio vuelve a entrar a la banda tras cerrar fuera de ella (reversión a la media).
- **Stop**: ATR × multiplicador (por defecto 1,5).
- **Objetivo**: distancia del stop × R:R (por defecto 1,5).
- **Tamaño**: riesgo fijo del 1% del equity por operación.
- **Costos incluidos**: comisión 0,01% por lado + 2 ticks de slippage (ajustar al broker real).

## Cuándo debería fallar
Rupturas con volatilidad creciente: la banda se expande y el precio la recorre.

## Registro de pruebas
Anotar cada corrida en `resultados.csv` y guardar el CSV exportado en `datos_tv/`.
Pegar acá los aprendizajes (qué se vio, qué se cambió y por qué):

- _(sin pruebas todavía)_
