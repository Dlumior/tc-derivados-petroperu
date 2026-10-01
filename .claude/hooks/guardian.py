#!/usr/bin/env python3
"""Hooks del proyecto (un solo script, varios modos). Lee el JSON del hook por stdin.

  pre-edit    PreToolUse(Edit|Write|MultiEdit): bloquea edición de fuentes crudas y archivos generados.
  post-edit   PostToolUse(Edit|Write|MultiEdit): ruff + pytest para .py; controles de fuente/cifras para .tex.
  post-bash   PostToolUse(Bash): tras compilar LaTeX, verifica el límite de 10 páginas.
  inicio      SessionStart: inyecta estado del proyecto (días al plazo, insumos pendientes, páginas).

Código 2 = feedback bloqueante que Claude ve y debe corregir.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
PY = str(RAIZ / ".venv" / "bin" / "python") if (RAIZ / ".venv" / "bin" / "python").exists() else sys.executable
PLAZO = dt.datetime(2026, 10, 5, 19, 30)

PROTEGIDOS = {
    "data/raw/": "Las fuentes originales son inmutables. Trabaje sobre data/procesado/.",
    "informe/generado/": "Archivo generado. Cambie src/ o scripts/run_all.py y ejecute `make calc`.",
}


def _entrada() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def _rel(ruta: str) -> str:
    try:
        return str(Path(ruta).resolve().relative_to(RAIZ.resolve()))
    except ValueError:
        return ruta


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, timeout=240)


def pre_edit(d: dict) -> int:
    rel = _rel(d.get("tool_input", {}).get("file_path", ""))
    for pref, motivo in PROTEGIDOS.items():
        if rel.startswith(pref):
            print(f"BLOQUEADO: {rel}. {motivo}", file=sys.stderr)
            return 2
    return 0


def post_edit(d: dict) -> int:
    rel = _rel(d.get("tool_input", {}).get("file_path", ""))
    problemas: list[str] = []
    if rel.endswith(".py"):
        _run(["ruff", "format", rel])
        r = _run(["ruff", "check", "--fix", rel])
        if r.returncode:
            problemas.append("ruff:\n" + r.stdout[-2000:])
        if rel.startswith(("src/derivados/", "tests/")):
            r = _run([PY, "-m", "pytest", "-q", "-x", "--no-header"])
            if r.returncode:
                problemas.append("pytest FALLA (¿se rompió la réplica del Excel de referencia?):\n" + r.stdout[-2500:])
    elif rel.startswith("informe/secciones/") and rel.endswith(".tex"):
        r = _run([PY, "scripts/verificar_informe.py"])
        salida = r.stdout + r.stderr
        lineas = [ln for ln in salida.splitlines() if rel in ln and ("✗" in ln or "cifra escrita a mano" in ln)]
        if lineas:
            problemas.append("Controles del informe:\n" + "\n".join(lineas))
    if problemas:
        print("\n\n".join(problemas), file=sys.stderr)
        return 2
    return 0


def post_bash(d: dict) -> int:
    cmd = d.get("tool_input", {}).get("command", "")
    if not any(k in cmd for k in ("latexmk", "lualatex", "make pdf", "make final", "make all")):
        return 0
    r = _run([PY, "scripts/verificar_informe.py", "--solo-paginas"])
    if r.returncode:
        print(
            r.stdout + r.stderr + "\nRecorte contenido: el enunciado solo evalúa 10 páginas POR TODO CONCEPTO.",
            file=sys.stderr,
        )
        return 2
    return 0


def inicio(_: dict) -> int:
    restante = PLAZO - dt.datetime.now()
    pend = "?"
    try:
        sys.path.insert(0, str(RAIZ / "src"))
        from derivados.datos import pendientes

        pend = str(len(pendientes("exposiciones", "mercado")))
    except Exception:  # noqa: BLE001
        pass
    pdf = RAIZ / "informe" / "out" / "main.pdf"
    paginas = "sin compilar"
    if pdf.exists():
        try:
            from pypdf import PdfReader

            paginas = f"{len(PdfReader(str(pdf)).pages)}/10"
        except Exception:  # noqa: BLE001
            pass
    print(
        f"[Estado TC Derivados] Entrega: 5-oct-2026 19:30 (quedan {restante.days} d {restante.seconds // 3600} h). "
        f"Insumos PENDIENTES: {pend}. Páginas: {paginas}. Ver CLAUDE.md para el flujo."
    )
    return 0


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"pre-edit": pre_edit, "post-edit": post_edit, "post-bash": post_bash, "inicio": inicio}.get(modo)
    sys.exit(fn(_entrada()) if fn else 0)
