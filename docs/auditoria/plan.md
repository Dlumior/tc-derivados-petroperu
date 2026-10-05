# Plan para levantar los hallazgos del dictamen de auditoría

Dictamen: [`dictamen.md`](dictamen.md), recibido el 3-oct-2026. Entrega impresa: **5-oct-2026, 19:30**.
Este archivo es el registro de avance: marcar `[x]` al cerrar cada tarea y cambiar el estado en la tabla.

**Reglas que siguen aplicando** (CLAUDE.md): cero cifras tecleadas (todo por `m.set` + `make calc`), todo
insumo con fuente, toda fórmula nueva en `src/derivados/` con su test, y **≤ 10 páginas de cuerpo** (las referencias no cuentan, 3-oct). Cada párrafo que se
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
| C1 | ✅ levantado (cronograma inferido del EEFF de jun-2026; sigue siendo un supuesto declarado) | 2, 4 |
| C2 | ✅ levantado | 2 |
| C3 | ✅ levantado | 1, 2 |
| C4 | ✅ levantado | 2 |
| C5 | ✅ levantado ((a) queda declarado: inventario al cierre de 2025) | 3 |
| C6 | ✅ levantado | 1 |
| M1 | ✅ levantado | 3 |
| M2 | ✅ levantado (salvo el skew, que queda declarado) | 2, 4 |
| M3 | ✅ levantado en BN y Citibank; ➖ CxP y CxC en S/ a sep-2026 (los EEFF intermedios no traen la posición en S/) | 3, 4 |
| M4 | ✅ levantado | 3 |
| M5 | ✅ levantado | 3 |
| M6 | ✅ levantado (VaR + vega; ES y backtesting quedan fuera de alcance) | 2 |
| M7 | ✅ levantado | 1 |
| M8 | ✅ levantado | 1 |
| M9 | ✅ levantado | 5 |
| B1 | ✅ levantado | 1 |
| B2 | ✅ levantado | 1 |
| B3 | ✅ levantado | 1, 4 |
| B4 | ✅ levantado | 1 |
| B5 | ✅ levantado | 5 |

Estados: ⬜ pendiente · 🟡 en curso · ✅ levantado · ➖ aceptado como limitación (declarado en el informe)

## 3. Tareas por fase

### Fase 0 — Línea base
- [x] `make test && make calc && make pdf` y anotar aquí el número de páginas actual: **9 páginas** (la 9 está
      llena: termina en las referencias). **Margen: ~1 página** para todo lo que agreguen las fases 1 a 5.
      26 tests OK. `make calc` regenera sin cambios de cifras (las figuras solo cambian en metadatos).
      Avisos: 1 insumo PENDIENTE (`tasas.spread_credito_petroperu`, ya conocido) y 3 *overfull hbox*
      (10.6 pt, 1.8 pt y 0.8 pt); resolverlos en la Fase 5 con `make final`.
- [x] Commit de la línea base antes de tocar nada (2a0a387: plan + dictamen; el estado del informe es el de 9167c85).

### Fase 1 — Coherencia y correcciones rápidas (solo código, yaml y texto)
- [x] **C6** `exposiciones.yaml`: `crudo.cobertura_objetivo` → 0.80, dentro del límite, con fuente "Supuesto de
      diseño: tope de la política propuesta". `make calc` y revisar cuánto cambian las cifras de E2.
- [x] **M7** `run_all.py`: `CostoSwap` × `reparto`, para que refleje solo el volumen del swap. Etiquetar el volumen en
      los Cuadros 8, 9 y 10 ("sobre X MMbl, Y % del inventario"). Redacción: "frente al precio de hoy; frente al
      forward el costo esperado es nulo, porque el *backwardation* ya lo descuenta el mercado".
- [x] **C3 (texto)** Unificar: el Cuadro 10 dice "Cero (antes de CVA)" hasta tener la cifra de la Fase 2.
- [x] **M8** `run_all.py`: `FwdSwapRate` con plazo de 2027 a 2030 (3 años), igual al vencimiento del CESCE.
      Reescribir 04 l. 393-398: es una *opción a evaluar* si la refinanciación pasa a ser altamente probable
      (NIIF 9 6.3.3); comparar tasa swap + spread (`\SpreadBonosPb`) frente al 3.285 %; mencionar el riesgo de
      *repricing* de las líneas revolventes. En el Cuadro 10, la columna NIIF 9 de tasa pasa a "Solo si la
      transacción es altamente probable".
- [x] **B1** Nota al pie o aclaración en la Figura 3: Nota 14(a) frente a 14(d) (la diferencia es el costo
      amortizado y los intereses devengados). Rotular el CESCE como "nominal" frente a "libros". Unificar la base del
      TC del escenario −10 % (usar la misma en los Cuadros 6 y 7).
- [x] **B2** 02 l. 101: "tipo de cambio interbancario de cierre (promedio compra-venta)".
- [x] **B3** Revisar la oración que cita a Reuters: solo el contexto, porque el precio viene de BCRP/NYMEX.
      Completar los integrantes en `main.tex:12` (pedir los nombres al grupo).
- [x] **B4** Una línea después de la Ec. (1): "las cuotas incluyen amortización, por lo que no hay intercambio final
      de nocional". Decidir el TC del VR: **recomendación: TC medio** en el registro contable (NIIF 13 ¶71, precio
      medio como práctica) y TC compra solo en el pricing de la tasa. Aplicarlo en `run_all.py:462-465`.
- [x] `make test && make calc && make pdf`, revisar páginas y hacer commit "Fase 1".

  **Resultado de la Fase 1:**
  - **E2 al 80 %:** ahora los Cuadros 8, 9 y 10 miden el resultado sobre el **inventario total**, con el 20 %
    abierto. Como con ese 20 % la pérdida ya no tiene piso, "pérdida máxima" se cambió por "pérdida si el WTI cae
    30 %": 80.6 sin cobertura, 50.2 con el collar y 36.9 con la propuesta. El costo del swap bajó de 9.3 a 3.7.
  - **Tasa forward del swap de inicio diferido:** 4.85 % (2027-2030).
  - **B1, base del TC:** no se unificó. Cada cuadro se rotuló con su base (NDF a TC compra, escenarios a TC medio),
    porque forzar el TC medio en el NDF distorsionaba su costo. El valor razonable del registro contable pasó a TC
    medio.
  - **Páginas:** el PDF tiene 10 en total, pero el **cuerpo ocupa 9/10**. Desde el 3-oct las referencias no cuentan
    para el límite (`make check` mide hasta `\label{fin-cuerpo}`). Queda **~1 página** de cuerpo para las fases 2 a 5.

### Fase 2 — Cálculos nuevos (cada uno en `src/derivados/` + test, con macros en `run_all.py`)
- [x] **C2 Liquidez por colateral.** Nueva función: valor de mercado conjunto de E1 + E2 bajo choques combinados
      (TC +5/+10 %, WTI +10/+30 %, y el caso adverso conjunto: sol depreciado + crudo al alza). Cuadro pequeño:
      colateral exigible con umbral 0 frente a liquidez disponible (líneas libres 22.3; verificar si se puede citar el
      préstamo puente de US$ 475 MM de Moody's, sep-2026, que está en `data/raw/mercado_2026-09-30/`).
      Conclusión explícita: **la ejecución queda condicionada** a un umbral CSA ≥ X o a la garantía del Estado.
      Cambiar "Bajo" en el Cuadro 10 por la cifra.
- [x] **C3 CVA.** EPE del CCS con simulación simple del TC (vol `usdpen.vol_implicita_1a`), multiplicada por el spread
      de PETROPERÚ (569 pb, ya calculado) y por LGD 60 % (supuesto declarado). Convertir a pb anuales y obtener la
      tasa all-in = `\CCSTasaUSD` + CVA. Mencionar el riesgo *wrong-way* de forma cualitativa. Macros
      `\CCSCVApb` y `\CCSTasaAllIn`; actualizar el Cuadro 10 y las conclusiones.
- [x] **C1 Sensibilidad al cronograma.** Recalcular la tasa y el nocional del CCS con cronogramas alternativos
      (36 cuotas desde ene-2026 [base]; 46 cuotas desde mar-2025, que dan 48 − 2 de gracia; tasa nominal/12 frente a
      TEA). Rango de `\CCSTasaUSD` en una línea del Cuadro 3. Explicar la convención TEA → (1+TEA)^(1/12) − 1.
- [x] **C4 Base.** Usar h* contra Brent (1.156, ρ² = 0.80, ya en `mercado.yaml`) como cifra principal, con h* WTI
      como referencia. Número de contratos con el h* de Brent. Corregir la fuente del yaml: p. 70 = precios de
      **venta** por paridad WTI + spreads. Agregar una oración sobre la alternativa de swaps Brent (ICE).
- [x] **M6 Métricas.** VaR al 95 % a 1 mes (paramétrico, con la vol histórica diaria) del TC y del inventario, con
      y sin cobertura: una sola tabla de 2×2. Agregar la vega del collar (`opciones.py`).
- [x] **M2 Volatilidad.** Sensibilidad del strike del call a σ ∈ {35 %, 45 %, 56 %}. Aclarar que el 29.3 % sale de
      promedios mensuales. Mencionar el *skew* como limitación.
- [ ] Pedir al agente `validador-cuantitativo` que recalcule independientemente C2, C3 y C1 (pendiente: validé a
      mano las cifras clave y hay tests nuevos, incluido uno que contrasta la EPE analítica con Monte Carlo).
- [x] Commit "Fase 2" (184a824).

  **Resultado de la Fase 2** (nuevo módulo `src/derivados/riesgo.py` + `tests/test_riesgo.py`, 33 tests):
  - **C2 (colateral con umbral cero):** 97.0 con TC +10 %, 52.5 con WTI +30 % y **149.5 en el estrés conjunto**,
    frente a 22.2 de líneas libres. La ejecución queda condicionada a un umbral CSA ≥ US$ 127 MM o a la garantía del
    Estado. El préstamo puente de US$ 475 MM (Moody's) se menciona, pero no se cuenta como liquidez porque tiene
    destino específico. Se agregó el Cuadro 12.
  - **C3 (CVA):** con EPE analítica (put de Black sobre 1/S), σ TC 6.75 %, spread de 569 pb y LGD de 60 % (supuesto,
    agregado en `mercado.yaml`), el CVA es de **US$ 1.0 MM ≈ 10 pb**, para una tasa all-in de **5.98 %**. Se declara
    que es un mínimo (sin FVA ni wrong-way).
  - **C1 (cronograma):** con cronogramas alternativos (TNA/12, lineal, 2026 solo intereses), la tasa del CCS queda
    entre 5.88 % y 6.02 % y el nocional entre US$ 821.8 y 1,095.7 MM. La convención TEA → mensual queda explicada
    (cuota de 113.6 frente a 113.8 con TNA/12).
  - **C4 (base):** h* se recalcula en `run_all.py`. Brent: **1.14 (ρ² = 79 %)**; WTI Cushing: 1.01 (99 %). Con
    Brent serían 2,648 contratos. El WTI se justifica por la Nota 11(viii), p. 70 (precios de venta por paridad
    WTI + spreads), que antes estaba citada como "costos de compra"; ya está corregido en el yaml.
  - **M2:** la volatilidad realizada del CL en un año es **55.8 %**, prácticamente igual al OVX (56.1 %). El strike
    del call casi no se mueve (97.19 con σ 35 %, 97.60 con 45 %, 98.08 con 56 %).
  - **M6:** VaR al 95 % al vencimiento: E1 baja de 63.7 a 3.1 y E2 de 94.3 a 39.6 (Cuadro 11). La vega del collar
    es casi nula.
  - **Páginas: cuerpo 10/10**; termina a ~1/3 de la página 10, así que quedan **~0.6 páginas**. Las fases 3 y 5
    deben **reemplazar** texto, no agregarlo.

### Fase 3 — Rediseño de la exposición y de la contabilidad (prosa + parámetros)
- [x] **C5 + M5 Exposición de crudo.** Recomendación: redefinir la partida cubierta como el **desfase de precio
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
- [x] **M4 Contabilidad E1.** NDF como cobertura económica a VR con cambios en resultados, compensando la diferencia de
      cambio de la NIC 21 en el mismo estado. CCS como cobertura de flujos con fuentes de inefectividad (basis,
      CVA, diferencias de cronograma) y opción de excluir el basis (NIIF 9 6.5.16). Quitar "coinciden" y "se
      neutraliza".
- [x] **M1 Curvas.** Conciliar el forward NDF teórico con el implícito en la curva sintética US$ de la SBS
      (`tasas.usd_sintetica_1a`) y reportar la diferencia como proxy del basis. Citar la fuente de la tasa S/ a
      3 meses en el Cuadro 3. Oración: "tasa indicativa; la ejecutable requiere cotización bancaria".
- [x] **M3 Posición.** Oración sobre los swaps de Citibank: vencidos o a integrar en la PND según su vencimiento. Si
      la Fase 4 consigue EEFF de jun-2026, actualizar la PCC.
- [x] Commit "Fase 3".

  **Resultado de la Fase 3:**
  - **C5 + M5:** la exposición se redefinió como el **desfase entre la compra y la fijación del precio de venta**.
    Las compras sin precio no suman exposición, porque las ventas que financian fijan su precio en el mismo mercado.
    La rotación es de 33 días (macro `\RotacionDias`). El collar pasó a **3 capas mensuales** (CLX26, CLZ26 y CLF27,
    con vencimientos de 21, 52 y 81 días; puts 83.30 / 80.10 / 77.90; calls 103.80 / 100.42 / 98.08). El swap liquida
    mensualmente. Cada capa se designa por su mes y se discontinúa al venderse (6.5.6), y el Cuadro 9 se aclara como
    económico (NIC 2). El inventario de productos no se cubre y se dice por qué. Nuevas cifras: pérdida con WTI −30 %
    de 34.0 con la propuesta y 44.4 con el collar; colateral en el estrés conjunto de 148.9.
    Se agregaron los vencimientos de nov/dic a `mercado.yaml` como `supuesto` (por confirmar en la Fase 4).
  - **M4:** el CCS se designa como cobertura de flujos, con sus fuentes de inefectividad y la opción de excluir el
    basis (6.5.16). El NDF queda a VR con cambios en resultados, compensando la NIC 21 sin contabilidad de coberturas.
    Se eliminaron "coinciden" y "se neutraliza" (esto también cierra la parte NIIF 9 de C1).
  - **M1:** con la curva sintética US$ de la SBS (CSBCRD), el forward es 3.4346 (0.6 pips de diferencia) y la tasa del
    CCS 5.92 % (frente a 5.88 %): el basis local es de ~4 pb. Se cita la fuente de la tasa a 3 meses (SBS, 91 días).
  - **M3:** una oración sobre la antigüedad de la posición y sobre los swaps de Citibank (se suponen vencidos; si no,
    se restan del NDF).
  - **Páginas: cuerpo 10/10**; termina hacia la línea 32 de 55 de la página 10, así que quedan **~0.4 páginas** para
    la Fase 5.

### Fase 4 — Datos a buscar (lanzar en paralelo desde el inicio con `investigador-mercado`)
- [x] EEFF intermedios de PETROPERÚ a jun-2026 (sitio de inversionistas; copia en `data/raw/eeff_2026/`):
      saldo del préstamo BN (¿amortizó en 2026? para validar C1), posición en S/ (M3), inventario de crudo (C5a),
      swaps de Citibank.
- [x] Fecha exacta de vencimiento de las opciones LO (B3, M2). La página de CME no respondió; se usó la regla
      publicada por StoneX. Queda como `supuesto` con su fuente.
- [x] (Opcional) Vol implícita ATM de CL a 3 meses (M2): no hay fuente pública. Se mantiene el OVX, ya respaldado
      por la vol realizada (Fase 2).

  **Resultado de la Fase 4:**
  - **BN (C1):** al 30-jun-2026 el saldo sigue en **S/ 3,765.6 MM, sin pagos de principal**, e **íntegramente no
    corriente** (Nota 13). Por la NIC 1, no vence principal antes de jul-2027. **Nuevo caso base:** solo intereses
    hasta jun-2027 (S/ 17.0 MM/mes) y 18 cuotas francesas de S/ 218.3 MM (jul-2027 a dic-2028). El supuesto anterior
    (36 cuotas desde ene-2026) quedaba refutado. Cifras E1 nuevas:
    - nocional del CCS: US$ 1,095.7 MM;
    - tasa: 5.87 %, o 5.98 % con CVA de 11 pb; rango por cronograma: 5.82 %-6.01 %;
    - PCC hoy: S/ 4,704.0 MM, igual que en dic-2025;
    - pérdida con TC −10 %: 152.0 sin cobertura y 6.1 con cobertura.
  - **C2 recalculado:** colateral de **121.2 con TC +10 %** y **172.9 en el estrés conjunto**; el umbral CSA
    necesario sube a **US$ 151 MM**.
  - **Citibank (M3):** los swaps **siguen vigentes** (activo de US$ 5.9 MM al 30-jun-2026, Nota 8). El texto ahora
    dice que su nocional debe restarse del NDF.
  - **Posición en S/ a jun-2026:** los EEFF intermedios no traen la tabla de la Nota 3; queda como limitación.
    Inventario de crudo a jun-2026: US$ 204.9 MM (sin MBL); registrado en el yaml.
  - **Vencimientos LO (B3):** con la regla "7 días hábiles antes del 26 del mes previo" son **17 / 50 / 79 días**
    (15-oct, 17-nov y 16-dic-2026). La regla anterior era errónea.
  - Nueva referencia: `petroperu2026eeffjun`.
  - **Páginas:** cuerpo 10/10, sin cambios (termina en la línea 32 de la p. 10).

### Fase 5 — Gobierno, revelaciones y cierre
- [x] **M9** En las condiciones de implementación, agregar como **condiciones previas**: opinión legal sobre el uso
      de los compromisos del D.U. 003-2026 para líneas de derivados, autorización del régimen aplicable a empresas
      del Estado (**verificar la norma** con `investigador-mercado` antes de citarla; no citar sin fuente) y
      verificación independiente de precios con jerarquía de VR Nivel 2 para los instrumentos propuestos.
- [x] **B5** Media línea: revelaciones NIIF 7 ¶21A-24G en los EEFF; reporte regulatorio a cargo del dealer.
- [x] Párrafo "Limitaciones" (en la sección 4 o como nota): cronograma BN supuesto, posición a dic-2025, curva
      soberana como proxy, OVX como proxy, sin cotizaciones bancarias. Esto convierte los hallazgos parciales en ➖.
- [x] Ajustar las conclusiones (05): tasa all-in, condición de liquidez y volumen al 80 %.
- [x] `make final` (cero avisos, ≤ 10 páginas) y `/revisar`.
- [x] Actualizar el tablero de la sección 2 y hacer el commit final.

  **Resultado de la Fase 5:**
  - **M9:** se agregó la condición previa (iii): opinión de la Gerencia Legal y autorización del régimen de
    endeudamiento y tesorería de la empresa estatal, incluida la viabilidad de usar el D.U. 003-2026. La condición
    (vi) agrega la verificación independiente de precios y el Nivel 2 de la NIIF 13. No se citó ninguna norma
    específica de autorización sin verificarla.
  - **B5:** revelaciones NIIF 7 ¶21A-24G y reporte regulatorio a cargo del banco.
  - Nuevo párrafo **Limitaciones** en la sección 4. Conclusiones: el CCS se ejecuta una vez firmado el CSA con el
    umbral requerido.
  - `tasas.spread_credito_petroperu` pasó de PENDIENTE a `supuesto`, con la nota de que no se usa; ya no bloquea
    `make final`. Se corrigieron las líneas desbordadas (`\emergencystretch`, ancho del minipage del NDF) y
    `\headheight`.
  - **`make final`: OK, 0 errores y 0 avisos; cuerpo 10/10** (termina en la línea 37 de la p. 10).

### Revisión independiente (`/revisar`, 3-oct-2026)
El **validador cuantitativo** recalculó unas 50 cifras sin la librería: **0 errores aritméticos**. Su hallazgo de
"11 páginas" no aplica, porque las referencias no cuentan; ya se actualizó su definición. El **revisor de rúbrica**
estimó **17.4/20**. El grupo aprobó aplicar todo:
- [x] **A (consistencia):**
  - colateral sobre el MtM total a TC medio: 121.6 con TC +10 %, **173.4** en el estrés conjunto, umbral **151**;
  - spread y rendimiento rotulados "a dic-2025", con un CVA de **6 pb** usando el spread de ago-2026 (318 pb);
  - swap de inicio diferido con pago anual (**4.91 %**);
  - rótulos de volumen en E2 ("Solo swap/collar/put (80 %)", collar de 1.16 MMbl);
  - crudo con WTI −20 % a precio de cierre (33.3) y al de hoy (53.7);
  - explicación de la brecha entre la compensación nominal y el valor razonable (inefectividad);
  - volatilidad del TC con su fuente; repricing de las líneas en el Cuadro 1; canal wrong-way; columna "=F ene".
- [x] **B (forma):** "setiembre" también en la bibliografía; fuentes de los Cuadros 11 y 12; supuestos rotulados
  (umbral cero, estrés conjunto); se quitó "importador neto" (sin fuente); la primera conclusión ahora es una
  recomendación; "cayó 19.9 %" sin doble signo.
- [x] **C3:** la Fig. 6 traza la propuesta 50/50.
- [x] **C1:** demostración del neto constante del swap y Cuadro de posiciones en barriles (físico / derivados /
  global: 2.90 → 1.12 MMbl).
- [x] **C2:** el Cuadro 6 pasó a Inicio/Vencimiento con fila Total y valor por S/ 1,000.
- [x] **C4:** se recortaron a una frase la sensibilidad del BN y el párrafo OVX/skew.
- `make final`: OK, 0 errores y 0 avisos; cuerpo 10/10 (termina en la línea 50 de la p. 10).

## 4. Decisiones abiertas (requieren al grupo)
1. ~~Integrantes del grupo (B3).~~ Resuelto el 3-oct.
2. ~~Volumen de E2~~: el grupo eligió **80 %** (3-oct).
3. Si el EEFF de jun-2026 contradice el supuesto del BN: rehacer la E1 con el saldo real o mantener el supuesto con
   sensibilidad. Recomendación: usar el saldo real si está disponible.

## 5. Registro de avance
| Fecha | Qué se hizo | Commit |
|---|---|---|
| 2026-10-03 | Dictamen recibido, validado y plan creado | 2a0a387 |
| 2026-10-03 | Fase 0: línea base, 9 páginas, 26 tests OK | 5ebfac7 |
| 2026-10-03 | Fase 1: C6, M7, M8, B1, B2, B4 levantados; C3 y B3 parciales | 91a725a |
| 2026-10-03 | Referencias fuera del límite de 10 páginas; el verificador mide solo el cuerpo (9/10) | ffdfc4d |
| 2026-10-03 | Fase 2: C2, C3, C4, M2 y M6 levantados; C1 parcial; cuerpo 10/10 | 184a824 |
| 2026-10-03 | Fase 3: C5, M1, M4 y M5 levantados; C1 y M3 a la espera de la Fase 4 | 610b583 |
| 2026-10-03 | Fase 4: EEFF jun-2026 (BN sin amortizar hasta jul-2027, swaps Citi vigentes) y vencimientos LO | ec98d53 |
| 2026-10-03 | Fase 5: M9, B5, limitaciones; make final OK | 840c8b1 |
| 2026-10-03 | /revisar: correcciones A, B y C del validador y del revisor de rúbrica | (este commit) |
| 2026-10-05 | Reescritura con la skill informe-para-gerente-general: respuesta ejecutiva (memo Para/De/Asunto), conclusión al inicio de cada sección, definiciones operativas, objeciones respondidas, supuestos etiquetados, indicadores a vigilar y principio final; títulos de cuadros con la conclusión; macros `SensFXUnPct` y `SensWTIUnDolar`. make final OK, cuerpo 10/10 | (sin commit) |
| 2026-10-05 | Sin recuadro ejecutivo y títulos simplificados (grupo); se quitan las fórmulas del CCS/NDF y de Black (método en prosa) y se agrega la Fig. `f_e2_collar` (armado del collar en 3 pasos). make final OK, cuerpo 10/10 | (sin commit) |
