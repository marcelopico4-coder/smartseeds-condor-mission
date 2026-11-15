"""
Corre las pruebas rápidas de la carpeta unida (smartseeds-costa) y muestra `git status`.
No procesa datos, no hace commit y no sube nada. El resultado queda en correr_pruebas.txt.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI / "smartseeds-costa"
entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
with open(AQUI / "correr_pruebas.txt", "a", encoding="utf-8") as notas:
    notas.write(f"\n===== pruebas · {datetime.now():%Y-%m-%d %H:%M:%S}\n")
    for orden in ([sys.executable, "tests/prueba_rapida.py"],
                  [sys.executable, "-m", "py_compile", "app/app.py", "app/smartseeds.py", "app/analisis.py"],
                  ["git", "status", "--short"]):
        p = subprocess.run(orden, cwd=REPO, env=entorno, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
        texto = f">>> {' '.join(orden[1:] if orden[0] == sys.executable else orden)}\n{p.stdout}{p.stderr}[código {p.returncode}]\n"
        print(texto, flush=True)
        notas.write(texto)
