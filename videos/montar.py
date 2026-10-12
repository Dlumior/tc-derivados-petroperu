"""Une las escenas de un capítulo en el orden en que están definidas y normaliza el audio para YouTube.

uv run python montar.py 08 [calidad]   → out/c08.mp4      (calidad: 480p15 | 1080p60, por defecto 1080p60)
"""
import inspect
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path

from manim import Scene

cap = sys.argv[1].zfill(2)
calidad = sys.argv[2] if len(sys.argv) > 2 else "1080p60"
modulos = sorted(Path(".").glob(f"c{cap}_*.py"))
if len(modulos) != 1:
    sys.exit(f"Se esperaba un único c{cap}_*.py y hay {len(modulos)}")
nombre = modulos[0].stem
modulo = import_module(nombre)

escenas = sorted(
    (c for c in vars(modulo).values()
     if inspect.isclass(c) and issubclass(c, Scene) and c.__module__ == nombre),
    key=lambda c: inspect.getsourcelines(c)[1],
)
videos = [Path("media/videos") / nombre / calidad / f"{c.__name__}.mp4" for c in escenas]
faltan = [str(v) for v in videos if not v.exists()]
if faltan:
    sys.exit("Faltan renders:\n  " + "\n  ".join(faltan))

Path("out").mkdir(exist_ok=True)
salida = Path("out") / f"c{cap}{'' if calidad == '1080p60' else '_' + calidad}.mp4"
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lista:
    lista.writelines(f"file '{v.resolve()}'\n" for v in videos)
subprocess.run(
    ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista.name,
     "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", str(salida)],
    check=True,
)
print(f"{salida}  ({len(videos)} escenas: {', '.join(c.__name__ for c in escenas)})")
