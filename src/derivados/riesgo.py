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
    t = cron_pen["t"].to_numpy()
    c_pen, c_usd = cron_pen["cuota"].to_numpy(), cron_usd["cuota"].to_numpy()
    df_pen = np.array([curva_pen(x) for x in t])
    df_usd = np.array([curva_usd(x) for x in t])
    filas = []
    for k in range(len(t)):
        a = float((c_pen[k + 1 :] * df_pen[k + 1 :]).sum() / df_pen[k])
        b = float((c_usd[k + 1 :] * df_usd[k + 1 :]).sum() / df_usd[k])
        fwd = spot * df_usd[k] / df_pen[k]  # S/ por US$ a plazo t_k
        if a <= 0 or b <= 0:
            epe = 0.0
        else:
            v = sigma * sqrt(t[k])
            d1 = (log(a / (fwd * b)) + v * v / 2) / v
            epe = b * N(-(d1 - v)) - a / fwd * N(-d1)
        filas.append({"t": t[k], "epe": epe, "df_usd": df_usd[k]})
    return pd.DataFrame(filas)


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
