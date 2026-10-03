"""Controles de calidad del informe (usados por `make check`, `make final` y los hooks).

  1. Páginas del cuerpo ≤ 10, hasta \\label{fin-cuerpo}; las referencias quedan fuera del límite (acordado con el
     profesor: no se evalúan como extensión).
  2. Cada table/figure tiene \\fuente{...} (criterio Material de apoyo: su omisión resta nota).
  3. Cifras escritas a mano en secciones/*.tex (deben venir de macros generadas).
  4. Marcas \\pendiente{...} restantes y insumos PENDIENTE en data/procesado/*.yaml.

Uso: python scripts/verificar_informe.py [--final] [--solo-paginas]
Sale con código 1 si hay errores (en --final, los avisos también son errores).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
INF = RAIZ / "informe"
PDF = INF / "out" / "main.pdf"
MAX_PAGINAS = 10

sys.path.insert(0, str(RAIZ / "src"))

# Números "permitidos" a mano: años, numeración de notas, porcentajes de escenario redondos, fórmulas.
PERMITIDOS = re.compile(r"^(19|20)\d{2}$|^\d{1,2}$")
NUMERO = re.compile(r"(?<![\\\w{])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d{3,})(?![\w}])")


def sin_comentarios(tex: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in tex.splitlines())


def sin_matematica(tex: str) -> str:
    tex = re.sub(r"\\begin\{(equation|align)\*?\}.*?\\end\{\1\*?\}", "", tex, flags=re.S)
    return re.sub(r"\$[^$]*\$", "", tex)


def conteo_paginas() -> tuple[int, int | None]:
    """(páginas totales del PDF, página donde termina el cuerpo según \\label{fin-cuerpo} o None)."""
    from pypdf import PdfReader

    total = len(PdfReader(str(PDF)).pages)
    aux = PDF.with_suffix(".aux")
    m = re.search(r"\\newlabel\{fin-cuerpo\}\{\{[^}]*\}\{(\d+)\}", aux.read_text()) if aux.exists() else None
    return total, int(m.group(1)) if m else None


def paginas() -> tuple[list[str], list[str]]:
    if not PDF.exists():
        return [f"No existe {PDF.relative_to(RAIZ)} (compile con `make pdf`)."], []
    total, cuerpo = conteo_paginas()
    if cuerpo is None:
        return [], [f"Sin \\label{{fin-cuerpo}} en el .aux: se cuenta el PDF completo ({total} páginas)."] + (
            [f"El PDF tiene {total} páginas (> {MAX_PAGINAS})."] if total > MAX_PAGINAS else []
        )
    if cuerpo > MAX_PAGINAS:
        return [f"El cuerpo termina en la página {cuerpo} (> {MAX_PAGINAS}). Lo que exceda NO se evalúa."], []
    return [], [f"Páginas: cuerpo {cuerpo}/{MAX_PAGINAS} (PDF {total} con referencias)"]


def fuentes_y_cifras() -> tuple[list[str], list[str]]:
    errores, avisos = [], []
    archivos = sorted((INF / "secciones").glob("*.tex")) + sorted((INF / "generado" / "tablas").glob("*.tex"))
    for f in archivos:
        tex = sin_comentarios(f.read_text(encoding="utf-8"))
        rel = f.relative_to(RAIZ)
        for m in re.finditer(r"\\begin\{(table|figure)\}(.*?)\\end\{\1\}", tex, flags=re.S):
            if "\\fuente{" not in m.group(2):
                linea = tex[: m.start()].count("\n") + 1
                errores.append(f"{rel}:{linea}: {m.group(1)} sin \\fuente{{...}}")
        if "secciones" in f.parts:
            limpio = sin_matematica(re.sub(r"\\pendiente\{[^}]*\}", "", tex))
            limpio = re.sub(r"Notas? \d+(\.\d+)*(\.[a-z](\.[ivx]+)?)?(\([ivx]+\))?", "", limpio)
            # Citas de normas: "NIIF~9, 6.3.3", "NIIF 13 ¶71", "NIC~21"
            limpio = re.sub(r"(NIIF|NIC)(~|\s)*\d+(,?(~|\s)*¶?[A-Z]?\d+(\.\d+)*[A-Z]?)?", "", limpio)
            limpio = re.sub(
                r"\\(parencite|textcite|cite|ref|label|input|includegraphics)(\[[^]]*\])?\{[^}]*\}", "", limpio
            )
            for n in NUMERO.findall(limpio):
                if not PERMITIDOS.match(n.replace(",", "")):
                    avisos.append(f"{rel}: cifra escrita a mano '{n}' → use una macro de generado/valores.tex")
            k = len(re.findall(r"\\pendiente\{", tex))
            if k:
                avisos.append(f"{rel}: {k} marca(s) \\pendiente")
    return errores, avisos


def insumos() -> list[str]:
    try:
        from derivados.datos import pendientes

        return [f"Insumo PENDIENTE: {i.clave} ({i.fuente})" for i in pendientes("exposiciones", "mercado")]
    except Exception as e:  # noqa: BLE001
        return [f"No se pudieron leer insumos: {e}"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true", help="avisos cuentan como errores")
    ap.add_argument("--solo-paginas", action="store_true")
    a = ap.parse_args()

    errores, info = paginas()
    avisos: list[str] = []
    if not a.solo_paginas:
        e2, av = fuentes_y_cifras()
        errores += e2
        avisos += av + insumos()

    for s in info:
        print(f"  ✓ {s}")
    for s in avisos:
        print(f"  ! {s}")
    for s in errores:
        print(f"  ✗ {s}", file=sys.stderr)
    fallo = bool(errores) or (a.final and bool(avisos))
    print("RESULTADO:", "FALLA" if fallo else "OK", f"({len(errores)} errores, {len(avisos)} avisos)")
    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main())
