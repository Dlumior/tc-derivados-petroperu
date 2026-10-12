"""Storyboard del capítulo 8: un cuadro fijo por escena del guion (guiones/c08.md), en el momento más cargado.

make storyboard CAP=08   → out/storyboard/c08.png (hoja de contacto) y un PNG por cuadro
Cada función `cuadro_*` devuelve la composición para reutilizarla al animar.
"""
import numpy as np
from manim import (DOWN, DR, LEFT, ORIGIN, RIGHT, UP, UR, Arrow, DashedLine, Dot, Line, MathTex, NumberLine,
                   Rectangle, RoundedRectangle, SurroundingRectangle, Text, VGroup, VMobject)

from componentes import ejes, llave, marca_k, quebrada, tarjeta, titulo
from datos import C08, V08
from derivados.opciones import black76
from estilo import AZUL, GRIS, MORADO, ORO, ROJO, TEXTO, VERDE, Cuadro, apoyar, fuente

# Ejemplo didáctico del libro (cap. 8 §Payoffs y §Put protectora): no son cifras del caso.
K, C, P = 90, 6, 5
ACTIVO, K_PROT, P_PROT = 90, 80, 3
WTI_ALTO = 120
CRUDO = "#6b5436"


def cuadro_gancho():
    tanque = RoundedRectangle(corner_radius=0.2, width=1.6, height=2.2, stroke_color=GRIS, fill_color="#1c232b",
                              fill_opacity=1)
    nivel = Rectangle(width=1.5, height=1.5, stroke_width=0, fill_color=CRUDO, fill_opacity=1)
    nivel.align_to(tanque, DOWN).shift(UP * 0.05)
    precio = Text(f"US$ {C08['WTISpot']}/bbl", font_size=24).next_to(tanque, UP)
    volumen = Text(f"{C08['InvCubiertoMMbl']} MMbl ≈ US$ {C08['InvCubiertoValor']} millones", font_size=20,
                   color=GRIS).next_to(tanque, DOWN)
    caida = Text(f"−10 % → −US$ {C08['Caida10Mill']} millones", font_size=20, color=ROJO).next_to(volumen, DOWN)
    izquierda = VGroup(precio, tanque, nivel, volumen, caida).to_edge(LEFT, buff=0.6)

    rng = np.random.default_rng(7)
    sig, s0, pasos = V08["VolCrudo"], V08["WTISpot"], 60
    t = np.linspace(0, 3, pasos + 1)
    dt = 3 / 12 / pasos
    caminos = [s0 * np.exp(np.concatenate([[0], np.cumsum(-0.5 * sig**2 * dt + sig * np.sqrt(dt)
                                                          * rng.standard_normal(pasos))])) for _ in range(30)]
    bajo, alto = 20 * np.floor(min(map(min, caminos)) / 20), 20 * np.ceil(max(map(max, caminos)) / 20)
    e = ejes([0, 3, 1], [bajo, alto, 20], x_length=7.2, y_length=4.6, etiquetas=(r"\text{meses}", r"\text{US\$/bbl}"))
    apoyar(e).to_edge(RIGHT, buff=0.4)
    trayectorias = VGroup()
    for s in caminos:
        color = VERDE if s[-1] > s0 else ROJO
        trayectorias.add(VMobject(stroke_color=color, stroke_width=1.5, stroke_opacity=0.45)
                         .set_points_as_corners([e.c2p(ti, si) for ti, si in zip(t, s)]))
    forward = DashedLine(e.c2p(0, s0), e.c2p(3, s0), color=ORO, stroke_width=5)
    rotulo = Text("forward", font_size=22, color=ORO).next_to(forward, UP, buff=0.08).align_to(forward, RIGHT)
    nota = Text("trayectorias ilustrativas", font_size=16, color=GRIS).next_to(e, UP, buff=0.05).align_to(e, RIGHT)
    return VGroup(izquierda, e, trayectorias, forward, rotulo, nota,
                  fuente(f"informe; trayectorias simuladas con σ = {C08['VolCrudo']}"))


def cuadro_seguro():
    hoy = Dot([-5, 0.9, 0], color=TEXTO)
    choque, sin_choque = np.array([1.2, 2.3, 0]), np.array([1.2, -0.5, 0])
    ramas = VGroup(Line(hoy.get_center(), choque, color=GRIS), Line(hoy.get_center(), sin_choque, color=GRIS))
    textos = VGroup(
        Text("hoy", font_size=24).next_to(hoy, LEFT),
        Text("choque", font_size=24).next_to(choque, RIGHT),
        Text("sin choque", font_size=24).next_to(sin_choque, RIGHT),
    )
    prima = Arrow(hoy.get_center(), hoy.get_center() + DOWN * 1.0, color=ROJO, buff=0.1)
    prima_txt = Text("prima", font_size=22, color=ROJO).next_to(prima, LEFT, buff=0.1)
    pago = Arrow(textos[1].get_right() + RIGHT * 0.5 + DOWN * 0.5, textos[1].get_right() + RIGHT * 0.5 + UP * 0.7,
                 color=VERDE, buff=0)
    pago_txt = Text("la aseguradora\npaga el daño", font_size=22, color=VERDE).next_to(pago, RIGHT, buff=0.15)
    cero = Text("recibimos 0", font_size=24, color=GRIS).next_to(textos[2], RIGHT, buff=0.5)
    prima_perdida = Text("la prima no se recupera", font_size=20, color=GRIS).next_to(cero, DOWN, buff=0.15)
    cartas = VGroup(tarjeta(["Forward", "obligación en ambas direcciones"], ORO, ancho=4.8),
                    tarjeta(["Opción", "derecho: ejercemos si conviene"], AZUL, ancho=4.8)).arrange(RIGHT, buff=0.8)
    apoyar(cartas, margen=0.15)
    return VGroup(titulo("Un seguro sobre un precio"), ramas, hoy, textos, prima, prima_txt, pago, pago_txt, cero,
                  prima_perdida, cartas)


def cuadro_definiciones():
    call = tarjeta(["call (opción de compra)", "derecho a comprar el subyacente", "a K en la fecha T"], AZUL, ancho=5.4)
    put = tarjeta(["put (opción de venta)", "derecho a vender el subyacente", "a K en la fecha T"], ROJO, ancho=5.4)
    cartas = VGroup(call, put).arrange(DOWN, buff=0.35).to_edge(LEFT, buff=0.7).shift(UP * 0.35)
    simbolos = [MathTex(s, font_size=34, color=ORO) for s in ("K", "T", "S_T", "c,\\ p")]
    textos = [Text(t, font_size=22) for t in ("strike o precio de ejercicio", "vencimiento", "precio del subyacente en T",
                                              "primas de la call y la put")]
    ancho = max(m.width for m in simbolos) + 0.35
    glosario = VGroup(*[VGroup(m, t.next_to(m, RIGHT, buff=ancho - m.width)) for m, t in zip(simbolos, textos)])
    glosario.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    glosario.to_edge(RIGHT, buff=0.7).align_to(cartas, UP)
    subyacente = Text("subyacente: futuro de WTI", font_size=22, color=ORO).next_to(glosario, DOWN, buff=0.45)
    subyacente.align_to(glosario, LEFT)
    ejercicio = VGroup(MathTex(r"\text{call: ejercemos si } S_T > K", font_size=32, color=AZUL),
                       MathTex(r"\text{put: ejercemos si } S_T < K", font_size=32, color=ROJO),
                       Text("si no conviene, la opción vence sin valor", font_size=20, color=GRIS))
    ejercicio[:2].arrange(RIGHT, buff=1.0)
    ejercicio[2].next_to(ejercicio[:2], DOWN, buff=0.15)
    apoyar(ejercicio, margen=0.1)
    return VGroup(titulo("Call y put"), cartas, glosario, subyacente, ejercicio)


def cuadro_posiciones():
    celdas = {
        ("call", "larga"): (AZUL, ["call larga", "derecho a comprar · pagamos 6", "visión: alcista",
                                   "pérdida máx: 6 · ganancia máx: ilimitada"]),
        ("call", "corta"): (AZUL, ["call corta", "obligación de vender · cobramos 6", "visión: no alcista",
                                   "ganancia máx: 6 · pérdida máx: ilimitada"]),
        ("put", "larga"): (ROJO, ["put larga", "derecho a vender · pagamos 5", "visión: bajista",
                                  "pérdida máx: 5 · ganancia máx: 85"]),
        ("put", "corta"): (ROJO, ["put corta", "obligación de comprar · cobramos 5", "visión: no bajista",
                                  "ganancia máx: 5 · pérdida máx: 85"]),
    }
    grid = VGroup(*[tarjeta(lineas, color, ancho=5.6, alto=1.75, font_size=19, discontinua=pos == "corta")
                    for (_, pos), (color, lineas) in celdas.items()])
    grid.arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.25))
    cabeceras = VGroup(Text("larga (compramos)", font_size=24).next_to(grid[0], UP, buff=0.15),
                       Text("corta (vendemos)", font_size=24).next_to(grid[1], UP, buff=0.15))
    flechas = VGroup(*[
        VGroup(Arrow(grid[i].get_right(), grid[i + 1].get_left(), buff=0.05, color=GRIS, stroke_width=3),
               Arrow(grid[i + 1].get_left(), grid[i].get_right(), buff=0.05, color=GRIS, stroke_width=3))
        for i in (0, 2)
    ])
    suma = VGroup(*[Text("+x / −x", font_size=16, color=GRIS).next_to(f, UP, buff=0.02) for f in flechas])
    bloque = VGroup(cabeceras, grid, flechas, suma)
    apoyar(bloque, margen=0.95)
    lema = Text("largo: pagar poco, ganar mucho  ·  corto: cobrar poco, perder mucho (la aseguradora)",
                font_size=20, color=ORO)
    apoyar(lema, margen=0.45)
    return VGroup(titulo("Cuatro posiciones: largo y corto"), bloque, lema,
                  fuente("ejemplo del libro, cap. 8: K = 90, prima de la call 6, prima de la put 5"))


def _mini_payoff(nombre, f, g, color):
    e = ejes([50, 130, 20], [-40, 40, 20], x_length=5.2, y_length=1.9, etiquetas=None, numeros=False, font_size=16)
    e.y_axis.add_numbers(font_size=16)
    xs = [50, K, 130]
    return VGroup(Text(nombre, font_size=22, color=color).next_to(e, UP, buff=0.05), e, marca_k(e, K, "K = 90", font_size=20),
                  quebrada(e, xs, f, color, ancho=4), quebrada(e, xs, g, color, ancho=2.5, discontinua=True))


def cuadro_payoffs():
    call = lambda s: max(s - K, 0)  # noqa: E731
    put = lambda s: max(K - s, 0)  # noqa: E731
    paneles = VGroup(
        _mini_payoff("call larga", call, lambda s: call(s) - C, AZUL),
        _mini_payoff("put larga", put, lambda s: put(s) - P, ROJO),
        _mini_payoff("call corta", lambda s: -call(s), lambda s: C - call(s), AZUL),
        _mini_payoff("put corta", lambda s: -put(s), lambda s: P - put(s), ROJO),
    ).arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.45))
    apoyar(paneles)
    formula = MathTex(r"\text{call: } \max(S_T - K,\ 0) \qquad \text{put: } \max(K - S_T,\ 0)", font_size=34)
    formula.to_edge(UP, buff=0.3)
    pie = fuente("ejemplo del libro, cap. 8: primas 6 y 5; equilibrio en 96 y 85")
    leyenda = VGroup(Line(ORIGIN, RIGHT * 0.5, color=TEXTO, stroke_width=4), Text("payoff", font_size=18),
                     DashedLine(ORIGIN, RIGHT * 0.5, color=TEXTO, stroke_width=2), Text("ganancia", font_size=18)
                     ).arrange(RIGHT, buff=0.15).to_edge(RIGHT, buff=0.3).align_to(pie, DOWN)
    return VGroup(formula, paneles, leyenda, pie)


def cuadro_valor_tiempo():
    kp, r, sig = V08["CollarPut"], V08["r"], V08["VolCrudo"]
    e = ejes([60, 110, 10], [0, 20, 5], x_length=8.6, y_length=4.2, etiquetas=("F", r"\text{prima}"))
    apoyar(e, margen=0.85).to_edge(LEFT, buff=0.8)
    intrinseco = quebrada(e, [60, kp, 110], lambda f: max(kp - f, 0), GRIS, ancho=3)
    curvas = {d: e.plot(lambda f, d=d: black76(f, kp, d / 365, r, sig, "put"), x_range=[60, 110],
                        color=AZUL, stroke_width=5 if d == V08["PlazoDiasOpc"] else 2)
              for d in (V08["PlazoDiasOpc"], V08["DiasDic"], V08["DiasNov"])}
    for d, c in curvas.items():
        if d != V08["PlazoDiasOpc"]:
            c.set_stroke(opacity=0.35)
    principal = curvas[V08["PlazoDiasOpc"]]
    area = e.get_area(principal, x_range=[60, 110], bounded_graph=intrinseco_plot(e, kp), color=MORADO, opacity=0.35)
    f0, prima = V08["WTIFut"], V08["PrimaPutEne"]
    punto = Dot(e.c2p(f0, prima), color=ORO)
    marca = DashedLine(e.c2p(f0, 0), e.c2p(f0, prima), color=ORO)
    medida = llave(e.c2p(f0, 0), e.c2p(f0, prima), "", RIGHT, color=ORO)
    rotulo = Text(f"{C08['PrimaPutEne']}: todo valor tiempo", font_size=20, color=ORO).move_to(e.c2p(99, 9))
    guia = Line(medida[0].get_tip(), rotulo.get_bottom() + DOWN * 0.05, color=ORO, stroke_width=1.5)
    k_txt = MathTex(rf"K = {C08['CollarPut']}", font_size=26, color=ROJO).move_to(e.c2p(70, 1.8))
    f_txt = Text(f"futuro de enero: {C08['WTIFut']}", font_size=18, color=ORO).next_to(e.c2p(f0, 0), DOWN, buff=0.45)
    bandas = VGroup(Text("dentro del dinero", font_size=18, color=ROJO).move_to(e.c2p(68, 18.5)),
                    Text("fuera del dinero", font_size=18, color=VERDE).move_to(e.c2p(100, 18.5)))
    leyenda = VGroup(
        VGroup(Line(ORIGIN, RIGHT * 0.5, color=AZUL, stroke_width=5), Text(f"prima a {C08['PlazoDiasOpc']} días", font_size=18)).arrange(RIGHT, buff=0.15),
        VGroup(Line(ORIGIN, RIGHT * 0.5, color=AZUL, stroke_width=2).set_stroke(opacity=0.4),
               Text(f"a {C08['DiasDic']} y {C08['DiasNov']} días", font_size=18)).arrange(RIGHT, buff=0.15),
        VGroup(Line(ORIGIN, RIGHT * 0.5, color=GRIS, stroke_width=3), Text("valor intrínseco", font_size=18)).arrange(RIGHT, buff=0.15),
        VGroup(Rectangle(width=0.5, height=0.2, fill_color=MORADO, fill_opacity=0.35, stroke_width=0),
               Text("valor tiempo", font_size=18)).arrange(RIGHT, buff=0.15),
        Text(f"σ = {C08['VolCrudo']}", font_size=18),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(RIGHT, buff=0.5).shift(UP * 0.8)
    return VGroup(titulo("Valor intrínseco y valor tiempo: la put de enero"), e, area, intrinseco, *curvas.values(),
                  marca, punto, medida, rotulo, guia, k_txt, f_txt, bandas, leyenda,
                  fuente("informe; libro/v2/capas.json; modelo de Black (cap. 9)"))


def intrinseco_plot(e, kp):
    """Valor intrínseco como gráfico de Manim (para `get_area`)."""
    return e.plot(lambda f: max(kp - f, 0), x_range=[60, 110], stroke_opacity=0)


def cuadro_paridad():
    kp = V08["CollarPut"]
    ecuaciones = VGroup(
        MathTex(r"c - p = e^{-rT}\,(F_0 - K)", font_size=40),
        MathTex(rf"c = {C08['PrimaPutEne']} + {C08['VPDif']} = {C08['CallParidad']}", font_size=40, color=VERDE),
    ).arrange(DOWN, buff=0.25).next_to(titulo("x"), DOWN, buff=0.45)
    caja = SurroundingRectangle(ecuaciones[1], color=VERDE, buff=0.12)
    datos = Text(f"put {C08['PrimaPutEne']} · F₀ = {C08['WTIFut']} · K = {C08['CollarPut']} · {C08['PlazoDiasOpc']} días",
                 font_size=20, color=GRIS).next_to(caja, DOWN, buff=0.15)
    xs = [50, kp, 110]
    izq, der = (ejes([50, 110, 20], [-40, 40, 20], x_length=4.8, y_length=2.4, etiquetas=("S_T", None), numeros=False,
                     font_size=16) for _ in range(2))
    for e in (izq, der):
        e.y_axis.add_numbers(font_size=16)
        e.add(marca_k(e, kp, "K", font_size=22))
    graficos = VGroup(izq, der).arrange(RIGHT, buff=2.2)
    apoyar(graficos, margen=0.55)
    a = VGroup(quebrada(izq, xs, lambda s: max(s - kp, 0), AZUL, ancho=4),
               quebrada(izq, xs, lambda s: -max(kp - s, 0), ROJO, ancho=4))
    b = quebrada(der, xs, lambda s: s - kp, VERDE, ancho=5)
    rotulos = VGroup(Text("call comprada + put vendida", font_size=20).next_to(izq, UP, buff=0.08),
                     Text("= forward a K", font_size=20, color=VERDE).next_to(der, UP, buff=0.08))
    igual = MathTex("=", font_size=60).move_to(VGroup(izq, der))
    return VGroup(titulo("Paridad put-call"), ecuaciones, caja, datos, graficos, a, b, rotulos, igual,
                  fuente("informe; libro/v2/capas.json"))


def cuadro_put_protectora():
    e = ejes([60, 120, 10], [-30, 30, 10], x_length=6.8, y_length=4.4, etiquetas=("S_T", r"\text{resultado}"),
             numeros=False)
    e.y_axis.add_numbers(font_size=20)
    e.add(MathTex("K = 80", font_size=24, color=ORO).next_to(e.c2p(K_PROT, K_PROT - ACTIVO - P_PROT), DR, buff=0.1))
    apoyar(e).to_edge(LEFT, buff=0.7)
    xs = [60, K_PROT, 120]
    activo = quebrada(e, xs, lambda s: s - ACTIVO, GRIS, ancho=3, discontinua=True)
    protegido = quebrada(e, xs, lambda s: max(s, K_PROT) - ACTIVO - P_PROT, AZUL, ancho=5)
    piso = llave(e.c2p(62, 0), e.c2p(62, K_PROT - ACTIVO - P_PROT), "13", RIGHT, font_size=22)
    rotulos = VGroup(Text("solo el activo", font_size=18, color=GRIS).move_to(e.c2p(101, 25)),
                     Text("activo + put", font_size=18, color=AZUL).move_to(e.c2p(110, 7)))
    costo = tarjeta(["Solo puts, todo el inventario",
                     f"{C08['InvCubiertoMMbl']} MMbl × US$ {C08['PrimaPut']}/bbl",
                     f"≈ US$ {C08['CostoPutTotal']} millones"], ROJO, ancho=5.2, font_size=20)
    barra_fondo = Rectangle(width=4.6, height=0.32, stroke_color=GRIS, fill_opacity=0)
    usada = float(C08["LineasPct"].split()[0]) / 100
    barra = Rectangle(width=4.6 * usada, height=0.32, stroke_width=0, fill_color=ROJO, fill_opacity=0.8)
    barra.align_to(barra_fondo, LEFT)
    lineas = VGroup(Text(f"líneas de crédito usadas: {C08['LineasPct']}", font_size=18), VGroup(barra_fondo, barra)
                    ).arrange(DOWN, buff=0.12)
    plan_b = tarjeta(["plan B", "put en el tramo más expuesto:", "sin colateral"], ORO, ancho=5.2, font_size=20)
    derecha = VGroup(costo, lineas, plan_b).arrange(DOWN, buff=0.35).to_edge(RIGHT, buff=0.6)
    apoyar(derecha)
    deducible = MathTex(r"\text{pérdida máx} = (90 - 80) + 3 = 13", font_size=26).move_to(e.c2p(76, 14))
    return VGroup(titulo("Put protectora: un seguro con deducible"), e, activo, protegido, piso, rotulos, deducible,
                  derecha,
                  fuente("ejemplo del libro (activo a 90, put 80, prima 3); informe, Cuadro 8"))


def cuadro_collar():
    kp, kc, s0 = V08["CollarPut"], V08["CollarCall"], V08["WTISpot"]
    e = ejes([60, 130, 10], [-40, 40, 10], x_length=7.4, y_length=4.4, etiquetas=("S_T", r"\text{resultado / bbl}"),
             numeros=False)
    e.y_axis.add_numbers(font_size=20)
    e.add(marca_k(e, kp, "K_p", color=ROJO), marca_k(e, s0, "S_0", color=TEXTO), marca_k(e, kc, "K_c", color=MORADO))
    apoyar(e).to_edge(LEFT, buff=0.7)
    xs = [60, kp, kc, 130]
    put = quebrada(e, xs, lambda s: max(kp - s, 0), ROJO, ancho=3)
    call = quebrada(e, xs, lambda s: -max(s - kc, 0), MORADO, ancho=3)
    inventario = quebrada(e, xs, lambda s: s - s0, GRIS, ancho=3, discontinua=True)
    collar = quebrada(e, xs, lambda s: min(max(s, kp), kc) - s0, AZUL, ancho=6)
    piso = DashedLine(e.c2p(60, kp - s0), e.c2p(130, kp - s0), color=ORO, stroke_width=2)
    techo = DashedLine(e.c2p(60, kc - s0), e.c2p(130, kc - s0), color=ORO, stroke_width=2)
    renuncia = DashedLine(e.c2p(WTI_ALTO, kc - s0), e.c2p(WTI_ALTO, WTI_ALTO - s0), color=ROJO, stroke_width=4)
    rotulos = VGroup(
        Text(f"piso −{C08['PisoEne']}", font_size=18, color=ORO).next_to(e.c2p(68, kp - s0), UP, buff=0.1),
        Text(f"techo +{C08['TechoEne']}", font_size=18, color=ORO).next_to(e.c2p(108, kc - s0), UP, buff=0.1),
        Text(f"renuncia {C08['Renuncia120']}\nsi el WTI llega a 120", font_size=16, color=ROJO).move_to(e.c2p(106, 31)),
    )
    leyenda = VGroup(*[
        VGroup(Line(ORIGIN, RIGHT * 0.5, color=col, stroke_width=4), Text(t, font_size=18)).arrange(RIGHT, buff=0.15)
        for col, t in [(ROJO, f"put comprada: {C08['CollarPut']}"), (MORADO, f"call vendida: {C08['CollarCall']}"),
                       (GRIS, f"inventario sin cobertura (hoy: {C08['WTISpot']})"), (AZUL, "inventario + collar")]
    ], Text("prima neta = 0", font_size=20, color=VERDE)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    leyenda.to_edge(RIGHT, buff=0.3).align_to(e, UP)
    return VGroup(titulo("Collar de costo cero: capa de enero"), e, inventario, put, call, collar, piso, techo,
                  renuncia, rotulos, leyenda, fuente("informe; libro/v2/capas.json; WTI a 120: ejemplo del libro"))


def cuadro_capas():
    e = ejes([0, 4, 1], [70, 110, 10], x_length=8.0, y_length=4.6, etiquetas=(r"\text{mes de venta}", r"\text{US\$/bbl}"),
             numeros=False)
    e.y_axis.add_numbers(font_size=18)
    apoyar(e)
    meses = [("nov", "KpNov", "KcNov", "FNov"), ("dic", "KpDic", "KcDic", "FDic"),
             ("ene", "CollarPut", "CollarCall", "WTIFut")]
    elementos = VGroup()
    for i, (mes, kp, kc, f) in enumerate(meses, start=1):
        banda = Rectangle(width=1.1, height=abs(e.c2p(0, V08[kc])[1] - e.c2p(0, V08[kp])[1]), stroke_color=AZUL,
                          fill_color=AZUL, fill_opacity=0.25).move_to(e.c2p(i, (V08[kp] + V08[kc]) / 2))
        elementos.add(banda, Dot(e.c2p(i, V08[f]), color=ORO),
                      Text(C08[kc], font_size=18).next_to(banda, UP, buff=0.06),
                      Text(C08[kp], font_size=18).next_to(banda, DOWN, buff=0.06),
                      Text(mes, font_size=22).next_to(e.c2p(i, 70), DOWN, buff=0.15))
    flecha = Arrow(e.c2p(1.0, V08["FNov"]) + LEFT * 0.4 + UP * 0.25, e.c2p(3.0, V08["WTIFut"]) + RIGHT * 0.6 + DOWN * 0.15,
                   color=ORO, buff=0, stroke_width=3, max_tip_length_to_length_ratio=0.06)
    leyenda = VGroup(VGroup(Rectangle(width=0.4, height=0.25, fill_color=AZUL, fill_opacity=0.25, stroke_color=AZUL),
                            Text("collar (piso–techo)", font_size=18)).arrange(RIGHT, buff=0.15),
                     VGroup(Dot(color=ORO), Text("futuro del mes", font_size=18)).arrange(RIGHT, buff=0.15),
                     VGroup(Arrow(LEFT * 0.25, RIGHT * 0.25 + DOWN * 0.1, color=ORO, buff=0, stroke_width=3),
                            Text("backwardation:\nlos futuros caen mes a mes", font_size=18, color=ORO)).arrange(RIGHT, buff=0.15),
                     ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
    return VGroup(titulo("Tres capas, tres collares"), e, elementos, flecha, leyenda,
                  fuente("informe; libro/v2/capas.json"))


def cuadro_cierre():
    recta = NumberLine(x_range=[75, 100, 5], length=11, include_numbers=True, font_size=22, color=GRIS)
    recta.shift(UP * 0.2)
    marcas = VGroup()
    for llave_, nombre, color, lado in [("CollarPut", "put", ROJO, DOWN), ("WTIFut", "futuro de enero ?", ORO, DOWN),
                                        ("WTISpot", "hoy", TEXTO, DOWN), ("CollarCall", "call", MORADO, DOWN)]:
        p = recta.n2p(V08[llave_])
        marcas.add(Dot(p, color=color, radius=0.1),
                   Text(f"{nombre}\n{C08[llave_]}", font_size=20, color=color).next_to(p, lado, buff=0.55))
    hoy, kp, kc = (recta.n2p(V08[k]) for k in ("WTISpot", "CollarPut", "CollarCall"))
    distancias = VGroup(llave(kp, hoy, f"−{C08['DistPutPct']}", UP, color=ROJO),
                        llave(hoy, kc, f"+{C08['DistCallPct']}", UP, color=MORADO))
    pregunta = Text("¿Por qué cuestan lo mismo?", font_size=34).next_to(distancias, UP, buff=0.4)
    gancho = VGroup(Text(f"¿De dónde sale {C08['PrimaPutEne']}?", font_size=26, color=ORO),
                    Text("→  Capítulo 9: Valoración de opciones", font_size=26)).arrange(RIGHT, buff=0.4)
    apoyar(gancho, margen=0.2)
    return VGroup(titulo("Un misterio para el próximo capítulo"), recta, marcas, distancias, pregunta, gancho)


CUADROS = [
    ("01_gancho", cuadro_gancho), ("02_seguro", cuadro_seguro), ("03_definiciones", cuadro_definiciones),
    ("04_posiciones", cuadro_posiciones), ("05_payoffs", cuadro_payoffs), ("06_valor_tiempo", cuadro_valor_tiempo),
    ("07_paridad", cuadro_paridad), ("08_put_protectora", cuadro_put_protectora), ("09_collar", cuadro_collar),
    ("09b_capas", cuadro_capas), ("10_cierre", cuadro_cierre),
]

for _nombre, _f in CUADROS:
    globals()["SB" + _nombre] = type("SB" + _nombre, (Cuadro,), {"construct": lambda self, f=_f: self.add(f())})
