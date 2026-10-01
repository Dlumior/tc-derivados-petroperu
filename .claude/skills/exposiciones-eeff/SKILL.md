---
name: exposiciones-eeff
description: Extrae y cuantifica exposiciones a riesgos financieros (tipo de cambio, precio de commodities, tasa de interés, liquidez, crédito) desde estados financieros auditados o reportes SMV, con trazabilidad a nota y página. Úsala al leer el dictamen de PETROPERÚ, EEFF intermedios 2026, memorias anuales, o al poblar data/procesado/exposiciones.yaml.
---

# Extracción de exposiciones desde EEFF

## Dónde mirar (NIIF 7 obliga a revelarlo)

| Riesgo | Nota típica | Qué extraer |
|---|---|---|
| Tipo de cambio | "Gestión de riesgos financieros" (PETROPERÚ: **Nota 3.1.a.i**, p. 42) | Activos y pasivos por moneda, **exposición neta**, TC de cierre, **sensibilidad ±x %**, diferencia de cambio del año, derivados vigentes |
| Precio commodity | Nota 3.1.a.iii, **Nota 10 Inventarios** (MBL, precio de cierre), **Nota 23 Costo de ventas** (volumen y precio de compras) | Barriles en inventario, MBDC comprados, precio promedio, desvalorización, mecanismos de traslado (FEPC) |
| Tasa de interés | Nota 3.1.a.ii, **Nota 14 Otros pasivos financieros** | Cada deuda: moneda, nominal, tasa fija/variable, vencimiento, cronograma, covenants, reclasificaciones |
| Liquidez | Nota 3.1.c, Nota 1-f (empresa en marcha) | Líneas disponibles/usadas, capital de trabajo, vencimientos corrientes |
| Derivados existentes | Notas de otras cuentas por cobrar/pagar (PETROPERÚ: **Nota 9(g)** swap Citibank) | Tipo, contraparte, valor razonable, si califica como cobertura |

## Reglas

1. **Cita exacta**: `"EEFF 2025, Nota 14(ii), p. 74"`. La página es la numeración `- n -` del informe (no el folio `00nn`).
2. **Unidades explícitas** (`US$000`, `S/000`, `miles bbl`). Moneda funcional de PETROPERÚ = **US$**.
3. **Dirección del riesgo** en `nota`: qué movimiento del mercado genera pérdida.
4. `estado: verificado` solo si el número se leyó del documento; supuestos propios → `supuesto` con justificación.
5. Distinguir **exposición contable** (partidas monetarias, lo que mide la sensibilidad NIIF 7) de **exposición económica** (ventas locales en S/ indexadas a precios internacionales; compras de crudo en US$). La segunda explica coberturas naturales parciales — suma puntos en "Identificación de riesgos".
6. Señalar **inconsistencias** entre notas (p. ej. Nota 3 dice "sin derivados FX" y la Nota 9(g) revela swaps con Citibank) — muestra lectura crítica.

## Limitación conocida del archivo actual

`data/raw/Dictamen_EEFF_2025_Petroperu.txt` es texto extraído del PDF: **los estados primarios
(situación financiera, resultados, flujos de efectivo; folios 0010–0014) eran imágenes y no están**.
Para ratios o totales del balance, obtener el PDF original o los EEFF en la SMV y extraer con `pdftotext -layout`.

## Salida

Actualizar `data/procesado/exposiciones.yaml` manteniendo el esquema `{valor, unidad, fuente, estado, nota}`
y ejecutar `make calc` para que las macros se regeneren.
