"""
Revisa la carpeta unida (smartseeds-costa) ANTES de subirla a GitHub. No cambia nada:
no hace commit y no sube. Solo mira y anota en revisar_subida.txt, al lado de este archivo:
rama, repositorio remoto, si GitHub tiene cambios nuevos, qué archivos se subirían y cuánto pesan,
si alguno parece guardar una clave, si esta computadora tiene permiso para subir, y las pruebas.
"""
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI / "smartseeds-costa"
NOTAS = open(AQUI / "revisar_subida.txt", "w", encoding="utf-8")
ENTORNO = {**os.environ, "PYTHONIOENCODING": "utf-8", "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}


def decir(texto=""):
    print(texto, flush=True)
    NOTAS.write(texto + "\n")
    NOTAS.flush()


def git(*orden, espera=90):
    try:
        p = subprocess.run(["git", *orden], cwd=REPO, env=ENTORNO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=espera)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, f"(sin respuesta en {espera} s)"


decir(f"===== revisar_subida · {datetime.now():%Y-%m-%d %H:%M:%S}")
for titulo, orden in (("rama", ("branch", "--show-current")), ("remoto", ("remote", "-v")),
                      ("último commit", ("log", "-1", "--format=%h %ad %s", "--date=iso")),
                      ("nombre para firmar", ("config", "user.name"))):
    decir(f"--- {titulo}\n{git(*orden)[1]}")
decir("--- correo para firmar: " + ("configurado" if git("config", "user.email")[1] else "NO configurado"))

codigo, salida = git("fetch", "origin")
decir(f"--- fetch origin [código {codigo}]\n{salida}")
decir("--- commits (míos sin subir / de GitHub sin bajar): " + git("rev-list", "--left-right", "--count", "HEAD...origin/main")[1])
decir("--- commits de GitHub que no tengo:\n" + git("log", "--format=%h %ad %an %s", "--date=iso", "HEAD..origin/main")[1])
decir("--- archivos que cambiaron en GitHub y aquí no están:\n" + git("diff", "--stat", "HEAD...origin/main")[1])

decir("--- git status --short\n" + git("status", "--short")[1])

nuevos = git("ls-files", "--others", "--exclude-standard")[1].splitlines()
cambiados = git("diff", "--name-only", "HEAD")[1].splitlines()
archivos = sorted({a for a in nuevos + cambiados if a.strip()})
pesos = []
for nombre in archivos:
    ruta = REPO / nombre
    if ruta.is_file():
        pesos.append((ruta.stat().st_size, nombre))
pesos.sort(reverse=True)
total = sum(p for p, _ in pesos)
decir(f"--- se subirían {len(pesos)} archivos nuevos o cambiados, {total / 1e6:.1f} MB en total")
decir("--- los 25 más pesados:")
for peso, nombre in pesos[:25]:
    decir(f"{peso / 1e6:9.2f} MB  {nombre}")
grandes = [(p, n) for p, n in pesos if p > 50e6]
decir(f"--- archivos de más de 50 MB (GitHub rechaza los de más de 100 MB): {len(grandes)}")
for peso, nombre in grandes:
    decir(f"{peso / 1e6:9.2f} MB  {nombre}")

decir("--- peso de todo lo que ya está en el repositorio (git count-objects)\n" + git("count-objects", "-vH")[1])

# Posibles claves: solo se anota el archivo y el número de línea, NUNCA el contenido.
SOSPECHA = re.compile(r"eyJ[A-Za-z0-9_-]{30,}|EARTHDATA_TOKEN|Bearer\s+[A-Za-z0-9._-]{20,}|"
                      r"(password|passwd|contrase[nñ]a|clave|token|api[_-]?key|secret)\s*[:=]\s*['\"][^'\"]{6,}['\"]|"
                      r"machine\s+urs\.earthdata", re.IGNORECASE)
CORREO = re.compile(r"[A-Za-z0-9._%+-]+@(gmail|hotmail|outlook|yahoo)\.[a-z.]+", re.IGNORECASE)
decir("--- posibles claves o correos personales en lo que se subiría (archivo:línea, sin mostrar el texto)")
hallazgos = 0
for peso, nombre in pesos:
    if peso > 3e6:
        continue
    try:
        texto = (REPO / nombre).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    for numero, linea in enumerate(texto.splitlines(), 1):
        if SOSPECHA.search(linea):
            decir(f"CLAVE?  {nombre}:{numero}")
            hallazgos += 1
        if CORREO.search(linea):
            decir(f"CORREO  {nombre}:{numero}")
            hallazgos += 1
decir(f"hallazgos: {hallazgos}")
decir("--- lo mismo en los archivos que ya estaban en el repositorio")
codigo, salida = git("grep", "-n", "-I", "-i", "-E", "-l",
                     "eyJ[A-Za-z0-9_-]{30,}|EARTHDATA_TOKEN|machine +urs\\.earthdata|@(gmail|hotmail|outlook|yahoo)\\.")
decir(salida or "(nada)")

decir("--- ¿esta computadora puede subir? (ensayo, no sube nada)")
codigo, salida = git("push", "--dry-run", "origin", "HEAD:refs/heads/_ensayo_permiso", espera=60)
decir(f"[código {codigo}]\n{salida}")

decir("--- pruebas")
for orden in ([sys.executable, "tests/prueba_rapida.py"],
              [sys.executable, "-m", "py_compile", "app/app.py", "app/smartseeds.py", "app/analisis.py"]):
    p = subprocess.run(orden, cwd=REPO, env=ENTORNO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    decir(f">>> {' '.join(orden[1:])}\n{(p.stdout + p.stderr)[-1500:]}[código {p.returncode}]")
decir(f"===== fin · {datetime.now():%H:%M:%S}")
