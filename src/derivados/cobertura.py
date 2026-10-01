"""Diseño y evaluación de coberturas: ratio de mínima varianza, número de contratos,
escenarios con/sin cobertura, VaR paramétrico y efectividad (NIIF 9: 80–125 % referencial).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from math import sqrt

import numpy as np
import pandas as pd

Z = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}


def ratio_minima_varianza(dS: Sequence[float], dF: Sequence[float]) -> dict[str, float]:
    """h* = ρ·σ_S/σ_F ; efectividad = ρ² (Hull, cap. 3)."""
    s, f = np.asarray(dS, float), np.asarray(dF, float)
    rho = float(np.corrcoef(s, f)[0, 1])
    sig_s, sig_f = float(s.std(ddof=1)), float(f.std(ddof=1))
    return {"h": rho * sig_s / sig_f, "rho": rho, "sigma_S": sig_s, "sigma_F": sig_f, "efectividad": rho**2}


def numero_contratos(h: float, exposicion: float, tamano_contrato: float) -> int:
    """N* = h·Q_A / Q_F (redondeado)."""
    return int(round(h * exposicion / tamano_contrato))


def var_parametrico(exposicion: float, sigma_diaria: float, dias: int = 10, confianza: float = 0.95) -> float:
    """VaR = z·σ·√días·|exposición| (en unidades de la exposición)."""
    return Z[confianza] * sigma_diaria * sqrt(dias) * abs(exposicion)


def tabla_escenarios(
    escenarios: dict[str, float], exposicion: Callable[[float], float], derivados: dict[str, Callable[[float], float]]
) -> pd.DataFrame:
    """Matriz de escenarios: resultado de la exposición y de cada estrategia alternativa.

    escenarios: {"−20 %": precio, ...}; exposicion(x) y derivados[nombre](x) devuelven resultados.
    Columnas: Sin cobertura | <estrategia> derivado | <estrategia> neto ...
    """
    filas = {}
    for nombre, x in escenarios.items():
        e = exposicion(x)
        fila = {"Variable": x, "Sin cobertura": e}
        for est, fn in derivados.items():
            d = fn(x)
            fila[f"{est}: derivado"] = d
            fila[f"{est}: neto"] = e + d
        filas[nombre] = fila
    return pd.DataFrame(filas).T


def efectividad_dolar_offset(cambio_derivado: float, cambio_cubierto: float) -> float:
    """Ratio dollar-offset = −ΔDerivado/ΔPartida cubierta (referencial 80 %–125 %)."""
    return -cambio_derivado / cambio_cubierto
