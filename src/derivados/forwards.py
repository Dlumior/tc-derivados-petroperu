"""Forwards y futuros sobre activos de inversión / commodities (capitalización continua).

Replica la lógica de la Pregunta 1 del Examen Parcial de referencia:
teorema spot-forward, oportunidad de arbitraje, tabla de operaciones
Inicio/Vencimiento y valorización de una posición forward abierta.

Convención: tasas anuales con capitalización continua, T en años.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp

import pandas as pd


def anios(meses: float = 0.0, dias: float = 0.0, base: int = 360) -> float:
    """Convierte meses y/o días a años (meses/12 + días/base)."""
    return meses / 12 + dias / base


def forward_teorico(spot: float, r: float, T: float, q: float = 0.0, u: float = 0.0) -> float:
    """F = S·exp((r + u − q)·T).

    q: rendimiento de conveniencia / dividendo continuo.
    u: costo de almacenamiento continuo (commodities).
    """
    return spot * exp((r + u - q) * T)


def rendimiento_conveniencia_implicito(spot: float, forward: float, r: float, T: float, u: float = 0.0) -> float:
    """Despeja q de F = S·exp((r + u − q)·T):  q = r + u − ln(F/S)/T.

    Con backwardation (F < S) resulta q > r: el mercado paga por tener el crudo hoy.
    """
    from math import log

    return r + u - log(forward / spot) / T


def ganancia_arbitraje_inicio(f_mercado: float, spot: float, r: float, T: float) -> float:
    """Ganancia hoy = F·exp(−rT) − S.

    > 0: forward sobrevaluado → cash-and-carry (préstamo, largo spot, corto forward).
    < 0: forward subvaluado → reverse cash-and-carry.
    """
    return f_mercado * exp(-r * T) - spot


def ganancia_arbitraje_vencimiento(f_mercado: float, spot: float, r: float, T: float) -> float:
    """Ganancia al vencimiento = F − S·exp(rT)."""
    return f_mercado - spot * exp(r * T)


def tabla_arbitraje(f_mercado: float, spot: float, r: float, T: float, al_inicio: bool = True) -> pd.DataFrame:
    """Tabla de operaciones (formato del Excel): flujo en Inicio y en Vencimiento.

    La verificación clave: la suma de flujos en la fecha opuesta a la ganancia es 0
    (demuestra que es arbitraje: sin riesgo y sin inversión neta).
    """
    fac = exp(r * T)
    sobrevaluado = f_mercado > spot * fac
    s = 1 if sobrevaluado else -1  # signo: cash-and-carry (+1) o reverse (−1)
    if al_inicio:
        filas = [
            ("Préstamo VP de F" if sobrevaluado else "Depósito VP de F", s * f_mercado / fac, "−F" if s > 0 else "+F"),
            ("Largo spot" if sobrevaluado else "Venta corta spot", -s * spot, "+S_T" if s > 0 else "−S_T"),
            ("Corto forward" if sobrevaluado else "Largo forward", 0.0, "F − S_T" if s > 0 else "S_T − F"),
        ]
        total_inicio = s * (f_mercado / fac - spot)
        total_venc = "0"
    else:
        filas = [
            ("Préstamo S" if sobrevaluado else "Depósito S", s * spot, f"{-s * spot * fac:,.4f}"),
            ("Largo spot" if sobrevaluado else "Venta corta spot", -s * spot, "+S_T" if s > 0 else "−S_T"),
            ("Corto forward" if sobrevaluado else "Largo forward", 0.0, f"{s * f_mercado:,.4f}"),
        ]
        total_inicio = 0.0
        total_venc = f"{s * (f_mercado - spot * fac):,.4f}"
    df = pd.DataFrame(filas, columns=["Operación", "Inicio", "Vencimiento"])
    df.loc[len(df)] = ["Ganancia de arbitraje", total_inicio, total_venc]
    return df


def valor_forward(
    K: float, spot_t: float, r: float, tau: float, posicion: str = "larga", q: float = 0.0, u: float = 0.0
) -> float:
    """Valor de un forward pactado a K, a la fecha t (quedan tau años).

    Larga: V = S_t·exp(−(q−u)·tau) − K·exp(−r·tau) = (F_t − K)·exp(−r·tau)
    Corta: −V.
    (Excel P1b: VF corto = F/exp(r·tau) − S_t.)
    """
    v_larga = spot_t * exp(-(q - u) * tau) - K * exp(-r * tau)
    if posicion == "larga":
        return v_larga
    if posicion == "corta":
        return -v_larga
    raise ValueError("posicion debe ser 'larga' o 'corta'")


def registro_contable(valor: float) -> str:
    """NIIF 9: el derivado se registra según su VALOR (no su payoff): >0 activo, <0 pasivo."""
    return "Activo" if valor > 0 else ("Pasivo" if valor < 0 else "Cero")


@dataclass
class ResultadoCobertura:
    """Resultado de cobertura con forward a un precio final S_T."""

    exposicion: float
    derivado: float

    @property
    def neto(self) -> float:
        return self.exposicion + self.derivado


def payoff_forward(spot_T: float, K: float, cantidad: float, posicion: str) -> float:
    """Payoff al vencimiento: largo (S_T − K)·Q ; corto (K − S_T)·Q."""
    s = 1 if posicion == "larga" else -1
    return s * (spot_T - K) * cantidad
