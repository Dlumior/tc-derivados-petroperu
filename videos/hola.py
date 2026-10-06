"""Escena de prueba de la Fase 0: tildes en Text (Pango) y en MathTex (LaTeX en español)."""
from manim import BLUE, DOWN, UP, Create, MathTex, Scene, TexTemplate, Text, Transform, Write

ESPANOL = TexTemplate()
ESPANOL.preamble = ESPANOL.preamble.replace(
    r"\usepackage[english]{babel}", r"\usepackage[spanish,es-noshorthands,es-nolayout]{babel}"
)


class Hola(Scene):
    def construct(self):
        titulo = Text("Opciones: un derecho, no una obligación").scale(0.7).to_edge(UP)
        payoff = MathTex(r"\text{Payoff}_{\text{compra}} = \max(S_T - K,\ 0)", tex_template=ESPANOL)
        paridad = MathTex(r"C - P = S_0 - K e^{-rT}", tex_template=ESPANOL, color=BLUE)
        nota = Text("Paridad put-call", font_size=28).next_to(paridad, DOWN)
        self.play(Write(titulo))
        self.play(Create(payoff))
        self.wait(0.5)
        self.play(Transform(payoff, paridad), Write(nota))
        self.wait()
