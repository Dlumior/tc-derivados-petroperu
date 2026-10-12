"""Estilo común de la serie: paleta, tipografía, plantilla LaTeX en español, pie de fuente, franja de
subtítulos y la clase base `Escena`.

Importar `estilo` antes de construir objetos: fija el fondo y la tipografía por defecto.
"""
from manim import DL, UP, MathTex, Scene, Tex, TexTemplate, Text, config
from manim_voiceover import VoiceoverScene

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


# Franja inferior reservada a los subtítulos de YouTube (el espectador elige su tamaño): ningún objeto entra en ella.
FRANJA_SUBTITULOS = 0.15 * config.frame_height
PISO = -config.frame_height / 2 + FRANJA_SUBTITULOS  # coordenada y más baja que puede ocupar el contenido


def fuente(texto: str) -> Text:
    """Pie de fuente a la izquierda, justo encima de la franja de subtítulos (como \\fuente{...} en el libro)."""
    pie = Text(f"Fuente: {texto}", font_size=16, color=GRIS).to_corner(DL, buff=0.25)
    return pie.shift(UP * (PISO + 0.05 - pie.get_bottom()[1]))


def apoyar(mobject, margen: float = 0.45):
    """Asienta el objeto sobre el piso; el margen por defecto deja sitio al pie de fuente."""
    return mobject.shift(UP * (PISO + margen - mobject.get_bottom()[1]))


def verificar_franja(mobjects) -> None:
    """Falla si algún objeto baja a la franja de subtítulos."""
    invasores = [m for m in mobjects if m.get_bottom()[1] < PISO - 1e-3]
    if invasores:
        detalle = ", ".join(f"{type(m).__name__} (borde inferior {m.get_bottom()[1]:.2f})" for m in invasores)
        raise ValueError(f"Invaden la franja de subtítulos (y < {PISO:.2f}): {detalle}")


class Escena(VoiceoverScene):
    """Escena narrada de la serie: usa la voz de narrador.py y falla si algo invade la franja de subtítulos."""

    def setup(self):
        from narrador import servicio

        super().setup()
        self.set_speech_service(servicio())

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        verificar_franja(self.mobjects)


class Cuadro(Scene):
    """Fotograma fijo (storyboard): mismo estilo y mismo control de la franja, sin voz."""

    def tear_down(self):
        verificar_franja(self.mobjects)
        super().tear_down()
