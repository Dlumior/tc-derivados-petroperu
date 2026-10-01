# Fórmulas y ejemplos numéricos (del Excel de referencia)

## P1 — Commodity (exportador de cobre): teorema spot-forward y arbitraje

Insumos: S = 14 714 US$/TM, r = 3.5 %, T = 9 meses = 0.75 años.

- Forward teórico: `F = S·e^{rT}` = **15 105.36**
- Forward de mercado sobrevaluado 3 %: F' = 15 558.52 → `F' > S·e^{rT}` ⇒ arbitraje
- Ganancia hoy: `F'·e^{−rT} − S` = **441.42** por TM

| Operación (ganancia al inicio) | Inicio | Vencimiento |
|---|---|---|
| Prestarse VP de F | +F·e^{−rT} | −F |
| Largo spot | −S | +S_T |
| Corto forward | 0 | F − S_T |
| **Total** | **441.42** | **0** ← prueba de arbitraje |

Alternativa (ganancia al vencimiento): prestarse S → al vencimiento `F' − S·e^{rT}` = **453.16** (= 441.42·e^{rT}).

P1b — Valor de la posición forward corta a los 6 meses (S_t = 15 450, r = 3.75 %, τ = 3 m):
`VF = F·e^{−rτ} − S_t` = **−485.59** por TM; ×100 TM = **−48 559**. Negativo → **pasivo**.
Interpretación: el spot subió; la cobertura "perdió" pero cumplió su función (fijó el precio). Es conveniente aunque el riesgo no se haya dado.

## P2 — Cuenta por pagar USD 1.1 MM a 6 meses (empresa en PEN)

Spot 3.407/3.408; puntos 230/250 → Fwd 3.430/3.433. Empresa compra USD a plazo ⇒ **ask 3.433**.
Diferencial implícito: `(3.433/3.408)^{1/0.5} − 1` = **1.4725 %** anual = costo de la cobertura.

| | TC = 3.382 | TC = 3.421 |
|---|---|---|
| Cuenta por pagar (S₀ − S_T)·N | 28 600 | −14 300 |
| Forward largo (S_T − F)·N | −56 100 | −13 200 |
| **Neto** | **−27 500** | **−27 500** |
| Alterno (S₀ − F)·N | −27 500 | −27 500 |

PCC = −1.1 MM (corto USD, riesgo depreciación) + PND = +1.1 MM ⇒ **PCG = 0**.

## P3 — Registro y efectos de mercado
- Fwd venta: S sube ⇒ VF < 0 ⇒ pasivo; S cae ⇒ VF > 0 ⇒ activo.
- AFP (portafolio USD) cubren con fwd venta (contra apreciación); No Residentes (portafolio PEN) con fwd compra (contra depreciación).
- Vencimiento con entrega: PCC baja, PND sube, PCG constante ⇒ sin efecto cambiario.
  Sin entrega (NDF): PCC no cambia, PND sube ⇒ PCG sube ⇒ banca vende USD spot ⇒ presión a la apreciación del PEN.

## P4 — Depósito sintético en USD (90 días)
Monto 3 MM USD; spot 3.355/3.357; puntos 90/100 → fwd 3.364/3.367; r_USD 1.5 %, r_PEN 3.4 %.

| Operación | Hoy USD | Hoy PEN | Venc. USD | Venc. PEN |
|---|---|---|---|---|
| 1) Vende USD spot (bid) | −3 000 000 | +10 065 000 | | |
| 2) Depósito PEN | | −10 065 000 | | +10 149 482.85 |
| 3) Compra fwd USD (ask) | | | +3 014 399.42 | −10 149 482.85 |

Tasa sintética `(USD_T/USD_0)^{360/90} − 1` = **1.9338 %** > 1.5 % ⇒ conviene.
Directo: `(S_bid/F_ask)^{360/d}·(1 + r_PEN) − 1` = 1.9338 %.
Posiciones: PCC 12 MM → 9 MM; PND 6 MM → 9.01 MM; PCG 18 MM → 18.01 MM (casi sin cambio).

## Extensiones para el trabajo (no están en el Excel; mismo patrón)

- **CCS fija-fija**: `V = (1/S₀)·Σ C_k^{PEN}·DF^{PEN}(t_k) − Σ C_k^{USD}·DF^{USD}(t_k)`; tasa USD justa ⇒ V₀ = 0.
  Equivale a una tira de forwards (uno por cuota) ⇒ comparar con `tira_forwards_pen`.
- **IRS**: `V_pagador = B_var − B_fija`; tasa par `= (1 − DF_n)/Σ(DF_i·Δ)`; forward-starting `= (DF_a − DF_n)/Σ(DF_i·Δ)`.
- **Futuros de crudo**: `h* = ρ·σ_S/σ_F`, `N* = h*·Q_A/Q_F` (Q_F = 1 000 bbl, NYMEX CL). Riesgo de base: crudo Oriente/Napo vs WTI/Brent.
- **Opciones**: Black-76 sobre futuro; collar costo cero (compra put K₁, vende call K₂ con prima_put = prima_call).
- **Efectividad**: dollar-offset 80–125 % (referencial NIIF 9 / NIC 39), ρ² de la regresión.
