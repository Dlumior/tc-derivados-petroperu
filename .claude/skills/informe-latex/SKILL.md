---
name: informe-latex
description: Convenciones para redactar y compilar el informe LaTeX del Trabajo Calificado (máx. 10 páginas de cuerpo, referencias aparte, rúbrica de 20 pts, APA 7, fuente en cada cuadro/gráfico). Úsala al escribir o editar cualquier archivo en informe/, al recortar extensión o al preparar la versión final para imprimir.
---

# Informe LaTeX — reglas del proyecto

## Restricciones duras del enunciado
- **≤ 10 páginas de cuerpo** (portada y anexos incluidos). Las **referencias quedan fuera del límite**: son un extra
  que no se evalúa como extensión (acordado el 3-oct-2026). Lo que exceda del cuerpo **no se evalúa**.
  `make check` mide hasta `\label{fin-cuerpo}` en `main.tex`. Portada compacta en la página 1, sin índice, sin anexos largos.
- **Todo cuadro/gráfico con fuente y elaboración** → macro `\fuente{...}` bajo cada `table`/`figure`. Omitirla *resta* nota.
- Contenido original; textos de terceros citados (`\parencite{clave}`, APA 7 vía biblatex-apa).
- Entrega impresa: **5-oct-2026, 19:30**, Sesión 9.

## Presupuesto de páginas (alineado a puntaje)

| Sección | Archivo | Pts | Páginas |
|---|---|---|---|
| Introducción y objetivo | `01_introduccion.tex` | 1.5 | 0.6 |
| Identificación de riesgos | `02_riesgos.tex` | 4 | 2.0 |
| Estrategias con derivados (≥ 2) | `03_estrategias.tex` | 4 | 2.4 |
| Análisis / cálculos | `04_analisis.tex` | 4 | 2.8 |
| Conclusiones | `05_conclusiones.tex` | 1.5 | 0.6 |
| Referencias | `referencias.bib` | 1.5 | fuera del límite |
| Material de apoyo (transversal) | tablas/figuras | 3.5 | — |

## Reglas de redacción
- Registro: **informe de Gerencia de Finanzas a Gerencia General** — directo, cuantificado, con recomendación. No tono de examen.
- Cada afirmación cuantitativa → macro de `generado/valores.tex` (el hook bloquea cifras tecleadas en `secciones/`).
  Excepciones permitidas: años, números de nota, enteros ≤ 2 dígitos (plazos, escenarios ±10 %).
- Tablas: `\input{generado/tablas/<nombre>}` (se generan con `make calc`, ya traen `\fuente`).
- Figuras: `\includegraphics{<nombre>}` desde `generado/figuras/` + `\caption` + `\fuente{...}`.
- Usar `\pendiente{...}` para huecos; `make final` falla si queda alguno.
- Ecuaciones solo las necesarias para seguir el cálculo (una por estrategia, máximo dos).
- Cada estrategia responde: ¿qué riesgo? ¿qué instrumento y posición? ¿nocional y plazo? ¿costo? ¿efectividad? ¿qué se descarta y por qué? ¿tratamiento NIIF 9?
- Conclusiones = decisiones, no resumen.

## Compilación
- Motor: **LuaLaTeX + biber** (`latexmk`, salida en `informe/out/`) — igual que la receta de VS Code.
- `make pdf` compila; `make check` controla páginas/fuentes/cifras; `make final` = calc + pdf + control estricto.
- Si el cuerpo pasa de 10 páginas: 1) reducir figuras a `width=0.7\linewidth` o poner dos lado a lado,
  2) fusionar tablas de escenarios, 3) acortar prosa en 02/03 — nunca eliminar fuentes ni referencias.
