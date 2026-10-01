---
description: Redacta o mejora una sección del informe (argumento: número o nombre de sección)
argument-hint: "[01|02|03|04|05] [instrucciones]"
---
Trabaja en `informe/secciones/$1*.tex` siguiendo las skills `informe-latex` y `calculo-derivados`.

- Respeta el presupuesto de páginas de esa sección.
- Toda cifra con macro de `generado/valores.tex`; si falta, agrégala en `scripts/run_all.py` y corre `make calc`.
- Para la sección 03/04, cada estrategia debe cubrir los 7 pasos del patrón de cálculo.
- Compila con `make pdf`, verifica páginas y muéstrame un resumen de lo que cambió (no el texto completo).

Instrucciones adicionales: $ARGUMENTS
