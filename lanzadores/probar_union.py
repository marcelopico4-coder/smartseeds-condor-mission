"""
Lanza el procesamiento de la Sierra en la carpeta unida (smartseeds-costa) desde VS Code.

1) Cierra las corridas anteriores de procesar_sierra.py que se hayan quedado colgadas (solo los
   procesos python/conda/cmd cuya línea de comando nombra procesar_sierra.py, _prueba_lectura.py,
   _diagnostico.py o src.lectura_remota).
2) Ejecuta smartseeds-costa/procesar_sierra.py, que deja su registro en
   smartseeds-costa/datos/crudos/registros/procesar_sierra.txt
3) Muestra `git status` de la carpeta unida (no hace commit ni sube nada).
Lo que pasa aquí se anota en probar_union.txt, al lado de este archivo.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI / "smartseeds-costa"
NOTAS = open(AQUI / "probar_union.txt", "a", encoding="utf-8")


def decir(texto):
    print(texto, flush=True)
    NOTAS.write(texto + "\n")
    NOTAS.flush()


decir(f"\n===== probar_union · {datetime.now():%Y-%m-%d %H:%M:%S}")
buscar = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|conda|cmd)' -and "
          "$_.CommandLine -match 'procesar_sierra\\.py|_prueba_lectura\\.py|_diagnostico\\.py|src\\.lectura_remota' } | "
          "ForEach-Object { $_.ProcessId.ToString() + ' ' + $_.Name }")
try:
    r = subprocess.run(["powershell", "-NoProfile", "-Command", buscar], capture_output=True, text=True,
                       timeout=60, stdin=subprocess.DEVNULL)
    colgados = [linea.split() for linea in r.stdout.splitlines() if linea.strip()]
    decir(f"Corridas anteriores todavía abiertas: {len(colgados)}")
    for pid, nombre in colgados:
        if pid.isdigit() and int(pid) != os.getpid():
            k = subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True, text=True,
                               stdin=subprocess.DEVNULL)
            decir(f"  cerrado {nombre} ({pid}): código {k.returncode}")
except Exception as error:  # noqa: BLE001
    decir(f"No se pudo revisar si había corridas colgadas: {error!r}")

decir("Lanzando procesar_sierra.py ...")
codigo = subprocess.run([sys.executable, str(REPO / "procesar_sierra.py")], cwd=REPO,
                        stdin=subprocess.DEVNULL).returncode
decir(f"procesar_sierra.py terminó con código {codigo} · {datetime.now():%H:%M:%S}")
g = subprocess.run(["git", "status", "--short"], cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
decir("git status --short (sin commit, sin subir):\n" + g.stdout)
