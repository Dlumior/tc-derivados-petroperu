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
4. **Franja de subtítulos**: el 15 % inferior del cuadro queda libre para los subtítulos de YouTube (el espectador
   elige su tamaño). Las escenas heredan de `estilo.Escena`, que falla si algo entra en la franja; `apoyar()` asienta
   gráficos sobre el piso dejando sitio al pie de fuente.
5. Idioma: español (Perú); números leídos según el normalizador (`1,234.5` → "mil doscientos treinta y cuatro coma cinco").

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
| 08 | Opciones financieras (**piloto**) | 🔊 | 14.4 min | Borrador 480p con voz; en revisión |
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

- [x] `espeak-ng` (ya estaba instalado, 1.52).
- [x] `sudo dnf install cairo-devel pango-devel` (sin ellos no compila `manimpango`) y los paquetes TeX que pida
      Manim (`standalone`, `preview`, `babel-spanish`, `physics`, `relsize`, `ragged2e`, `doublestroke`, `rsfs`).
- [x] Crear `videos/` como **proyecto `uv` propio**, con `derivados = { path = "..", editable = true }`.
      **No usar `uv add --editable ..`**: convierte el repo en *workspace* y cambia el `uv.lock` del informe.
- [x] Python 3.12 fijado en `videos/.python-version` (el sistema trae 3.14).
- [x] `kokoro` + `soundfile` + torch **solo-CPU** (índice `pytorch-cpu`; el de PyPI baja varios GB de CUDA).
      Hay que exigir `transformers>=4.40`: sin eso el resolvedor cae a la 4.12 y falla `tokenizers`.
- [x] Prueba de Kokoro en español (`em_alex`): 8.7 s de audio en ≈ 10 s de CPU.
      Requiere `ESPEAK_DATA_PATH=/usr/share/espeak-ng-data` (el `espeakng-loader` de PyPI trae una ruta rota);
      `narrador.py` debe fijarla antes de importar `kokoro`.
- [x] `uv add manim "manim-voiceover[transcribe]"` (Manim CE 0.21.0).
- [ ] Opcional: `sudo dnf install sox` (`manim-voiceover` avisa al arrancar; solo se usa para cambiar la velocidad del audio).
- [x] Agregar a `.gitignore`: `videos/.venv/`, `videos/media/`, `videos/out/`, `videos/**/voiceovers/`.
- [x] Escena de prueba `hola.py` (un `MathTex` con tilde + un `Text`) renderiza en `-ql`.
      La plantilla de Manim ya carga `babel` en inglés: hay que **reemplazarlo** por
      `[spanish,es-noshorthands,es-nolayout]` (agregar otro `babel` da *option clash*). Con español, `\max` sale "máx".

### Fase 1: Voz y estilo

- [x] Script `elegir_voz.py`: el mismo párrafo del cap. 8 con dos acentos y tres velocidades (`make voces VOZ=em_alex`).
- [x] Elegir voz y velocidad (D1): `em_alex`, `es-419`, 0.95.
- [x] `narrador.py`: `KokoroService(SpeechService)` + selector (`VOZ_SERVICIO=elevenlabs` para el respaldo).
      Devuelve el texto **normalizado** para que las marcas `<bookmark/>` se alineen con la transcripción de Whisper.
- [x] `narrador.py`: normalizador de texto con test (`videos/tests/`, 33 casos):
  - [x] Números estilo EEFF (`1,234.5`, `(12.3)` → "menos doce coma tres"), con apócope ("veintiún días").
  - [x] Monedas y unidades: `US$`, `S/`, `%`, `pb`, `bbl`, "millones".
  - [x] Siglas por su nombre (D2) y anglicismos con escritura fonética ("col", "estráik", "suap", "péy-of").
  - [x] Fechas (`28-sep-2026`) y tasas (`5.25 %`).
- [x] `espeak-ng es` cecea ("opθión"): se usa `es-419`, que sesea.
- [x] `revisar_pronunciacion.py` (`make pronunciacion`): sintetiza cada término y lo transcribe con Whisper
      (`out/pronunciacion.tsv`). "péiof" se oía "peo" → "péy-of". Probar siempre **dentro de una frase real**: en
      la frase de prueba, "cólar" y "sófer" salían "color" y "software", pero en contexto se reconocen bien.
- [x] `estilo.py`: paleta de `libro/figuras.py` aclarada sobre fondo `#0f1419`, CMU Serif, `TexTemplate` en
      español, pie `fuente(...)`.
- [x] Escena de prueba `prueba_voz.py` (24 s) con voz real y tres marcas `<bookmark/>` sincronizadas.
- [x] Franja de subtítulos (15 % inferior) con control automático en `estilo.Escena`; pie de fuente encima de ella.
- [x] `Makefile` (`make test | voces | pronunciacion | prueba | borrador CAP=08 | final CAP=08`) y `montar.py`
      (une las escenas en orden de definición, `loudnorm` → −14.7 LUFS medido). Además une los `.srt` en
      `out/subtitulos/` y genera `out/vista_previa/` con subtítulos pequeños quemados (Liberation Sans: la Noto Sans
      variable sale con números diminutos en libass). Revisar siempre desde `out/`: en `media/` el reproductor
      carga el `.srt` de Manim a tamaño proporcional y tapa el video.

### Fase 2: Piloto (capítulo 8, Opciones)

- [x] `guiones/c08.md`: 10 escenas con narración, marcas y visual; cifras del caso como `{llaves}` con su origen.
- [x] Guion v2 (2026-10-11): ≈ 15 min; escena nueva "Largo y corto" (call/put larga y corta), desgaste del valor
      tiempo, arbitraje de paridad, tres capas del collar y plan B de la put.
- [ ] Revisión del guion por el autor (rigor + claridad).
- [x] Storyboard: `storyboard_c08.py` (11 cuadros) + `storyboard.py` → `out/storyboard/c08.png` (`make storyboard`).
      Cada cuadro es una función reutilizable al animar; la clase `Cuadro` aplica el control de la franja.
      Criterios que salieron de la revisión: en gráficos de payoff, **no numerar el eje horizontal** (cruza las
      líneas en y = 0); marcar solo K, S₀, K_p, K_c con `marca_k`. Rótulos en espacio libre, unidos con guía si hace falta.
- [x] Aprobación del storyboard por el autor (2026-10-11), **sin títulos** en pantalla: la narración guía.
- [x] Animar las escenas (`c08_opciones.py`, una `Escena` por sección). La narración se lee del guion
      (`guion.py`: `⟨A⟩` → marca, `{Llave}` → cifra) y la composición sale de los cuadros del storyboard, que
      devuelven `Partes` con nombre. `make borrador` renderiza solo las escenas del guion, en su orden.
- [x] Narración con Kokoro; tiempos con marcas. Pausas `‖` en el guion (33 en el cap. 8, 2.5 s cada una):
      dentro de un bloque de voz, `self.wait` no detiene el audio, así que `Escena.narracion` reproduce el texto por
      tramos. Primer borrador sin pausas: 12.8 min (la voz es continua; la estimación de 1.3× pausas no se cumplió).
- [ ] Render final, montaje, música y `loudnorm`.
- [ ] Medir y anotar en §5: tiempo de render por minuto de video, horas de trabajo, problemas de pronunciación.
- [ ] Revisión crítica del piloto (¿se entiende sin el libro?, ¿ritmo?, ¿voz aceptable?) → decisión D3.

### Fase 3: Componentes reutilizables (`videos/componentes.py`)

Empezado con el storyboard del piloto: `titulo`, `ejes`, `quebrada`, `tarjeta` (con borde discontinuo para el lado
corto), `marca_k`, `llave`. Datos del caso en `videos/datos.py` (`C08` texto, `V08` números, `llenar()`), con test.


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
- [ ] Por video: subir `out/subtitulos/cNN.srt` (español) y miniatura 1280×720.
- [ ] Tráiler de 60–90 s de la serie (opcional).
- [ ] Publicar en el orden de la serie (1 → 13), no en el de producción.

## 4. Decisiones abiertas

| # | Decisión | Estado |
|---|---|---|
| D1 | Voz y velocidad de Kokoro (`ef_dora` / `em_alex` / `em_santa`) | ✅ `em_alex`, acento latinoamericano (`es-419`), velocidad 0.95 (2026-10-11) |
| D2 | Siglas: deletreadas ("ce-ce-ese") o leídas por su nombre ("cross currency swap") | ✅ Por su nombre; las que se pronuncian como palabra (ISDA, NYMEX, SOFR, NIIF) quedan así (2026-10-11) |
| D3 | Tras el piloto: Kokoro definitivo o regenerar la narración con ElevenLabs | Pendiente (Fase 2) |
| D4 | Visibilidad en YouTube: pública o no listada | Pendiente (Fase 6) |
| D5 | Créditos: autores del libro / curso / profesor en la descripción | Pendiente (Fase 6) |

## 5. Registro de avance

| Fecha | Avance |
|---|---|
| 2026-10-05 | Plan creado. Voz: Kokoro local con respaldo ElevenLabs; destino: YouTube. |
| 2026-10-05 | Fase 0 cerrada: entorno `videos/` aislado, Kokoro en CPU, Manim 0.21 con LaTeX en español (`hola.py`). |
| 2026-10-11 | Fase 1 cerrada: D1 (`em_alex`, `es-419`, 0.95) y D2 (siglas por su nombre); normalizador, servicio Kokoro, estilo y montaje probados. |
| 2026-10-11 | Voz aprobada tras escuchar la prueba. Franja de subtítulos reservada y subtítulos del capítulo en `montar.py`. |
| 2026-10-11 | Guion del piloto v2: ≈ 15 min, primera persona del plural, trayectorias simuladas, cierre como gancho. |
| 2026-10-11 | Storyboard del piloto (11 cuadros) y `datos.py`: las 26 cifras del capítulo 8 coinciden con el libro. |
| 2026-10-12 | Piloto animado: 10 escenas con voz; borrador 480p de 14.4 min (−14.5 LUFS). Pausas de 2.5 s tras 33 momentos clave. |
