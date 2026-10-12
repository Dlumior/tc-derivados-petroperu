"""Estilo común de la serie: paleta, tipografía, plantilla LaTeX en español y pie de fuente.

Las escenas importan `from estilo import *` antes de construir objetos: fija el fondo y la tipografía por defecto.
"""
from manim import DL, MathTex, Tex, TexTemplate, Text, config

# Paleta de libro/figuras.py, aclarada para fondo oscuro (mismo tono, más luminosidad).
FONDO = "#0f1419"
TEXTO = "#ece8e1"
AZUL = "#5b8def"
ROJO = "#f0663f"
VERDE = "#4cc26b"
GRIS = "#9aa0a6"
ORO = "#f2b632"
MORADO = "#b67be0"

FUENTE = "CMU Serif"  # la de 3Blue1Brown y la de LaTeX: texto y fórmulas combinan

ESPANOL = TexTemplate()
# La plantilla de Manim ya carga babel en inglés; agregar otro babel da "option clash". Con español, \max sale "máx".
ESPANOL.preamble = ESPANOL.preamble.replace(
    r"\usepackage[english]{babel}", r"\usepackage[spanish,es-noshorthands,es-nolayout]{babel}"
)

config.background_color = FONDO
Text.set_default(font=FUENTE, color=TEXTO)
MathTex.set_default(tex_template=ESPANOL, color=TEXTO)
Tex.set_default(tex_template=ESPANOL, color=TEXTO)


def fuente(texto: str) -> Text:
    """Pie de fuente en la esquina inferior izquierda, como \\fuente{...} en el libro."""
    return Text(f"Fuente: {texto}", font_size=16, color=GRIS).to_corner(DL, buff=0.25)
