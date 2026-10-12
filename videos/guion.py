"""Lee la narración de guiones/cNN.md: el guion es la única fuente del texto que se narra.

Cada sección `## N. Título (`Clase`) · ≈ …` aporta las líneas `> …` de su bloque **Narración**. Las marcas `⟨A⟩` pasan
a `<bookmark mark="A"/>` y las `{Llaves}` se llenan con las cifras de `datos.py`.
"""
import re
from pathlib import Path

from datos import C08, llenar

CIFRAS = {"08": C08}
SECCION = re.compile(r"^## \d+\. .*?\(`(\w+)`\)", re.M)


def narracion(cap: str) -> dict[str, str]:
    texto = (Path(__file__).parent / "guiones" / f"c{cap}.md").read_text()
    partes = SECCION.split(texto)[1:]  # [Clase, cuerpo, Clase, cuerpo, ...]
    escenas = {}
    for clase, cuerpo in zip(partes[::2], partes[1::2]):
        bloque = cuerpo.split("**Narración**", 1)[1].split("**Visual**", 1)[0]
        lineas = " ".join(l[2:] for l in bloque.splitlines() if l.startswith("> "))
        lineas = re.sub(r"⟨(\w+)⟩", r'<bookmark mark="\1"/>', lineas)
        escenas[clase] = llenar(" ".join(lineas.split()), CIFRAS[cap])
    return escenas


def marcas(texto: str) -> list[str]:
    return re.findall(r'<bookmark mark="(\w+)"/>', texto)
