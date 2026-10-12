"""Piezas visuales reutilizables de la serie (Fase 3 del plan; crecen con cada capítulo)."""
from manim import (DOWN, RIGHT, UP, Axes, BraceBetweenPoints, DashedVMobject, MathTex, RoundedRectangle, Text, VGroup,
                   VMobject)

from estilo import FONDO, GRIS, TEXTO


def titulo(texto: str) -> Text:
    """Título de sección, arriba y discreto."""
    return Text(texto, font_size=34).to_edge(UP, buff=0.3)


def ejes(x_range, y_range, x_length=8.0, y_length=3.4, etiquetas=("S_T", r"\text{Payoff}"), numeros=True,
         font_size=20) -> Axes:
    """Ejes con el estilo de la serie. `etiquetas` son MathTex (None, o un elemento None, para omitirlas).
    La del eje horizontal va a la derecha de su extremo; la del vertical, encima."""
    e = Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length, tips=False,
             axis_config={"color": GRIS, "include_numbers": numeros, "font_size": font_size, "stroke_width": 2})
    if etiquetas:
        x, y = etiquetas
        e.etiquetas = VGroup()
        if x:
            e.etiquetas.add(MathTex(x, font_size=font_size + 6).next_to(e.x_axis.get_end(), RIGHT, buff=0.15))
        if y:
            e.etiquetas.add(MathTex(y, font_size=font_size + 6).next_to(e.y_axis.get_end(), UP, buff=0.1))
        e.add(e.etiquetas)
    return e


def quebrada(e: Axes, xs, f, color, ancho=5.0, discontinua=False) -> VMobject:
    """Línea poligonal de f evaluada en los quiebres xs: payoffs exactos, sin suavizado."""
    linea = VMobject(color=color, stroke_width=ancho).set_points_as_corners([e.c2p(x, f(x)) for x in xs])
    return DashedVMobject(linea, num_dashes=40) if discontinua else linea


def tarjeta(lineas: list[str], color, ancho=4.6, alto=None, font_size=22, primera_negrita=True,
            discontinua=False) -> VGroup:
    """Recuadro redondeado con texto en líneas; la primera, en negrita y del color de la tarjeta.
    `discontinua` marca el lado corto (el vendedor) con borde punteado."""
    textos = VGroup(*[
        Text(t, font_size=font_size + (4 if i == 0 and primera_negrita else 0), color=color if i == 0 else TEXTO,
             weight="BOLD" if i == 0 and primera_negrita else "NORMAL")
        for i, t in enumerate(lineas)
    ]).arrange(DOWN, aligned_edge=UP, buff=0.2)
    if primera_negrita and len(textos) > 1:
        textos[1:].shift(DOWN * 0.08)
    caja = RoundedRectangle(corner_radius=0.15, width=ancho, height=alto or textos.height + 0.5,
                            stroke_color=color, stroke_width=2.5, fill_color=FONDO, fill_opacity=1)
    if discontinua:
        caja = VGroup(caja.copy().set_stroke(width=0), DashedVMobject(caja.copy().set_fill(opacity=0), num_dashes=60))
    return VGroup(caja, textos.move_to(caja))


def marca_k(e: Axes, k, texto="K", color=None, font_size=24) -> MathTex:
    """Rótulo del strike bajo el eje horizontal (en lugar de numerar todo el eje)."""
    from estilo import ORO

    return MathTex(texto, font_size=font_size, color=color or ORO).next_to(e.c2p(k, 0), DOWN, buff=0.12)


def llave(p1, p2, texto: str, direccion, color=TEXTO, font_size=22) -> VGroup:
    """Llave entre dos puntos con su rótulo del lado de `direccion`."""
    b = BraceBetweenPoints(p1, p2, direction=direccion, color=color)
    return VGroup(b, Text(texto, font_size=font_size, color=color).next_to(b, direccion, buff=0.1))
