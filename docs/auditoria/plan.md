# Plan para levantar los hallazgos del dictamen de auditoría

Dictamen: [`dictamen.md`](dictamen.md), recibido el 3-oct-2026. Entrega impresa: **5-oct-2026, 19:30**.
Este archivo es el registro de avance: marcar `[x]` al cerrar cada tarea y cambiar el estado en la tabla.

**Reglas que siguen aplicando** (CLAUDE.md): cero cifras tecleadas (todo por `m.set` + `make calc`), todo
insumo con fuente, toda fórmula nueva en `src/derivados/` con su test, y **≤ 10 páginas**. Cada párrafo que se
agregue tiene que compensarse recortando otro.

## 1. Validación de los hallazgos

Revisé cada hallazgo contra `informe/secciones/*.tex`, `scripts/run_all.py`, `data/procesado/*.yaml` y el texto
del EEFF (`data/raw/Dictamen_EEFF_2025_Petroperu.txt`).

| # | Veredicto | Severidad ajustada | Evidencia de la verificación |
|---|---|---|---|
| C1 | **Válido** | Crítico | Ene-2025 a dic-2028 son 48 meses, pero el EEFF dice 46 cuotas (EEFF l. 2970-2972). Según la Nota 14(c), en 2025 no hubo pagos de principal. El supuesto de 36 cuotas está declarado en 03 l. 166, pero 03 l. 271 afirma que "nocional, fechas y tasa coinciden": eso es una sobreafirmación. La convención TEA→mensual no se explica. |
| C2 | **Válido** | Crítico | Verifiqué 77.4 + 19.7 + 8.4 + 12.8 = 118.3 frente a 376.9 − 354.6 = 22.3. El Cuadro 10 dice "Efecto en liquidez: Bajo" sin ningún cálculo que lo respalde. |
| C3 | **Válido** | Crítico (arreglo simple) | 04 l. 380 dice "CVA incluido en la tasa"; 03 l. 211 y 05 l. 415-416 dicen "antes de CVA". El spread de crédito ya está calculado (`\SpreadBonosPb` = 569 pb), así que el CVA se puede estimar. |
| C4 | **Parcial** | Medio-alto | Es cierto que h* compara WTI Cushing con CL (`mercado.yaml`). El informe sí reconoce el riesgo de base (03 l. 343-347), pero presenta h* como si sirviera para dimensionar. La justificación del yaml ("costos de compra con WTI + spreads, p. 70") está mal citada: esa página habla de los **precios de venta** por paridad de importación (EEFF l. 2766-2768). Bien citado, ese pasaje respalda el uso del WTI como componente de riesgo. En el yaml ya existe h* contra Brent (1.156, ρ² = 0.80), pero no se usa. |
| C5 | **Válido** (b, d); **parcial** (a, c) | Crítico | (b) 2,901 / 87 ≈ 33 días de rotación frente a una cobertura de ~3 meses. (d) El propio informe dice que los precios de venta siguen la paridad de importación (02 l. 107-109), pero E2 no lo considera. (a) La mezcla de fechas es una limitación ya declarada (01 l. 26-27). (c) El inventario de productos se menciona (02 l. 125), pero no se cubre ni se justifica por qué. |
| C6 | **Válido** | Crítico (arreglo trivial) | `exposiciones.yaml: crudo.cobertura_objetivo = 1.0` frente a `\LimiteCrudo` = 50 %-80 %. |
| M1 | **Parcial** | Medio | El uso de la curva soberana está declarado como supuesto (03 l. 185). La tasa a 3 meses de 3.90 % **sí tiene fuente** (SBS CCPSS interpolada a 91 días, `run_all.py:362`), pero el cuadro no la cita. La convención d/360 con tasas efectivas viene del Excel del profesor y se mantiene, explicándola. Falta conciliar el forward con la curva sintética US$ de la SBS (CSBCRD), que es el único proxy público del basis. |
| M2 | **Parcial** | Medio | El desfase OVX/CL es real y sin superficie pública no tiene solución completa. La "brecha" con el 29.3 % es en parte un artefacto: esa cifra sale de **promedios mensuales**, que suavizan la volatilidad. |
| M3 | **Parcial** | Medio | Usar la posición de dic-2025 es una limitación de datos. Los swaps de Citibank son de corto plazo y probablemente ya vencieron, pero el informe no lo dice. Los EEFF intermedios de jun-2026 (SMV) podrían actualizar la posición. |
| M4 | **Válido** | Medio | Designar el NDF como cobertura de flujos sobre partidas monetarias reconocidas es innecesario, porque la NIC 21 ya lleva el efecto a resultados. Es más simple y correcto tratarlo como cobertura económica a VR con cambios en resultados. |
| M5 | **Parcial** | Medio | La NIIF 9 sí permite la cobertura de valor razonable de inventarios. Son válidos los puntos sobre discontinuación y rotación, y sobre que el Cuadro 9 es económico y no contable. |
| M6 | **Parcial** | Medio → bajo en este contexto | Un VaR simple y la vega del collar caben en el informe y suman puntos en Cálculos. El paquete completo (ES, backtesting, stress 2020/2022) no cabe en 10 páginas. |
| M7 | **Válido** | Medio | `run_all.py:565` calcula `CostoSwap` con `q` completo, sin multiplicar por `reparto`: 9.3 en lugar de ~4.7. Medirlo contra el spot y no contra el forward también es discutible. |
| M8 | **Válido** | Medio | 2027 + 4 = 2031 > 2030; la refinanciación no es altamente probable (NIIF 9 6.3.3); se compara una tasa swap con un cupón all-in. |
| M9 | **Parcial** | Bajo-medio (académico) | El uso del D.U. 003-2026 es una propuesta sin análisis legal. Basta una oración de condiciones previas, sin inventar normas. |
| B1 | **Válido** | Bajo | 3,096.0 (Nota 14(d)) frente a 2,110.9 + 996.1 = 3,107.0 (Nota 14(a)). CESCE nominal 722.2 frente a 705.3 en libros. |
| B2 | **Parcial** | Bajo | `TCcierreBCRP*` es de cierre, pero el texto dice "interbancario medio" (quiere decir compra-venta), lo que se presta a confusión. Solo requiere precisar la redacción. |
| B3 | **Parcial** | Bajo | La fecha del 5-oct es la de entrega: **no es un error**. Reuters se cita para el contexto, no para el precio (el precio viene del BCRP), pero hay que revisar la oración. Son válidos: el vencimiento "por confirmar" y los integrantes `\pendiente{...}` (`main.tex:12`). |
| B4 | **Válido** | Bajo | La Ec. (1) no explica que el CCS amortizable intercambia principal dentro de las cuotas. El VR se calcula a TC compra y el Cuadro 5 a TC medio. |
| B5 | **Parcial** | Bajo | La mención a NIIF 7 es válida (una línea). EMIR no aplica a PETROPERÚ; Dodd-Frank solo afecta a un dealer de EE. UU., así que basta una mención. |

**Resumen:** 9 hallazgos válidos, 10 parciales y ninguno inválido por completo. B3 tiene una parte no válida: la
fecha. La aritmética está bien. Lo que falla son la coherencia (C3, C6, M7), los supuestos sobreafirmados (C1, M4)
y dos análisis ausentes (C2 liquidez y C5 exposición).

**Criterio para un trabajo académico:** cuando el dato no es público (contrato BN, CSA, superficie CL, curva swap PEN),
el hallazgo **se levanta declarando el supuesto, cuantificando la sensibilidad y dejando la verificación como
condición previa a la ejecución**, no inventando el dato.

## 2. Tablero de estado

| # | Estado | Fase |
|---|---|---|
| C1 | ⬜ pendiente | 2, 4 |
| C2 | ⬜ pendiente | 2 |
| C3 | ⬜ pendiente | 1, 2 |
| C4 | ⬜ pendiente | 2 |
| C5 | ⬜ pendiente | 3 |
| C6 | ⬜ pendiente | 1 |
| M1 | ⬜ pendiente | 3 |
| M2 | ⬜ pendiente | 2, 4 |
| M3 | ⬜ pendiente | 3, 4 |
| M4 | ⬜ pendiente | 3 |
| M5 | ⬜ pendiente | 3 |
| M6 | ⬜ pendiente | 2 |
| M7 | ⬜ pendiente | 1 |
| M8 | ⬜ pendiente | 1 |
| M9 | ⬜ pendiente | 5 |
| B1 | ⬜ pendiente | 1 |
| B2 | ⬜ pendiente | 1 |
| B3 | ⬜ pendiente | 1, 4 |
| B4 | ⬜ pendiente | 1 |
| B5 | ⬜ pendiente | 5 |

Estados: ⬜ pendiente · 🟡 en curso · ✅ levantado · ➖ aceptado como limitación (declarado en el informe)

## 3. Tareas por fase

### Fase 0 — Línea base
- [ ] `make test && make calc && make pdf` y anotar aquí el número de páginas actual: **__ páginas**.
- [ ] Commit de la línea base antes de tocar nada.

### Fase 1 — Coherencia y correcciones rápidas (solo código, yaml y texto)
- [ ] **C6** `exposiciones.yaml`: `crudo.cobertura_objetivo` → 0.80, dentro del límite, con fuente "Supuesto de
      diseño: tope de la política propuesta". `make calc` y revisar cuánto cambian las cifras de E2.
- [ ] **M7** `run_all.py`: `CostoSwap` × `reparto`, para que refleje solo el volumen del swap. Etiquetar el volumen en
      los Cuadros 8, 9 y 10 ("sobre X MMbl, Y % del inventario"). Redacción: "frente al precio de hoy; frente al
      forward el costo esperado es nulo, porque el *backwardation* ya lo descuenta el mercado".
- [ ] **C3 (texto)** Unificar: el Cuadro 10 dice "Cero (antes de CVA)" hasta tener la cifra de la Fase 2.
- [ ] **M8** `run_all.py`: `FwdSwapRate` con plazo de 2027 a 2030 (3 años), igual al vencimiento del CESCE.
      Reescribir 04 l. 393-398: es una *opción a evaluar* si la refinanciación pasa a ser altamente probable
      (NIIF 9 6.3.3); comparar tasa swap + spread (`\SpreadBonosPb`) frente al 3.285 %; mencionar el riesgo de
      *repricing* de las líneas revolventes. En el Cuadro 10, la columna NIIF 9 de tasa pasa a "Solo si la
      transacción es altamente probable".
- [ ] **B1** Nota al pie o aclaración en la Figura 3: Nota 14(a) frente a 14(d) (la diferencia es el costo
      amortizado y los intereses devengados). Rotular el CESCE como "nominal" frente a "libros". Unificar la base del
      TC del escenario −10 % (usar la misma en los Cuadros 6 y 7).
- [ ] **B2** 02 l. 101: "tipo de cambio interbancario de cierre (promedio compra-venta)".
- [ ] **B3** Revisar la oración que cita a Reuters: solo el contexto, porque el precio viene de BCRP/NYMEX.
      Completar los integrantes en `main.tex:12` (pedir los nombres al grupo).
- [ ] **B4** Una línea después de la Ec. (1): "las cuotas incluyen amortización, por lo que no hay intercambio final
      de nocional". Decidir el TC del VR: **recomendación: TC medio** en el registro contable (NIIF 13 ¶71, precio
      medio como práctica) y TC compra solo en el pricing de la tasa. Aplicarlo en `run_all.py:462-465`.
- [ ] `make test && make calc && make pdf`, revisar páginas y hacer commit "Fase 1".

### Fase 2 — Cálculos nuevos (cada uno en `src/derivados/` + test, con macros en `run_all.py`)
- [ ] **C2 Liquidez por colateral.** Nueva función: valor de mercado conjunto de E1 + E2 bajo choques combinados
      (TC +5/+10 %, WTI +10/+30 %, y el caso adverso conjunto: sol depreciado + crudo al alza). Cuadro pequeño:
      colateral exigible con umbral 0 frente a liquidez disponible (líneas libres 22.3; verificar si se puede citar el
      préstamo puente de US$ 475 MM de Moody's, sep-2026, que está en `data/raw/mercado_2026-09-30/`).
      Conclusión explícita: **la ejecución queda condicionada** a un umbral CSA ≥ X o a la garantía del Estado.
      Cambiar "Bajo" en el Cuadro 10 por la cifra.
- [ ] **C3 CVA.** EPE del CCS con simulación simple del TC (vol `usdpen.vol_implicita_1a`), multiplicada por el spread
      de PETROPERÚ (569 pb, ya calculado) y por LGD 60 % (supuesto declarado). Convertir a pb anuales y obtener la
      tasa all-in = `\CCSTasaUSD` + CVA. Mencionar el riesgo *wrong-way* de forma cualitativa. Macros
      `\CCSCVApb` y `\CCSTasaAllIn`; actualizar el Cuadro 10 y las conclusiones.
- [ ] **C1 Sensibilidad al cronograma.** Recalcular la tasa y el nocional del CCS con cronogramas alternativos
      (36 cuotas desde ene-2026 [base]; 46 cuotas desde mar-2025, que dan 48 − 2 de gracia; tasa nominal/12 frente a
      TEA). Rango de `\CCSTasaUSD` en una línea del Cuadro 3. Explicar la convención TEA → (1+TEA)^(1/12) − 1.
- [ ] **C4 Base.** Usar h* contra Brent (1.156, ρ² = 0.80, ya en `mercado.yaml`) como cifra principal, con h* WTI
      como referencia. Número de contratos con el h* de Brent. Corregir la fuente del yaml: p. 70 = precios de
      **venta** por paridad WTI + spreads. Agregar una oración sobre la alternativa de swaps Brent (ICE).
- [ ] **M6 Métricas.** VaR al 95 % a 1 mes (paramétrico, con la vol histórica diaria) del TC y del inventario, con
      y sin cobertura: una sola tabla de 2×2. Agregar la vega del collar (`opciones.py`).
- [ ] **M2 Volatilidad.** Sensibilidad del strike del call a σ ∈ {35 %, 45 %, 56 %}. Aclarar que el 29.3 % sale de
      promedios mensuales. Mencionar el *skew* como limitación.
- [ ] Pedir al agente `validador-cuantitativo` que recalcule independientemente C2, C3 y C1.
- [ ] Commit "Fase 2".

### Fase 3 — Rediseño de la exposición y de la contabilidad (prosa + parámetros)
- [ ] **C5 + M5 Exposición de crudo.** Recomendación: redefinir la partida cubierta como el **desfase de precio
      entre la compra de crudo y la fijación del precio de venta** (paridad de importación). La exposición pasa a ser
      el inventario que rota en ~1 mes, renovado cada mes. Opciones:
      - (recomendada) mantener el horizonte de 3 meses como **cobertura por capas mensuales** (1/3 del volumen por
        vencimiento nov/dic/ene), cada capa designada sobre el inventario de ese mes y discontinuada al venderse.
        Así se responden (b) y M5 sin rehacer todo el modelo.
      - Agregar una oración sobre (c): el inventario de productos no se cubre porque su precio se traslada por paridad
        de importación con un desfase menor (o se cubre con *crack spreads*, fuera de alcance).
      - (d): explicar el signo, en una oración de la sección 2. Las compras futuras sin precio fijado quedan **largas**
        en el precio y su traslación a ventas las neutraliza; solo el desfase queda expuesto.
      - (a): queda como ➖ limitación declarada.
- [ ] **M4 Contabilidad E1.** NDF como cobertura económica a VR con cambios en resultados, compensando la diferencia de
      cambio de la NIC 21 en el mismo estado. CCS como cobertura de flujos con fuentes de inefectividad (basis,
      CVA, diferencias de cronograma) y opción de excluir el basis (NIIF 9 6.5.16). Quitar "coinciden" y "se
      neutraliza".
- [ ] **M1 Curvas.** Conciliar el forward NDF teórico con el implícito en la curva sintética US$ de la SBS
      (`tasas.usd_sintetica_1a`) y reportar la diferencia como proxy del basis. Citar la fuente de la tasa S/ a
      3 meses en el Cuadro 3. Oración: "tasa indicativa; la ejecutable requiere cotización bancaria".
- [ ] **M3 Posición.** Oración sobre los swaps de Citibank: vencidos o a integrar en la PND según su vencimiento. Si
      la Fase 4 consigue EEFF de jun-2026, actualizar la PCC.
- [ ] Commit "Fase 3".

### Fase 4 — Datos a buscar (lanzar en paralelo desde el inicio con `investigador-mercado`)
- [ ] EEFF intermedios de PETROPERÚ a jun-2026 (SMV): saldo del préstamo BN (¿amortizó en 2026? para validar C1),
      posición en S/ (M3), inventario de crudo (C5a), swaps de Citibank.
- [ ] Fecha exacta de vencimiento de las opciones LO sobre CLF27 en el calendario de CME (B3, M2). Si cambia,
      actualizar `crudo.dias_venc_opciones` y cambiar `estado` a verificado.
- [ ] (Opcional) Vol implícita ATM de CL a 3 meses de alguna fuente pública (M2).

### Fase 5 — Gobierno, revelaciones y cierre
- [ ] **M9** En las condiciones de implementación, agregar como **condiciones previas**: opinión legal sobre el uso
      de los compromisos del D.U. 003-2026 para líneas de derivados, autorización del régimen aplicable a empresas
      del Estado (**verificar la norma** con `investigador-mercado` antes de citarla; no citar sin fuente) y
      verificación independiente de precios con jerarquía de VR Nivel 2 para los instrumentos propuestos.
- [ ] **B5** Media línea: revelaciones NIIF 7 ¶21A-24G en los EEFF; reporte regulatorio a cargo del dealer.
- [ ] Párrafo "Limitaciones" (en la sección 4 o como nota): cronograma BN supuesto, posición a dic-2025, curva
      soberana como proxy, OVX como proxy, sin cotizaciones bancarias. Esto convierte los hallazgos parciales en ➖.
- [ ] Ajustar las conclusiones (05): tasa all-in, condición de liquidez y volumen al 80 %.
- [ ] `make final` (cero avisos, ≤ 10 páginas) y `/revisar`.
- [ ] Actualizar el tablero de la sección 2 y hacer el commit final.

## 4. Decisiones abiertas (requieren al grupo)
1. Integrantes del grupo (B3).
2. Volumen de E2: 80 % (tope) o 70 % (centro del rango). Recomendación: **80 %**, que es el menor cambio.
3. Si el EEFF de jun-2026 contradice el supuesto del BN: rehacer la E1 con el saldo real o mantener el supuesto con
   sensibilidad. Recomendación: usar el saldo real si está disponible.

## 5. Registro de avance
| Fecha | Qué se hizo | Commit |
|---|---|---|
| 2026-10-03 | Dictamen recibido, validado y plan creado | — |
