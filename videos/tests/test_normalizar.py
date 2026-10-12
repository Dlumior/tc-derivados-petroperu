import pytest

from narrador import normalizar


@pytest.mark.parametrize(
    "texto, esperado",
    [
        # Números estilo EEFF
        ("1,234.5", "mil doscientos treinta y cuatro coma cinco"),
        ("3.05", "tres coma cero cinco"),
        ("(12.3)", "menos doce coma tres"),
        ("vence a 17, 50 y 79 días", "vence a diecisiete, cincuenta y setenta y nueve días"),
        # Monedas, escalas y unidades
        ("US$ 2,110.9 millones", "dos mil ciento diez coma nueve millones de dólares"),
        ("US$ 1 millón", "un millón de dólares"),
        ("S/ 3.75", "tres coma setenta y cinco soles"),
        ("US$ 21", "veintiún dólares"),
        ("US$ 1", "un dólar"),
        ("(US$ 9.3 millones)", "menos nueve coma tres millones de dólares"),
        ("(costo de US$ 6)", "(costo de seis dólares)"),
        ("US$ 65.3/bbl", "sesenta y cinco coma tres dólares por barril"),
        ("2,901 bbl", "dos mil novecientos un barriles"),
        ("21 días", "veintiún días"),
        ("tasa de 21 %", "tasa de veintiuno por ciento"),
        ("5.25 %", "cinco coma veinticinco por ciento"),
        ("569 pb", "quinientos sesenta y nueve puntos básicos"),
        # Fechas
        ("28-sep-2026", "veintiocho de septiembre de dos mil veintiséis"),
        ("5-oct-2026", "cinco de octubre de dos mil veintiséis"),
        # Signos
        ("K = 90", "K igual a noventa"),
        # Siglas y términos en inglés
        ("el WTI", "el uést téxas"),
        ("un CCS y un NDF", "un cros cárrensi suap y un fóruard sin entrega"),
        ("el VaR al 99 %", "el valor en riesgo al noventa y nueve por ciento"),
        ("derivados OTC", "derivados fuera de bolsa"),
        ("su payoff", "su péy-of"),
        ("la call y la put", "la col y la put"),
        ("Call", "col"),
        ("un swap", "un suap"),
        ("el strike", "el estráik"),
        ("la paridad put-call", "la paridad put-col"),
    ],
)
def test_normalizar(texto, esperado):
    assert normalizar(texto) == esperado


def test_no_toca_palabras_que_contienen_siglas():
    assert normalizar("calle y computadora") == "calle y computadora"


def test_conserva_marcas():
    texto = 'Con K = 90 <bookmark mark="k90"/>la call cuesta US$ 6.'
    assert normalizar(texto) == 'Con K igual a noventa <bookmark mark="k90"/>la col cuesta seis dólares.'


def test_texto_sin_cambios():
    texto = "Una opción es un derecho, no una obligación."
    assert normalizar(texto) == texto
