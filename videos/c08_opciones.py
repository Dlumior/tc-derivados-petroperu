"""Capítulo 8 — Opciones financieras (piloto). Una escena por sección de guiones/c08.md.

La narración sale del guion (guion.py) y la composición, del storyboard aprobado (storyboard_c08.py); aquí solo se
decide qué aparece en cada marca ⟨letra⟩.
make borrador CAP=08 · make final CAP=08
"""
from manim import (DOWN, LEFT, RIGHT, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash, GrowArrow,
                   GrowFromCenter, GrowFromEdge, Indicate, LaggedStart, MathTex, MoveAlongPath, ReplacementTransform,
                   Text, Transform, VGroup, Write)

import storyboard_c08 as sb
from componentes import ejes, marca_k, quebrada
from datos import C08, V08
from derivados.opciones import black76
from estilo import AZUL, GRIS, ORO, ROJO, VERDE, Escena, apoyar, fuente
from guion import narracion

N = narracion("08")
K, C, P = sb.K, sb.C, sb.P


class EscenaC08(Escena):
    def limpiar(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.8)


class Gancho(EscenaC08):
    def construct(self):
        c = sb.cuadro_gancho()
        with self.narracion(N["Gancho"]):
            self.play(FadeIn(c.tanque), GrowFromEdge(c.nivel, DOWN))
            self.m("A")
            self.play(Write(c.precio))
            self.m("B")
            self.play(FadeIn(c.volumen, shift=UP * 0.2), Create(c.ejes), FadeIn(c.fuente))
            self.play(FadeIn(Dot(c.ejes.c2p(0, V08["WTISpot"]), color=ORO), scale=1.5))
            self.m("C")
            self.play(FadeIn(c.nota), LaggedStart(*[Create(t) for t in c.trayectorias], lag_ratio=0.05, run_time=3))
            self.play(FadeIn(c.caida, shift=DOWN * 0.2))
            self.m("D")
            self.play(Create(c.forward), Write(c.rotulo))
            originales = c.trayectorias.copy()
            plano = c.forward.copy().set_stroke(width=1.5, opacity=0.45)
            self.play(*[Transform(t, plano.copy().set_color(t.get_color())) for t in c.trayectorias], run_time=1.5)
            self.m("E")
            es_roja = [t.get_stroke_color().to_hex().lower() == ROJO.lower() for t in originales]
            rojas = VGroup(*[t for t, r in zip(originales, es_roja) if r]).set_stroke(opacity=0.25)
            verdes = VGroup(*[t for t, r in zip(originales, es_roja) if not r]).set_stroke(opacity=0.25)
            protegido = MathTex(r"\checkmark\ \text{protegido}", color=ROJO, font_size=30).move_to(
                c.ejes.c2p(2.2, c.ejes.y_range[0] + 12))
            renunciado = MathTex(r"\times\ \text{renunciado}", color=VERDE, font_size=30).move_to(
                c.ejes.c2p(2.2, c.ejes.y_range[1] - 12))
            self.play(FadeIn(rojas), Write(protegido))
            self.play(FadeIn(verdes), Write(renunciado))
            self.m("F")
            self.limpiar()
            pregunta = Text("¿Protección solo contra el escenario malo?", font_size=40)
            self.play(Write(pregunta))
        self.limpiar()


class Seguro(EscenaC08):
    def construct(self):
        c = sb.cuadro_seguro()
        with self.narracion(N["Seguro"]):
            self.play(FadeIn(c.hoy), FadeIn(c.textos[0]))
            self.m("A")
            self.play(GrowArrow(c.prima), Write(c.prima_txt))
            self.m("B")
            self.play(Create(c.ramas[0]), FadeIn(c.textos[1]))
            self.play(GrowArrow(c.pago), Write(c.pago_txt))
            self.m("C")
            self.play(Create(c.ramas[1]), FadeIn(c.textos[2]))
            self.play(FadeIn(c.cero), FadeIn(c.prima_perdida))
            self.m("D")
            self.play(Indicate(c.prima_txt, color=ROJO), Indicate(c.pago_txt, color=VERDE), run_time=1.5)
            self.m("E")
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.3) for t in c.cartas], lag_ratio=0.4))
        self.limpiar()


class Definiciones(EscenaC08):
    def construct(self):
        c = sb.cuadro_definiciones()
        call, put = c.cartas
        nota = Text("comprador: paga la prima y tiene el derecho  ·  vendedor: cobra la prima y tiene la obligación",
                    font_size=20, color=GRIS)
        apoyar(nota, margen=0.3)
        estilo = Text("europea: se ejerce solo en T  ·  americana: en cualquier momento hasta T", font_size=20,
                      color=GRIS).move_to(nota)
        with self.narracion(N["Definiciones"]):
            self.m("A")
            self.play(FadeIn(call, shift=RIGHT * 0.3))
            self.m("B")
            self.play(FadeIn(put, shift=RIGHT * 0.3))
            self.m("C")
            self.play(Write(c.subyacente))
            self.m("D")
            self.play(FadeIn(nota))
            self.m("E")
            self.play(ReplacementTransform(nota, estilo))
            self.m("F")
            self.play(LaggedStart(*[FadeIn(fila, shift=LEFT * 0.2) for fila in c.glosario], lag_ratio=0.5, run_time=2))
            self.m("G")
            self.play(FadeOut(estilo), FadeIn(c.ejercicio[0]), FadeIn(c.ejercicio[1]))
            self.play(FadeIn(c.ejercicio[2]))
        self.limpiar()


class Posiciones(EscenaC08):
    def construct(self):
        c = sb.cuadro_posiciones()
        with self.narracion(N["Posiciones"]):
            self.play(FadeIn(c.cabeceras), *[Create(celda[0]) for celda in c.grid], FadeIn(c.fuente))
            for marca, celda in zip("ABCD", c.grid):
                self.m(marca)
                self.play(Write(celda[1]), run_time=1.5)
            self.m("E")
            self.play(Write(c.lema))
            self.m("F")
            self.play(*[GrowArrow(f) for par in c.flechas for f in par], FadeIn(c.suma))
            self.m("G")
        self.limpiar()


class Payoffs(EscenaC08):
    def construct(self):
        c = sb.cuadro_payoffs()
        call_l, put_l, call_c, put_c = c.paneles
        e = ejes([50, 130, 10], [-20, 40, 10], x_length=9, y_length=4.2, etiquetas=("S_T", r"\text{payoff}"),
                 numeros=False)
        e.y_axis.add_numbers(font_size=20)
        k = marca_k(e, K, "K = 90")
        e.add(k)
        apoyar(VGroup(e)).move_to([0, e.get_center()[1], 0])
        plano = quebrada(e, [50, K], lambda s: 0, AZUL)
        subida = quebrada(e, [K, 130], lambda s: s - K, AZUL)
        punto = Dot(e.c2p(50, 0), color=ORO)
        no_ejerce = Text("en 70: no se ejerce → 0", font_size=20).next_to(e.c2p(70, 0), UP, buff=0.3)
        guia = DashedLine(e.c2p(110, 0), e.c2p(110, 20), color=VERDE)
        cuenta = MathTex("110 - 90 = 20", color=VERDE, font_size=30).next_to(e.c2p(110, 20), LEFT, buff=0.3)
        formula = MathTex(r"\max(S_T - K,\ 0)", font_size=40).to_edge(UP, buff=0.4)
        with self.narracion(N["Payoffs"]):
            self.m("A")
            self.play(Create(e), FadeIn(c.fuente))
            self.m("B")
            self.add(punto)
            self.play(Create(plano), MoveAlongPath(punto, plano.copy()), run_time=2)
            self.play(FadeIn(no_ejerce))
            self.m("C")
            self.play(Create(subida), MoveAlongPath(punto, subida.copy()), run_time=2)
            self.play(Create(guia), Write(cuenta))
            self.m("D")
            self.play(Write(formula))
            self.m("E")
            self.play(Flash(e.c2p(K, 0), color=ORO, flash_radius=0.5))
            self.m("F")
            self.play(FadeOut(punto, no_ejerce, guia, cuenta),
                      ReplacementTransform(formula, c.formula),
                      ReplacementTransform(e, call_l.ejes), ReplacementTransform(VGroup(plano, subida), call_l.payoff))
            self.play(FadeIn(call_l.nombre), FadeIn(call_l.marca), FadeIn(put_l.ejes), FadeIn(put_l.nombre),
                      FadeIn(put_l.marca))
            espejo = call_l.payoff.copy()
            self.play(espejo.animate.move_to(put_l.payoff).flip(UP).set_color(ROJO), run_time=1.5)
            self.remove(espejo)
            self.add(put_l.payoff)
            self.m("G")
            self.play(*[FadeIn(p.ejes) for p in (call_c, put_c)], *[FadeIn(p.nombre) for p in (call_c, put_c)],
                      *[FadeIn(p.marca) for p in (call_c, put_c)])
            espejos = [call_l.payoff.copy(), put_l.payoff.copy()]
            self.play(espejos[0].animate.flip(RIGHT).move_to(call_c.payoff),
                      espejos[1].animate.flip(RIGHT).move_to(put_c.payoff), run_time=1.5)
            self.remove(*espejos)
            self.add(call_c.payoff, put_c.payoff)
            self.m("H")
            eq_call = VGroup(Dot(call_l.ejes.c2p(K + C, 0), color=ORO, radius=0.06),
                             MathTex("96", font_size=24, color=ORO).next_to(call_l.ejes.c2p(K + C, 0), UP, buff=0.1))
            self.play(Create(call_l.ganancia), FadeIn(c.leyenda))
            self.play(FadeIn(eq_call))
            self.m("I")
            eq_put = VGroup(Dot(put_l.ejes.c2p(K - P, 0), color=ORO, radius=0.06),
                            MathTex("85", font_size=24, color=ORO).next_to(put_l.ejes.c2p(K - P, 0), UP, buff=0.1))
            self.play(Create(put_l.ganancia), FadeIn(eq_put))
            maxima = Text("pérdida máx = prima", font_size=20, color=ORO).move_to(put_l.ejes.c2p(112, -25))
            self.play(FadeIn(maxima))
            self.m("J")
            self.play(Create(call_c.ganancia), Create(put_c.ganancia))
            sin_limite = Text("sin límite ↘", font_size=20, color=ROJO).next_to(call_c.ejes.c2p(120, -30), LEFT, buff=0.2)
            self.play(FadeIn(sin_limite), Indicate(call_c.ganancia, color=ROJO))
        self.limpiar()


class ValorTiempo(EscenaC08):
    def construct(self):
        c = sb.cuadro_valor_tiempo()
        e, kp, r, sig = c.ejes, V08["CollarPut"], V08["r"], V08["VolCrudo"]
        rastro_50, rastro_17 = c.curvas[1], c.curvas[2]
        curva = c.principal.copy()
        cero_dias = quebrada(e, [60, kp, 110], lambda f: max(kp - f, 0), AZUL, ancho=5)
        dias = Text(f"{C08['PlazoDiasOpc']} días", font_size=26, color=AZUL).move_to(e.c2p(100, 13))
        with self.narracion(N["ValorTiempo"]):
            self.play(Create(e), FadeIn(c.fuente))
            self.m("A")
            self.play(Create(c.intrinseco), FadeIn(c.k_txt))
            self.m("B")
            self.play(Create(curva), run_time=1.5)
            self.m("C")
            self.play(FadeIn(c.area), FadeIn(c.leyenda[0]), FadeIn(c.leyenda[2]), FadeIn(c.leyenda[3]))
            self.m("D")
            self.play(FadeIn(c.bandas))
            self.m("E")
            self.play(FadeIn(c.marca), FadeIn(c.punto, scale=1.5), FadeIn(c.f_txt))
            self.m("F")
            self.play(Indicate(c.intrinseco, color=GRIS, scale_factor=1.05))
            self.m("G")
            self.play(GrowFromCenter(c.medida), Create(c.guia), Write(c.rotulo), FadeIn(c.leyenda[4]))
            self.m("H")
            self.play(FadeOut(c.medida, c.guia, c.rotulo, c.punto, c.marca, c.f_txt, c.area), FadeIn(dias))
            for objetivo, texto in [(rastro_50, C08["DiasDic"]), (rastro_17, C08["DiasNov"]), (cero_dias, "0")]:
                self.add(curva.copy().set_stroke(width=2, opacity=0.35))
                nuevo = objetivo.copy().set_stroke(color=AZUL, width=5, opacity=1)
                self.play(Transform(curva, nuevo), Transform(dias, Text(f"{texto} días", font_size=26, color=AZUL)
                                                                .move_to(dias)), run_time=1.5)
            self.play(FadeIn(c.leyenda[1]))
            self.m("I")
            base = c.principal.copy()
            self.play(Transform(curva, base), Transform(dias, Text(f"{C08['PlazoDiasOpc']} días", font_size=26,
                                                                   color=AZUL).move_to(dias)))
            for factor, rotulo in [(0.5, "σ a la mitad"), (1.5, "σ × 1.5"), (1.0, f"σ = {C08['VolCrudo']}")]:
                nueva = e.plot(lambda f, k=factor: black76(f, kp, V08["PlazoDiasOpc"] / 365, r, sig * k, "put"),
                               x_range=[60, 110], color=AZUL, stroke_width=5)
                self.play(Transform(curva, nueva), Transform(dias, Text(rotulo, font_size=26, color=AZUL).move_to(dias)),
                          run_time=1.5)
        self.limpiar()


class Paridad(EscenaC08):
    def construct(self):
        c = sb.cuadro_paridad()
        mismo = Text("mismos pagos en todo escenario ⇒ mismo precio hoy", font_size=26).move_to(c.ecuaciones[0])
        arbitraje = VGroup(
            Text("si la call costara 14: la vendemos, compramos la put y un futuro", font_size=22, color=ROJO),
            Text(f"→ +{C08['ArbitrajeGan']} por barril, sin riesgo", font_size=22, color=VERDE),
        ).arrange(DOWN, buff=0.12).next_to(c.datos, DOWN, buff=0.35)
        with self.narracion(N["Paridad"]):
            self.m("A")
            self.play(Create(c.izq), FadeIn(c.rotulos[0]))
            self.play(Create(c.a[0]))
            self.play(Create(c.a[1]))
            self.m("B")
            self.play(Indicate(c.a, scale_factor=1.03))
            self.m("C")
            self.play(Write(c.igual), Create(c.der), FadeIn(c.rotulos[1]))
            self.play(Create(c.b))
            self.m("D")
            self.play(FadeIn(mismo))
            self.m("E")
            self.play(ReplacementTransform(mismo, c.ecuaciones[0]))
            self.m("F")
            self.play(FadeIn(c.datos), FadeIn(c.fuente))
            self.m("G")
            self.play(Write(c.ecuaciones[1]), Create(c.caja))
            self.m("H")
            self.play(FadeIn(arbitraje[0]))
            self.play(FadeIn(arbitraje[1]))
        self.limpiar()


class PutProtectora(EscenaC08):
    def construct(self):
        c = sb.cuadro_put_protectora()
        put = quebrada(c.ejes, [60, sb.K_PROT, 120], lambda s: max(sb.K_PROT - s, 0) - sb.P_PROT, ROJO, ancho=3)
        pregunta = Text("¿Piso sin prima?", font_size=44)
        with self.narracion(N["PutProtectora"]):
            self.m("A")
            self.play(Create(c.ejes), FadeIn(c.fuente))
            self.play(Create(c.activo), FadeIn(c.rotulos[0]))
            self.m("B")
            self.play(Create(put))
            self.m("C")
            self.play(Create(c.protegido), FadeIn(c.rotulos[1]), FadeOut(put), run_time=1.5)
            self.m("D")
            self.play(GrowFromCenter(c.piso), Write(c.deducible))
            self.m("E")
            self.play(FadeIn(c.costo, shift=LEFT * 0.3))
            self.m("F")
            self.play(FadeIn(c.lineas[0]), FadeIn(c.lineas[1][0]), GrowFromEdge(c.lineas[1][1], LEFT))
            self.m("G")
            self.play(FadeIn(c.plan_b, shift=LEFT * 0.3))
            self.m("H")
            self.limpiar()
            self.play(Write(pregunta))
        self.limpiar()


class Collar(EscenaC08):
    def construct(self):
        c = sb.cuadro_collar()
        capas = sb.cuadro_capas()
        with self.narracion(N["Collar"]):
            self.m("A")
            self.play(Create(c.ejes), FadeIn(c.fuente))
            self.play(Create(c.put), FadeIn(c.leyenda[0]))
            self.m("B")
            self.play(Create(c.call), FadeIn(c.leyenda[1]))
            self.m("C")
            self.play(FadeIn(c.leyenda[4]))
            self.m("D")
            self.play(Create(c.inventario), FadeIn(c.leyenda[2]))
            self.play(Create(c.collar), FadeIn(c.leyenda[3]), run_time=1.5)
            self.m("E")
            self.play(Create(c.piso), FadeIn(c.rotulos[0]))
            self.m("F")
            self.play(Indicate(c.collar, color=AZUL, scale_factor=1.02))
            self.m("G")
            self.play(Create(c.techo), FadeIn(c.rotulos[1]))
            self.m("H")
            self.play(c.piso.animate.set_stroke(width=4), c.techo.animate.set_stroke(width=4))
            self.m("I")
            self.play(Create(c.renuncia), FadeIn(c.rotulos[2]))
            self.m("J")
            self.limpiar()
            self.play(Create(capas.ejes), FadeIn(capas.fuente))
            bandas = [capas.elementos[i:i + 5] for i in range(0, len(capas.elementos), 5)]
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in bandas], lag_ratio=0.5, run_time=2.5))
            self.play(GrowArrow(capas.flecha), FadeIn(capas.leyenda))
        self.limpiar()


class Cierre(EscenaC08):
    def construct(self):
        c = sb.cuadro_cierre()
        ideas = VGroup(*[
            Text(t, font_size=26, color=col) for t, col in [
                ("una opción es un derecho: su payoff se dobla en K", AZUL),
                ("prima = valor intrínseco + valor tiempo", ORO),
                ("paridad put-call: calls y puts ligadas sin modelo", VERDE),
                ("put protectora (con prima) y collar (sin prima)", ROJO),
            ]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([0, 0.6, 0])
        futuro = VGroup(c.marcas[2], c.marcas[3])
        with self.narracion(N["Cierre"]):
            for marca, idea in zip("ABCD", ideas):
                self.m(marca)
                self.play(FadeIn(idea, shift=RIGHT * 0.3))
            self.m("E")
            self.play(FadeOut(ideas))
            self.play(Create(c.recta), FadeIn(VGroup(*[m for i, m in enumerate(c.marcas) if i not in (2, 3)])))
            self.play(GrowFromCenter(c.distancias[0]), GrowFromCenter(c.distancias[1]))
            self.play(Write(c.pregunta))
            self.play(FadeIn(futuro, scale=1.5))
            self.m("F")
            self.play(Write(c.gancho))
        self.limpiar()
