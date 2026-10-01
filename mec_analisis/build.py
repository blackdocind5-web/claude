"""Arma la presentación XAUUSD_Backtest_2026.html a partir de plantilla.html, comparativa.js y datos.json."""
t = open("plantilla.html", encoding="utf-8").read()
t = t.replace("__COMPARE__", open("comparativa.js", encoding="utf-8").read())
t = t.replace("__ANUAL_HTML__", open("anual.html", encoding="utf-8").read())
t = t.replace("__ANUAL_JS__", open("anual.js", encoding="utf-8").read())
t = t.replace("__DATA__", open("datos.json", encoding="utf-8").read())
open("XAUUSD_Backtest_2026.html", "w", encoding="utf-8").write(t)
print("ok", len(t))
