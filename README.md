# TC Derivados — PETROPERÚ

```bash
make setup          # uv sync: .venv + dependencias (Python ≥ 3.11)
make test           # 19 tests: réplica exacta del Excel de referencia + propiedades teóricas
make calc           # genera informe/generado/ (macros, tablas, figuras)
make pdf            # LuaLaTeX + biber → informe/out/main.pdf   (o receta "LuaLaTeX (local)" en VS Code)
make check          # cuerpo ≤10 páginas (sin referencias), \fuente en cuadros, cifras a mano, pendientes
make final          # versión para imprimir (falla si queda algún PENDIENTE)
```

En VS Code, abrir `informe/main.tex` y compilar con la receta **LuaLaTeX (local)** (usa `informe/.latexmkrc` → biber).

Plan de trabajo sugerido (6 días):

| Día | Tarea | Quién |
|---|---|---|
| 30-sep | Datos de mercado reales + series; decidir fecha de valorización | `investigador-mercado` |
| 1-oct | Sección 2 (riesgos) + mapa de riesgos; completar exposiciones | `analista-riesgos` + grupo |
| 2-oct | Estrategias E1 y E2 (secciones 3 y 4), escenarios y gráficos | grupo + `/seccion` |
| 3-oct | Intro, conclusiones, referencias; `/revisar` | grupo |
| 4-oct | Correcciones, `make final`, lectura en papel | grupo |
| 5-oct | Imprimir antes de las 19:30 | — |

Ver `CLAUDE.md` para reglas y arquitectura.
