"""Forwards de tipo de cambio, paridad de tasas, posiciones de cambio y arbitraje.

Replica la lógica de las Preguntas 2, 3 y 4 del Examen Parcial de referencia.

Convenciones (mercado peruano USD/PEN):
- Cotización en PEN por USD. Puntos forward en pips: F = S + puntos/10 000.
- Bid = compra (el banco compra USD), Ask = venta (el banco vende USD).
- Quien COMPRA USD a plazo (forward largo USD) pacta al ASK (venta);
  quien VENDE USD a plazo pacta al BID (compra).
- Tasas efectivas anuales, base 360 días: factor = (1 + r)^(días/360).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Cotizacion:
    bid: float  # compra
    ask: float  # venta

    @property
    def medio(self) -> float:
        return (self.bid + self.ask) / 2


def forward_desde_puntos(spot: float, puntos: float) -> float:
    """F = S + puntos/10 000."""
    return spot + puntos / 10_000


def cotizacion_forward(spot: Cotizacion, puntos: Cotizacion) -> Cotizacion:
    return Cotizacion(forward_desde_puntos(spot.bid, puntos.bid), forward_desde_puntos(spot.ask, puntos.ask))


def precio_pactado(cot: Cotizacion, compra_usd: bool) -> float:
    """El cliente que compra USD paga el ask; el que vende USD recibe el bid."""
    return cot.ask if compra_usd else cot.bid


def forward_paridad(spot: float, r_pen: float, r_usd: float, dias: float, base: int = 360) -> float:
    """Paridad cubierta de tasas: F = S·[(1 + r_PEN)/(1 + r_USD)]^(días/base)."""
    return spot * ((1 + r_pen) / (1 + r_usd)) ** (dias / base)


def diferencial_implicito(forward: float, spot: float, T: float) -> float:
    """Diferencial de tasas implícito anualizado: (F/S)^(1/T) − 1.

    Es el COSTO (o beneficio) de la cobertura por año. T en años.
    """
    return (forward / spot) ** (1 / T) - 1


def tasa_efectiva_desde_simple(r_simple: float, dias: float, base: int = 360) -> float:
    """Convierte una tasa simple (money market, p. ej. SOFR OIS ACT/360) a efectiva anual base `base`.

    (1 + r·d/base) = (1 + r_ef)^(d/base)  ⇒  r_ef = (1 + r·d/base)^(base/d) − 1.
    """
    return (1 + r_simple * dias / base) ** (base / dias) - 1


def tasa_continua_desde_simple(r_simple: float, dias: float, base_simple: int = 360, base_anual: int = 365) -> float:
    """r_c = ln(1 + r·d/base_simple) / (d/base_anual). Para descontar con e^(−r·T), T = d/base_anual."""
    from math import log

    return log(1 + r_simple * dias / base_simple) / (dias / base_anual)


def puntos_desde_tasas(spot: float, r_pen: float, r_usd: float, dias: float, base: int = 360) -> float:
    """Puntos forward teóricos (pips)."""
    return (forward_paridad(spot, r_pen, r_usd, dias, base) - spot) * 10_000


# --------------------------------------------------------------------------- posiciones


@dataclass
class PosicionCambio:
    """PCG = PCC + PND (en USD; + = activa/larga en USD, − = pasiva/corta en USD).

    PCC: posición de cambio contable (AME − PME del balance).
    PND: posición neta en derivados (forwards compra − forwards venta).
    PCG: posición de cambio global = exposición efectiva al tipo de cambio.
    """

    pcc: float
    pnd: float = 0.0

    @property
    def pcg(self) -> float:
        return self.pcc + self.pnd

    def riesgo(self) -> str:
        if self.pcg > 0:
            return "Largo USD: pierde si el PEN se aprecia (TC baja)"
        if self.pcg < 0:
            return "Corto USD: pierde si el PEN se deprecia (TC sube)"
        return "Cubierto: resultado no depende del TC"

    def tabla(self, variacion_pcc: float = 0.0, variacion_pnd: float = 0.0) -> pd.DataFrame:
        ini = [self.pcc, self.pnd, self.pcg]
        var = [variacion_pcc, variacion_pnd, variacion_pcc + variacion_pnd]
        fin = [a + b for a, b in zip(ini, var, strict=True)]
        return pd.DataFrame({"Inicial": ini, "Variación": var, "Final": fin}, index=["PCC", "PND", "PCG"])


def resultados_cobertura_pasivo_usd(
    nocional_usd: float, spot0: float, f_pactado: float, fixings: dict[str, float]
) -> pd.DataFrame:
    """Cuenta por pagar en USD (empresa con moneda funcional PEN) cubierta con forward largo USD.

    Pasivo: (S0 − S_T)·N   | Forward largo: (S_T − F)·N   | Neto: (S0 − F)·N (constante).
    """
    filas = {}
    for nombre, st in fixings.items():
        exp_ = (spot0 - st) * nocional_usd
        der = (st - f_pactado) * nocional_usd
        filas[nombre] = {"TC fixing": st, "Exposición": exp_, "Forward": der, "Neto": exp_ + der}
    df = pd.DataFrame(filas)
    df.loc["Neto (alterno) (S0−F)·N"] = (spot0 - f_pactado) * nocional_usd
    return df


def resultados_ndf_pasivo_pen(
    nocional_pen: float, spot0: float, f_pactado: float, fixings: dict[str, float]
) -> pd.DataFrame:
    """Pasivo en PEN de una empresa con moneda funcional USD, cubierto con NDF de COMPRA de PEN (venta de USD).

    Resultados en USD (+ = ganancia):
    Pasivo: N/S0 − N/S_T | NDF: N/S_T − N/F | Neto: N/S0 − N/F (constante: costo o beneficio de la cobertura).
    """
    filas = {}
    for nombre, st in fixings.items():
        exp_ = nocional_pen / spot0 - nocional_pen / st
        der = nocional_pen / st - nocional_pen / f_pactado
        filas[nombre] = {"TC fixing": st, "Exposición": exp_, "NDF": der, "Neto": exp_ + der}
    df = pd.DataFrame(filas)
    df.loc["Neto (alterno) N(1/S0−1/F)"] = nocional_pen / spot0 - nocional_pen / f_pactado
    return df


# --------------------------------------------------------------------------- depósito sintético


@dataclass
class DepositoSintetico:
    """Depósito sintético en USD: venta spot USD + depósito PEN + compra forward USD.

    Excel P4. Conviene si la tasa implícita supera la tasa pasiva directa en USD.
    """

    monto_usd: float
    dias: int
    spot: Cotizacion
    fwd: Cotizacion
    r_usd: float
    r_pen: float
    base: int = 360

    def _fac(self, r: float) -> float:
        return (1 + r) ** (self.dias / self.base)

    @property
    def usd_final_directo(self) -> float:
        return self.monto_usd * self._fac(self.r_usd)

    @property
    def pen_iniciales(self) -> float:
        return self.monto_usd * self.spot.bid  # vende USD al bid

    @property
    def pen_finales(self) -> float:
        return self.pen_iniciales * self._fac(self.r_pen)

    @property
    def usd_final_sintetico(self) -> float:
        return self.pen_finales / self.fwd.ask  # compra USD a plazo al ask

    @property
    def tasa_sintetica(self) -> float:
        return (self.usd_final_sintetico / self.monto_usd) ** (self.base / self.dias) - 1

    @property
    def tasa_implicita_directa(self) -> float:
        return (self.spot.bid / self.fwd.ask) ** (self.base / self.dias) * (1 + self.r_pen) - 1

    def conviene(self) -> bool:
        return self.tasa_sintetica > self.r_usd

    def tabla_flujos(self) -> pd.DataFrame:
        pen0, pen_t, usd_t = self.pen_iniciales, self.pen_finales, self.usd_final_sintetico
        return pd.DataFrame(
            [
                ["1) Vende USD spot", -self.monto_usd, pen0, 0.0, 0.0],
                ["2) Depósito PEN", 0.0, -pen0, 0.0, pen_t],
                ["3) Compra forward USD", 0.0, 0.0, usd_t, -pen_t],
                ["Flujos netos", -self.monto_usd, 0.0, usd_t, 0.0],
            ],
            columns=["Operación", "Hoy USD", "Hoy PEN", "Venc. USD", "Venc. PEN"],
        )
