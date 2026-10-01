"""Regresión contra data/raw/Examen_Parcial_Prom44_Referencia.xlsx (valores calculados por Excel).

Si alguno falla, la librería dejó de replicar la lógica de referencia del profesor.
"""

from math import exp

import pytest

from derivados import forwards as fw
from derivados import fx

APROX = dict(rel=1e-9)


class TestPregunta1Commodity:
    S, r, T = 14714, 0.035, fw.anios(meses=9)

    def test_forward_teorico(self):
        assert fw.forward_teorico(self.S, self.r, self.T) == pytest.approx(15105.356582980912, **APROX)

    def test_arbitraje_inicio(self):
        f_mkt = fw.forward_teorico(self.S, self.r, self.T) * 1.03
        assert f_mkt == pytest.approx(15558.51728047034, **APROX)
        assert fw.ganancia_arbitraje_inicio(f_mkt, self.S, self.r, self.T) == pytest.approx(441.42, rel=1e-9)
        tabla = fw.tabla_arbitraje(f_mkt, self.S, self.r, self.T, al_inicio=True)
        assert tabla.iloc[-1]["Inicio"] == pytest.approx(441.42, rel=1e-9)
        assert tabla.iloc[-1]["Vencimiento"] == "0"  # prueba de arbitraje

    def test_arbitraje_vencimiento(self):
        f_mkt = fw.forward_teorico(self.S, self.r, self.T) * 1.03
        g = fw.ganancia_arbitraje_vencimiento(f_mkt, self.S, self.r, self.T)
        assert g == pytest.approx(453.16069748942755, **APROX)
        assert g == pytest.approx(441.42 * exp(self.r * self.T), **APROX)

    def test_valor_forward_corto(self):
        K = fw.forward_teorico(self.S, self.r, self.T)
        v = fw.valor_forward(K, 15450, 0.0375, fw.anios(meses=3), posicion="corta")
        assert v == pytest.approx(-485.5943949213324, **APROX)
        assert v * 100 == pytest.approx(-48559.43949213324, **APROX)
        assert fw.registro_contable(v) == "Pasivo"


class TestPregunta2CuentaPorPagarUSD:
    spot = fx.Cotizacion(3.407, 3.408)
    pts = fx.Cotizacion(230, 250)
    N, T = 1_100_000, 0.5

    def test_forward_pactado_ask(self):
        f = fx.precio_pactado(fx.cotizacion_forward(self.spot, self.pts), compra_usd=True)
        assert f == pytest.approx(3.433, **APROX)

    def test_diferencial_implicito(self):
        d = fx.diferencial_implicito(3.433, self.spot.ask, self.T)
        assert d == pytest.approx(0.014725173714430717, **APROX)

    def test_resultados_neto_constante(self):
        df = fx.resultados_cobertura_pasivo_usd(self.N, self.spot.ask, 3.433, {"TC1": 3.382, "TC2": 3.421})
        assert df.loc["Exposición", "TC1"] == pytest.approx(28600.0, abs=1e-6)
        assert df.loc["Forward", "TC1"] == pytest.approx(-56100.0, abs=1e-6)
        assert df.loc["Exposición", "TC2"] == pytest.approx(-14300.0, abs=1e-6)
        assert df.loc["Forward", "TC2"] == pytest.approx(-13200.0, abs=1e-6)
        assert df.loc["Neto", "TC1"] == pytest.approx(-27500.0, abs=1e-6)
        assert df.loc["Neto", "TC2"] == pytest.approx(-27500.0, abs=1e-6)

    def test_posiciones(self):
        p = fx.PosicionCambio(pcc=-self.N, pnd=self.N)
        assert p.pcg == 0
        assert "Cubierto" in p.riesgo()


class TestPregunta4DepositoSintetico:
    dep = fx.DepositoSintetico(
        monto_usd=12_000_000 * 0.25,
        dias=90,
        spot=fx.Cotizacion(3.355, 3.357),
        fwd=fx.cotizacion_forward(fx.Cotizacion(3.355, 3.357), fx.Cotizacion(90, 100)),
        r_usd=0.015,
        r_pen=0.034,
    )

    def test_flujos(self):
        assert self.dep.fwd.bid == pytest.approx(3.364, **APROX)
        assert self.dep.fwd.ask == pytest.approx(3.367, **APROX)
        assert self.dep.usd_final_directo == pytest.approx(3011187.266814279, **APROX)
        assert self.dep.pen_iniciales == pytest.approx(10_065_000, **APROX)
        assert self.dep.pen_finales == pytest.approx(10149482.846574217, **APROX)
        assert self.dep.usd_final_sintetico == pytest.approx(3014399.4198319623, **APROX)

    def test_tasas(self):
        assert self.dep.tasa_sintetica == pytest.approx(0.019337898148904076, **APROX)
        assert self.dep.tasa_implicita_directa == pytest.approx(0.019337898148903854, **APROX)
        assert self.dep.conviene()
        assert fx.diferencial_implicito(3.367, 3.357, 90 / 360) == pytest.approx(0.011968747755761067, **APROX)

    def test_posiciones_cambio(self):
        p = fx.PosicionCambio(pcc=12_000_000, pnd=6_000_000)
        t = p.tabla(variacion_pcc=-3_000_000, variacion_pnd=self.dep.usd_final_sintetico)
        assert t.loc["PCG", "Final"] == pytest.approx(18014399.41983196, **APROX)
        assert t.loc["PND", "Final"] == pytest.approx(9014399.419831961, **APROX)
