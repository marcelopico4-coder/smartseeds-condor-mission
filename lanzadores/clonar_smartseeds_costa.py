"""
Clona el repositorio común de SmartSeeds (Costa) en una carpeta NUEVA, al lado de la de la Sierra.
No toca C:\\condor\\smartseeds. En VS Code: abre este archivo y pulsa "Run Python File".
Salida: C:\\condor\\clonar_smartseeds_costa.txt
"""
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DESTINO = AQUI / "smartseeds-costa"
REPO = "https://github.com/JotaCenfe/smartseeds-costa.git"
lineas = []


def di(texto):
    print(texto, flush=True)
    lineas.append(str(texto))


def correr(*cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    di(">>> " + " ".join(cmd))
    di((r.stdout + r.stderr).strip())
    return r.returncode


git = shutil.which("git")
if git is None:
    di("git NO está instalado o no está en el PATH: no se clonó nada.")
elif DESTINO.exists():
    di(f"{DESTINO} ya existe: no se vuelve a clonar.")
    correr(git, "status", "--short", "--branch", cwd=DESTINO)
    correr(git, "log", "--oneline", "-3", cwd=DESTINO)
else:
    if correr(git, "clone", "--branch", "main", REPO, str(DESTINO)) == 0:
        correr(git, "log", "--oneline", "-3", cwd=DESTINO)
        correr(git, "status", "--short", "--branch", cwd=DESTINO)
        di(f"Archivos en la carpeta nueva: {sum(1 for p in DESTINO.rglob('*') if p.is_file() and '.git' not in p.parts)}")
di(f"Python: {sys.executable}")
(AQUI / "clonar_smartseeds_costa.txt").write_text("\n".join(lineas), encoding="utf-8")
