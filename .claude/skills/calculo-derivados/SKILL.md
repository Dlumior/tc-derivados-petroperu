---
name: calculo-derivados
description: Método de cálculo y presentación de coberturas con derivados (forwards, futuros, swaps, opciones) según la lógica de referencia del Prof. Humala (Examen Parcial Prom. 44). Úsala siempre que haya que calcular, verificar o explicar un forward/NDF, arbitraje spot-forward, paridad de tasas, posiciones PCC/PND/PCG, depósito sintético, valorización de un derivado abierto, swap (IRS/CCS), collar u opción, o armar tablas de escenarios con/sin cobertura para el informe.
---

# Cálculo de derivados — método de referencia

El Excel `data/raw/Examen_Parcial_Prom44_Referencia.xlsx` muestra **cómo califica el profesor**:
no basta el número; cada cálculo debe venir con su explicación conceptual. Su columna de puntaje
(0.5 pts por ítem) premia exactamente estos elementos. Todo cálculo del informe sigue este patrón.

## El patrón de 7 pasos (obligatorio para cada estrategia)

1. **Riesgo y posición.** Qué partida, en qué dirección daña (ej. "pasivo neto en S/ → pierde si el PEN se aprecia"). Posición de cobertura contraria (ej. "forward largo PEN / corto USD").
2. **Insumos con fuente.** Tabla de parámetros: spot (bid/ask), tasas, plazo en meses **y** años, nocional. Cada insumo con Nota/página del EEFF o URL+fecha. Nada sin fuente.
3. **Fórmula teórica** escrita explícitamente (ecuación LaTeX) antes del número: `F = S·e^{rT}`, `F = S·[(1+r_PEN)/(1+r_USD)]^{d/360}`, `F = S + pts/10 000`, etc.
4. **Tabla de operaciones Inicio / Vencimiento** con los flujos de cada pata y la fila **Total**.
5. **Verificación**: la suma en la fecha opuesta es **0** (arbitraje) o el **neto es constante** en todos los escenarios (cobertura perfecta). Mostrar el cálculo alterno (ej. neto = (S₀ − F)·N) que confirma el resultado.
6. **Escenarios alternativos** (mínimo 2 valores del subyacente, uno favorable y otro adverso): exposición, derivado y neto. Siempre acompañar con **gráfico de payoff**.
7. **Interpretación**: costo de la cobertura (= diferencial de tasas implícito o prima), conveniencia aunque el riesgo no se materialice, registro contable (activo/pasivo según **valor**, no según payoff), efecto en PCC/PND/PCG.

## Convenciones (no negociables, son las del Excel)

| Tema | Convención |
|---|---|
| Commodities / activos de inversión | Capitalización **continua**: `e^{rT}`, T en años (`meses/12`) |
| Tipo de cambio USD/PEN | Tasas **efectivas** base **360**: `(1+r)^{d/360}`; puntos: `F = S + pts/10 000` |
| Bid / Ask | Compra USD a plazo → **ask (venta)**; vende USD a plazo → **bid (compra)**. Venta spot de USD → bid |
| Diferencial implícito | `(F/S)^{1/T} − 1` = costo anual de la cobertura |
| Valor de forward abierto | Largo: `S_t − K·e^{−rτ}`; Corto: el negativo. Para valorizar, "tomar la posición contraria" |
| Registro NIIF 9 | Valor > 0 → **activo**; valor < 0 → **pasivo** |
| Posiciones | `PCG = PCC + PND`; operaciones simultáneas contrapuestas **no** cambian la PCG |
| Moneda funcional | PETROPERÚ reporta en **US$**: su riesgo cambiario es sobre saldos en **S/** (lo inverso al Excel P2) |
| Signos en tablas | Egresos negativos; negativos entre paréntesis en el PDF (formato EEFF) |

## Dónde está implementado (no reescribir fórmulas: importar)

| Concepto (Excel) | Función |
|---|---|
| P1 forward teórico, arbitraje, tabla operaciones | `derivados.forwards.forward_teorico`, `ganancia_arbitraje_*`, `tabla_arbitraje` |
| P1b valor de forward abierto, registro | `forwards.valor_forward`, `forwards.registro_contable` |
| P2 forward pactado bid/ask, diferencial, escenarios | `fx.cotizacion_forward`, `fx.precio_pactado`, `fx.diferencial_implicito`, `fx.resultados_cobertura_pasivo_usd` |
| P3/P4 PCC, PND, PCG | `fx.PosicionCambio` (`.pcg`, `.riesgo()`, `.tabla()`) |
| P4 depósito sintético / arbitraje de tasas | `fx.DepositoSintetico` |
| Swaps (extensión) | `swaps.IRS`, `swaps.CrossCurrencySwap`, `swaps.tira_forwards_pen`, `swaps.forward_starting_rate` |
| Opciones (extensión) | `opciones.black76`, `opciones.garman_kohlhagen`, `opciones.strike_collar_costo_cero` |
| Diseño de cobertura | `cobertura.ratio_minima_varianza`, `numero_contratos`, `tabla_escenarios`, `var_parametrico` |
| Salida al informe | `reporte.Macros`, `reporte.tabla_latex` (exige `fuente`), `reporte.guardar_figura` |

Los tests `tests/test_referencia_excel.py` fijan los valores exactos del Excel. Si cambias una
función y un test falla, **la función está mal**, no el test.

## Flujo de trabajo

1. Insumos → `data/procesado/exposiciones.yaml` / `mercado.yaml` (con `fuente` y `estado`).
2. Cálculo → función en `scripts/run_all.py` (una por estrategia: `e1_...`, `e2_...`) usando la librería.
3. Salida → macros (`m.set("NombreEnLetras", valor, dec, pct)`), tablas (`tabla_latex(..., fuente=...)`) y figuras.
4. `make calc` y luego, en el `.tex`, usar `\NombreMacro` e `\input{generado/tablas/...}`. **Nunca teclear cifras.**
5. Si una fórmula nueva no existe: agrégala a `src/derivados/` **con un test** (propiedad teórica: paridad put-call, valor cero al inicio, etc.).

Para fórmulas detalladas y ejemplos numéricos del Excel: `referencia/formulas.md`.
Para el checklist de puntos que otorga el profesor: `referencia/checklist_puntaje.md`.
