# Dictamen de auditoría técnica (recibido el 3-oct-2026)

Copia textual del dictamen externo sobre el informe (versión con valorización al 28-sep-2026).
El plan para levantar los hallazgos está en [`plan.md`](plan.md).

## 1. Resumen ejecutivo del dictamen

- **Conclusión global:** **No aceptable** en su forma actual como base para una decisión de la Gerencia General.
- **Nº de hallazgos:** Críticos **6** | Medios **9** | Bajos **5**

Recalculé las cifras clave: el annuity del BN, el nocional del CCS, el forward del NDF, las primas Black del put y del call, el convenience yield, los Cuadros 5 a 9 y la sensibilidad de los bonos. La aritmética interna es en general consistente. Los problemas están en los supuestos de base, en la delimitación de la exposición, en la liquidez por colateral y en la elegibilidad contable. Esos problemas invalidan las conclusiones aunque las sumas cuadren.

## 2. Tabla de hallazgos

| # | Severidad | Área | Hallazgo | Por qué está mal / no claro | Evidencia faltante | Recomendación |
|---|---|---|---|---|---|---|
| C1 | **Crítico** | Valuación E1 / NIIF 9 | Toda la E1 descansa en un cronograma supuesto del préstamo BN (36 cuotas francesas desde ene-2026), que contradice la fuente citada (46 cuotas de ene-2025 a dic-2028). | Ene-2025 a dic-2028 son 48 meses, no 46, así que la fuente ya es incoherente tal como se cita. El nocional (838.2), la tasa (5.88 %), los flujos (Cuadro 4) y la afirmación de que "nocional, fechas y tasa coinciden" dependen de ese supuesto. | Cronograma contractual del BN, convención de la tasa (TEA vs. nominal) y fechas de pago. | Rehacer la E1 con el cronograma contractual. Mientras no exista, declarar la E1 como ilustrativa y no designable. |
| C2 | **Crítico** | Liquidez / colateral | No se cuantifica la exposición a llamadas de colateral bajo CSA. Aun así, el informe califica el efecto en liquidez como "Bajo". | Con TC +10 %, los derivados de E1 serían pasivos por US$ 97.1 MM (77.4 + 19.7). Con WTI +10 %, E2 suma US$ 21.2 MM más. Total: US$ 118.3 MM, frente a solo US$ 22.3 MM de líneas revolventes disponibles. | Términos CSA indicativos (umbral, MTA, IA), stress conjunto TC/WTI y flujos de liquidación trimestral de los NDF. | Modelar llamadas de margen bajo stress (PFE al 95-99 %), dimensionar la línea de liquidez y condicionar la ejecución a umbrales confirmados por los bancos. |
| C3 | **Crítico** | Contraparte / costo | El Cuadro 10 dice "Costo inicial: Cero (CVA incluido en la tasa)", pero el texto y las conclusiones dicen "5.88 % antes de CVA". El CVA no se cuantifica. | La contradicción altera el costo reportado de la estrategia principal. Para una contraparte B-/Caa1 hay además riesgo wrong-way: una depreciación del sol coincide con estrés soberano y de la Compañía. | CVA/FVA/KVA estimados, EPE/PFE del CCS y cotizaciones indicativas de bancos. | Estimar el CVA (EPE × spread × LGD) y FVA, reportar la tasa all-in y corregir el Cuadro 10. |
| C4 | **Crítico** | Riesgo de base / NIIF 9 | E2 cubre con WTI una exposición referida a Brent y a crudos pesados con descuento. El riesgo de base no se cuantifica. | h* = 1.01 se calculó con WTI Cushing contra el futuro CL, es decir, el instrumento contra sí mismo, así que no mide la base real (Brent-WTI hoy US$ 12.7/bl). Bajo NIIF 9 6.3.7, el componente WTI debe ser identificable por separado y medible con fiabilidad. No se demuestra. | Serie histórica de costos de compra por crudo y regresión contra WTI y contra Brent. | Evaluar swaps y opciones sobre Brent (ICE), estimar h* contra el costo real y justificar el componente de riesgo. |
| C5 | **Crítico** | Delimitación de exposición | La exposición de crudo está mal definida. | (a) Usa el volumen al 31-dic-2025 con precios de sep-2026. (b) La rotación implícita es de ~33 días (2,901 MBL / 87 MBDC), pero la cobertura dura ~3 meses, lo que deja sobrecobertura y una posición especulativa residual. (c) Omite el inventario de productos (hasta US$ 395.1 MM). (d) Ignora la exposición de compras, de signo opuesto, y la traslación vía paridad de importación y FEPC. | Inventario a la fecha de valorización, perfil de rotación y mapa de traslación de precios por producto. | Redefinir la exposición neta (inventario + compras comprometidas − ventas indexadas) por horizonte, y cubrir sobre esa base. |
| C6 | **Crítico** | Límites / coherencia | E2 cubre el 100 % del inventario (50 % swap + 50 % collar), por encima del límite de 50-80 % que el propio informe propone para la Política de Cobertura. | La estrategia incumpliría la política desde el primer día. | No aplica: la contradicción es interna al informe. | Ajustar el volumen al rango o justificar y modificar el límite. |
| M1 | Medio | Curvas / pricing E1 | La pata en S/ se descuenta con la curva soberana SBS, sin basis cross-currency. Se usa d/360 con tasas efectivas, y la tasa S/ a 3 meses (3.90 %) no tiene fuente. | Un CCS se valoriza con curvas swap/CCS en PEN y el basis de mercado; la curva soberana no es la de fondeo colateralizado. El 5.88 % no es una tasa ejecutable. | Curva swap PEN (OIS/IRS), puntos forward NDF de mercado (onshore y offshore) y fuente de la tasa a 3 m. | Revalorizar con curvas de mercado y el basis, y conciliar el forward teórico con los puntos NDF cotizados. |
| M2 | Medio | Volatilidad / opciones | σ = 56.1 % sale del OVX (30 días, opciones sobre USO), aplicado a opciones CL de 81 días con volatilidad plana y sin skew. | Hay desfase de plazo y de subyacente. Sin smile, el strike de costo cero (98.08) no es confiable. Además, la volatilidad histórica es 29.3 %, una brecha no explicada. | Superficie de volatilidad CL por strike y plazo, y cotizaciones indicativas. | Recalibrar con la superficie de mercado e incluir el bid-ask del banco en el strike del call. |
| M3 | Medio | Datos / exposición E1 | La posición en S/ al 28-sep-2026 arrastra saldos de dic-2025 (CxP, CxC) y solo descuenta las 9 cuotas del BN. Los swaps vigentes con Citibank (US$ 14.6 MM) se excluyen de la posición en derivados (PND). | El nocional del NDF (750.7) se apoya en datos de 9 meses de antigüedad, y los swaps de Citibank pueden duplicar cobertura. | Posición en S/ actualizada y detalle de los swaps de Citibank (nocional, sentido, vencimiento). | Recalcular la posición contable (PCC) y la PND con datos vigentes e integrar los swaps de Citibank. |
| M4 | Medio | Contabilidad E1 | Se designa el NDF como cobertura de flujos sobre CxP, que es una cartera rotativa, neta de CxC y formada por partidas monetarias ya reconocidas. Se afirma que la volatilidad "se neutraliza". | Una posición neta solo se admite con las condiciones de NIIF 9 6.6. Sobre partidas monetarias, la NIC 21 ya lleva el efecto a resultados. El basis y el CVA generan inefectividad, y no se trata la exclusión del basis (6.5.16). | Documentación de la cobertura, ratio de cobertura y fuentes de inefectividad. | Evaluar una cobertura económica a valor razonable con cambios en resultados para el NDF y documentar el CCS con su análisis de inefectividad. |
| M5 | Medio | Contabilidad E2 | Se propone cobertura de valor razonable de un inventario medido a costo/VNR (NIC 2). El Cuadro 9 asume que la pérdida equivale al cambio total de precio. | Al venderse el inventario, en ~33 días, la relación debe discontinuarse o rebalancearse. La pérdida contable depende del costo y del VNR, no del spot. | Política de discontinuación y rebalanceo, y costo unitario del inventario. | Diseñar coberturas por lotes o capas y definir el tratamiento de la discontinuación. |
| M6 | Medio | Métricas de riesgo | No hay VaR, ES, backtesting, PFE/EPE, griegas del collar (vega, gamma) ni sensibilidad a supuestos. Solo se presentan choques de ±10 % (TC) y ±30 % (WTI). | No se puede evaluar el riesgo residual ni el consumo de límites. | Ninguno de esos cálculos. | Incorporar VaR/ES, stress histórico (2020 y 2022), griegas y análisis de sensibilidad a cronograma y volatilidad. |
| M7 | Medio | Coherencia de cifras E2 | El Cuadro 10 asigna al swap un costo de US$ 9.3 MM (equivale al 100 % del volumen); con el 50 % propuesto sería ~US$ 4.7 MM. Ese "costo" por backwardation se mide contra el spot. | Hay mezcla de bases de volumen entre los Cuadros 8, 9 y 10 y el registro contable. El forward no es un costo frente al spot esperado. | No aplica. | Etiquetar los volúmenes de forma explícita y medir el costo contra el forward. |
| M8 | Medio | Tasa de interés | Se propone un forward-starting swap o rate lock sobre una refinanciación del CESCE que no es altamente probable, por el incumplimiento de covenant. El plazo (2027 + 4 = 2031) excede el vencimiento de 2030. Se compara una tasa swap con un cupón all-in. | Incumple NIIF 9 6.3.3 para una transacción prevista. La comparación de 4.83 % contra 3.285 % no es homogénea. Las líneas de corto plazo revolventes sí tienen riesgo de repricing. | Términos de la refinanciación y probabilidad de que ocurra. | Reformular como opción a evaluar, no como recomendación, y corregir plazo y comparativo. |
| M9 | Medio | Gobierno / legal / control | Se propone usar el D.U. 003-2026 como respaldo de líneas de derivados sin análisis legal. No se analiza el régimen de autorización de derivados para una empresa estatal (MEF/FONAFE). No se tratan la independencia de la valuación ni la jerarquía de valor razonable (Nivel 2/3). | Existe riesgo de que la estrategia no sea legalmente ejecutable, y falta control sobre los modelos. | Opinión legal, normativa de endeudamiento y tesorería aplicable, y esquema de verificación independiente de precios. | Obtener una opinión legal previa y definir la función de verificación independiente de precios y el nivel de jerarquía por instrumento. |
| B1 | Bajo | Cifras | Bonos: 3,096 en el texto vs. 3,107 en la Figura 3 (2,111 + 996). CESCE: 722.2 vs. 705. El escenario de TC −10 % usa 3.093 (compra) o 3.094 (medio) según el cuadro. | Pequeñas inconsistencias, probablemente por intereses devengados y por la base de TC. | — | Conciliar las cifras y unificar la base. |
| B2 | Bajo | Presentación | La diferencia de cambio del BN se explica con TC promedio (3.765 → 3.361), pero se calcula con TC de cierre. | Mezcla promedio con cierre. | — | Usar TC de cierre SBS. |
| B3 | Bajo | Trazabilidad | El informe está fechado el 5-oct-2026 (posterior a hoy). Usa un artículo de Reuters del 29-sep para un precio del 28-sep. El vencimiento de las opciones está "por confirmar". Los integrantes figuran como pendientes. | Problemas de trazabilidad documental. | — | Corregir. |
| B4 | Bajo | Metodología E1 | La Ec. (1) no explicita el tratamiento del intercambio de nocionales. El valor razonable se convierte a TC compra y no a TC medio (NIIF 13 ¶70-71), lo que no es consistente con el Cuadro 5. | Falta precisión metodológica. | — | Explicitar la convención. |
| B5 | Bajo | Revelaciones | No se mencionan las revelaciones de NIIF 7 (¶21A-24G) ni el reporte regulatorio de la contraparte (EMIR, Dodd-Frank). | Falta de exhaustividad documental. | — | Incluirlos en el plan de implementación. |

## 3. Detalle por hallazgo

**C1. Cronograma supuesto del préstamo BN**
- **Descripción:** El informe reconoce que "el EEFF no detalla el cronograma" y supone 36 cuotas francesas. Mi recálculo reproduce la cuota de S/ 113.6 MM solo con TEA 5.55 % convertida a tasa mensual, una convención que no se revela. Con tasa nominal/12, la cuota sería ≈ S/ 113.8 MM.
- **Fundamento:** NIIF 9 B6.4.14 exige que la relación económica se demuestre con los términos reales. Una designación basada en términos supuestos no es documentable (6.4.1(b)).
- **Riesgo:** Si el cronograma real difiere, el CCS genera flujos descalzados, inefectividad y una posible posición abierta de cientos de millones de soles.
- **Recomendación:** Obtener el contrato del BN y rehacer los Cuadros 3, 4, 5 y 7 y la tasa de equilibrio.

**C2. Liquidez por colateral**
- **Descripción:** El informe descarta los futuros por las llamadas de margen, pero propone US$ ~840 MM de nocional OTC con una contraparte Caa1 bajo CSA "con umbrales altos" que no se han confirmado.
- **Fundamento:** Con un rating B-/Caa1, la práctica bancaria es umbral cero o margen inicial independiente. Un shock conjunto (alza del crudo con depreciación del PEN) es plausible porque el Perú es importador neto de crudo.
- **Riesgo:** Llamadas de hasta US$ 118 MM frente a US$ 22 MM disponibles. La cobertura podría acelerar el problema de empresa en marcha que pretende mitigar.
- **Recomendación:** Calcular el PFE de colateral a 1 mes con choques conjuntos y no ejecutar sin umbrales firmados o sin una garantía estatal confirmada.

**C3. CVA no cuantificado y contradictorio**
- **Descripción:** La tasa del CCS se presenta antes de CVA en el texto y con CVA incluido en el Cuadro 10.
- **Fundamento:** NIIF 13 ¶42 y ¶48 exigen incorporar el riesgo de crédito en el valor razonable. El riesgo wrong-way agrava el CVA.
- **Riesgo:** El costo real está subestimado y existe la posibilidad de que ningún banco cotice.
- **Recomendación:** Estimar CVA y FVA, presentar la tasa all-in y el costo en puntos básicos, y corregir las conclusiones.

**C4. Base WTI frente a Brent y crudos pesados**
- **Descripción:** El ratio h* = 1.01 no mide la base porque compara el WTI contra su propio futuro.
- **Fundamento:** Hull, cap. 3: h* = ρ·σS/σF exige que S sea el precio del activo expuesto. NIIF 9 6.3.7 regula la designación de componentes de riesgo.
- **Riesgo:** La cobertura puede ser inefectiva o incluso aumentar la varianza. Hay riesgo de no calificar para contabilidad de coberturas.
- **Recomendación:** Estimar la regresión con los costos reales de compra y comparar los instrumentos Brent con los WTI.

**C5. Exposición de crudo mal delimitada**
- **Descripción:** La cobertura de ~3 meses se aplica a barriles que rotan en ~1 mes. Se ignoran el inventario de productos y la exposición de compras.
- **Fundamento:** Cubrir más allá de la vida de la partida cubierta crea una posición especulativa (NIIF 9 6.5.6, discontinuación). La exposición económica relevante es el margen y el desfase de precios, no el precio absoluto.
- **Riesgo:** Sobrecobertura, cobertura con signo equivocado y exposición real subestimada en hasta un 70 %.
- **Recomendación:** Construir un mapa de exposición neta por horizonte y producto antes de dimensionar.

**C6. Límite propio excedido**
- **Descripción:** La estrategia cubre el 100 % del inventario frente a un tope del 80 %.
- **Fundamento:** Es una incoherencia entre la estrategia y la política propuesta.
- **Riesgo:** Incumplimiento de la política desde su aprobación.
- **Recomendación:** Reducir el volumen al rango o modificar el límite con justificación.

**M1 a M9 (síntesis)**

- **M1 (curvas):** Los CCS PEN/USD se valorizan con curvas swap y basis de mercado; la curva soberana incorpora prima de liquidez y de tenencia local. Riesgo: la tasa del 5.88 % no es ejecutable. Recomendación: revalorizar y conciliar con cotizaciones.
- **M2 (volatilidad):** El OVX no es la volatilidad de las opciones CL a 81 días, y omitir el skew sesga el strike de costo cero. Recomendación: recalibrar con la superficie de mercado.
- **M3 (posición estimada):** La posición de nueve meses atrás no representa la posición a la fecha de valorización. Los swaps de Citibank existentes pueden generar sobrecobertura. Recomendación: actualizar e integrar.
- **M4 (designación del NDF):** NIIF 9 6.6 sobre posiciones netas y NIC 21 sobre partidas monetarias. Riesgo: complejidad contable sin beneficio y una inefectividad no prevista. Recomendación: optar por valor razonable con cambios en resultados para el NDF.
- **M5 (inventario a NIC 2):** Riesgo: discontinuaciones frecuentes. Recomendación: diseñar coberturas por capas.
- **M6 (métricas):** El análisis de sensibilidad es requisito mínimo de NIIF 7 ¶40, y la medición del riesgo residual es buena práctica. Recomendación: incorporar VaR/ES, stress, griegas y PFE.
- **M7 (volúmenes):** Riesgo: el costo de E2 está mal comunicado a la Gerencia. Recomendación: unificar las bases de volumen.
- **M8 (tasa):** NIIF 9 6.3.3 exige transacciones previstas altamente probables, y la refinanciación no lo es. Recomendación: reformular como opción a evaluar.
- **M9 (legal y control):** Riesgo: la estrategia podría no ser ejecutable, y la valuación quedaría sin control independiente. Recomendación: obtener una opinión legal y definir una función de verificación independiente de precios.

## 4. Limitaciones de la revisión

- **Información no provista:** contrato y cronograma del préstamo BN; detalle de los swaps de Citibank; posición en S/ e inventario al 28-sep-2026; costos de compra por tipo de crudo; cotizaciones bancarias, términos CSA y curvas de mercado de respaldo (SBS, BlueGamma, superficie CL).
- **No verificable con la información provista:** los insumos de mercado del 28-sep-2026 (TC, curvas, futuros CL, OVX); las acciones de calificación de S&P, Moody's y Fitch; el alcance legal del D.U. 003-2026; las cifras del EEFF auditado, que se tomaron tal como el informe las cita.
- **Alcance excluido:** la auditoría del EEFF 2025 en sí y la opinión legal. El documento es un trabajo académico; se auditó con el estándar de un informe a la Gerencia General, como indica el propio documento.

## 5. Conclusión

El informe identifica correctamente los dos riesgos dominantes y su aritmética interna es en gran medida consistente, pero sus conclusiones no son sostenibles. La Estrategia 1 se apoya en un cronograma supuesto que contradice la fuente, en curvas no ejecutables y en un costo de CVA contradictorio. La Estrategia 2 cubre con el subyacente equivocado una exposición mal delimitada y excede el límite propuesto. Ambas omiten la principal restricción del caso, que es la liquidez por colateral bajo estrés. Se requiere subsanar los hallazgos C1 a C6 antes de cualquier presentación al Directorio.
