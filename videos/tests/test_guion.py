import string

from guion import marcas, narracion

ESCENAS = ["Gancho", "Seguro", "Definiciones", "Posiciones", "Payoffs", "ValorTiempo", "Paridad", "PutProtectora",
           "Collar", "Cierre"]


def test_lee_las_diez_escenas_en_orden():
    assert list(narracion("08")) == ESCENAS


def test_sin_llaves_ni_marcas_sin_convertir():
    for texto in narracion("08").values():
        assert "{" not in texto and "⟨" not in texto and ">" not in texto.replace("/>", "")


def test_marcas_consecutivas_desde_a():
    for clase, texto in narracion("08").items():
        m = marcas(texto)
        assert m == list(string.ascii_uppercase[: len(m)]), clase


def test_cifras_llenas():
    assert "US$ 92.60/bbl" in narracion("08")["Gancho"]
    assert "13.42 dólares" in narracion("08")["Paridad"]


def test_pausas_entre_frases():
    from estilo import PAUSA

    for clase, texto in narracion("08").items():
        tramos = [t.strip() for t in texto.split(PAUSA)]
        assert all(tramos), clase  # ninguna pausa al inicio, al final ni duplicada
