"""Une las escenas de un capítulo (en el orden del guion, o en el de definición si no hay guion) y prepara la subida
a YouTube.

uv run python montar.py 08 [calidad]      (calidad: 480p15 | 1080p60, por defecto 1080p60)

Genera (sufijo _480p15 en los borradores):
  out/c08.mp4                 video limpio, audio a −14 LUFS: el que se sube
  out/subtitulos/c08.srt      subtítulos del capítulo: se suben aparte (carpeta propia para que el
                              reproductor no los cargue solo, a tamaño proporcional al video)
  out/vista_previa/c08.mp4    subtítulos pequeños quemados en la franja reservada, para revisar el encuadre
"""
import inspect
import re
import subprocess
import sys
import tempfile
from datetime import timedelta
from importlib import import_module
from pathlib import Path

from manim import Scene

# Estilo parecido al de YouTube: letra blanca sobre caja semitransparente, dentro de la franja de estilo.py.
# Las unidades son las de libass para .srt (alto de referencia 288): 12 ≈ 4 % del alto del cuadro.
ESTILO_SUBTITULOS = ("FontName=Liberation Sans,FontSize=12,PrimaryColour=&H00FFFFFF,BorderStyle=3,"
                     "OutlineColour=&H99000000,Outline=1,Shadow=0,MarginV=8")
TIEMPO = re.compile(r"(\d+):(\d+):(\d+),(\d+)")


def duracion(video: Path) -> float:
    salida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                             str(video)], capture_output=True, text=True, check=True)
    return float(salida.stdout)


def desplazar(srt: str, segundos: float) -> list[str]:
    """Bloques del .srt con los tiempos desplazados, sin numerar."""
    def mover(m):
        h, mi, s, ms = map(int, m.groups())
        t = timedelta(hours=h, minutes=mi, seconds=s, milliseconds=ms) + timedelta(seconds=segundos)
        total = int(t.total_seconds() * 1000)
        return f"{total // 3_600_000:02d}:{total // 60_000 % 60:02d}:{total // 1000 % 60:02d},{total % 1000:03d}"

    bloques = [b.strip().split("\n", 1)[1] for b in srt.strip().split("\n\n") if b.strip()]
    return [TIEMPO.sub(mover, b) for b in bloques]


cap = sys.argv[1].zfill(2)
calidad = sys.argv[2] if len(sys.argv) > 2 else "1080p60"
modulos = sorted(Path(".").glob(f"c{cap}_*.py"))
if len(modulos) != 1:
    sys.exit(f"Se esperaba un único c{cap}_*.py y hay {len(modulos)}")
nombre = modulos[0].stem
modulo = import_module(nombre)

if (Path("guiones") / f"c{cap}.md").exists():  # el guion manda el orden y excluye clases base
    from guion import narracion

    escenas = [getattr(modulo, clase) for clase in narracion(cap)]
else:
    escenas = sorted(
        (c for c in vars(modulo).values()
         if inspect.isclass(c) and issubclass(c, Scene) and c.__module__ == nombre and "construct" in vars(c)),
        key=lambda c: inspect.getsourcelines(c)[1],
    )
videos = [Path("media/videos") / nombre / calidad / f"{c.__name__}.mp4" for c in escenas]
faltan = [str(v) for v in videos if not v.exists()]
if faltan:
    sys.exit("Faltan renders:\n  " + "\n  ".join(faltan))

base = f"c{cap}{'' if calidad == '1080p60' else '_' + calidad}"
salida, srt, previa = Path("out") / f"{base}.mp4", Path("out/subtitulos") / f"{base}.srt", Path("out/vista_previa") / f"{base}.mp4"
for carpeta in (salida, srt, previa):
    carpeta.parent.mkdir(parents=True, exist_ok=True)

with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lista:
    lista.writelines(f"file '{v.resolve()}'\n" for v in videos)
subprocess.run(
    ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista.name,
     "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", str(salida)],
    check=True,
)

bloques, inicio = [], 0.0
for video in videos:
    if video.with_suffix(".srt").exists():
        bloques += desplazar(video.with_suffix(".srt").read_text(), inicio)
    inicio += duracion(video)
srt.write_text("\n\n".join(f"{i}\n{b}" for i, b in enumerate(bloques, 1)) + "\n")

subprocess.run(
    ["ffmpeg", "-loglevel", "error", "-y", "-i", str(salida),
     "-vf", f"subtitles={srt}:force_style='{ESTILO_SUBTITULOS}'",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy", str(previa)],
    check=True,
)
print(f"{salida}  ({len(videos)} escenas: {', '.join(c.__name__ for c in escenas)})\n{srt}  ({len(bloques)} subtítulos)\n{previa}")
