"""Arma Gestion_Hibrida.html desde plantilla_hibrida.html + estilos compartidos + datos_hibrida.json.
python hibrida.py && python build.py"""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: open(os.path.join(AQUI, f), encoding="utf-8").read()
base = rd("../mec_analisis/plantilla.html")
estilo = base[base.index("<style>"):base.index("</style>") + len("</style>")]
t = rd("plantilla_hibrida.html").replace("__ESTILO__", estilo).replace("__DATA__", rd("datos_hibrida.json"))
open(os.path.join(AQUI, "Gestion_Hibrida.html"), "w", encoding="utf-8").write(t)
print("ok Gestion_Hibrida.html", len(t))
