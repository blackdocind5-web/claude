"""Arma Backtest_2026.html: plantilla_informe.html + datos_informe.json.
python informe.py && python build_informe.py"""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: open(os.path.join(AQUI, f), encoding="utf-8").read()
t = rd("plantilla_informe.html").replace("__DATA__", rd("datos_informe.json"))
open(os.path.join(AQUI, "Backtest_2026.html"), "w", encoding="utf-8").write(t)
print("ok Backtest_2026.html", len(t))
