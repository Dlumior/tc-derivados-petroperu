"""Carga de insumos con trazabilidad.

Cada insumo en data/procesado/*.yaml es un dict con al menos:
    valor: número
    fuente: texto (Nota / página del EEFF, o URL + fecha de consulta)
    estado: "verificado" | "supuesto" | "PENDIENTE"
Los "PENDIENTE" bloquean la versión final (make final).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(__file__).resolve().parents[2]
ESTADOS = {"verificado", "supuesto", "PENDIENTE"}


@dataclass(frozen=True)
class Insumo:
    clave: str
    valor: float
    fuente: str
    estado: str
    unidad: str = ""
    nota: str = ""


def _aplanar(d: dict[str, Any], prefijo: str = "") -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for k, v in d.items():
        clave = f"{prefijo}.{k}" if prefijo else k
        if isinstance(v, dict) and "valor" in v:
            out[clave] = v
        elif isinstance(v, dict):
            out.update(_aplanar(v, clave))
    return out


def cargar(nombre: str) -> dict[str, Insumo]:
    """cargar('exposiciones') -> {'fx.pen_neto': Insumo(...), ...}"""
    ruta = RAIZ / "data" / "procesado" / f"{nombre}.yaml"
    crudo = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    res = {}
    for clave, v in _aplanar(crudo).items():
        estado = v.get("estado", "PENDIENTE")
        if estado not in ESTADOS:
            raise ValueError(f"{clave}: estado inválido {estado!r}")
        if not str(v.get("fuente", "")).strip():
            raise ValueError(f"{clave}: falta 'fuente'")
        res[clave] = Insumo(clave, float(v["valor"]), v["fuente"], estado, v.get("unidad", ""), v.get("nota", ""))
    return res


def pendientes(*nombres: str) -> list[Insumo]:
    return [i for n in nombres for i in cargar(n).values() if i.estado == "PENDIENTE"]
