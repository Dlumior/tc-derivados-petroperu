"""Escena de prueba de la Fase 1: voz de Kokoro, normalizador y marcas <bookmark/> sincronizadas.

uv run manim -ql prueba_voz.py PruebaVoz
"""
from manim import (DOWN, LEFT, UL, UP, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, GrowFromPoint, Line, MathTex,
                   Text, Write)
from manim_voiceover import VoiceoverScene

from estilo import AZUL, GRIS, ORO, VERDE, fuente
from narrador import servicio

# Ejemplo didáctico del libro, cap. 8 §Payoffs: K = 90, S_T = 110.
K, S_T = 90, 110


class PruebaVoz(VoiceoverScene):
    def construct(self):
        self.set_speech_service(servicio())

        titulo = Text("La opción de compra (call)", font_size=40).to_edge(UP)
        formula = MathTex(r"\text{Payoff} = \max(S_T - K,\ 0)").next_to(titulo, DOWN)
        with self.voiceover(
            "Una opción de compra, o call, da el derecho, pero no la obligación, de comprar un activo "
            "a un precio fijado: el strike."
        ):
            self.play(Write(titulo))
            self.play(FadeIn(formula, shift=DOWN * 0.2))

        ejes = Axes(x_range=[50, 130, 10], y_range=[0, 40, 10], x_length=8, y_length=3.6,
                    axis_config={"color": GRIS, "include_numbers": True, "font_size": 22}).shift(DOWN * 1.1)
        etiqueta = ejes.get_axis_labels(MathTex("S_T", font_size=30), MathTex(r"\text{Payoff}", font_size=30))
        plano = Line(ejes.c2p(50, 0), ejes.c2p(K, 0), color=AZUL, stroke_width=6)
        subida = Line(ejes.c2p(K, 0), ejes.c2p(130, 130 - K), color=AZUL, stroke_width=6)
        marca_k = MathTex("K", color=ORO, font_size=32).next_to(ejes.c2p(K, 0), UL, buff=0.15)
        with self.voiceover(
            "Dibujemos su payoff al vencimiento. Si el precio termina por debajo del strike, "
            '<bookmark mark="abajo"/>la opción no se ejerce y paga cero. Si termina por encima, '
            '<bookmark mark="arriba"/>paga la diferencia.'
        ) as tracker:
            self.play(Create(ejes), FadeIn(etiqueta), FadeIn(marca_k))
            self.wait_until_bookmark("abajo")
            self.play(Create(plano))
            self.wait_until_bookmark("arriba")
            self.play(Create(subida), run_time=max(tracker.get_remaining_duration(), 0.5))

        punto = Dot(ejes.c2p(S_T, S_T - K), color=VERDE)
        guia = DashedLine(ejes.c2p(S_T, 0), ejes.c2p(S_T, S_T - K), color=VERDE)
        texto = MathTex(rf"{S_T} - {K} = {S_T - K}", color=VERDE, font_size=34).next_to(punto, LEFT, buff=0.3)
        pie = fuente("ejemplo del libro, cap. 8")
        with self.voiceover(
            f'Con un strike de US$ {K} y un precio final de US$ {S_T}, <bookmark mark="paga"/>'
            f"la call paga US$ {S_T - K}."
        ):
            self.play(GrowFromPoint(guia, ejes.c2p(S_T, 0)), FadeIn(pie))
            self.wait_until_bookmark("paga")
            self.play(FadeIn(punto, scale=1.5), Write(texto))
        self.wait(0.5)
        self.play(FadeOut(*self.mobjects))
