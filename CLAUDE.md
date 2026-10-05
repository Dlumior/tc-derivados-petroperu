# Trabajo Calificado — Gestión de Derivados Financieros (Prom. 44, Prof. Humala)

Informe profesional (≤ **10 páginas de cuerpo**, portada incluida; las **referencias no cuentan**, LaTeX) de la Gerencia de Finanzas de **PETROPERÚ S.A.**
a la Gerencia General, sustentando **al menos dos estrategias con uso intensivo de derivados**.
Entrega impresa: **5-oct-2026, 19:30**. Rúbrica (20): Intro 1.5 · Riesgos 4 · Estrategias 4 · Cálculos 4 ·
Referencias 1.5 · Material de apoyo 3.5 · Conclusiones 1.5.

## Arquitectura (flujo de datos en un solo sentido)

```
data/raw/ (inmutable) ──► data/procesado/*.yaml (insumos con fuente+estado)
                              │
              src/derivados/ (librería probada) ◄── tests/ (réplica exacta del Excel de referencia)
                              │
                     scripts/run_all.py  (make calc)
                              │
          informe/generado/{valores.tex, tablas/, figuras/}   ← NO editar a mano
                              │
                informe/secciones/*.tex  (prosa + macros)  ──► make pdf ──► informe/out/main.pdf
```

## Reglas
1. **Cero cifras tecleadas** en `informe/secciones/`: usar macros (`\PenNeto`, `\CCSTasaUSD`, …). Nueva cifra → `m.set(...)` en `scripts/run_all.py` → `make calc`.
2. **Todo insumo con fuente** (Nota/página del EEFF o URL + fecha). Datos no verificados = `estado: PENDIENTE`. Nunca inventar datos de mercado.
3. **Todo cuadro/gráfico con `\fuente{...}`** (resta nota si falta).
4. Cálculos siguen la skill `calculo-derivados` (patrón de 7 pasos del Excel del profesor). Fórmulas nuevas → `src/derivados/` + test.
5. PETROPERÚ tiene **moneda funcional US$**: su riesgo cambiario es por saldos en **S/** (pasivo neto ⇒ pierde con apreciación del PEN).
6. Idioma: español (Perú). Números estilo EEFF: `1,234.5`, negativos entre paréntesis.

## Comandos
- `make test` · `make calc` · `make pdf` · `make check` · `make final` (cero avisos, para imprimir)
- Slash: `/calcular`, `/seccion 03 ...`, `/revisar` (validador + revisor en paralelo)

## Agentes (`.claude/agents/`)
- `analista-riesgos` — EEFF → exposiciones.yaml, borrador sección 2
- `investigador-mercado` — datos de mercado reales + bibliografía verificada
- `validador-cuantitativo` — recalcula todo sin usar la librería (independiente)
- `revisor-rubrica` — simula al profesor sobre el PDF

## Estrategias en curso (línea del borrador del compañero, `data/raw/PETROPERU_Derivados.docx`)
Exposiciones al 31-dic-2025 (EEFF); mercado a la **fecha de valorización 28-sep-2026**.
- **E1 FX**: CCS amortizable recibe S/ – paga US$ sobre el saldo remanente del préstamo BN (Nota 14(ii)) + NDF de compra de S/ a 3 meses sobre el 80 % del resto de la posición en S/.
- **E2 Crudo**: 80 % del inventario de crudo (Nota 10): mitad swap de WTI con liquidaciones mensuales y mitad collar de costo cero en 3 capas mensuales (nov/dic/ene). Solo OTC: **sin futuros** (márgenes diarios inviables por liquidez).
- **Tasa**: no se recomienda hoy; el forward-starting swap (2027-2030) queda como opción solo si la refinanciación del CESCE pasa a ser altamente probable.
- **Condición de ejecución**: un umbral CSA de al menos `\UmbralNecesario` o la garantía del Estado (colateral bajo estrés conjunto, `docs/auditoria/plan.md`).

## Limitaciones conocidas
- El .txt del dictamen **no incluye los estados primarios** (eran imágenes, folios 0010–0014).
- `mercado.yaml`: `tasas.spread_credito_petroperu` (318 pb, `supuesto`) es solo la **sensibilidad** de agosto-2026 (`CCSCVApbProxy`, `CCSTasaAllInProxy`); el caso base es 569 pb, calculado del valor razonable de los bonos (Nota 14(d)). No hay cotización pública al 28-sep. Ya no hay insumos `PENDIENTE` y `make final` pasa.
- Préstamo BN: el cronograma (solo intereses hasta jun-2027 + 18 cuotas) se infiere de los EEFF a jun-2026 (`data/raw/eeff_2026/`); no es contractual.

## Auditoría en curso
Dictamen externo (3-oct-2026) y plan de levantamiento con checklist: `docs/auditoria/plan.md`. Antes de editar el
informe, revisar qué fase sigue y marcar `[x]` / actualizar el tablero al cerrar cada tarea.
