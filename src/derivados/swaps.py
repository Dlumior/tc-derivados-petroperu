"""Swaps de tasa de interés (IRS) y de monedas (CCS) — valorización por flujos descontados.

Enfoque del curso: un swap es un portafolio de bonos (pata fija − pata variable)
o una serie de forwards. Aquí se usan ambos enfoques para validar.

Curvas: se pasan como función t(años) -> factor de descuento. `curva_plana` crea una
curva con tasa efectiva anual constante; `curva_interpolada` interpola tasas cero.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

Curva = Callable[[float], float]


def curva_plana(r: float, compuesta: str = "efectiva") -> Curva:
    if compuesta == "efectiva":
        return lambda t: (1 + r) ** (-t)
    if compuesta == "continua":
        return lambda t: float(np.exp(-r * t))
    raise ValueError(compuesta)


def curva_interpolada(plazos: Sequence[float], tasas_cero: Sequence[float]) -> Curva:
    """Interpolación lineal de tasas cero efectivas anuales (extrapolación plana)."""
    p, z = np.asarray(plazos, float), np.asarray(tasas_cero, float)
    return lambda t: float((1 + np.interp(t, p, z)) ** (-t))


def bootstrap_par_anual(plazos: Sequence[float], tasas_par: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Tasas cero efectivas desde tasas swap PAR con pago fijo anual (p. ej. SOFR swaps 1a…10a).

    Interpola linealmente las tasas par en la grilla anual 1..N y despeja cada factor:
    DF_n = (1 − c_n·Σ_{i<n} DF_i) / (1 + c_n);  z_n = DF_n^(−1/n) − 1.
    """
    p, c = np.asarray(plazos, float), np.asarray(tasas_par, float)
    grilla = np.arange(1, int(round(p.max())) + 1, dtype=float)
    par = np.interp(grilla, p, c)
    dfs: list[float] = []
    for cn in par:
        dfs.append((1 - cn * sum(dfs)) / (1 + cn))
    return grilla, np.asarray(dfs) ** (-1 / grilla) - 1


# --------------------------------------------------------------------------- cronogramas


def cronograma_cuota_constante(
    saldo: float,
    tasa_anual: float,
    n_cuotas: int,
    freq: int = 12,
    gracia: int = 0,
    convencion: str = "efectiva",
    tipo: str = "frances",
) -> pd.DataFrame:
    """Cronograma del préstamo BN en S/: `gracia` períodos de solo interés y luego `n_cuotas` de amortización.

    convencion: "efectiva" (TEA → (1+TEA)^(1/freq) − 1) o "nominal" (TNA/freq).
    tipo: "frances" (cuota constante) o "lineal" (amortización constante de capital).
    """
    i = (1 + tasa_anual) ** (1 / freq) - 1 if convencion == "efectiva" else tasa_anual / freq
    cuota = saldo * i / (1 - (1 + i) ** -n_cuotas)
    filas, s = [], saldo
    for k in range(1, gracia + n_cuotas + 1):
        interes = s * i
        if k <= gracia:
            amort = 0.0
        else:
            amort = cuota - interes if tipo == "frances" else saldo / n_cuotas
        filas.append(
            {"k": k, "t": k / freq, "saldo_inicial": s, "interes": interes, "amortizacion": amort,
             "cuota": interes + amort}
        )
        s -= amort
    return pd.DataFrame(filas)


def cronograma_bullet(nocional: float, cupon: float, anios: float, freq: int = 2) -> pd.DataFrame:
    n = int(round(anios * freq))
    filas = []
    for k in range(1, n + 1):
        amort = nocional if k == n else 0.0
        filas.append(
            {
                "k": k,
                "t": k / freq,
                "saldo_inicial": nocional,
                "interes": nocional * cupon / freq,
                "amortizacion": amort,
                "cuota": nocional * cupon / freq + amort,
            }
        )
    return pd.DataFrame(filas)


def vp_flujos(cron: pd.DataFrame, curva: Curva) -> float:
    return float(sum(c * curva(t) for c, t in zip(cron["cuota"], cron["t"], strict=True)))


def cronograma_remanente(
    cron: pd.DataFrame, pagadas: int, dias_a_primera: float, freq: int = 12, base: int = 360
) -> pd.DataFrame:
    """Cuotas pendientes tras `pagadas` pagos, con t medido desde la fecha de valorización.

    `base` debe coincidir con la de las curvas (SBS indexa la curva en días/360).
    """
    out = cron.iloc[pagadas:].copy().reset_index(drop=True)
    out["k"] = range(1, len(out) + 1)
    out["t"] = dias_a_primera / base + (out["k"] - 1) / freq
    return out


# --------------------------------------------------------------------------- bonos


def precio_bono(nocional: float, cupon: float, anios: float, y: float, freq: int = 2) -> float:
    """Precio de un bono bullet descontado a su rendimiento `y` (convención de la frecuencia del cupón)."""
    return vp_flujos(cronograma_bullet(nocional, cupon, anios, freq), lambda t: (1 + y / freq) ** (-t * freq))


def rendimiento_cartera(bonos: Sequence[tuple[float, float, float]], valor: float, freq: int = 2) -> float:
    """Rendimiento único y que iguala Σ precio_bono(nocional, cupón, años, y) al `valor` dado (bisección)."""
    lo, hi = -0.05, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        p = sum(precio_bono(n, c, a, mid, freq) for n, c, a in bonos)
        lo, hi = (mid, hi) if p > valor else (lo, mid)
    return (lo + hi) / 2


# --------------------------------------------------------------------------- IRS


@dataclass
class IRS:
    """Swap plain vanilla. pagador=True → paga fija, recibe variable (cubre alza de tasas)."""

    nocional: float
    tasa_fija: float
    anios: float
    freq: int = 2
    pagador: bool = True

    def tasa_par(self, curva: Curva) -> float:
        ts = np.arange(1, int(round(self.anios * self.freq)) + 1) / self.freq
        anualidad = sum(curva(t) for t in ts) / self.freq
        return (1 - curva(ts[-1])) / anualidad

    def valor(self, curva: Curva) -> float:
        """V = ±(B_var − B_fija), con B_var = nocional (en fecha de reseteo)."""
        cron = cronograma_bullet(self.nocional, self.tasa_fija, self.anios, self.freq)
        b_fija = vp_flujos(cron, curva)
        b_var = self.nocional
        v = b_var - b_fija
        return v if self.pagador else -v


def forward_starting_rate(curva: Curva, inicio: float, anios: float, freq: int = 2) -> float:
    """Tasa swap forward (bloquea hoy la tasa de un refinanciamiento que empieza en `inicio`)."""
    ts = inicio + np.arange(1, int(round(anios * freq)) + 1) / freq
    anualidad = sum(curva(t) for t in ts) / freq
    return (curva(inicio) - curva(ts[-1])) / anualidad


# --------------------------------------------------------------------------- CCS


@dataclass
class CrossCurrencySwap:
    """CCS fija-fija PEN/USD sobre un cronograma amortizable.

    Petroperú (moneda funcional USD) con deuda en PEN: RECIBE PEN (réplica de su préstamo)
    y PAGA USD → transforma el pasivo PEN en pasivo USD y elimina la exposición al PEN.
    """

    cron_pen: pd.DataFrame  # cronograma del pasivo en PEN (columnas t, cuota, saldo_inicial)
    spot: float  # PEN por USD
    tasa_usd: float  # tasa fija de la pata USD
    freq: int = 12  # pagos por año (el cronograma puede empezar a una fracción de periodo)

    def cron_usd(self) -> pd.DataFrame:
        """Pata USD con el mismo perfil de amortización, convertida al spot inicial."""
        c = self.cron_pen.copy()
        i = (1 + self.tasa_usd) ** (1 / self.freq) - 1
        c["saldo_inicial"] = c["saldo_inicial"] / self.spot
        c["amortizacion"] = c["amortizacion"] / self.spot
        c["interes"] = c["saldo_inicial"] * i
        c["cuota"] = c["interes"] + c["amortizacion"]
        return c

    def valor_usd(self, curva_pen: Curva, curva_usd: Curva, spot_hoy: float | None = None) -> float:
        """Valor para quien recibe PEN y paga USD, expresado en USD."""
        s = spot_hoy or self.spot
        return vp_flujos(self.cron_pen, curva_pen) / s - vp_flujos(self.cron_usd(), curva_usd)

    def tasa_usd_justa(self, curva_pen: Curva, curva_usd: Curva) -> float:
        """Tasa USD que hace V = 0 al inicio (bisección)."""
        lo, hi = -0.05, 0.40
        for _ in range(200):
            mid = (lo + hi) / 2
            v = CrossCurrencySwap(self.cron_pen, self.spot, mid, self.freq).valor_usd(curva_pen, curva_usd)
            lo, hi = (mid, hi) if v > 0 else (lo, mid)
        return (lo + hi) / 2


def tira_forwards_pen(cron_pen: pd.DataFrame, spot: float, r_pen: float, r_usd: float) -> pd.DataFrame:
    """Alternativa al CCS: un forward (NDF) de compra de PEN por cada cuota (paridad de tasas)."""
    out = cron_pen[["k", "t", "cuota"]].copy()
    out["forward"] = spot * ((1 + r_pen) / (1 + r_usd)) ** out["t"]
    out["usd_fijado"] = out["cuota"] / out["forward"]
    out["usd_al_spot"] = out["cuota"] / spot
    return out
