# Videos del libro. Uso: make borrador CAP=08 · make final CAP=08 · make test · make pronunciacion
CAP ?= 08
FUENTE = $(wildcard c$(CAP)_*.py)
ESCENAS = $(shell uv run python -c "from guion import narracion; print(' '.join(narracion('$(CAP)')))" 2>/dev/null)
MANIM = uv run manim

.PHONY: test voces pronunciacion prueba borrador final storyboard

test:
	uv run pytest -q

voces:  ## muestras de voz para elegir (out/voces/)
	uv run python elegir_voz.py $(VOZ)

prueba:  ## escena de 30 s con voz y marcas
	$(MANIM) -ql prueba_voz.py PruebaVoz

borrador:  ## 480p15, todas las escenas del capítulo, y montaje
	$(MANIM) -ql $(FUENTE) $(ESCENAS)
	uv run python montar.py $(CAP) 480p15

final:  ## 1080p60 para YouTube
	$(MANIM) -qh $(FUENTE) $(ESCENAS)
	uv run python montar.py $(CAP) 1080p60

pronunciacion:  ## cada término del diccionario → Whisper (out/pronunciacion.tsv)
	uv run python revisar_pronunciacion.py

storyboard:  ## un cuadro fijo por escena → out/storyboard/cNN.png
	uv run python storyboard.py $(CAP)
