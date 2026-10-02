"""Arma las presentaciones a partir de plantilla.html + piezas.
python build.py              -> XAUUSD_Backtest_2026.html (muestra con límite por sesión)
python build.py escalera     -> XAUUSD_Escalera_de_riesgo.html (muestra sin límite + escalera de riesgo)
"""
import sys
modo = sys.argv[1] if len(sys.argv) > 1 else "backtest"
rd = lambda f: open(f, encoding="utf-8").read()
t = rd("plantilla.html")
t = t.replace("__COMPARE__", rd("comparativa.js"))
t = t.replace("__ANUAL_HTML__", rd("anual.html")).replace("__ANUAL_JS__", rd("anual.js"))
if modo == "escalera":
    t = (t.replace("__TITULO__", "XAUUSD | Escalera de riesgo").replace("__H1BASE__", "XAUUSD | Sin límite · ")
          .replace("__MUESTRA__", " · Sin límite de operaciones por sesión")
          .replace("__EXTRA_TAB__", '\n  <button role="tab" id="tab-escalera" data-k="escalera" aria-controls="escalera">Escalera de riesgo</button>')
          .replace("__EXTRA_VIEW__", '<div id="escalera" class="view" role="tabpanel" hidden>' + rd("escalera.html") + "</div>")
          .replace("__EXTRA_JS__", rd("escalera.js"))
          .replace("__FUENTES__", "Fuente: listas de operaciones exportadas del Strategy Tester de TradingView sin límite de operaciones por sesión (XAU_m1_2025-2026_SIN_LIMITE_OPERATIVA_Envolvente_y_START, _Envolvente y _START), separadas por año, en horario de Nueva York. Cada año arranca con 1.000 USD. Escalera de riesgo: resultado de cada operación en unidades de riesgo = PyG / 1% del capital del backtest; simulaciones con reordenamientos al azar (2.000 para Envolvente, 300 para los otros modelos y 1.500 para la escalera con tope).")
          .replace("__DATA__", rd("datos_sin_limite.json")))
    out = "XAUUSD_Escalera_de_riesgo.html"
else:
    t = (t.replace("__TITULO__", "XAUUSD | Backtest 2026").replace("__H1BASE__", "XAUUSD | Backtest ").replace("__MUESTRA__", "")
          .replace("__EXTRA_TAB__", "").replace("__EXTRA_VIEW__", "")
          .replace("__FUENTES__", "Fuente: listas de operaciones exportadas del Strategy Tester de TradingView, horario de Nueva York. 2025: XAU_m1_2025_Envolvente_y_START, XAU_m1_2025_Envolvente y XAU_m1_2025_START. 2026: XAU_m1_2026_CORREGIDO_Envolvente_y_START, XAU_m1_2026_CORREGIDO_Envolvente y XAU_m1_2026_CORREGIDO_START. Cada año arranca con 1.000 USD.").replace("__EXTRA_JS__", "").replace("__DATA__", rd("datos.json")))
    out = "XAUUSD_Backtest_2026.html"
open(out, "w", encoding="utf-8").write(t)
print("ok", out, len(t))
