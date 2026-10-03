#!/usr/bin/env python3
"""Regenera empresa/organigrama.html incrustando el contenido de organigrama.json."""
import json
import re
from pathlib import Path

E = Path(__file__).resolve().parents[1]
datos = json.loads((E / "organigrama.json").read_text(encoding="utf-8"))
html = (E / "organigrama.html").read_text(encoding="utf-8")
nuevo = "const D = " + json.dumps(datos, ensure_ascii=False) + ";"
html, n = re.subn(r"^const D = .*?;$", lambda m: nuevo, html, count=1, flags=re.M)
assert n == 1, "No se encontró 'const D = ...;' en organigrama.html"
(E / "organigrama.html").write_text(html, encoding="utf-8")
print("organigrama.html actualizado")
