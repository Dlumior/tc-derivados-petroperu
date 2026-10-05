"""Riesgo residual: cronogramas alternativos del BN, vega, VaR monótono, colateral y CVA del CCS."""

import numpy as np
import pytest

from derivados import opciones, riesgo, swaps


def test_cronograma_con_gracia_y_lineal_amortizan_todo():
    for kw in ({"gracia": 12}, {"tipo": "lineal"}, {"convencion": "nominal"}):
        c = swaps.cronograma_cuota_constante(1000.0, 0.0555, 24, **kw)
        assert c["amortizacion"].sum() == pytest.approx(1000.0)
        assert (c["cuota"] == c["interes"] + c["amortizacion"]).all()
    g = swaps.cronograma_cuota_constante(1000.0, 0.0555, 24, gracia=12)
    assert (g["amortizacion"].iloc[:12] == 0).all() and len(g) == 36


def test_tasa_nominal_da_cuota_mayor_que_efectiva():
    ef = swaps.cronograma_cuota_constante(1000.0, 0.0555, 36)["cuota"].iloc[0]
    no = swaps.cronograma_cuota_constante(1000.0, 0.0555, 36, convencion="nominal")["cuota"].iloc[0]
    assert no > ef


def test_vega_por_diferencias_finitas():
    F, K, T, r, s = 86.5, 77.9, 0.22, 0.041, 0.56
    num = (opciones.black76(F, K, T, r, s + 1e-5, "put") - opciones.black76(F, K, T, r, s - 1e-5, "put")) / 2e-5
    assert opciones.vega_black76(F, K, T, r, s) == pytest.approx(num, rel=1e-6)


def test_var_monotono_lineal_coincide_con_cuantil_lognormal():
    var = riesgo.var_monotono(lambda x: (x - 100.0) * 10, 100.0, 0.30, 1 / 12)
    assert var == pytest.approx(-(100 * np.exp(-1.6449 * 0.30 * np.sqrt(1 / 12)) - 100) * 10)
    # una posición corta pierde con el alza
    assert riesgo.var_monotono(lambda x: (100.0 - x), 100.0, 0.3, 1 / 12, adverso="alza") > 0


def test_colateral_umbral_y_mta():
    assert riesgo.colateral_exigible(-50.0) == 50.0
    assert riesgo.colateral_exigible(-50.0, umbral=30.0) == 20.0
    assert riesgo.colateral_exigible(-50.0, umbral=45.0, mta=10.0) == 0.0
    assert riesgo.colateral_exigible(+50.0) == 0.0


def _ccs_plano():
    cron = swaps.cronograma_cuota_constante(3000.0, 0.0555, 24)
    curva_pen, curva_usd = swaps.curva_plana(0.045), swaps.curva_plana(0.047)
    ccs = swaps.CrossCurrencySwap(cron, 3.44, 0.0)
    ccs = swaps.CrossCurrencySwap(cron, 3.44, ccs.tasa_usd_justa(curva_pen, curva_usd))
    return cron, ccs.cron_usd(), curva_pen, curva_usd


def test_cva_crece_con_spread_y_es_cero_sin_riesgo_de_credito():
    cron, cron_usd, cp, cu = _ccs_plano()
    cero = riesgo.cva_ccs(cron, cron_usd, 3.44, cp, cu, 0.07, spread=0.0)
    bajo = riesgo.cva_ccs(cron, cron_usd, 3.44, cp, cu, 0.07, spread=0.02)
    alto = riesgo.cva_ccs(cron, cron_usd, 3.44, cp, cu, 0.07, spread=0.06)
    assert cero["cva"] == 0.0
    assert 0 < bajo["cva"] < alto["cva"] and 0 < bajo["pb"] < alto["pb"]


def test_epe_analitica_coincide_con_montecarlo():
    cron, cron_usd, cp, cu = _ccs_plano()
    perfil = riesgo.epe_ccs(cron, cron_usd, 3.44, cp, cu, 0.07)
    k = 11
    t = cron["t"].iloc[k]
    a = (cron["cuota"].iloc[k + 1 :] * [cp(x) for x in cron["t"].iloc[k + 1 :]]).sum() / cp(t)
    b = (cron_usd["cuota"].iloc[k + 1 :] * [cu(x) for x in cron["t"].iloc[k + 1 :]]).sum() / cu(t)
    fwd = 3.44 * cu(t) / cp(t)
    z = np.random.default_rng(0).standard_normal(400_000)
    v = 0.07 * np.sqrt(t)
    inv_s = (1 / fwd) * np.exp(-v * v / 2 + v * z)  # E[1/S] = 1/F
    assert perfil["epe"].iloc[k] == pytest.approx(np.maximum(b - a * inv_s, 0).mean(), rel=0.01)


def test_pfe_es_el_cuantil_montecarlo_y_supera_la_epe():
    cron, cron_usd, cp, cu = _ccs_plano()
    k = 11
    pfe = riesgo.pfe_ccs(cron, cron_usd, 3.44, cp, cu, 0.07, confianza=0.99)["pfe"].iloc[k]
    epe = riesgo.epe_ccs(cron, cron_usd, 3.44, cp, cu, 0.07)["epe"].iloc[k]
    assert pfe > epe > 0
    t = cron["t"].iloc[k]
    a = (cron["cuota"].iloc[k + 1 :] * [cp(x) for x in cron["t"].iloc[k + 1 :]]).sum() / cp(t)
    b = (cron_usd["cuota"].iloc[k + 1 :] * [cu(x) for x in cron["t"].iloc[k + 1 :]]).sum() / cu(t)
    fwd = 3.44 * cu(t) / cp(t)
    s = fwd * np.exp(0.07 * np.sqrt(t) * np.random.default_rng(1).standard_normal(400_000))
    assert pfe == pytest.approx(np.quantile(b - a / s, 0.99), rel=0.02)
    p95 = riesgo.pfe_ccs(cron, cron_usd, 3.44, cp, cu, 0.07, confianza=0.95)["pfe"].iloc[k]
    assert p95 < pfe


def test_agregar_exposiciones():
    assert riesgo.agregar_exposiciones(3.0, 4.0, 0.0) == pytest.approx(5.0)
    assert riesgo.agregar_exposiciones(3.0, 4.0, 1.0) == pytest.approx(7.0)
    assert riesgo.agregar_exposiciones(3.0, 4.0, -1.0) == pytest.approx(1.0)
