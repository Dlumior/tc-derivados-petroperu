"""Exportación a LaTeX: macros con cifras, tablas booktabs y figuras.

Regla del proyecto: NINGUNA cifra se escribe a mano en informe/secciones/*.tex.
Toda cifra viene de `informe/generado/valores.tex` (macros) o de una tabla generada.
Toda tabla/figura lleva obligatoriamente su nota de Fuente y Elaboración (criterio
"Material de apoyo", 3.5 pts: omitirlo resta nota).
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
GEN = RAIZ / "informe" / "generado"


def num(x: float, dec: int = 0, pct: bool = False) -> str:
    """Formato peruano de EEFF: coma de miles, punto decimal. pct=True multiplica por 100."""
    if pct:
        return f"{x * 100:,.{dec}f}\\,\\%"
    s = f"{abs(x):,.{dec}f}"
    return f"({s})" if x < 0 else s  # negativos entre paréntesis, estilo contable


def esc(texto: str) -> str:
    """Escapa caracteres especiales de LaTeX en celdas de texto (%, &, #, _) si no lo están."""
    return re.sub(r"(?<!\\)([%&#_])", r"\\\1", texto)


def _nombre_macro(clave: str) -> str:
    if not re.fullmatch(r"[A-Za-z]+", clave):
        raise ValueError(f"Macro LaTeX inválida (solo letras): {clave!r}")
    return clave


class Macros:
    """Acumula macros y las escribe en informe/generado/valores.tex."""

    def __init__(self) -> None:
        self._m: dict[str, str] = {}

    def set(self, clave: str, valor: float | str, dec: int = 0, pct: bool = False) -> None:
        self._m[_nombre_macro(clave)] = valor if isinstance(valor, str) else num(valor, dec, pct)

    def escribir(self, ruta: Path | None = None) -> Path:
        ruta = ruta or GEN / "valores.tex"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        lineas = ["% ARCHIVO GENERADO por scripts/run_all.py — NO EDITAR A MANO", ""]
        lineas += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(self._m.items())]
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        return ruta


def tabla_latex(
    df: pd.DataFrame,
    nombre: str,
    titulo: str,
    fuente: str,
    etiqueta: str,
    decimales: int | dict[str, int] = 0,
    indice: bool = True,
    nota: str | None = None,
    elaboracion: str = "Elaboración propia",
    flotante: bool = True,
) -> Path:
    """Escribe informe/generado/tablas/<nombre>.tex listo para \\input.

    flotante=False omite el entorno table (usa \\captionof) para poner dos cuadros lado a lado en minipages.

    `fuente` es obligatoria (p. ej. "PETROPERÚ, EEFF auditados 2025, Nota 3.1").
    """
    if not fuente.strip():
        raise ValueError("Toda tabla requiere 'fuente' (criterio Material de apoyo).")

    def fmt(col: str, v: object) -> str:
        if isinstance(v, int | float) and not isinstance(v, bool):
            d = decimales.get(col, 0) if isinstance(decimales, dict) else decimales
            return num(float(v), d)
        return esc(str(v))

    cols = list(df.columns)
    alin = ("l" if indice else "") + "r" * len(cols)
    enc = ([""] if indice else []) + [f"\\textbf{{{c}}}" for c in cols]
    cuerpo = []
    for idx, fila in df.iterrows():
        celdas = ([esc(str(idx))] if indice else []) + [fmt(c, fila[c]) for c in cols]
        cuerpo.append(" & ".join(celdas) + r" \\")
    pie = f"\\fuente{{{fuente}. {elaboracion}.{(' ' + nota) if nota else ''}}}"
    tex = "\n".join(
        [
            "% ARCHIVO GENERADO — NO EDITAR A MANO",
            r"\begin{table}[htbp]\centering\small" if flotante else r"\centering",
            f"\\{'caption' if flotante else 'captionof{table}'}{{{titulo}}}\\label{{{etiqueta}}}",
            f"\\begin{{tabular}}{{{alin}}}",
            r"\toprule",
            " & ".join(enc) + r" \\",
            r"\midrule",
            *cuerpo,
            r"\bottomrule",
            r"\end{tabular}",
            pie,
            *([r"\end{table}"] if flotante else []),
        ]
    )
    ruta = GEN / "tablas" / f"{nombre}.tex"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(tex + "\n", encoding="utf-8")
    return ruta


def estilo_figuras() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (6.0, 3.0),
            "figure.dpi": 150,
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "legend.frameon": False,
            "savefig.bbox": "tight",
        }
    )


def guardar_figura(fig: plt.Figure, nombre: str) -> Path:
    """Guarda PDF vectorial en informe/generado/figuras/. La fuente va en el \\caption del .tex."""
    ruta = GEN / "figuras" / f"{nombre}.pdf"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta
