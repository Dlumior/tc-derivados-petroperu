"""Pipeline único: insumos (YAML/CSV) → cálculos → informe/generado/{valores.tex, tablas/, figuras/}.

Uso:  python scripts/run_all.py          (o `make calc`)

Exposiciones: EEFF auditados al 31-dic-2025. Mercado: fecha de valorización 28-sep-2026.
Estrategias:
  E1  Riesgo cambiario (pasivo neto en S/): CCS amortizable recibe S/ – paga US$ sobre el préstamo BN
      + NDF de compra de S/ a 3 meses sobre el resto de la posición.
  E2  Riesgo de precio del crudo (inventario): swap de WTI a precio promedio vs. collar de costo cero
      (instrumentos OTC, sin márgenes diarios de bolsa).
  Tasa (no recomendada hoy): tasa de un swap de inicio diferido para la refinanciación del CESCE.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt  # noqa: E402

from derivados import cobertura, datos, fx, opciones, riesgo, swaps  # noqa: E402
from derivados import forwards as fw  # noqa: E402
from derivados.reporte import Macros, estilo_figuras, guardar_figura, tabla_latex  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
MERCADO = RAIZ / "data" / "mercado"

EEFF = "\\textcite{petroperu2026eeff}"  # mismo autor que la bibliografía (APA 7)
BCRP = "BCRP, series estadísticas"
SBS = "SBS, curva cupón cero soberana en soles (28-sep-2026)"
SOFR = "BlueGamma, swaps SOFR (28-sep-2026)"
NYMEX = "NYMEX CL vía Yahoo Finance; CBOE OVX vía FRED (28-sep-2026)"

AZUL, NARANJA, VERDE, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#888888"


def serie(nombre: str) -> pd.Series:
    df = pd.read_csv(MERCADO / f"{nombre}.csv")
    return pd.Series(df.iloc[:, 1].to_numpy(float), index=df.iloc[:, 0].astype(str))


def curva_sbs(archivo: str) -> swaps.Curva:
    """Curva cupón cero SBS (plazo en días, año de 360 días; tasa efectiva anual en %)."""
    df = pd.read_csv(MERCADO / archivo)
    return swaps.curva_interpolada(df["plazo_dias"] / 360, df["tasa_pct"] / 100)


def curva_sofr(mk: dict) -> swaps.Curva:
    """Curva cero US$: 3M SOFR OIS (simple ACT/360 → efectiva) + bootstrap de los swaps SOFR par anuales."""
    w = lambda k: mk[k].valor  # noqa: E731
    plazos = (1, 2, 3, 4, 5, 7, 10)
    grilla, ceros = swaps.bootstrap_par_anual(plazos, [w(f"tasas.usd_{p}a") for p in plazos])
    r3m = fx.tasa_efectiva_desde_simple(w("tasas.usd_3m"), 91)
    return swaps.curva_interpolada([91 / 360, *grilla], [r3m, *ceros])


# =========================================================================== contexto y riesgos


def contexto(ex: dict, mk: dict, m: Macros) -> None:
    v = lambda k: ex[k].valor  # noqa: E731
    mm = lambda k: v(k) / 1e3  # noqa: E731  US$000 → US$ millones

    m.set("IngresosVeinticinco", mm("empresa.ingresos_2025"), 1)
    m.set("IngresosVeinticuatro", mm("empresa.ingresos_2024"), 1)
    m.set("PerdidaVeinticinco", mm("empresa.perdida_neta_2025"), 1)
    m.set("PerdidaVeinticuatro", mm("empresa.perdida_neta_2024"), 1)
    m.set("CapTrabajoVeinticinco", mm("empresa.capital_trabajo_negativo"), 1)
    m.set("UtilidadBruta", mm("empresa.utilidad_bruta_2025"), 1)
    m.set("PerdidaVeinticincoAbs", abs(mm("empresa.perdida_neta_2025")), 1)
    m.set("FEPCpct", abs(v("empresa.fepc_pct_ingresos")), 2, pct=True)  # aporte neto (signo en el texto)

    tabla = pd.DataFrame(
        {
            "2024": [
                mm("empresa.ingresos_2024"),
                mm("empresa.perdida_neta_2024"),
                mm("empresa.capital_trabajo_negativo_2024"),
                mm("deuda.otros_pasivos_financieros_2024"),
                f'{v("empresa.apalancamiento_2024"):.2f}',
            ],
            "2025": [
                mm("empresa.ingresos_2025"),
                mm("empresa.perdida_neta_2025"),
                mm("empresa.capital_trabajo_negativo"),
                mm("deuda.otros_pasivos_financieros"),
                f'{v("empresa.apalancamiento_2025"):.2f}',
            ],
            "Comentario": [
                "Menor precio del crudo",
                "Pérdida menor que en 2024",
                "Pasivo corriente > activo corriente",
                "Tasa fija; las líneas se reprecian al renovar",
                "Mayor apalancamiento",
            ],
        },
        index=[
            "Ingresos de actividades ordinarias",
            "Resultado neto",
            "Capital de trabajo",
            "Otros pasivos financieros",
            "Deuda neta / capital total",
        ],
    )
    tabla_latex(
        tabla,
        "t_indicadores",
        "Indicadores financieros de PETROPERÚ (US\\$ millones)",
        f"{EEFF}, Notas 1, 3, 5 y 14",
        "tab:indicadores",
        decimales={"2024": 1, "2025": 1},
    )


def riesgo_cambiario(ex: dict, m: Macros) -> None:
    v = lambda k: ex[k].valor  # noqa: E731
    tc = 1 / v("fx.tc_cierre_usd_por_pen")
    pen = v("fx.pen_neto")

    m.set("TCcierre", tc, 3)
    m.set("PenNeto", pen / 1e3, 1)
    m.set("PenNetoAbs", abs(pen) / 1e3, 1)
    m.set("PenNetoUSD", abs(pen) / tc / 1e3, 0)
    m.set("PenNetoVeinticuatro", abs(v("fx.pen_neto_2024")) / 1e3, 1)
    m.set("PenNetoCrec", pen / v("fx.pen_neto_2024") - 1, 0, pct=True)
    m.set("PenOtrosPasFin", abs(v("fx.pen_otros_pasivos_financieros")) / 1e3, 1)
    m.set("EurNeto", v("fx.eur_neto") / 1e3, 1)
    m.set("JpyNeto", abs(v("fx.jpy_neto")) / 1e3, 1)
    m.set("SensibilidadFX", v("fx.sensibilidad_10pct") / 1e3, 1)
    m.set("DifCambioBN", v("fx.dif_cambio_prestamo_bn") / 1e3, 1)
    m.set("GananciaDifCambio", v("fx.ganancia_dif_cambio_2025") / 1e3, 1)
    m.set("SwapCiti", v("fx.swap_citibank_activo") / 1e3, 1)
    m.set("SwapCitiJunio", v("fx.swap_citibank_activo_jun26") / 1e3, 1)

    # Variación del TC en 2025 con cierres BCRP (interbancario medio)
    tc_mid = (serie("usdpen_interbancario_compra") + serie("usdpen_interbancario_venta")) / 2
    tc24, tc25 = tc_mid.loc[:"2024-12-31"].iloc[-1], tc_mid.loc[:"2025-12-31"].iloc[-1]
    m.set("TCcierreBCRPVeinticuatro", tc24, 3)
    m.set("TCcierreBCRPVeinticinco", tc25, 3)
    m.set("TCvarVeinticinco", tc25 / tc24 - 1, 1, pct=True)

    # Sensibilidad propia: ±10 % del TC sobre la posición neta (US$ millones)
    perdida = abs(pen) / (tc * 0.9) - abs(pen) / tc
    ganancia = abs(pen) / tc - abs(pen) / (tc * 1.1)
    m.set("SensApreciacion", perdida / 1e3, 1)
    m.set("ApreciacionSolDiez", 1 / 0.9 - 1, 1, pct=True)
    m.set("SensDepreciacion", ganancia / 1e3, 1)
    # Escala de decisión: pérdida por cada 1 % que baja el TC (US$ millones)
    m.set("SensFXUnPct", (abs(pen) / (tc * 0.99) - abs(pen) / tc) / 1e3, 1)

    # Figura: composición de la posición en S/
    partidas = {
        "Efectivo": v("fx.pen_efectivo"),
        "CxC comerciales": v("fx.pen_cxc_comerciales"),
        "Otras CxC": v("fx.pen_otras_cxc"),
        "Otros pasivos financieros": v("fx.pen_otros_pasivos_financieros"),
        "CxP comerciales": v("fx.pen_cxp_comerciales"),
        "CxP parte relacionada": v("fx.pen_cxp_relacionada"),
        "Otras CxP": v("fx.pen_otras_cxp"),
        "Arrendamientos": v("fx.pen_arrendamientos"),
    }
    fig, ax = plt.subplots(figsize=(6.2, 2.4))
    nombres, valores = list(partidas)[::-1], [x / 1e3 for x in list(partidas.values())[::-1]]
    ax.barh(nombres, valores, color=[VERDE if x > 0 else NARANJA for x in valores], height=0.65)
    for i, x in enumerate(valores):
        ax.text(x + (40 if x > 0 else -40), i, f"{x:,.1f}", va="center", ha="left" if x > 0 else "right", fontsize=8)
    ax.axvline(0, color=GRIS, lw=0.8)
    ax.set_xlim(-4700, 1100)
    ax.set_xlabel("S/ millones (activos +, pasivos −)")
    ax.grid(axis="y", visible=False)
    guardar_figura(fig, "f_posicion_pen")


def historia_mercado(mk: dict, m: Macros) -> None:
    df = pd.read_csv(MERCADO / "bcrp_mensual_tc_wti.csv")
    ret_tc = np.diff(np.log(df["tc_bancario_promedio"]))
    ret_wti = np.diff(np.log(df["wti_promedio"]))
    m.set("VolHistTC", ret_tc.std(ddof=1) * np.sqrt(12), 1, pct=True)
    m.set("VolHistWTI", ret_wti.std(ddof=1) * np.sqrt(12), 1, pct=True)
    m.set("HistDesde", "ene-2021")
    m.set("HistHasta", "ago-2026")

    x = pd.to_datetime(df["fecha"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.3))
    a1.plot(x, df["tc_bancario_promedio"], color=AZUL)
    a1.set_title("Tipo de cambio (S/ por US\\$)", fontsize=8, loc="left")
    a2.plot(x, df["wti_promedio"], color=NARANJA)
    a2.set_title("Petróleo WTI (US\\$ por barril)", fontsize=8, loc="left")
    for a in (a1, a2):
        a.axvspan(pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31"), color=GRIS, alpha=0.12, lw=0)
        a.tick_params(labelsize=7)
    a1.annotate("EEFF 2025", (pd.Timestamp("2025-02-01"), a1.get_ylim()[1]), fontsize=6.5, va="top", color=GRIS)
    guardar_figura(fig, "f_historia")


def riesgo_crudo(ex: dict, mk: dict, m: Macros) -> None:
    v = lambda k: ex[k].valor  # noqa: E731
    inv = v("crudo.inventario_crudo_mbl") * 1e3
    m.set("InvCrudoMbl", v("crudo.inventario_crudo_mbl"), 0)
    m.set("InvCrudoMMbl", inv / 1e6, 3)
    # Escala de decisión: US$ millones por cada US$ 1/bl que cae el WTI
    m.set("SensWTIUnDolar", inv / 1e6, 1)
    m.set("InvCrudoUSD", v("crudo.inventario_crudo_usd") / 1e3, 1)
    m.set("InvRefinadosUSD", v("crudo.inventario_refinados_usd") / 1e3, 1)
    m.set("InvHidroUSD", v("crudo.inventario_hidrocarburos_usd") / 1e3, 1)
    # Margen (crack): el inventario de productos queda fuera de E2 y pierde valor si cae el precio de los productos
    m.set("PerdidaInvProdDiez", 0.10 * v("crudo.inventario_refinados_usd") / 1e3, 1)
    m.set("WTIcierreVeinticinco", v("crudo.wti_cierre_2025"), 2)
    m.set("WTIcierreVeinticuatro", v("crudo.wti_cierre_2024"), 2)
    m.set("WTIvarVeinticinco", v("crudo.wti_cierre_2025") / v("crudo.wti_cierre_2024") - 1, 1, pct=True)
    m.set("WTICaidaVeinticinco", 1 - v("crudo.wti_cierre_2025") / v("crudo.wti_cierre_2024"), 1, pct=True)
    m.set("ComprasUSD", v("crudo.compras_usd") / 1e3, 1)
    m.set("ComprasMBDC", v("crudo.compras_mbdc"), 0)
    m.set("PrecioCompras", v("crudo.precio_prom_compras"), 2)
    perd20 = inv * v("crudo.wti_cierre_2025") * 0.20 / 1e6
    m.set("PerdidaInvVeinte", perd20, 1)
    m.set("PerdidaInvVeinteHoy", inv * mk["crudo.wti_spot"].valor * 0.20 / 1e6, 1)  # mismo volumen al WTI de hoy
    m.set("PerdidaInvVeinteXUB", perd20 / (v("empresa.utilidad_bruta_2025") / 1e3), 1)
    # Revaluación del inventario de crudo del cierre 2025 a precios de la fecha de valorización
    m.set("GananciaInvHoy", inv * (mk["crudo.wti_spot"].valor - v("crudo.wti_cierre_2025")) / 1e6, 1)


def riesgo_tasa(ex: dict, m: Macros) -> float:
    """Riesgo de tasa de los bonos; devuelve el spread de crédito implícito (base del CVA de E1)."""
    v = lambda k: ex[k].valor  # noqa: E731
    bonos = [
        (v("deuda.bonos_2032"), v("deuda.bonos_2032_cupon"), v("deuda.bonos_2032_anios_dic25")),
        (v("deuda.bonos_2047"), v("deuda.bonos_2047_cupon"), v("deuda.bonos_2047_anios_dic25")),
    ]
    vr = v("deuda.bonos_valor_razonable")
    y = swaps.rendimiento_cartera(bonos, vr)
    precio = lambda r: sum(swaps.precio_bono(n, c, a, r) for n, c, a in bonos)  # noqa: E731
    dv100 = (precio(y - 0.005) - precio(y + 0.005)) / 1e3
    dur_mod = dv100 * 1e3 / vr / 0.01
    ust7, ust10 = serie("ust_7a").loc[:"2025-12-31"].iloc[-1], serie("ust_10a").loc[:"2025-12-31"].iloc[-1]
    ust_dur = np.interp(dur_mod, [7, 10], [ust7, ust10]) / 100
    m.set("BonosLibros", v("deuda.bonos_libros_total") / 1e3, 1)
    m.set("BonosLibrosNotaA", (v("deuda.libros_bonos_2032") + v("deuda.libros_bonos_2047")) / 1e3, 1)
    m.set("CESCELibros", v("deuda.libros_cesce") / 1e3, 1)
    m.set("BonosVR", vr / 1e3, 1)
    m.set("YTMBonos", y, 1, pct=True)
    m.set("BonosDVCien", dv100, 0)
    m.set("BonosDurMod", dur_mod, 1)
    m.set("USTDurDic", ust_dur, 2, pct=True)
    m.set("SpreadBonosPb", (y - ust_dur) * 1e4, 0)
    m.set("CuponTreintaDos", v("deuda.bonos_2032_cupon"), 3, pct=True)
    m.set("CuponCuarentaSiete", v("deuda.bonos_2047_cupon"), 3, pct=True)
    m.set("BonosNominal", (v("deuda.bonos_2032") + v("deuda.bonos_2047")) / 1e3, 0)
    m.set("CESCESaldo", v("deuda.cesce") / 1e3, 1)
    m.set("CESCETasa", v("deuda.cesce_tasa"), 3, pct=True)
    m.set("LineasRev", v("deuda.lineas_revolventes") / 1e3, 1)
    m.set("LineasUsadas", v("deuda.lineas_utilizadas") / 1e3, 1)
    m.set("LineasPct", v("deuda.lineas_utilizadas") / v("deuda.lineas_revolventes"), 0, pct=True)
    m.set("VencMenosUnAnio", v("liquidez.venc_menos_1a_2025") / 1e3, 1)

    deuda = {
        "Bonos 2047 (5.625% fijo)": (v("deuda.libros_bonos_2047"), AZUL),
        "Bonos 2032 (4.750% fijo)": (v("deuda.libros_bonos_2032"), AZUL),
        "Préstamo BN en S/ (5.55% fijo, 2028)": (v("deuda.libros_prestamo_bn"), NARANJA),
        "Préstamo CESCE (3.285% fijo, 2030)": (v("deuda.libros_cesce"), AZUL),
        "Bancarios corto plazo S/ y US$": (v("deuda.libros_bancarios_cp"), NARANJA),
        "Parte relacionada MEF": (v("deuda.parte_relacionada_mef"), VERDE),
    }
    m.set("DeudaTotal", sum(x for x, _ in deuda.values()) / 1e3, 1)
    fig, ax = plt.subplots(figsize=(6.2, 2.2))
    nombres = list(deuda)[::-1]
    vals = [deuda[k][0] / 1e3 for k in nombres]
    ax.barh(nombres, vals, color=[deuda[k][1] for k in nombres], height=0.6)
    for i, x in enumerate(vals):
        ax.text(x + 25, i, f"{x:,.0f}", va="center", fontsize=8)
    ax.set_xlim(0, 2500)
    ax.set_xlabel("US\\$ millones (valor en libros)")
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch

    ax.legend(
        [Patch(color=c) for c in (AZUL, NARANJA, VERDE)],
        ["Mercado internacional US\\$", "Bancos (S/ y US\\$)", "Estado (MEF)"],
        fontsize=8,
        loc="lower right",
    )
    guardar_figura(fig, "f_deuda")
    return float(y - ust_dur)


# =========================================================================== E1: CCS + NDF


def e1_cambiario(ex: dict, mk: dict, m: Macros, spread: float) -> dict:
    v = lambda k: ex[k].valor  # noqa: E731
    w = lambda k: mk[k].valor  # noqa: E731
    bid, ask = w("usdpen.spot_bid"), w("usdpen.spot_ask")
    s0 = (bid + ask) / 2
    m.set("SpotBid", bid, 4)
    m.set("SpotAsk", ask, 4)
    m.set("SpotUSDPEN", s0, 4)

    # Partida cubierta: préstamo BN. EEFF jun-2026: sin amortización y saldo íntegro no corriente ⇒ solo intereses
    # hasta jun-2027 y 18 cuotas francesas (TEA) jul-2027 a dic-2028 (supuesto compatible con la NIC 1)
    gracia, n_amort = int(v("prestamo_bn.meses_solo_interes_desde_ene26")), int(v("prestamo_bn.cuotas_amortizacion"))
    cron = swaps.cronograma_cuota_constante(v("prestamo_bn.saldo_pen"), v("prestamo_bn.tasa"), n_amort, gracia=gracia)
    pagadas = int(v("prestamo_bn.cuotas_pagadas_a_valorizacion"))
    rem = swaps.cronograma_remanente(cron, pagadas, v("prestamo_bn.dias_a_primera_cuota"))
    saldo_rem = rem["saldo_inicial"].iloc[0]
    m.set("BNSaldoPEN", v("prestamo_bn.saldo_pen") / 1e3, 1)
    m.set("BNSaldoUSD", v("prestamo_bn.saldo_usd") / 1e3, 1)
    m.set("BNTasa", v("prestamo_bn.tasa"), 2, pct=True)
    m.set("BNCuotasTot", int(v("prestamo_bn.cuotas_totales")), 0)
    m.set("BNMesesGracia", gracia, 0)
    m.set("BNCuotasAmort", n_amort, 0)
    m.set("BNSaldoJunio", v("prestamo_bn.saldo_pen_jun26") / 1e3, 1)
    m.set("BNCuotasPagadas", pagadas, 0)
    m.set("BNCuotasRem", len(rem), 0)
    m.set("BNCuota", rem["cuota"].iloc[0] / 1e3, 1)  # cuota de solo interés (oct-2026)
    m.set("BNCuotaAmort", rem["cuota"].iloc[-1] / 1e3, 1)  # cuota francesa desde jul-2027
    m.set("BNSaldoRem", saldo_rem / 1e3, 1)

    # Curvas a la fecha de valorización
    c_pen = curva_sbs("sbs_curva_CCPSS_2026-09-28.csv")
    c_usd = curva_sofr(mk)
    m.set("PENUnAnio", w("tasas.pen_1a"), 2, pct=True)
    m.set("PENDosAnios", c_pen(2.0) ** (-1 / 2.0) - 1, 2, pct=True)
    m.set("PENTresAnios", w("tasas.pen_3a"), 2, pct=True)
    m.set("USDUnAnio", w("tasas.usd_1a"), 2, pct=True)
    m.set("USDDosAnios", w("tasas.usd_2a"), 2, pct=True)
    m.set("USDTresAnios", w("tasas.usd_3a"), 2, pct=True)

    # PETROPERÚ vende US$ (paga US$, recibe S/) → cotización de compra (bid) del banco
    ccs = swaps.CrossCurrencySwap(rem, bid, 0.0)
    t_usd = ccs.tasa_usd_justa(c_pen, c_usd)
    ccs = swaps.CrossCurrencySwap(rem, bid, t_usd)
    pata_usd = ccs.cron_usd()
    vp_pen_usd = swaps.vp_flujos(rem, c_pen) / bid
    m.set("CCSTasaUSD", t_usd, 2, pct=True)
    m.set("CCSNocionalUSD", saldo_rem / bid / 1e3, 1)
    m.set("CCSVPPataPEN", vp_pen_usd / 1e3, 1)
    m.set("CCSCuotaUSD", pata_usd["cuota"].iloc[0] / 1e3, 1)
    m.set("CCSTotalUSD", pata_usd["cuota"].sum() / 1e3, 1)
    m.set("CCSVsBN", (t_usd - v("prestamo_bn.tasa")) * 1e4, 0)

    # C1: sensibilidad al cronograma del BN (el EEFF no lo detalla: 46 cuotas entre ene-2025 y dic-2028)
    dias1 = v("prestamo_bn.dias_a_primera_cuota")
    alternativos = {
        "base": {"gracia": gracia},
        "nominal": {"gracia": gracia, "convencion": "nominal"},  # TNA/12 en lugar de TEA
        "lineal": {"gracia": gracia, "tipo": "lineal"},  # amortización constante de capital
        "solo 2028": {"gracia": gracia + 6, "n_cuotas": n_amort - 6},  # 12 cuotas en 2028
    }
    sens = {}
    for nombre, kw in alternativos.items():
        n = kw.pop("n_cuotas", n_amort)
        r_alt = swaps.cronograma_remanente(
            swaps.cronograma_cuota_constante(v("prestamo_bn.saldo_pen"), v("prestamo_bn.tasa"), n, **kw), pagadas, dias1
        )
        tasa_alt = swaps.CrossCurrencySwap(r_alt, bid, 0.0).tasa_usd_justa(c_pen, c_usd)
        sens[nombre] = (tasa_alt, r_alt["saldo_inicial"].iloc[0] / bid / 1e3, r_alt["cuota"].iloc[0] / 1e3)
    tasas_alt = [x[0] for x in sens.values()]
    nocionales_alt = [x[1] for x in sens.values()]
    m.set("CCSTasaMin", min(tasas_alt), 2, pct=True)
    m.set("CCSTasaMax", max(tasas_alt), 2, pct=True)
    m.set("CCSNocionalMin", min(nocionales_alt), 1)
    m.set("CCSNocionalMax", max(nocionales_alt), 1)
    m.set("BNCuotaNominal", swaps.cronograma_cuota_constante(
        v("prestamo_bn.saldo_pen"), v("prestamo_bn.tasa"), n_amort, gracia=gracia, convencion="nominal")["cuota"].iloc[-1] / 1e3, 1)

    # C3: CVA que el banco cargaría por el riesgo de crédito de PETROPERÚ (EPE analítica, Hull cap. 24)
    cva = riesgo.cva_ccs(rem, pata_usd, bid, c_pen, c_usd, w("usdpen.vol_implicita_1a"), spread, w("credito.lgd"))
    m.set("CCSCVApb", cva["pb"], 0)
    m.set("CCSCVAUSD", cva["cva"] / 1e3, 1)
    m.set("CCSEPEMax", cva["epe_max"] / 1e3, 1)
    m.set("CCSTasaAllIn", t_usd + cva["pb"] / 1e4, 2, pct=True)
    # Sensibilidad: spread proxy de ago-2026 (bono 2032 a 86.8, ver mercado.yaml)
    cva_proxy = riesgo.cva_ccs(rem, pata_usd, bid, c_pen, c_usd, w("usdpen.vol_implicita_1a"),
                               w("tasas.spread_credito_petroperu"), w("credito.lgd"))
    m.set("CCSCVApbProxy", cva_proxy["pb"], 0)
    m.set("SpreadProxyPb", w("tasas.spread_credito_petroperu") * 1e4, 0)
    m.set("CCSTasaAllInProxy", t_usd + cva_proxy["pb"] / 1e4, 2, pct=True)  # tasa all-in con el spread de ago-2026
    m.set("CCSDifSpreadPb", cva["pb"] - cva_proxy["pb"], 0)  # diferencia de tasa entre ambos spreads
    m.set("YTMBonoAgo", w("tasas.ytm_bono2032_agosto"), 1, pct=True)
    m.set("LGD", w("credito.lgd"), 0, pct=True)
    m.set("VolTC", w("usdpen.vol_implicita_1a"), 2, pct=True)

    # Flujos anuales del CCS (S/ y US$ millones)
    fechas = pd.date_range("2026-10-01", periods=len(rem), freq="MS") + pd.Timedelta(days=14)
    anio = fechas.year.to_numpy()
    filas = {}
    for a in sorted(set(anio)):
        sel = anio == a
        filas[str(a)] = {
            "Recibe S/": rem.loc[sel, "cuota"].sum() / 1e3,
            "Interés S/": rem.loc[sel, "interes"].sum() / 1e3,
            "Paga US\\$": pata_usd.loc[sel, "cuota"].sum() / 1e3,
            "Interés US\\$": pata_usd.loc[sel, "interes"].sum() / 1e3,
        }
    filas["Total"] = {
        "Recibe S/": rem["cuota"].sum() / 1e3,
        "Interés S/": rem["interes"].sum() / 1e3,
        "Paga US\\$": pata_usd["cuota"].sum() / 1e3,
        "Interés US\\$": pata_usd["interes"].sum() / 1e3,
    }
    m.set("CCSTotalPEN", filas["Total"]["Recibe S/"], 1)
    m.set("CCSIntPEN", filas["Total"]["Interés S/"], 1)
    m.set("CCSIntUSD", filas["Total"]["Interés US\\$"], 1)
    tabla_latex(
        pd.DataFrame(filas).T,
        "t_e1_flujos",
        "E1: Flujos del CCS por año calendario (millones)",
        f"{EEFF}, Nota 14(ii); {SBS}; {SOFR}",
        "tab:e1-flujos",
        decimales=1,
        nota="La pata en S/ replica el servicio de deuda al BN; PETROPERÚ solo desembolsa la pata en US\\$.",
    )

    # NDF sobre el resto de la posición en S/ (partidas distintas del préstamo BN)
    resto = abs(v("fx.pen_neto")) - v("prestamo_bn.saldo_pen")  # S/000 al cierre 2025 (se supone estable)
    ndf_nocional = resto * v("cobertura_fx.ndf_pct_residual")
    dias = v("cobertura_fx.ndf_dias")
    r_pen_3m = float(np.interp(dias, *pd.read_csv(MERCADO / "sbs_curva_CCPSS_2026-09-28.csv").to_numpy().T) / 100)
    # SOFR 3M OIS es tasa simple ACT/360 → efectiva base 360 para la paridad
    r_usd_3m = fx.tasa_efectiva_desde_simple(w("tasas.usd_3m"), dias)
    f_ndf = fx.forward_paridad(bid, r_pen_3m, r_usd_3m, dias)  # vende US$ → cotización compra (bid)
    m.set("RestoPEN", resto / 1e3, 1)
    m.set("NDFNocional", ndf_nocional / 1e3, 1)
    m.set("NDFPct", v("cobertura_fx.ndf_pct_residual"), 0, pct=True)
    m.set("NDFDias", int(dias), 0)
    m.set("PENTresMeses", r_pen_3m, 2, pct=True)
    m.set("USDTresMesesSimple", w("tasas.usd_3m"), 2, pct=True)
    m.set("USDTresMeses", r_usd_3m, 2, pct=True)
    m.set("NDFForward", f_ndf, 4)
    m.set("NDFPuntos", (f_ndf - bid) * 1e4, 1)
    m.set("NDFPuntosAbs", abs(f_ndf - bid) * 1e4, 1)  # prosa: "x pips bajo el spot"
    # M1: conciliación con el mercado local. La curva sintética US$ de la SBS (CSBCRD) es la tasa US$ implícita en los
    # forwards USD/PEN locales: el único proxy público del basis cross-currency.
    c_sint = curva_sbs("sbs_curva_CSBCRD_2026-09-28.csv")
    r_sint_3m = float(np.interp(dias, *pd.read_csv(MERCADO / "sbs_curva_CSBCRD_2026-09-28.csv").to_numpy().T) / 100)
    f_sbs = fx.forward_paridad(bid, r_pen_3m, r_sint_3m, dias)
    m.set("NDFForwardSBS", f_sbs, 4)
    m.set("NDFDifSBSPips", abs(f_sbs - f_ndf) * 1e4, 1)
    m.set("CCSTasaSBS", swaps.CrossCurrencySwap(rem, bid, 0.0).tasa_usd_justa(c_pen, c_sint), 2, pct=True)
    # (F/S)^(360/d) − 1 < 0: comprar S/ a plazo cuesta (F < S), mismo origen que el costo del CCS
    m.set("NDFCostoAnual", -fx.diferencial_implicito(f_ndf, bid, dias / 360), 2, pct=True)
    m.set("NDFCostoUSD", ndf_nocional / f_ndf / 1e3 - ndf_nocional / bid / 1e3, 2)  # costo (> 0)

    # Tabla de resultados al vencimiento del NDF (patrón Inicio/Vencimiento: neto constante)
    fix = {f"TC {p:+.0%}".replace("%", "\\%") if p else "TC sin cambio": bid * (1 + p) for p in (-0.10, 0.0, 0.10)}
    t_ndf = fx.resultados_ndf_pasivo_pen(ndf_nocional / 1e3, bid, f_ndf, fix)
    t_ndf.loc["NDF por S/ 1,000 (US\\$)"] = [1e3 * (1 / x - 1 / f_ndf) for x in fix.values()]
    t_ndf = t_ndf.drop(index=["TC fixing", "Neto (alterno) N(1/S0−1/F)"])
    t_ndf.index = ["Cuentas por pagar en S/", "NDF: N(1/S − 1/F)", "Total", "NDF por S/ 1,000 (US\\$)"]
    t_ndf.insert(0, "Inicio", 0.0)
    m.set("NDFPorMilMenosDiez", 1e3 * (1 / (bid * 0.9) - 1 / f_ndf), 2)
    tabla_latex(
        t_ndf,
        "t_e1_ndf",
        f"E1: NDF a {int(dias)} días, resultado al vencimiento (US\\$ MM)",
        f"{EEFF}, Nota 3; {SBS}; {SOFR}",
        "tab:e1-ndf",
        decimales=2,
        nota=f"TC compra (al que PETROPERÚ pacta); S de liquidación: {bid * 0.9:.3f} / {bid:.3f} / {bid * 1.1:.3f}. Inicio: valor cero, sin flujo. Total constante = N(1/S0 − 1/F).",
        flotante=False,
    )

    # Escenarios de TC sobre la posición a la fecha de valorización (US$ millones)
    pos = saldo_rem + resto
    residuo_ccs = resto
    residuo_total = resto - ndf_nocional
    m.set("PosicionHoy", pos / 1e3, 1)
    m.set("ResiduoTotal", residuo_total / 1e3, 1)
    m.set("CoberturaFX", 1 - residuo_total / pos, 0, pct=True)

    def resultado(pasivo_pen: float, s: float) -> float:
        return (pasivo_pen / s0 - pasivo_pen / s) / 1e3

    shocks = (-0.10, -0.05, 0.0, 0.05, 0.10)
    esc = pd.DataFrame(
        {
            f"{s0 * (1 + p):.3f} ({p:+.0%})" if p else f"{s0:.3f} (base)": {
                "Sin cobertura": resultado(pos, s0 * (1 + p)),
                "Solo CCS": resultado(residuo_ccs, s0 * (1 + p)),
                "CCS + NDF": resultado(residuo_total, s0 * (1 + p)),
            }
            for p in shocks
        }
    )
    esc.columns = [c.replace("%", "\\%") for c in esc.columns]
    tabla_latex(
        esc,
        "t_e1_escenarios",
        "E1: con CCS + NDF la pérdida cambiaria casi desaparece en todo escenario (US\\$ millones)",
        f"{EEFF}, Notas 3 y 14; {BCRP} (TC interbancario 28-sep-2026)",
        "tab:e1-escenarios",
        decimales=1,
        nota="TC medio (compra-venta). Negativo = pérdida. Posición en S/ estimada a la fecha de valorización.",
    )
    m.set("EscSinCobMenosDiez", abs(resultado(pos, s0 * 0.9)), 1)
    m.set("EscConCobMenosDiez", abs(resultado(residuo_total, s0 * 0.9)), 1)
    m.set("ReduccionFX", 1 - residuo_total / pos, 0, pct=True)

    # Posiciones de cambio (en S/; − = pasiva en S/): PCC contable, PND derivados, PCG global
    pc = fx.PosicionCambio(pcc=-pos, pnd=saldo_rem + ndf_nocional)
    t_pos = pd.DataFrame(
        {
            "S/ MM": [pc.pcc / 1e3, saldo_rem / 1e3, ndf_nocional / 1e3, pc.pcg / 1e3],
            "TC −10\\% (US\\$)": [
                resultado(-pc.pcc, s0 * 0.9),
                -resultado(saldo_rem, s0 * 0.9),
                -resultado(ndf_nocional, s0 * 0.9),
                resultado(-pc.pcg, s0 * 0.9),
            ],
        },
        index=["PCC: pasivo neto en S/", "PND: CCS (recibe S/)", "PND: NDF (compra S/)", "PCG = PCC + PND"],
    )
    tabla_latex(
        t_pos,
        "t_e1_posiciones",
        "E1: posiciones de cambio (S/ MM)",
        f"{EEFF}, Notas 3 y 14",
        "tab:e1-posiciones",
        decimales=1,
        nota="Negativo = posición pasiva en S/ (o pérdida). Efecto a TC medio; el Cuadro~\\ref{tab:e1-ndf} usa el TC de compra pactado.",
        flotante=False,
    )

    # NIIF 9: valor razonable de los derivados ante un choque instantáneo de ±10 % del TC
    def valor_ndf(s: float) -> float:  # compra de S/ a F: V = N·(1/F' − 1/F)·DF_US$
        f_nuevo = fx.forward_paridad(s, r_pen_3m, r_usd_3m, dias)
        return ndf_nocional * (1 / f_nuevo - 1 / f_ndf) * c_usd(dias / 360) / 1e3

    # Registro contable a TC medio (NIIF 13 ¶71); el pricing de la tasa usa el TC compra
    m.set("NDFValMenosDiez", valor_ndf(s0 * 0.9), 1)
    m.set("NDFValMasDiez", abs(valor_ndf(s0 * 1.1)), 1)  # pasivo
    m.set("CCSValMenosDiez", ccs.valor_usd(c_pen, c_usd, spot_hoy=s0 * 0.9) / 1e3, 1)
    m.set("CCSValMasDiez", abs(ccs.valor_usd(c_pen, c_usd, spot_hoy=s0 * 1.1)) / 1e3, 1)  # pasivo
    m.set("CCSValPct", ccs.valor_usd(c_pen, c_usd, spot_hoy=s0 * 0.9) / (saldo_rem / bid), 1, pct=True)  # valor por unidad de nocional

    xs = np.linspace(s0 * 0.88, s0 * 1.12, 100)
    fig, ax = plt.subplots(figsize=(6.2, 2.3))
    ax.plot(xs, [resultado(pos, x) for x in xs], color=NARANJA, label="Sin cobertura")
    ax.plot(xs, [resultado(residuo_ccs, x) for x in xs], color="#e0a800", label="Solo CCS")
    ax.plot(xs, [resultado(residuo_total, x) for x in xs], color=AZUL, lw=2.2, label="CCS + NDF")
    ax.axhline(0, color=GRIS, lw=0.8)
    ax.axvline(s0, color=GRIS, lw=0.8, ls="--")
    ax.set_xlabel("Tipo de cambio al cierre (S/ por US\\$)")
    ax.set_ylabel("US\\$ millones")
    ax.legend(fontsize=8)
    guardar_figura(fig, "f_e1_escenarios")

    return {
        "s0": s0,
        "resultado_sin": lambda s: resultado(pos, s),
        "resultado_con": lambda s: resultado(residuo_total, s),
        "valor": lambda s: (ccs.valor_usd(c_pen, c_usd, spot_hoy=s) + valor_ndf(s) * 1e3) / 1e3,  # US$ MM
        "valor_ccs": lambda s: ccs.valor_usd(c_pen, c_usd, spot_hoy=s) / 1e3,
    }


# =========================================================================== E2: swap + collar WTI


def e2_crudo(ex: dict, mk: dict, m: Macros) -> dict:
    v = lambda k: ex[k].valor  # noqa: E731
    w = lambda k: mk[k].valor  # noqa: E731
    spot = w("crudo.wti_spot")
    f1, f2, f3 = w("crudo.wti_fut_1m"), w("crudo.wti_fut_2m"), w("crudo.wti_fut_3m")
    # Cobertura por capas mensuales (C5/M5): un tercio del volumen por contrato CLX26, CLZ26 y CLF27, cada capa
    # sobre el inventario que se vende ese mes. El collar de enero (CLF27) es la capa de referencia del texto.
    dias_op = w("crudo.dias_venc_opciones")
    T, sig = dias_op / 365, w("crudo.vol_implicita")
    r = fx.tasa_continua_desde_simple(w("tasas.usd_3m"), dias_op)
    reparto = v("crudo.reparto_swap")
    q_tot = v("crudo.inventario_crudo_mbl") * 1e3  # barriles en inventario
    q = q_tot * v("crudo.cobertura_objetivo")  # barriles cubiertos (límite de la política)
    p_swap = (f1 + f2 + f3) / 3  # swap de precio promedio de los 3 próximos meses
    capas = []
    for f_i, clave in ((f1, "crudo.dias_venc_opciones_nov"), (f2, "crudo.dias_venc_opciones_dic"), (f3, "crudo.dias_venc_opciones")):
        t_i = w(clave) / 365
        kp = round(f_i * v("crudo.put_pct_forward"), 1)
        kc = opciones.strike_collar_costo_cero(f_i, kp, t_i, r, sig, fijo="put")
        capas.append({"F": f_i, "T": t_i, "kp": kp, "kc": kc, "prima": opciones.black76(f_i, kp, t_i, r, sig, "put"),
                      "delta": opciones.delta_black76(f_i, kp, t_i, r, sig, "put")})
    k_put, k_call, prima = capas[-1]["kp"], capas[-1]["kc"], capas[-1]["prima"]  # capa de enero
    n_capas = len(capas)

    m.set("WTISpot", spot, 2)
    m.set("WTIFutUno", f1, 2)
    m.set("WTIFutDos", f2, 2)
    m.set("WTIFut", f3, 2)
    m.set("WTIFutDoce", w("crudo.wti_fut_12m"), 2)
    m.set("Backwardation", 1 - f3 / spot, 1, pct=True)
    m.set("BrentFut", w("crudo.brent_fut_1m"), 2)
    m.set("BrentWTI", w("crudo.brent_fut_1m") - f1, 1)
    m.set("SwapPrecio", p_swap, 2)
    m.set("VolCrudo", sig, 1, pct=True)
    m.set("RUSDCont", r, 2, pct=True)
    m.set("PlazoMeses", round(v("crudo.plazo_cobertura_anios") * 12), 0)
    m.set("PlazoDiasOpc", int(dias_op), 0)
    # Costo de acarreo entre el contrato frente (nov-26) y el de ene-27: F = S·e^{(r−y)T}, T = 2 meses
    m.set("ConvenienciaImplicita", fw.rendimiento_conveniencia_implicito(f1, f3, r, 2 / 12), 1, pct=True)
    m.set("CollarPut", k_put, 2)
    m.set("CollarCall", k_call, 2)
    m.set("PutPctFwd", v("crudo.put_pct_forward"), 0, pct=True)
    m.set("CollarPutsCapas", " / ".join(f"{c['kp']:.2f}" for c in capas))
    m.set("CollarCallsCapas", " / ".join(f"{c['kc']:.2f}" for c in capas))
    m.set("PlazoDiasCapas", " / ".join(f"{round(c['T'] * 365)}" for c in capas))
    m.set("PrimaPut", np.mean([c["prima"] for c in capas]), 2)
    m.set("DeltaPutAbs", abs(np.mean([c["delta"] for c in capas])), 2)
    m.set("CostoPutTotal", sum(c["prima"] for c in capas) * q / n_capas / 1e6, 1)
    m.set("NCapas", n_capas, 0)
    # Programa rodante: cada capa cubre 1/n del volumen; sin reposición la cobertura cae al vencer cada capa
    m.set("CapaMMbl", q / n_capas / 1e6, 3)
    m.set("CapaContratos", f"{round(q / n_capas / w('crudo.tamano_contrato')):,}")
    m.set("CobSinReposUno", v("crudo.cobertura_objetivo") * (n_capas - 1) / n_capas, 0, pct=True)
    m.set("CobSinReposDos", v("crudo.cobertura_objetivo") * (n_capas - 2) / n_capas, 0, pct=True)
    m.set("CoberturaCrudoPct", v("crudo.cobertura_objetivo"), 0, pct=True)
    m.set("ContratosEquiv", f"{n_capas * round(q / n_capas / w('crudo.tamano_contrato')):,}")  # = capas × contratos por capa
    m.set("RepartoSwap", reparto, 0, pct=True)
    m.set("RepartoCollar", 1 - reparto, 0, pct=True)
    m.set("InvValorHoy", q_tot * spot / 1e6, 1)
    m.set("InvCubiertoMMbl", q / 1e6, 2)
    m.set("RotacionDias", q_tot / (v("crudo.compras_mbdc") * 1e3), 0)  # días de compras que representa el inventario
    m.set("InvCubiertoValor", q * spot / 1e6, 1)

    def neto(st: float, estrategia: str) -> float:
        """Resultado sobre TODO el inventario: la parte no cubierta (q_tot − q) queda expuesta al spot."""
        abierto = (st - spot) * (q_tot - q) / 1e6
        if estrategia == "Sin cobertura":
            return (st - spot) * q_tot / 1e6
        if estrategia == "Swap":
            return (p_swap - spot) * q / 1e6 + abierto
        if estrategia == "Collar":
            return sum(min(max(st, c["kp"]), c["kc"]) - spot for c in capas) * q / n_capas / 1e6 + abierto
        if estrategia == "Mixto":
            return reparto * neto(st, "Swap") + (1 - reparto) * neto(st, "Collar")
        return sum(max(st, c["kp"]) - spot - c["prima"] for c in capas) * q / n_capas / 1e6 + abierto  # solo put

    cob = v("crudo.cobertura_objetivo")
    etiquetas = {
        "Sin cobertura": "Sin cobertura",
        "Swap": f"Solo swap a {p_swap:.2f} ({cob:.0%})",
        "Collar": f"Solo collar en {n_capas} capas ({cob:.0%})",
        "Put": f"Solo put, prima pagada ({cob:.0%})",
        "Mixto": f"Propuesta: {reparto:.0%} swap + {1 - reparto:.0%} collar".replace("%", "\\%"),
    }
    # Escenarios alrededor del precio de hoy + el escenario "WTI converge al futuro" (F, backwardation)
    precios = {f"{p:+.0%}".replace("%", "\\%") if p else "0\\%": spot * (1 + p) for p in (-0.30, -0.20, -0.10)}
    precios["$=F$ ene"] = f3
    precios |= {f"{p:+.0%}".replace("%", "\\%") if p else "0\\%": spot * (1 + p) for p in (0.0, 0.10, 0.20, 0.30)}
    tabla = pd.DataFrame({c: {etiquetas[e]: neto(x, e) for e in etiquetas} for c, x in precios.items()})
    tabla.loc["WTI (US\\$/bbl)"] = list(precios.values())
    tabla = tabla.loc[["WTI (US\\$/bbl)", *etiquetas.values()]]
    tabla_latex(
        tabla,
        "t_e2_escenarios",
        "E2: la propuesta limita la pérdida del inventario si el WTI cae y cede parte de la ganancia si sube (US\\$ millones)",
        f"{EEFF}, Nota 10; {NYMEX}",
        "tab:e2-escenarios",
        decimales=1,
        nota="Inventario total; las coberturas se aplican al 80 \\% (el 20 \\% queda abierto). Variación del WTI respecto del 28-sep-2026; $=F$ ene: WTI igual al futuro de enero, para todas las capas. Negativo = pérdida.",
    )
    m.set("PerdidaSinCobTreinta", abs(neto(spot * 0.7, "Sin cobertura")), 1)
    # Con 20 % abierto la pérdida no tiene piso: se compara en el mismo escenario de −30 %
    m.set("PerdidaMaxCollar", abs(neto(spot * 0.7, "Collar")), 1)
    m.set("GananciaMaxCollar", neto(spot * 1.3, "Collar"), 1)
    m.set("CostoSwap", (spot - p_swap) * q * reparto / 1e6, 1)  # solo el volumen del swap, frente al precio de hoy
    m.set("PerdidaSinCobForward", abs(neto(f3, "Sin cobertura")), 1)
    m.set("PerdidaMaxMixto", abs(neto(spot * 0.7, "Mixto")), 1)
    m.set("GananciaMaxMixto", neto(spot * 1.3, "Mixto"), 1)

    # NIIF 9: valor razonable ante un choque instantáneo de ±10 % de la curva de futuros
    q_col, q_swap = q * (1 - reparto), q * reparto
    def valor_collar(choque: float) -> float:
        """Valor de las capas del collar ante un choque proporcional de toda la curva de futuros (US$ MM)."""
        return sum(
            opciones.black76(c["F"] * (1 + choque), c["kp"], c["T"], r, sig, "put")
            - opciones.black76(c["F"] * (1 + choque), c["kc"], c["T"], r, sig, "call")
            for c in capas
        ) * q_col / n_capas / 1e6

    df_swap = np.exp(-r * T)
    m.set("InvCollarMMbl", q_col / 1e6, 2)
    m.set("InvSwapMMbl", q_swap / 1e6, 2)

    # C1 (checklist): posiciones en barriles, análogo de PCC / PND / PCG (equivalentes delta)
    delta_collar = sum(opciones.delta_black76(c["F"], c["kp"], c["T"], r, sig, "put")
                       - opciones.delta_black76(c["F"], c["kc"], c["T"], r, sig, "call") for c in capas) / n_capas
    pos = {"Físico: inventario de crudo": q_tot, "Swap (vende a precio fijo)": -q_swap,
           "Collar (equivalente delta)": delta_collar * q_col}
    pos["Global (físico + derivados)"] = sum(pos.values())
    t_pos2 = pd.DataFrame({"MMbl": {k: x / 1e6 for k, x in pos.items()},
                           "WTI $-10$\\,\\% (US\\$)": {k: -0.10 * spot * x / 1e6 for k, x in pos.items()}})
    tabla_latex(
        t_pos2,
        "t_e2_posiciones",
        "E2: posiciones en barriles (MM)",
        f"{EEFF}, Nota 10; {NYMEX}",
        "tab:e2-posiciones",
        decimales=2,
        nota="Positivo = largo en crudo. Collar: delta medio de las capas. Efecto lineal de una caída de 10 \\% del WTI.",
        flotante=False,
    )
    # Checklist: demostración Inicio/Vencimiento del swap (neto constante = (P_swap − S0)·Q_swap)
    fix_wti = {"WTI $-30$\\,\\%": spot * 0.7, "$=F$ ene": f3, "WTI $+30$\\,\\%": spot * 1.3}
    t_sw = pd.DataFrame({c: {"Inventario (vol. del swap)": (x - spot) * q_swap / 1e6,
                             "Swap: $(P - S)\\,Q$": (p_swap - x) * q_swap / 1e6} for c, x in fix_wti.items()})
    t_sw.loc["Total"] = t_sw.sum()
    t_sw.insert(0, "Inicio", 0.0)
    tabla_latex(
        t_sw,
        "t_e2_swap",
        "E2: swap al vencimiento (US\\$ MM)",
        f"{EEFF}, Nota 10; {NYMEX}",
        "tab:e2-swap",
        decimales=1,
        nota=f"{q_swap / 1e6:.2f} MMbl a P = {p_swap:.2f}; S$_0$ = {spot:.2f}. Inicio: valor cero, sin flujo. Total constante = (P $-$ S$_0$)\\,Q.",
        flotante=False,
    )
    m.set("PosGlobalMMbl", pos["Global (físico + derivados)"] / 1e6, 2)
    m.set("PosGlobalPct", pos["Global (físico + derivados)"] / q_tot, 0, pct=True)
    m.set("CollarValMenosDiez", valor_collar(-0.10), 1)
    m.set("CollarValMasDiez", abs(valor_collar(0.10)), 1)  # pasivo
    m.set("SwapValDiez", 0.10 * p_swap * q_swap * df_swap / 1e6, 1)
    m.set("SwapValBl", 0.10 * p_swap * df_swap, 2)  # US$ por barril ante un choque de 10 % de la curva
    # Casos extremos de cada instrumento solo (para sustentar el reparto 50/50)
    m.set("PerdidaSwapTreinta", abs(neto(spot * 0.7, "Swap")), 1)
    m.set("GananciaSwapTreinta", neto(spot * 1.3, "Swap"), 1)
    m.set("CostoSwapTotal", (spot - p_swap) * q / 1e6, 1)  # swap sobre todo el volumen cubierto, frente al precio de hoy

    # M6: vega del collar (put comprado − call vendido), US$ MM por punto de volatilidad
    vega = sum(opciones.vega_black76(c["F"], c["kp"], c["T"], r, sig) - opciones.vega_black76(c["F"], c["kc"], c["T"], r, sig)
               for c in capas)
    m.set("VegaCollar", vega * q_col / n_capas / 100 / 1e6, 2)
    # M2: strike del call de costo cero según la volatilidad supuesta
    for nombre, s_alt in (("Baja", 0.35), ("Media", 0.45)):
        m.set(f"VolSens{nombre}", s_alt, 0, pct=True)
        m.set(f"CollarCallVol{nombre}", opciones.strike_collar_costo_cero(f3, k_put, T, r, s_alt, fijo="put"), 2)

    # Skew: el call vendido se cotiza con menos volatilidad que el put comprado => el techo de costo cero baja
    skew = {"Misma volatilidad": 0.0, "Call 5 puntos más barato": 0.05, "Call 10 puntos más barato": 0.10}
    t_skew = pd.DataFrame(
        {f"Call {mes}": {k: opciones.strike_collar_costo_cero(c["F"], c["kp"], c["T"], r, sig, fijo="put", sigma_otro=sig - d)
                         for k, d in skew.items()}
         for mes, c in zip(("nov", "dic", "ene"), capas)}
    )
    tabla_latex(
        t_skew,
        "t_skew",
        "E2: Sensibilidad del collar al \\emph{skew}: strikes de costo cero (US\\$/bl)",
        f"{NYMEX}; \\textcite{{black1976}}",
        "tab:skew",
        decimales=2,
        nota="Put comprado a " + " / ".join(f"{c['kp']:.2f}" for c in capas)
        + " (nov / dic / ene); \\emph{skew}: puntos de volatilidad que el call se cotiza por debajo del put.",
    )
    m.set("VegaCollarMil", abs(vega) * q_col / n_capas / 100 / 1e3, 0)
    m.set("CollarCallSkewCinco", t_skew.loc["Call 5 puntos más barato", "Call ene"], 2)
    m.set("CollarCallSkewDiez", t_skew.loc["Call 10 puntos más barato", "Call ene"], 2)

    xs = np.linspace(spot * 0.6, spot * 1.4, 200)
    fig, ax = plt.subplots(figsize=(6.2, 2.4))
    ax.plot(xs, [neto(x, "Sin cobertura") for x in xs], color=NARANJA, label="Inventario sin cobertura")
    ax.plot(xs, [neto(x, "Swap") for x in xs], color=AZUL, label=f"Inventario + swap WTI ({p_swap:.2f})")
    ax.plot(xs, [neto(x, "Collar") for x in xs], color=VERDE, label=f"Inventario + collar en {n_capas} capas")
    ax.plot(xs, [neto(x, "Mixto") for x in xs], color="#6b3fa0", lw=2.4, label="Propuesta: 50 % swap + 50 % collar")
    ax.axhline(0, color=GRIS, lw=0.8)
    ax.set_xlabel("Precio WTI al vencimiento (US\\$/bbl)")
    ax.set_ylabel("US\\$ millones")
    ax.legend(fontsize=8, loc="upper left")
    guardar_figura(fig, "f_e2_payoff")

    # Figura: cómo se arma el collar de costo cero (capa de enero, por barril)
    st = np.linspace(k_put * 0.7, k_call * 1.25, 300)
    put_l, call_c = opciones.payoff_put(st, k_put), -opciones.payoff_call(st, k_call)
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.3), sharey=False)
    paneles = (
        ("1. Compra un put (piso)", put_l, AZUL, "Cobra si el WTI\ncae bajo el piso", (0.62, 0.5)),
        ("2. Vende un call (techo)", call_c, NARANJA, "Paga si el WTI\nsupera el techo;\nsu prima paga el put", (0.36, 0.3)),
    )
    for ax, (tit, y, col, txt, xy) in zip(axs[:2], paneles):
        ax.plot(st, y, color=col, lw=2)
        ax.axhline(0, color=GRIS, lw=0.8)
        ax.set_title(tit, fontsize=8.5)
        ax.text(*xy, txt, transform=ax.transAxes, fontsize=7, ha="center", color=col)
    axs[0].set_ylabel("US\\$/bl")
    ax = axs[2]
    ax.plot(st, st, color=GRIS, ls="--", lw=1.2, label="Sin cobertura")
    ax.plot(st, st + put_l + call_c, color=VERDE, lw=2.2, label="Con collar")
    ax.axvspan(k_put, k_call, color=VERDE, alpha=0.08)
    ax.annotate(f"Piso {k_put:.1f}", (st[0], k_put), xytext=(0, 3), textcoords="offset points", fontsize=7)
    ax.annotate(f"Techo {k_call:.1f}", (k_call, k_call), xytext=(-6, 5), textcoords="offset points", fontsize=7)
    ax.set_title("3. Inventario + put + call", fontsize=8.5)
    ax.legend(fontsize=6.5, loc="lower right")
    for ax in axs:
        ax.set_xlabel("WTI al vencimiento (US\\$/bl)", fontsize=7.5)
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    guardar_figura(fig, "f_e2_collar")

    return {
        "spot": spot,
        "T": T,
        "resultado_sin": lambda x: neto(x, "Sin cobertura"),
        "resultado_con": lambda x: neto(x, "Mixto"),
        # valor de mercado de swap + collar ante un choque proporcional de la curva de futuros (US$ MM)
        "valor": lambda p: valor_collar(p) - p * p_swap * q_swap * df_swap / 1e6,
    }


# =========================================================================== riesgo residual y liquidez


def h_minima_varianza(partida: str) -> dict[str, float]:
    """h* semanal (miércoles) de la partida cubierta frente al futuro CL frente, 2 años al 22-sep-2026."""
    def s(nombre: str) -> pd.Series:
        x = serie(nombre)
        x.index = pd.to_datetime(x.index)
        return x
    df = pd.concat({"S": s(partida), "F": s("cl_front_yahoo")}, axis=1, sort=True).loc["2024-09-22":"2026-09-22"]
    d = df.dropna()
    d = d[d.index.weekday == 2].diff().dropna()
    return cobertura.ratio_minima_varianza(d["S"], d["F"]) | {"n": len(d)}


def riesgo_residual(ex: dict, mk: dict, m: Macros, e1: dict, e2: dict) -> None:
    v = lambda k: ex[k].valor  # noqa: E731
    w = lambda k: mk[k].valor  # noqa: E731

    # C4: riesgo de base. WTI Cushing frente a CL (casi idéntico) y Brent frente a CL (base real)
    h_wti, h_brent = h_minima_varianza("wti_spot_eia"), h_minima_varianza("brent_spot_eia")
    q = v("crudo.inventario_crudo_mbl") * 1e3 * v("crudo.cobertura_objetivo")
    m.set("RatioH", h_wti["h"], 2)
    m.set("RatioHBrent", h_brent["h"], 2)
    m.set("EfectividadBrent", h_brent["efectividad"], 0, pct=True)
    m.set("EfectividadWTI", h_wti["efectividad"], 0, pct=True)
    m.set("ContratosH", f"{cobertura.numero_contratos(h_wti['h'], q, w('crudo.tamano_contrato')):,}")
    m.set("ContratosHBrent", f"{cobertura.numero_contratos(h_brent['h'], q, w('crudo.tamano_contrato')):,}")
    m.set("SemanasH", h_brent["n"], 0)

    # M6: VaR al 95 % al vencimiento de las coberturas (~3 meses), con volatilidad realizada de un año
    def vol_realizada(nombre: str) -> float:
        x = serie(nombre).loc["2025-09-28":"2026-09-28"]
        return float(np.log(x).diff().dropna().std(ddof=1) * np.sqrt(252))
    tc = (serie("usdpen_interbancario_compra") + serie("usdpen_interbancario_venta")) / 2
    vol_tc = float(np.log(tc.loc["2025-09-28":"2026-09-28"]).diff().dropna().std(ddof=1) * np.sqrt(252))
    vol_cl = vol_realizada("cl_front_yahoo")
    m.set("VolRealCL", vol_cl, 1, pct=True)
    T_fx, T_cr = v("cobertura_fx.ndf_dias") / 360, e2["T"]
    var = {
        ("E1 (TC)", "Sin cob."): riesgo.var_monotono(e1["resultado_sin"], e1["s0"], vol_tc, T_fx),
        ("E1 (TC)", "Con cob."): riesgo.var_monotono(e1["resultado_con"], e1["s0"], vol_tc, T_fx),
        ("E2 (crudo)", "Sin cob."): riesgo.var_monotono(e2["resultado_sin"], e2["spot"], vol_cl, T_cr),
        ("E2 (crudo)", "Con cob."): riesgo.var_monotono(e2["resultado_con"], e2["spot"], vol_cl, T_cr),
    }
    t_var = pd.DataFrame({e: {c: var[(e, c)] for c in ("Sin cob.", "Con cob.")} for e in ("E1 (TC)", "E2 (crudo)")}).T
    t_var["Reducción"] = [f"{1 - r['Con cob.'] / r['Sin cob.']:.0%}".replace("%", "\\%") for _, r in t_var.iterrows()]
    tabla_latex(
        t_var,
        "t_var",
        "VaR al 95\\,\\% al vencimiento (US\\$ MM)",
        f"{EEFF}, Notas 3 y 10; {BCRP}; {NYMEX}. Volatilidad realizada de un año",
        "tab:var",
        decimales=1,
        nota="Horizonte: 91 días (E1) y vencimiento de las opciones (E2). La E2 incluye el 20 \\% no cubierto.",
        flotante=False,
    )
    m.set("VaRFXSin", var[("E1 (TC)", "Sin cob.")], 1)
    m.set("VaRFXCon", var[("E1 (TC)", "Con cob.")], 1)
    m.set("VaRCrudoSin", var[("E2 (crudo)", "Sin cob.")], 1)
    m.set("VaRCrudoCon", var[("E2 (crudo)", "Con cob.")], 1)

    # C2: colateral exigible bajo un CSA con umbral cero ante choques adversos para PETROPERÚ
    s0 = e1["s0"]
    libres = (v("deuda.lineas_revolventes") - v("deuda.lineas_utilizadas")) / 1e3
    choques = {
        "TC $+10$\\,\\%": (0.10, 0.0),
        "WTI $+30$\\,\\%": (0.0, 0.30),
        "TC $+5$\\,\\% y WTI $+10$\\,\\%": (0.05, 0.10),
        "TC $+10$\\,\\% y WTI $+30$\\,\\%": (0.10, 0.30),
    }
    filas = {}
    for nombre, (p_tc, p_wti) in choques.items():
        v1 = e1["valor"](s0 * (1 + p_tc))  # MtM total a TC medio: el CSA colateraliza el valor completo
        v2 = e2["valor"](p_wti)
        col = riesgo.colateral_exigible(v1 + v2)
        filas[nombre] = {"E1": -v1, "E2": -v2, "Colat.": col, "Déficit": max(col - libres, 0.0)}
    t_col = pd.DataFrame(filas).T
    tabla_latex(
        t_col,
        "t_colateral",
        "Colateral exigible con umbral cero (US\\$ MM)",
        f"{EEFF}, Nota 3.1(c); {BCRP}; {NYMEX}",
        "tab:colateral",
        decimales=1,
        nota=f"E1 y E2: pasivo de los derivados, a TC medio; el 0.4 de E1 con TC sin cambio es la diferencia entre el TC de compra pactado y el medio. Déficit: colateral menos líneas libres (US\\$ {libres:.1f} MM).",
        flotante=False,
    )
    peor = t_col.iloc[-1]
    m.set("LineasLibres", libres, 1)
    m.set("ColateralTC", t_col.iloc[0]["Colat."], 1)
    m.set("ColateralWTI", t_col.iloc[1]["Colat."], 1)
    # plan B: contratar primero 50 % del CCS (su valor es lineal en el nocional); el NDF se mantiene completo
    m.set("ColateralTCMitad", riesgo.colateral_exigible(e1["valor"](s0 * 1.1) - e1["valor_ccs"](s0 * 1.1) / 2), 1)
    m.set("ColateralConjunto", peor["Colat."], 1)
    m.set("DeficitConjunto", peor["Déficit"], 1)
    m.set("UmbralNecesario", float(np.ceil(peor["Déficit"])), 0)  # umbral (redondeado hacia arriba) que haría el colateral ≤ líneas libres
    m.set("PrestamoPuente", w("credito.prestamo_puente") / 1e3, 0)


def tasa_refinanciacion(mk: dict, m: Macros) -> None:
    w = lambda k: mk[k].valor  # noqa: E731
    c_usd = curva_sofr(mk)
    # Refinanciación del CESCE: de 2027 a su vencimiento contractual (2030), 3 años
    # Pago fijo anual, la misma convención de los swaps SOFR con que se construye la curva
    m.set("FwdSwapRate", swaps.forward_starting_rate(c_usd, inicio=1.0, anios=3.0, freq=1), 2, pct=True)
    m.set("USDCincoAnios", w("tasas.usd_5a"), 2, pct=True)


def main() -> None:
    estilo_figuras()
    ex, mk = datos.cargar("exposiciones"), datos.cargar("mercado")
    m = Macros()
    contexto(ex, mk, m)
    riesgo_cambiario(ex, m)
    historia_mercado(mk, m)
    riesgo_crudo(ex, mk, m)
    spread = riesgo_tasa(ex, m)
    e1 = e1_cambiario(ex, mk, m, spread)
    e2 = e2_crudo(ex, mk, m)
    riesgo_residual(ex, mk, m, e1, e2)
    tasa_refinanciacion(mk, m)
    m.set("FechaValorizacion", "28 de setiembre de 2026")
    m.set("DUCrisis", "N.°~003-2026")  # EEFF 2025, Nota 1, p. 25
    m.set("DUCrisisMonto", ex["empresa.du_003_2026_compromisos"].valor / 1e3, 0)
    m.set("LimiteFX", "70\\,\\%--100\\,\\%")  # política propuesta (supuesto de diseño)
    m.set("LimiteCrudo", "50\\,\\%--80\\,\\%")
    pend = datos.pendientes("exposiciones", "mercado")
    m.set("InsumosPendientes", str(len(pend)))
    ruta = m.escribir()
    print(f"OK → {ruta.relative_to(RAIZ)}")
    if pend:
        print(f"AVISO: {len(pend)} insumos PENDIENTES (no apto para versión final):")
        for i in pend:
            print(f"  - {i.clave}: {i.fuente[:120]}")


if __name__ == "__main__":
    main()
