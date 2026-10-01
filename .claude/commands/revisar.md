---
description: Revisión independiente en paralelo (cálculos + rúbrica) antes de imprimir
---
1. Ejecuta `make calc pdf check`.
2. Lanza EN PARALELO dos subagentes: `validador-cuantitativo` y `revisor-rubrica`. No les pases tu razonamiento: solo pídeles que revisen el estado actual del proyecto.
3. Consolida sus hallazgos en una sola lista priorizada (errores de cálculo primero, luego puntos recuperables por página).
4. Pregúntame cuáles aplicar antes de editar nada.
