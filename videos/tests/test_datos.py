"""Las cifras del capítulo 8 deben coincidir con las que imprime el libro (libro/cap/c08.tex)."""
import pytest

from datos import C08, llenar


@pytest.mark.parametrize(
    "llave, libro",
    [
        ("WTISpot", "92.60"), ("WTIFut", "86.54"), ("CollarPut", "77.90"), ("CollarCall", "98.05"),
        ("PrimaPutEne", "4.85"), ("PlazoDiasOpc", "79"), ("VolCrudo", "56.1 %"), ("CaidaPutPct", "10 %"),
        ("VPDif", "8.56"), ("CallParidad", "13.42"), ("CoberturaCrudoPct", "80 %"), ("InvCubiertoMMbl", "2.32"),
        ("CostoPutTotal", "7.2"), ("PrimaPut", "3.12"), ("LineasPct", "94 %"), ("PisoEne", "14.70"),
        ("TechoEne", "5.45"), ("DistPutPct", "16 %"), ("DistCallPct", "6 %"), ("KpNov", "83.30"),
        ("KpDic", "80.10"), ("KcNov", "103.68"), ("KcDic", "100.38"),
        # Derivadas en el guion, no impresas en el libro:
        ("Renuncia120", "21.95"), ("ArbitrajeGan", "0.58"), ("Caida10Mill", "21.5"),
    ],
)
def test_cifra_coincide_con_el_libro(llave, libro):
    assert C08[llave] == libro


def test_llenar():
    assert llenar("put a {CollarPut} con F = {WTIFut}") == "put a 77.90 con F = 86.54"


def test_llenar_falla_con_llave_desconocida():
    with pytest.raises(KeyError):
        llenar("{NoExiste}")
