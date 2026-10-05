"""Riesgo residual de las coberturas: VaR de una posición con resultado monótono, colateral exigible
bajo un CSA y CVA de un cross currency swap amortizable (exposición esperada analítica, Hull cap. 24).
"""

from __future__ import annotations

from collections.abc import Callable
from math import exp, log, sqrt

import numpy as np
import pandas as pd

from .cobertura import Z
from .opciones import N
from .swaps import Curva


def var_monotono(
    resultado: Callable[[float], float],
    x0: float,
    sigma: float,
    T: float,
    confianza: float = 0.95,
    adverso: str = "baja",
) -> float:
    """VaR de una posición cuyo resultado es monótono en el factor x (lognormal, sin deriva).

    Al ser monótono, el cuantil del resultado es el resultado en el cuantil del factor:
    VaR = −resultado(x0·e^{∓z·σ·√T}). Vale para posiciones con opciones (collar), no solo lineales.
    """
    z = Z[confianza] * sigma * sqrt(T)
    x = x0 * exp(-z if adverso == "baja" else z)
    return max(-resultado(x), 0.0)


def colateral_exigible(mtm: float, umbral: float = 0.0, mta: float = 0.0) -> float:
    """Colateral que PETROPERÚ entrega bajo un CSA: lo que su pasivo (−MtM) exceda el umbral, si supera el MTA."""
    exceso = max(-mtm - umbral, 0.0)
    return exceso if exceso >= mta else 0.0


def _flujos_futuros(
    cron_pen: pd.DataFrame, cron_usd: pd.DataFrame, spot: float, curva_pen: Curva, curva_usd: Curva
) -> list[tuple[float, float, float, float, float]]:
    """(t_k, A_k en S/, B_k en US$, F_k, DF_US$(t_k)) tras cada pago: valor en t_k de los flujos restantes con las
    curvas forward de hoy y forward de paridad F_k (S/ por US$)."""
    t = cron_pen["t"].to_numpy()
    c_pen, c_usd = cron_pen["cuota"].to_numpy(), cron_usd["cuota"].to_numpy()
    df_pen = np.array([curva_pen(x) for x in t])
    df_usd = np.array([curva_usd(x) for x in t])
    return [
        (
            float(t[k]),
            float((c_pen[k + 1 :] * df_pen[k + 1 :]).sum() / df_pen[k]),
            float((c_usd[k + 1 :] * df_usd[k + 1 :]).sum() / df_usd[k]),
            spot * df_usd[k] / df_pen[k],
            float(df_usd[k]),
        )
        for k in range(len(t))
    ]


def epe_ccs(
    cron_pen: pd.DataFrame,
    cron_usd: pd.DataFrame,
    spot: float,
    curva_pen: Curva,
    curva_usd: Curva,
    sigma: float,
) -> pd.DataFrame:
    """Exposición esperada del BANCO frente a PETROPERÚ (que recibe S/ y paga US$), en US$, tras cada pago.

    Valor para el banco en t_k: B_k − A_k/S_k, con A_k (S/) y B_k (US$) el valor en t_k de los flujos restantes
    descontados con las curvas forward de hoy. 1/S_k es lognormal con media 1/F_k (F_k forward de paridad),
    así que E[max(B − A/S, 0)] es un put de Black sobre 1/S.
    """
    filas = []
    for t, a, b, fwd, df in _flujos_futuros(cron_pen, cron_usd, spot, curva_pen, curva_usd):
        if a <= 0 or b <= 0:
            epe = 0.0
        else:
            v = sigma * sqrt(t)
            d1 = (log(a / (fwd * b)) + v * v / 2) / v
            epe = b * N(-(d1 - v)) - a / fwd * N(-d1)
        filas.append({"t": t, "epe": epe, "df_usd": df})
    return pd.DataFrame(filas)


def pfe_ccs(
    cron_pen: pd.DataFrame,
    cron_usd: pd.DataFrame,
    spot: float,
    curva_pen: Curva,
    curva_usd: Curva,
    sigma: float,
    confianza: float = 0.99,
) -> pd.DataFrame:
    """Exposición potencial futura (PFE): pasivo de PETROPERÚ en el CCS en el cuantil `confianza` del TC, tras cada pago.

    El valor B_k − A_k/S_k crece con S, así que su cuantil es el valor en S_k = F_k·e^{z·σ·√t_k} (lognormal con
    mediana en el forward, la misma convención que `var_monotono`). Es lo que el banco pediría de colateral con
    umbral cero en ese cuantil, a lo largo de toda la vida del swap.
    """
    z = Z[confianza]
    filas = [
        {"t": t, "pfe": max(b - a / (fwd * exp(z * sigma * sqrt(t))), 0.0)}
        for t, a, b, fwd, _ in _flujos_futuros(cron_pen, cron_usd, spot, curva_pen, curva_usd)
    ]
    return pd.DataFrame(filas)


def agregar_exposiciones(e1: float, e2: float, rho: float) -> float:
    """Exposición conjunta de dos posiciones casi lineales en factores con correlación rho (varianza-covarianza):
    √(e1² + e2² + 2ρ·e1·e2). Con rho = 1 es la suma; con rho = 0, la raíz de la suma de cuadrados."""
    return sqrt(max(e1 * e1 + e2 * e2 + 2 * rho * e1 * e2, 0.0))


def cva_ccs(
    cron_pen: pd.DataFrame,
    cron_usd: pd.DataFrame,
    spot: float,
    curva_pen: Curva,
    curva_usd: Curva,
    sigma: float,
    spread: float,
    lgd: float = 0.60,
) -> dict[str, float]:
    """CVA unilateral = LGD·Σ DF(t_k)·EPE(t_k)·PD(t_{k−1}, t_k), con intensidad λ = spread/LGD.

    Devuelve el CVA en US$ y su equivalente en pb anuales sobre el saldo en US$ del swap (lo que el banco
    sumaría a la tasa fija de la pata en US$).
    """
    perfil = epe_ccs(cron_pen, cron_usd, spot, curva_pen, curva_usd, sigma)
    lam = spread / lgd
    t = perfil["t"].to_numpy()
    t_prev = np.concatenate([[0.0], t[:-1]])
    pd_marg = np.exp(-lam * t_prev) - np.exp(-lam * t)
    cva = float(lgd * (perfil["df_usd"] * perfil["epe"] * pd_marg).sum())
    anualidad = float((cron_usd["saldo_inicial"].to_numpy() * (t - t_prev) * perfil["df_usd"].to_numpy()).sum())
    return {"cva": cva, "pb": cva / anualidad * 1e4, "epe_max": float(perfil["epe"].max()), "lambda": lam}
