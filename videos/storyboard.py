"""Renderiza el storyboard de un capítulo: un PNG por cuadro y una hoja de contacto.

uv run python storyboard.py 08 [cuadro ...]   → out/storyboard/c08/*.png y out/storyboard/c08.png
"""
import sys
from importlib import import_module
from pathlib import Path

from manim import tempconfig
from PIL import Image, ImageDraw, ImageFont

cap = sys.argv[1].zfill(2)
modulo = import_module(f"storyboard_c{cap}")
pedidos = set(sys.argv[2:])
salida = Path("out/storyboard") / f"c{cap}"
salida.mkdir(parents=True, exist_ok=True)

imagenes = []
for nombre, _ in modulo.CUADROS:
    archivo = salida / f"{nombre}.png"
    if not pedidos or nombre in pedidos:
        with tempconfig({"quality": "high_quality", "write_to_movie": False, "disable_caching": True,
                         "verbosity": "WARNING"}):
            escena = getattr(modulo, f"SB{nombre}")()
            escena.render()
            escena.renderer.camera.get_image().convert("RGB").save(archivo)
        print(archivo)
    imagenes.append((nombre, Image.open(archivo)))

# Hoja de contacto: 3 columnas, miniaturas de 640 × 360 con su nombre.
cols, w, h, rot = 3, 640, 360, 28
filas = -(-len(imagenes) // cols)
hoja = Image.new("RGB", (cols * w, filas * (h + rot)), "#0b0f13")
dibujo = ImageDraw.Draw(hoja)
letra = ImageFont.truetype("/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf", 18)
for i, (nombre, img) in enumerate(imagenes):
    x, y = i % cols * w, i // cols * (h + rot)
    dibujo.text((x + 8, y + 4), nombre, fill="#f2b632", font=letra)
    hoja.paste(img.resize((w, h)), (x, y + rot))
hoja.save(salida.with_suffix(".png"))
print(salida.with_suffix(".png"))
