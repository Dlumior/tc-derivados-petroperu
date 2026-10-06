# Libro de estudio: dos ediciones del mismo contenido
OUT := out
LATEXMK := latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=$(OUT)

.PHONY: all kobo a4 clean
all: kobo a4     ## ambas ediciones

kobo:            ## out/libro-kobo.pdf (120x160 mm, Kobo Libra Colour)
	$(LATEXMK) libro-kobo.tex

a4:              ## out/libro-a4.pdf (A4)
	$(LATEXMK) libro-a4.tex

clean:
	latexmk -C -outdir=$(OUT) libro-kobo.tex libro-a4.tex
