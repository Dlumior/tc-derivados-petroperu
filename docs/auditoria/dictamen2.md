# Segundo dictamen técnico (5-oct-2026)

Recibido el 5-oct-2026, sobre el informe en el estado del commit 8a46b5d. Conclusión del auditor: **No aceptable**
(4 críticos, 12 medios, 8 bajos). Su tabla de hallazgos, resumida:

| # | Sev. | Hallazgo |
|---|---|---|
| C1 | Crítico | El umbral CSA (US$ 152 MM) sale de choques instantáneos, no de la PFE en la vida del CCS (27 meses); consume el 100 % de las líneas libres; no dice si es por banco; no define MPOR ni *independent amount*. |
| C2 | Crítico | El CVA usa una "exposición máxima" de 23.9 frente a un pasivo de 101.9 con TC +10 %; no depende del CSA; spread sin estructura de plazos; omite DVA, FVA y KVA. |
| C3 | Crítico | Cobertura de valor razonable "del inventario de su mes" para capas de dic/ene sobre un inventario que rota en 33 días; WTI como componente de un crudo comprado a Brent; ratio 1:1 frente a h* = 1.14. |
| C4 | Crítico | No se analizan el *cross-default* (ISDA §5(a)(vi)) ni las ATE, con el covenant del CESCE ya incumplido. |
| M1 | Medio | Posición en S/ e inventario de dic-2025 con precios de sep-2026. |
| M2 | Medio | Swaps con Citibank sin nocional ni dirección. |
| M3 | Medio | Curva soberana como proxy del CCS, sin *basis*; la "verificación independiente" la hacen los autores. |
| M4 | Medio | Eficacia de E1 nominal (6.1) frente al valor razonable (4.3); sin derivado hipotético ni prueba de 6.4.1(c)(ii). |
| M5 | Medio | VaR: método y volatilidades no revelados (dice que E1 implica 7 % y que E2 daría ~115); sin ES. |
| M6 | Medio | OVX plano, sin *skew*; costo cero *mid-market*; valor temporal (6.5.15). |
| M7 | Medio | Se excluye el inventario de productos (US$ 313.5 MM); "falta de series" es débil (existen HO/RBOB). |
| M8 | Medio | Brent–WTI de 12.7 atípico; el riesgo base no entra en escenarios ni VaR. |
| M9 | Medio | "Toda la deuda es a tasa fija" contradice el repricing de las líneas. |
| M10 | Medio | Programa rodante sin reglas de *roll*. |
| M11 | Medio | Sin límites de contraparte, *stop-loss* ni aprobación de modelos; Nivel 2 afirmado sin análisis. |
| M12 | Medio | Régimen legal de empresa estatal genérico. |
| B1 | Bajo | Cuadro 11 asigna 52.2 a E2; el Cuadro 13 da 51.8. |
| B2 | Bajo | Put de nov 83.30 frente a 90 % × 92.60 = 83.34. |
| B3 | Bajo | Mezcla de TC (SBS, BCRP, compra, medio). |
| B4 | Bajo | "De 2.90 a 1.12 MMbl (39 %)": el 39 % es lo que queda. |
| B5 | Bajo | Utilidad bruta sin nota fuente en el texto. |
| B6 | Bajo | Valor del collar ante ±10 % con delta lineal. |
| B7 | Bajo | Yahoo Finance y BlueGamma como fuentes. |
| B8 | Bajo | Obligaciones de reporte no mapeadas. |
