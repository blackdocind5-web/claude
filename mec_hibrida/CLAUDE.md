# Gestión Híbrida (cartera multiactivo del sistema MEC)

Objetivo de Fabián: preservar y crecer el capital durante una década. Nada de riesgos agresivos.

## Flujo
1. CSV de AUDUSD, EURUSD y GBPUSD en `datos/` (`<PAR>_m1_2025-2026_{Envolvente,START,Envolvente_y_START}.csv`); XAUUSD se toma de `../mec_analisis` (XAU_m1_2025_* y XAU_m1_2026_CORREGIDO_*). Filtrar con `../mec_filtros/filtrar_trades.py`.
2. `python hibrida.py` → `datos_hibrida.json`; `python build.py` → `Gestion_Hibrida.html` (usa los estilos de `../mec_analisis/plantilla.html`).
3. Publicar en https://claude.ai/artifact/3rCqw6v7s2hgLMaWYg8sVN

## Reglas de la simulación
- Riesgo fijo 1% del capital realizado al entrar; operaciones de todos los activos en orden cronológico de entrada; límite 1 TP / 2 SL por sesión (ya en los datos).
- Objetivo semanal (+nR, 1R = 0,9%) y freno de pérdida semanal (−nR): al alcanzarlo no se abren operaciones hasta el lunes.
- Un activo-patrón entra solo si gana en 2025 y en 2026 por separado; una regla de gestión se acepta solo si mejora los dos años sin subir la caída máxima.
- Simulaciones: remuestreo con reposición dentro de cada activo.
- `duplicados()` detecta un START idéntico al Envolvente y lo excluye (pasó con el primer AUDUSD_START; ya se reemplazó por el correcto el 05/10/2026).

## Gestión ganadora (decisión de Fabián, 06/10/2026)
XAUUSD Envolvente + EURUSD Envolvente y START + GBPUSD START, de lunes a jueves (sin viernes en ningún activo), riesgo fijo 1%, límite 1 TP / 2 SL por sesión, freno de pérdida semanal −3R, sin objetivo semanal. Fijada en `hibrida.py` (`final = dict(vie=False, stop=3)`).
