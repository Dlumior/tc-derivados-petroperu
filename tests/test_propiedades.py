"""Propiedades teóricas que deben cumplirse siempre (no dependen del Excel)."""

import numpy as np
import pytest

from derivados import cobertura, fx, opciones, swaps
from derivados import forwards as fw


def test_paridad_put_call_black76():
    F, K, T, r, s = 60.0, 55.0, 0.5, 0.04, 0.35
    c = opciones.black76(F, K, T, r, s, "call")
    p = opciones.black76(F, K, T, r, s, "put")
    assert c - p == pytest.approx(np.exp(-r * T) * (F - K), rel=1e-10)


def test_collar_costo_cero_con_skew():
    """Si el call se cotiza con menos volatilidad que el put, el techo de costo cero baja (y sigue siendo costo cero)."""
    F, T, r, s = 60.0, 0.25, 0.04, 0.35
    k0 = opciones.strike_collar_costo_cero(F, 54.0, T, r, s, fijo="put")
    k5 = opciones.strike_collar_costo_cero(F, 54.0, T, r, s, fijo="put", sigma_otro=s - 0.05)
    k10 = opciones.strike_collar_costo_cero(F, 54.0, T, r, s, fijo="put", sigma_otro=s - 0.10)
    assert F < k10 < k5 < k0
    assert opciones.black76(F, k5, T, r, s - 0.05, "call") == pytest.approx(
        opciones.black76(F, 54.0, T, r, s, "put"), rel=1e-6
    )


def test_collar_costo_cero():
    F, T, r, s = 60.0, 0.25, 0.04, 0.35
    kc = opciones.strike_collar_costo_cero(F, 54.0, T, r, s, fijo="put")
    assert kc > F
    assert opciones.black76(F, kc, T, r, s, "call") == pytest.approx(
        opciones.black76(F, 54.0, T, r, s, "put"), rel=1e-6
    )


def test_forward_sin_arbitraje_vale_cero():
    S, r, T = 100.0, 0.05, 1.0
    K = fw.forward_teorico(S, r, T)
    assert fw.valor_forward(K, S, r, T) == pytest.approx(0.0, abs=1e-10)


def test_paridad_y_diferencial_consistentes():
    F = fx.forward_paridad(3.40, 0.045, 0.040, 360)
    assert fx.diferencial_implicito(F, 3.40, 1.0) == pytest.approx(1.045 / 1.040 - 1, rel=1e-12)


def test_irs_a_tasa_par_vale_cero():
    curva = swaps.curva_plana(0.045)
    irs = swaps.IRS(100.0, 0.0, 5, freq=2)
    par = irs.tasa_par(curva)
    assert swaps.IRS(100.0, par, 5, freq=2).valor(curva) == pytest.approx(0.0, abs=1e-8)


def test_ccs_tasa_justa_vale_cero():
    cron = swaps.cronograma_cuota_constante(3_000.0, 0.0555, 36)
    c_pen, c_usd = swaps.curva_plana(0.055), swaps.curva_plana(0.045)
    ccs = swaps.CrossCurrencySwap(cron, 3.40, 0.0)
    t = ccs.tasa_usd_justa(c_pen, c_usd)
    assert swaps.CrossCurrencySwap(cron, 3.40, t).valor_usd(c_pen, c_usd) == pytest.approx(0.0, abs=1e-6)


def test_cronograma_amortiza_todo():
    cron = swaps.cronograma_cuota_constante(1000.0, 0.0555, 46)
    assert cron["amortizacion"].sum() == pytest.approx(1000.0, rel=1e-10)


def test_cronograma_remanente_conserva_saldo():
    cron = swaps.cronograma_cuota_constante(1000.0, 0.0555, 36)
    rem = swaps.cronograma_remanente(cron, pagadas=9, dias_a_primera=17)
    assert len(rem) == 27
    assert rem["amortizacion"].sum() == pytest.approx(cron["saldo_inicial"].iloc[9], rel=1e-12)
    assert rem["t"].iloc[0] == pytest.approx(17 / 360)
    assert rem["t"].iloc[1] - rem["t"].iloc[0] == pytest.approx(1 / 12)


def test_ccs_remanente_interes_usd_mensual():
    """Con cronograma que empieza a fracción de mes, la pata USD sigue usando la tasa mensual."""
    cron = swaps.cronograma_remanente(swaps.cronograma_cuota_constante(3400.0, 0.0555, 36), 9, 17)
    c = swaps.CrossCurrencySwap(cron, 3.40, 0.06).cron_usd()
    i = 1.06 ** (1 / 12) - 1
    assert c["interes"].iloc[0] == pytest.approx(cron["saldo_inicial"].iloc[0] / 3.40 * i, rel=1e-12)


def test_bono_a_la_par_rinde_cupon():
    assert swaps.precio_bono(100.0, 0.05, 10, 0.05) == pytest.approx(100.0, rel=1e-12)
    bonos = [(1000.0, 0.0475, 6.5), (2000.0, 0.05625, 21.5)]
    valor = sum(swaps.precio_bono(n, c, a, 0.09) for n, c, a in bonos)
    assert swaps.rendimiento_cartera(bonos, valor) == pytest.approx(0.09, abs=1e-10)


def test_ratio_minima_varianza_perfecto():
    rng = np.random.default_rng(0)
    dF = rng.normal(size=500)
    r = cobertura.ratio_minima_varianza(0.8 * dF, dF)
    assert r["h"] == pytest.approx(0.8, rel=1e-10)
    assert r["efectividad"] == pytest.approx(1.0, rel=1e-10)


def test_tasa_simple_a_efectiva_y_continua_equivalentes():
    r, d = 0.0408, 91
    fac = 1 + r * d / 360
    assert (1 + fx.tasa_efectiva_desde_simple(r, d)) ** (d / 360) == pytest.approx(fac, rel=1e-12)
    assert np.exp(fx.tasa_continua_desde_simple(r, d) * d / 365) == pytest.approx(fac, rel=1e-12)
    assert fx.tasa_efectiva_desde_simple(r, d) > r  # capitalizar a un año eleva la tasa


def test_ndf_pasivo_pen_neto_constante():
    df = fx.resultados_ndf_pasivo_pen(750.0, 3.4367, 3.4347, {"−10 %": 3.093, "base": 3.4367, "+10 %": 3.780})
    esperado = 750.0 / 3.4367 - 750.0 / 3.4347
    for c in df.columns:
        assert df.loc["Neto", c] == pytest.approx(esperado, rel=1e-12)
    assert df.loc["Exposición", "−10 %"] < 0 < df.loc["NDF", "−10 %"]  # sol apreciado: pierde el pasivo, gana el NDF


def test_bootstrap_par_reprecia_swaps_a_la_par():
    plazos, par = [1, 2, 3, 5], [0.045, 0.0472, 0.048, 0.048]
    grilla, z = swaps.bootstrap_par_anual(plazos, par)
    dfs = (1 + z) ** (-grilla)
    for n, c in zip(grilla, np.interp(grilla, plazos, par), strict=True):
        k = int(n)
        assert c * dfs[:k].sum() + dfs[k - 1] == pytest.approx(1.0, abs=1e-12)
    assert z[0] == pytest.approx(0.045, rel=1e-12)  # a 1 año, par = cero


def test_rendimiento_conveniencia_inverso_del_forward():
    S, r, T, q = 92.6, 0.041, 2 / 12, 0.40
    F = fw.forward_teorico(S, r, T, q=q)
    assert fw.rendimiento_conveniencia_implicito(S, F, r, T) == pytest.approx(q, rel=1e-12)
