"""Arma Sesion_NY.html: plantilla_ny.html + estilos y funciones de gráficos compartidos + datos_ny.json.
python analisis_ny.py && python build_ny.py"""
import os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: open(os.path.join(AQUI, f), encoding="utf-8").read()
base = rd("../mec_analisis/plantilla.html")
estilo = base[base.index("<style>"):base.index("</style>") + len("</style>")]
hib = rd("../mec_hibrida/plantilla_hibrida.html")
i = hib.index("<style>\n/* Gestión Híbrida"); estilo_h = hib[i:hib.index("</style>", i) + len("</style>")]
js = hib[hib.index("const $ = s =>"):hib.index("/* ================= RECOMENDACIÓN")]
js = "\n".join(l for l in js.splitlines() if not re.match(r"const (AC|NUM|R|yrs)=", l))
js = js.replace("${pc(it.v,2)}", "${unit==='%'?pc(it.v,2):sg(it.v,2)+unit}")
t = (rd("plantilla_ny.html").replace("__ESTILO__", estilo).replace("__ESTILO_HIBRIDA__", estilo_h)
     .replace("__HELPERS__", js).replace("__DATA__", rd("datos_ny.json")))
open(os.path.join(AQUI, "Sesion_NY.html"), "w", encoding="utf-8").write(t)
print("ok Sesion_NY.html", len(t))
