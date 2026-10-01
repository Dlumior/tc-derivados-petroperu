"""Opciones europeas: Black-76 (futuros/commodities), Garman-Kohlhagen (tipo de cambio),
collares de costo cero y payoffs para gráficos.
"""

from __future__ import annotations

from math import erf, exp, log, sqrt

import numpy as np


def N(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


def black76(F: float, K: float, T: float, r: float, sigma: float, tipo: str = "call") -> float:
    """Opción sobre futuro/forward (crudo WTI/Brent). r continua."""
    d1 = (log(F / K) + 0.5 * sigma**2 * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    df = exp(-r * T)
    if tipo == "call":
        return df * (F * N(d1) - K * N(d2))
    if tipo == "put":
        return df * (K * N(-d2) - F * N(-d1))
    raise ValueError(tipo)


def garman_kohlhagen(
    S: float, K: float, T: float, r_dom: float, r_ext: float, sigma: float, tipo: str = "call"
) -> float:
    """Opción de tipo de cambio (S en moneda doméstica por unidad extranjera). Tasas continuas."""
    F = S * exp((r_dom - r_ext) * T)
    return black76(F, K, T, r_dom, sigma, tipo)


def delta_black76(F: float, K: float, T: float, r: float, sigma: float, tipo: str = "call") -> float:
    d1 = (log(F / K) + 0.5 * sigma**2 * T) / (sigma * sqrt(T))
    return exp(-r * T) * (N(d1) if tipo == "call" else N(d1) - 1)


def strike_collar_costo_cero(F: float, K_fijo: float, T: float, r: float, sigma: float, fijo: str = "put") -> float:
    """Encuentra el strike de la otra pata para que prima neta = 0.

    fijo='put': se compra put a K_fijo (piso) y se busca el call vendido (techo) — protege inventario (largo crudo).
    fijo='call': se compra call a K_fijo (techo) y se busca el put vendido (piso) — protege compras (corto crudo).
    """
    otro = "call" if fijo == "put" else "put"
    prima = black76(F, K_fijo, T, r, sigma, fijo)
    lo, hi = (F, F * 5) if otro == "call" else (1e-6, F)
    for _ in range(200):
        mid = (lo + hi) / 2
        p = black76(F, mid, T, r, sigma, otro)
        if otro == "call":
            lo, hi = (mid, hi) if p > prima else (lo, mid)
        else:
            lo, hi = (lo, mid) if p > prima else (mid, hi)
    return (lo + hi) / 2


# --------------------------------------------------------------------------- payoffs (vectorizados)


def payoff_call(ST: np.ndarray, K: float) -> np.ndarray:
    return np.maximum(ST - K, 0.0)


def payoff_put(ST: np.ndarray, K: float) -> np.ndarray:
    return np.maximum(K - ST, 0.0)


def payoff_collar_largo_activo(ST: np.ndarray, K_put: float, K_call: float, prima_neta: float = 0.0) -> np.ndarray:
    """Tenedor del activo: + put(K_put) − call(K_call) − prima neta (por unidad)."""
    return payoff_put(ST, K_put) - payoff_call(ST, K_call) - prima_neta
