"""
Abre SmartSeeds (la interfaz nueva de la carpeta unida smartseeds-costa) en el navegador.

Si ya está corriendo en http://localhost:8766 solo abre el navegador. Si no, la arranca (Streamlit)
y abre el navegador cuando está lista. Para apagarla: cierra la terminal donde quedó corriendo.
La app solo se ve en esta computadora: no se publica nada.
La vista técnica de antes (app/app.py) sigue aparte, en el puerto 8765 (▷ abrir_app_union.py).
"""
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

DIRECCION = "http://localhost:8766"
REPO = Path(__file__).resolve().parent / "smartseeds-costa"


def ya_esta_corriendo() -> bool:
    try:
        with urllib.request.urlopen(DIRECCION + "/_stcore/health", timeout=3) as respuesta:
            return respuesta.status == 200
    except Exception:  # noqa: BLE001
        return False


if ya_esta_corriendo():
    print(f"La app ya está corriendo: se abre {DIRECCION} en el navegador.")
    webbrowser.open(DIRECCION)
else:
    print(f"Arrancando la app en {DIRECCION} (cierra esta terminal para apagarla) ...", flush=True)
    _env = Path(sys.executable).parent
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if (_env / "Library" / "bin").exists():
        entorno["PATH"] = os.pathsep.join(str(r) for r in (_env, _env / "Library" / "bin", _env / "Scripts")) \
            + os.pathsep + entorno.get("PATH", "")
    proceso = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app/smartseeds.py",
                                "--server.headless", "true", "--server.port", "8766",
                                "--server.address", "localhost", "--browser.gatherUsageStats", "false"],
                               cwd=REPO, env=entorno, stdin=subprocess.DEVNULL)
    for _ in range(40):                 # espera a que responda (hasta 40 segundos) y abre el navegador
        if ya_esta_corriendo():
            webbrowser.open(DIRECCION)
            break
        time.sleep(1)
    proceso.wait()
