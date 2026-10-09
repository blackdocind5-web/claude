"""Arma Cartera_Esencial.html: plantilla_cartera.html + estilos y funciones de gráficos compartidos + datos_cartera.json.
python analisis.py && python build_cartera.py"""
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
t = (rd("plantilla_cartera.html").replace("__ESTILO__", estilo).replace("__ESTILO_HIBRIDA__", estilo_h)
     .replace("__HELPERS__", js).replace("__DATA__", rd("datos_cartera.json")))
open(os.path.join(AQUI, "Cartera_Esencial.html"), "w", encoding="utf-8").write(t)
print("ok Cartera_Esencial.html", len(t))
