"""
Paso 2 de la subida a GitHub (pedido del usuario, 14 nov 23:32). Se puede ejecutar más de una vez.

1) En la rama `interfaz-agricultor` une lo que el equipo subió a GitHub (origin/main). Los tres archivos que
   chocan (app/app.py, recolectar_referencia.py, CLAUDE.md) se toman ya unidos a mano de C:\\condor\\_union\\resuelto.
   Si choca cualquier otro archivo, o si las pruebas fallan, deshace la unión y no sube nada.
2) Corre las pruebas.
3) Sube la rama a la copia (fork) de la cuenta marcelopico4-coder, si ya existe. Nunca toca `main`
   ni el repositorio de JotaCenfe.
Todo queda anotado en unir_y_subir.txt, al lado de este archivo.
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI / "smartseeds-costa"
RESUELTO = AQUI / "_union" / "resuelto"
RAMA = "interfaz-agricultor"
COPIA = "https://github.com/marcelopico4-coder/smartseeds-costa.git"
UNIDOS = {"app/app.py": "app__app.py", "recolectar_referencia.py": "recolectar_referencia.py", "CLAUDE.md": "CLAUDE.md"}
NOTAS = open(AQUI / "unir_y_subir.txt", "w", encoding="utf-8")
FIRMA = {"GIT_AUTHOR_NAME": "Condor Mission", "GIT_COMMITTER_NAME": "Condor Mission",
         "GIT_AUTHOR_EMAIL": "marcelopico4-coder@users.noreply.github.com",
         "GIT_COMMITTER_EMAIL": "marcelopico4-coder@users.noreply.github.com"}
ENTORNO = {**os.environ, **FIRMA, "PYTHONIOENCODING": "utf-8", "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}

MENSAJE = """Une lo subido por el equipo (MAG, uso de la tierra, HLS y VH) con la interfaz nueva

Choques resueltos a mano, sin descartar nada de ningún lado:
- app/app.py: el bloque «Cultivo mapeado (MAG)» va dentro del detalle del terreno.
- recolectar_referencia.py: se conserva la lectura con leer_recuadro; entra la exclusión del banano beta.
- CLAUDE.md: se juntan las dos versiones.

Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Pg3QeeiaHoi9YWNm54TH1E
"""


def decir(texto=""):
    print(texto, flush=True)
    NOTAS.write(texto + "\n")
    NOTAS.flush()


def git(*orden, espera=180):
    try:
        p = subprocess.run(["git", *orden], cwd=REPO, env=ENTORNO, capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=espera)
    except subprocess.TimeoutExpired:
        return -1, f"(sin respuesta en {espera} s)"
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", errors="replace").strip()


def pruebas() -> bool:
    bien = True
    modulos = sorted(str(r.relative_to(REPO)).replace("\\", "/") for r in (REPO / "src").glob("*.py"))
    for orden in ([sys.executable, "tests/prueba_rapida.py"],
                  [sys.executable, "-m", "py_compile", "app/app.py", "app/smartseeds.py", "app/analisis.py",
                   "recolectar_referencia.py", *modulos]):
        p = subprocess.run(orden, cwd=REPO, env=ENTORNO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
        decir(f">>> {' '.join(orden[1:4])} ...\n{(p.stdout + p.stderr)[-2500:]}[código {p.returncode}]")
        bien = bien and p.returncode == 0
    return bien


decir(f"===== unir_y_subir · {datetime.now():%Y-%m-%d %H:%M:%S}")
rama = git("branch", "--show-current")[1]
if rama != RAMA:
    decir(f"La rama es '{rama}', no '{RAMA}': no sigo.")
    raise SystemExit(1)

if git("merge-base", "--is-ancestor", "origin/main", "HEAD")[0] == 0:
    decir("--- la unión con origin/main ya estaba hecha")
else:
    if git("status", "--porcelain")[1]:
        decir("Hay cambios sin guardar en la carpeta: no sigo.\n" + git("status", "--short")[1])
        raise SystemExit(1)
    codigo, salida = git("merge", "origin/main", "--no-commit", "--no-ff")
    decir(f"--- git merge origin/main [código {codigo}]\n{salida[-3000:]}")
    chocan = [a for a in git("diff", "--name-only", "--diff-filter=U")[1].splitlines() if a.strip()]
    decir(f"--- archivos que chocan: {chocan}")
    if set(chocan) - set(UNIDOS):
        decir("Chocó un archivo que no estaba previsto: deshago la unión.\n" + git("merge", "--abort")[1])
        raise SystemExit(1)
    for nombre, plano in UNIDOS.items():
        shutil.copyfile(RESUELTO / plano, REPO / nombre)
        codigo, salida = git("add", "--", nombre)
        decir(f"  unido a mano: {nombre} [código {codigo}] {salida[-300:]}")
    if not pruebas():
        decir("Las pruebas fallaron con la unión: la deshago y no subo nada.\n" + git("merge", "--abort")[1])
        raise SystemExit(1)
    (AQUI / "_union" / "mensaje_union.txt").write_text(MENSAJE, encoding="utf-8")
    codigo, salida = git("commit", "-F", str(AQUI / "_union" / "mensaje_union.txt"))
    decir(f"--- commit de la unión [código {codigo}]\n{salida[-1500:]}")
    if codigo != 0:
        raise SystemExit(1)

decir("--- commits de la rama que no están en origin/main:\n" + git("log", "--format=%h %an %s", "origin/main..HEAD")[1])
decir("--- git status --short:\n" + (git("status", "--short")[1] or "(limpio)"))
decir("--- pruebas con todo unido")
if not pruebas():
    decir("Las pruebas fallan: no subo nada.")
    raise SystemExit(1)

codigo, salida = git("ls-remote", "--heads", COPIA, espera=60)
if codigo != 0:
    decir(f"--- la copia todavía no existe en la cuenta marcelopico4-coder: NO se subió nada.\n{salida[-600:]}")
else:
    decir(f"--- ramas de la copia:\n{salida}")
    if "copia" not in git("remote")[1].split():
        git("remote", "add", "copia", COPIA)
    codigo, salida = git("push", "-u", "copia", RAMA, espera=600)
    decir(f"--- git push copia {RAMA} [código {codigo}]\n{salida[-2500:]}")
    decir("--- comprobación: " + git("ls-remote", "--heads", COPIA, RAMA, espera=60)[1])
    decir("--- commit local: " + git("rev-parse", "HEAD")[1])
decir(f"===== fin · {datetime.now():%H:%M:%S}")
