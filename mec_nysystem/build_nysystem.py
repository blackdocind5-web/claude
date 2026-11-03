"""Arma NY_SYSTEM.html: plantilla_nysystem.html + datos_nysystem.json.
python analisis.py && python build_nysystem.py"""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: open(os.path.join(AQUI, f), encoding="utf-8").read()
t = rd("plantilla_nysystem.html").replace("__DATA__", rd("datos_nysystem.json"))
open(os.path.join(AQUI, "NY_SYSTEM.html"), "w", encoding="utf-8").write(t)
print("ok NY_SYSTEM.html", len(t))
