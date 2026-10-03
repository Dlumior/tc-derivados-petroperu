PY ?= uv run python

.PHONY: setup test calc pdf check final all clean

setup:            ## crea .venv e instala dependencias (uv)
	uv sync

test:             ## tests (incluye regresión contra el Excel de referencia)
	$(PY) -m pytest -q

calc: test        ## genera informe/generado/{valores.tex,tablas,figuras}
	$(PY) scripts/run_all.py

pdf:              ## compila con LuaLaTeX + biber (mismo motor que VS Code)
	cd informe && latexmk -lualatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex

check:            ## controles: cuerpo ≤10 páginas (sin referencias), \fuente en tablas/figuras, cifras a mano, pendientes
	$(PY) scripts/verificar_informe.py

final: calc pdf   ## versión para imprimir: CERO avisos permitidos
	$(PY) scripts/verificar_informe.py --final

all: calc pdf check

clean:
	cd informe && latexmk -C -output-directory=out main.tex; rm -rf informe/generado/*
