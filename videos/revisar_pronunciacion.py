"""Sintetiza cada término de SIGLAS e INGLES en una frase y la transcribe con Whisper.

Si Whisper no reconoce el término, probablemente el oyente tampoco: hay que cambiar su escritura en narrador.py.
uv run python revisar_pronunciacion.py [término ...]   → tabla en out/pronunciacion.tsv
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import stable_whisper

import narrador
from narrador import ACENTO, INGLES, SIGLAS, VELOCIDAD, VOZ, normalizar

terminos = sys.argv[1:] or list(INGLES) + list(SIGLAS)
pipeline = narrador._kokoro_service().pipeline(ACENTO)
whisper = stable_whisper.load_model("base")
Path("out").mkdir(exist_ok=True)
wav = Path("out/_pronunciacion.wav")

with open("out/pronunciacion.tsv", "w") as tabla:
    tabla.write("término\tse sintetiza\twhisper oye\n")
    for termino in terminos:
        frase = normalizar(f"Ahora veremos el {termino} con calma.")
        audio = np.concatenate([a for _, _, a in pipeline(frase, voice=VOZ, speed=VELOCIDAD)])
        sf.write(wav, audio, 24000)
        oido = whisper.transcribe(str(wav), language="es", verbose=None).text.strip()
        fila = f"{termino}\t{frase}\t{oido}"
        tabla.write(fila + "\n")
        tabla.flush()
        print(fila, flush=True)
wav.unlink(missing_ok=True)
