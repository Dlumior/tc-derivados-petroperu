# Plan de producción: videos del libro al estilo 3Blue1Brown

Serie de **13 videos para YouTube**, uno por capítulo de `libro/cap/cNN.tex`, animados con Manim y narrados en
español con **Kokoro-82M en local**. La voz es intercambiable (una línea en `narrador.py`): si el piloto no
convence, solo la narración final se regenera con ElevenLabs.
Este archivo es el registro de avance: marcar `[x]` al cerrar cada tarea y actualizar el tablero.

**Reglas** (heredadas de `CLAUDE.md`):
1. **Cero cifras tecleadas** en escenas o guiones: toda cifra sale de `src/derivados/`, `data/procesado/*.yaml`
   o `libro/v2/*.csv`, igual que en el libro.
2. **Toda cifra del caso con fuente** en pantalla (pie pequeño, como `\fuente{...}`) y en la descripción de YouTube.
3. **Adaptar, no leer**: cada video dura 10–14 min (≈ 1,600–2,000 palabras de narración). El capítulo tiene
   ≈ 2,800 palabras: hay que elegir una intuición central por sección.
4. Idioma: español (Perú); números leídos según el normalizador (`1,234.5` → "mil doscientos treinta y cuatro coma cinco").

## 1. Herramientas

| Necesidad | Herramienta | Nota |
|---|---|---|
| Animación | Manim Community Edition (`manim`) | Requiere `cairo-devel`, `pango-devel` y LaTeX (ya instalado, con `dvisvgm`) |
| Sincronía voz–animación | `manim-voiceover` + servicio propio `KokoroService` | Caché de audio; las marcas `<bookmark/>` usan Whisper local (`manim-voiceover[transcribe]`) |
| Voz | Kokoro-82M (`kokoro`, `soundfile`) + `espeak-ng` | Voces en español: `ef_dora`, `em_alex`, `em_santa`. Licencia Apache 2.0. Corre en CPU |
| Voz de respaldo | ElevenLabs (`eleven_multilingual_v2`) | Solo si Kokoro no alcanza la calidad; mismo `narrador.py` |
| Montaje y audio | `ffmpeg` (`loudnorm` a −14 LUFS) | Une escenas, mezcla música a −28/−30 dB |
| Subtítulos | `.srt` de `manim-voiceover` o Whisper | Español; se suben a YouTube |
| Música | Pista libre de derechos (YouTube Audio Library / Jamendo CC-BY) | Registrar autor y licencia en `videos/creditos.md` |
| Miniaturas | Fotograma de Manim + texto (1280×720) | Plantilla común en `estilo.py` |

## 2. Tablero de estado

Estados: ⬜ pendiente · ✍️ guion · 🎞️ animación · 🔊 voz · ✅ render final · 📺 publicado

| Cap. | Título | Estado | Duración | Notas |
|---|---|---|---|---|
| 08 | Opciones financieras (**piloto**) | ⬜ | | Fija el estilo |
| 02 | El valor del dinero en el tiempo | ⬜ | | |
| 03 | Riesgo, rendimiento y exposición | ⬜ | | |
| 04 | Mercados, posiciones y participantes | ⬜ | | |
| 05 | Forwards y no arbitraje | ⬜ | | |
| 06 | Futuros, costo de acarreo y base | ⬜ | | |
| 07 | Swaps | ⬜ | | |
| 09 | Valoración de opciones y griegas | ⬜ | | |
| 01 | El caso PETROPERÚ | ⬜ | | Datos del repo |
| 10 | Diagnóstico de riesgos | ⬜ | | Datos del repo |
| 11 | E1: CCS y NDF | ⬜ | | Datos del repo |
| 12 | E2: swap y collar sobre el WTI | ⬜ | | Datos del repo |
| 13 | NIIF 9, colateral e implementación | ⬜ | | Datos del repo |

## 3. Tareas por fase

### Fase 0: Entorno

- [ ] `sudo dnf install cairo-devel pango-devel espeak-ng` y los paquetes TeX que pida Manim
      (`standalone`, `preview`, `babel-spanish`, `physics`, `relsize`, `ragged2e`, `doublestroke`, `rsfs`).
- [ ] Crear `videos/` como **proyecto `uv` propio** (torch y manim no deben ensuciar el entorno del informe), con
      dependencia editable al paquete raíz para importar `derivados`.
- [ ] Verificar la versión de Python que exige `kokoro`; fijarla en `videos/.python-version`.
- [ ] `uv add manim "manim-voiceover[transcribe]" kokoro soundfile`.
- [ ] Agregar a `.gitignore`: `videos/media/`, `videos/out/`, `videos/**/voiceovers/` (caché de audio).
- [ ] Escena de prueba `hola.py` (un `MathTex` con tilde + un `Text`) renderiza en `-ql`.

### Fase 1: Voz y estilo

- [ ] Script `elegir_voz.py`: el mismo párrafo del cap. 8 con `ef_dora`, `em_alex` y `em_santa`, a 0.9/1.0/1.1 de velocidad.
- [ ] Escuchar y elegir voz y velocidad (decisión D1). Si ninguna convence, probar ElevenLabs con el mismo párrafo.
- [ ] `narrador.py`: `KokoroService(SpeechService)` (genera `.wav`, devuelve ruta y duración) + selector de servicio.
- [ ] `narrador.py`: normalizador de texto con test (`videos/tests/`):
  - [ ] Números estilo EEFF (`1,234.5`, `(12.3)` → "menos doce coma tres").
  - [ ] Monedas y unidades: `US$`, `S/`, `%`, `pb`, `bbl`, "millones".
  - [ ] Siglas: WTI, CCS, NDF, IRS, CSA, ISDA, CVA, NIIF, BCRP, SOFR (deletreadas o leídas según D2).
  - [ ] Fechas (`28-sep-2026`) y tasas (`5.25 %`).
- [ ] Verificar si `espeak-ng es` suena peninsular; probar `es-419` si Kokoro lo permite.
- [ ] `estilo.py`: paleta de `libro/figuras.py` (AZUL, ROJO, VERDE, GRIS, ORO, MORADO) sobre fondo oscuro,
      `TexTemplate` con `babel` en español y `utf8`, tipografías, pie de fuente estándar.
- [ ] Escena de prueba de 30 s con voz real y una marca `<bookmark/>` sincronizada.
- [ ] `Makefile`: `make borrador CAP=08` (480p15), `make final CAP=08` (1080p60), `make montar CAP=08`.

### Fase 2: Piloto (capítulo 8, Opciones)

- [ ] `guiones/c08.md`: guion escena por escena, columnas *narración* | *visual*, con duración estimada.
- [ ] Revisión del guion por el autor (rigor + claridad).
- [ ] Storyboard: un fotograma por escena (`manim -s`), aprobado.
- [ ] Animar las escenas (`c08_opciones.py`, una `Scene` por sección).
- [ ] Narración con Kokoro; ajustar tiempos con marcas.
- [ ] Render final, montaje, música y `loudnorm`.
- [ ] Medir y anotar en §5: tiempo de render por minuto de video, horas de trabajo, problemas de pronunciación.
- [ ] Revisión crítica del piloto (¿se entiende sin el libro?, ¿ritmo?, ¿voz aceptable?) → decisión D3.

### Fase 3: Componentes reutilizables (`videos/componentes/`)

- [ ] `EjePayoff`: ejes de payoff/ganancia con tramos que se construyen.
- [ ] `LineaDeTiempo`: fechas, flujos y flechas de pago/cobro.
- [ ] `FlujoSwap`: dos patas que se cruzan (IRS, CCS, swap de commodities).
- [ ] `ArbolBinomial`: árbol que crece paso a paso con valores en los nodos.
- [ ] `Balance`: activos/pasivos en S/ y US$ como bloques que se desequilibran.
- [ ] `Fuente`: pie de fuente consistente.
- [ ] Refactorizar el piloto para usar los componentes.

### Fase 4: Serie teórica (caps. 2–7 y 9)

Por cada capítulo, en el orden del tablero: guion → revisión → storyboard → animación → voz → render → control.

- [ ] Cap. 02: crecimiento simple/compuesto/continuo simultáneo; curva cupón cero por *bootstrap*.
- [ ] Cap. 03: histograma de rendimientos → campana normal; VaR como área coloreada.
- [ ] Cap. 04: largo y corto como espejos; margen consumiéndose día a día.
- [ ] Cap. 05: arbitraje como circuito cerrado; paridad cubierta de tasas como dos caminos al mismo punto.
- [ ] Cap. 06: convergencia de la base; contango vs. *backwardation*.
- [ ] Cap. 07: flujos que se cruzan en el tiempo; CCS como dos préstamos espejo.
- [ ] Cap. 09: árbol binomial que converge a Black-Scholes; griegas como pendiente y curvatura.

### Fase 5: Serie del caso (caps. 1 y 10–13)

- [ ] Módulo `videos/datos.py` que lee `data/procesado/*.yaml`, `libro/v2/*.csv` y la librería; ninguna cifra a mano.
- [ ] Cap. 01: balance de PETROPERÚ que se desequilibra con el tipo de cambio.
- [ ] Cap. 10: matriz de riesgos animada.
- [ ] Cap. 11: saldo BN, perfil del CCS, posiciones de cambio y escenarios E1.
- [ ] Cap. 12: capas del collar, costo de la *backwardation*, escenarios E2.
- [ ] Cap. 13: registro contable NIIF 9 y mapa de condiciones de ejecución.
- [ ] Control cruzado: toda cifra mostrada coincide con `informe/generado/valores.tex` (pedir al `validador-cuantitativo`).

### Fase 6: Publicación en YouTube

- [ ] Crear el canal o la lista de reproducción; decidir visibilidad (D4).
- [ ] Revisar la política de YouTube sobre contenido sintético (voz generada) y marcar la divulgación si corresponde.
- [ ] Por video: título, descripción con capítulos (marcas de tiempo), referencias del libro y créditos de música.
- [ ] Por video: subtítulos `.srt` en español y miniatura 1280×720.
- [ ] Tráiler de 60–90 s de la serie (opcional).
- [ ] Publicar en el orden de la serie (1 → 13), no en el de producción.

## 4. Decisiones abiertas

| # | Decisión | Estado |
|---|---|---|
| D1 | Voz y velocidad de Kokoro (`ef_dora` / `em_alex` / `em_santa`) | Pendiente (Fase 1) |
| D2 | Siglas: deletreadas ("ce-ce-ese") o leídas por su nombre ("cross currency swap") | Pendiente (Fase 1) |
| D3 | Tras el piloto: Kokoro definitivo o regenerar la narración con ElevenLabs | Pendiente (Fase 2) |
| D4 | Visibilidad en YouTube: pública o no listada | Pendiente (Fase 6) |
| D5 | Créditos: autores del libro / curso / profesor en la descripción | Pendiente (Fase 6) |

## 5. Registro de avance

| Fecha | Avance |
|---|---|
| 2026-10-05 | Plan creado. Voz: Kokoro local con respaldo ElevenLabs; destino: YouTube. |
