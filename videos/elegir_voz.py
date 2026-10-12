"""Muestras de voz para la decisión D1: un mismo párrafo del cap. 8 con variantes de acento y velocidad.

Uso: uv run python elegir_voz.py [voz]   → out/voces/<voz>_<acento>_<velocidad>.wav
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("ESPEAK_DATA_PATH", "/usr/share/espeak-ng-data")  # el espeakng-loader de PyPI trae una ruta rota

import numpy as np
import soundfile as sf
from kokoro import KPipeline
from misaki import espeak

PARRAFO = (
    "Un seguro de auto le da un derecho: si choca, la aseguradora paga el daño. "
    "Si no choca, usted no recibe nada, pero tampoco recupera la prima. "
    "Una opción funciona como el seguro: protege contra el escenario malo y conserva el bueno. "
    "A cambio, cuesta una prima."
)
# Texto crudo del libro, sin normalizar: muestra qué tendrá que corregir el normalizador.
CRUDO = (
    "Las opciones del informe son opciones sobre futuros de WTI, con vencimiento a 17, 50 y 79 días. "
    "Con K = 90, la call cuesta 6 y la put 5; el punto de equilibrio es 96."
)

voz = sys.argv[1] if len(sys.argv) > 1 else "em_alex"
salida = Path("out/voces")
salida.mkdir(parents=True, exist_ok=True)
pipeline = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")


def generar(texto, nombre, velocidad):
    audio = np.concatenate([a for _, _, a in pipeline(texto, voice=voz, speed=velocidad)])
    sf.write(salida / f"{nombre}.wav", audio, 24000)
    print(f"{nombre}.wav  {len(audio) / 24000:.1f} s")


for acento in ("es", "es-419"):
    pipeline.g2p = espeak.EspeakG2P(language=acento)
    for velocidad in (0.9, 1.0, 1.1):
        generar(PARRAFO, f"{voz}_{acento}_{velocidad}", velocidad)
generar(CRUDO, f"{voz}_es-419_crudo", 1.0)
