"""
SmartSeeds · bajar los dos Excel oficiales del SIPA (MAG) y MOSTRAR cómo quedaría tablas/mercado.csv.
En VS Code: abre este archivo y pulsa "Run Python File". NO escribe la tabla: solo muestra el resultado
(`python -m src.preparar_mercado ver`) y lo deja en datos/crudos/registros/actualizar_mercado.txt para
revisarlo. Si se ve bien, se escribe después con  python -m src.preparar_mercado

Primero pregunta el tamaño de cada archivo al servidor; si entre los dos pasan de LIMITE_MB no baja nada.
"""
import os
import subprocess
import sys
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent
CARPETA = RAIZ / "datos" / "crudos" / "mercado"
REGISTRO = RAIZ / "datos" / "crudos" / "registros" / "actualizar_mercado.txt"
LIMITE_MB = 80
BASE = "https://sipa.agricultura.gob.ec/descargas/base-estadistica/"
ARCHIVOS = {"superficie-produccion.xlsx": BASE + "modulo_productivo/superficie-produccion.xlsx",
            "precios-productor-ponderado.xlsx": BASE + "modulo_economico/precios-productor-ponderado.xlsx"}

CARPETA.mkdir(parents=True, exist_ok=True)
REGISTRO.parent.mkdir(parents=True, exist_ok=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
registro = open(REGISTRO, "w", encoding="utf-8")


def decir(texto):
    print(texto, flush=True)
    registro.write(str(texto) + "\n")
    registro.flush()


try:
    faltan = {n: u for n, u in ARCHIVOS.items() if not (CARPETA / n).exists()}
    tamanos = {}
    for nombre, url in faltan.items():
        r = requests.head(url, timeout=60, allow_redirects=True)
        tamanos[nombre] = int(r.headers.get("content-length") or 0) / 1e6
        decir(f"{nombre}: {tamanos[nombre]:.1f} MB (respuesta {r.status_code})")
    if sum(tamanos.values()) > LIMITE_MB:
        raise SystemExit(f"Pesan más de {LIMITE_MB} MB entre los dos: no se baja nada. Decide tú si subir el límite.")
    for nombre, url in faltan.items():
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        (CARPETA / nombre).write_bytes(r.content)
        decir(f"bajado {nombre}: {len(r.content) / 1e6:.1f} MB")
    base = Path(sys.executable).parent
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
               "PATH": os.pathsep.join([str(base), str(base / "Library" / "bin"), os.environ.get("PATH", "")])}
    p = subprocess.run([sys.executable, "-m", "src.preparar_mercado", "ver"], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    decir(p.stdout + p.stderr)
    decir(f"[código de salida {p.returncode}] · NO se escribió tablas/mercado.csv")
except Exception as error:  # noqa: BLE001
    decir(f"ERROR: {error!r}")
