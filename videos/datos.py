"""Cifras del caso para los videos, leídas de las mismas fuentes que el libro (regla 1: ninguna cifra a mano).

- Macros de `informe/generado/valores.tex` (generadas por `make calc` en la raíz).
- `libro/v2/capas.json`: las tres capas del collar (F, días, strikes, prima) y la tasa r.
- Cálculos con `derivados.opciones` para lo que el libro deriva en el texto.

`C08` reúne las cifras del capítulo 8 como texto (lo que se muestra y se narra); `V08`, como números (para graficar).
`llenar(texto)` reemplaza las {llaves} del guion.
"""
import json
import math
import re
from functools import cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VALORES = RAIZ / "informe/generado/valores.tex"
CAPAS = RAIZ / "libro/v2/capas.json"


@cache
def macros() -> dict[str, str]:
    """Macro → texto, con `\\,\\%` convertido a " %"."""
    texto = VALORES.read_text()
    return {m[1]: m[2].replace(r"\,\%", " %").replace(r"\%", "%")
            for m in re.finditer(r"\\newcommand\{\\(\w+)\}\{([^\n]*)\}\s*$", texto, re.M)}


def numero(nombre: str) -> float:
    return float(re.sub(r"[^\d.\-]", "", macros()[nombre].replace(",", "")))


@cache
def capas() -> dict:
    return json.loads(CAPAS.read_text())


def f2(x: float) -> str:
    return f"{x:,.2f}"


def pct(x: float) -> str:
    return f"{round(x * 100):.0f} %"


def _c08() -> tuple[dict[str, float], dict[str, str]]:
    m, c = macros(), capas()
    nov, dic, ene = c["capas"]
    r, T = c["r"], ene["d"] / 365
    spot = numero("WTISpot")
    vpdif = math.exp(-r * T) * (ene["F"] - ene["kp"])
    call_paridad = ene["prima"] + vpdif
    v = {
        "WTISpot": spot, "WTIFut": ene["F"], "CollarPut": ene["kp"], "CollarCall": ene["kc"],
        "PrimaPutEne": ene["prima"], "PlazoDiasOpc": ene["d"], "VolCrudo": c["sig"], "r": r,
        "CaidaPutPct": 1 - ene["kp"] / ene["F"], "VPDif": vpdif, "CallParidad": call_paridad,
        "InvCubiertoMMbl": numero("InvCubiertoMMbl"), "InvCubiertoValor": numero("InvCubiertoValor"),
        "Caida10Mill": 0.10 * numero("InvCubiertoValor"),  # el 10 % es didáctico
        "CostoPutTotal": numero("CostoPutTotal"), "PrimaPut": numero("PrimaPut"),
        "PisoEne": spot - ene["kp"], "TechoEne": ene["kc"] - spot, "Renuncia120": 120 - ene["kc"],  # 120: libro
        "DistPutPct": 1 - ene["kp"] / spot, "DistCallPct": ene["kc"] / spot - 1,
        "ArbitrajeGan": 14 - call_paridad,  # 14: precio hipotético del guion
        "KpNov": nov["kp"], "KpDic": dic["kp"], "KcNov": nov["kc"], "KcDic": dic["kc"],
        "FNov": nov["F"], "FDic": dic["F"], "DiasNov": nov["d"], "DiasDic": dic["d"],
    }
    t = {k: f2(x) for k, x in v.items()}
    t.update({
        "PlazoDiasOpc": f"{ene['d']}", "DiasNov": f"{nov['d']}", "DiasDic": f"{dic['d']}",
        "VolCrudo": m["VolCrudo"], "CoberturaCrudoPct": m["CoberturaCrudoPct"], "LineasPct": m["LineasPct"],
        "InvCubiertoMMbl": m["InvCubiertoMMbl"], "InvCubiertoValor": m["InvCubiertoValor"],
        "CostoPutTotal": m["CostoPutTotal"], "PrimaPut": m["PrimaPut"], "Caida10Mill": f"{v['Caida10Mill']:,.1f}",
        "CaidaPutPct": pct(v["CaidaPutPct"]), "DistPutPct": pct(v["DistPutPct"]), "DistCallPct": pct(v["DistCallPct"]),
    })
    return v, t


V08, C08 = _c08()


def llenar(texto: str, cifras: dict[str, str] = C08) -> str:
    """Reemplaza las {llaves} del guion; falla si alguna no existe."""
    return re.sub(r"\{(\w+)\}", lambda m: cifras[m[1]], texto)
