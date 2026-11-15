"""
Sube TODO SmartSeeds a un repositorio nuevo de tu cuenta de GitHub.

    Destino: https://github.com/marcelopico4-coder/smartseeds-condor-mission  (rama main)

Qué hace, en orden:
  1. Copia a `lanzadores/` los programitas sueltos de la carpeta de arriba (ver_app.py y parecidos),
     para que la otra computadora también los tenga.
  2. Prepara todo lo del proyecto (código, tablas, datos procesados, modelos 3D, documentos) y,
     como respaldo, también `datos/crudos/` (los Excel y mapas descargados), que normalmente no se suben.
  3. Revisa que no se cuele ninguna clave: no sube archivos de credenciales ni archivos de más de 95 MB.
  4. Guarda todo en un commit y lo sube a la rama `main` del repositorio nuevo.
  5. Comprueba que GitHub tiene exactamente lo mismo que esta computadora.

Antes de ejecutarlo hay que crear el repositorio vacío en GitHub (una sola vez):
  https://github.com/new  ->  nombre: smartseeds-condor-mission  ->  Public  ->  SIN marcar "Add a README"

Se puede volver a ejecutar las veces que haga falta: solo sube lo que haya cambiado.
Deja lo que hizo en `subir_a_mi_github.txt`.
"""
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CUENTA = "marcelopico4-coder"
REPOSITORIO = "smartseeds-condor-mission"
DESTINO = f"https://github.com/{CUENTA}/{REPOSITORIO}.git"
REMOTO = "personal"
REGISTRO = RAIZ / "subir_a_mi_github.txt"
TAMANO_MAXIMO = 95 * 1024 * 1024          # GitHub rechaza archivos de 100 MB o más

# Nombres de archivo que nunca se suben (credenciales)
PROHIBIDOS = re.compile(r"(^|[\\/])(\.netrc|_netrc|\.dodsrc|\.env|secrets\.toml|id_rsa|id_ed25519|.*\.pem|.*\.pfx|"
                        r"\.urs_cookies|\.edl_token|credentials(\.json)?)$", re.IGNORECASE)
# Contenido que delata una clave (se revisa en los archivos de texto pequeños)
CLAVES = re.compile(r"machine\s+urs\.earthdata|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|"
                    r"eyJ[A-Za-z0-9_-]{40,}\.[A-Za-z0-9_-]{20,}\.|-----BEGIN [A-Z ]*PRIVATE KEY-----")

lineas = []


def decir(texto=""):
    print(texto, flush=True)
    lineas.append(str(texto))


def terminar(codigo):
    REGISTRO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    sys.exit(codigo)


def buscar_git():
    encontrado = shutil.which("git")
    if encontrado:
        return encontrado
    for ruta in (r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files (x86)\Git\cmd\git.exe"):
        if Path(ruta).exists():
            return ruta
    return None


GIT = buscar_git()


def git(*argumentos, tope=600, callado=False):
    """Ejecuta git en la raíz del repositorio. Devuelve (código, salida)."""
    entorno = dict(os.environ, GIT_TERMINAL_PROMPT="0")          # si falta la sesión, que falle en vez de quedarse esperando
    try:
        r = subprocess.run([GIT, "-c", "core.quotepath=false", *argumentos], cwd=RAIZ, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=tope, env=entorno)
    except subprocess.TimeoutExpired:
        return 1, f"(se pasó de {tope} segundos)"
    salida = (r.stdout + r.stderr).strip()
    if not callado and salida:
        decir("    " + salida.replace("\n", "\n    ")[:3000])
    return r.returncode, salida


def copiar_lanzadores():
    """Los .py y .md sueltos de la carpeta de arriba (C:\\condor) pasan a `lanzadores/`."""
    arriba, destino, copiados = RAIZ.parent, RAIZ / "lanzadores", 0
    for archivo in sorted(arriba.glob("*.py")) + sorted(arriba.glob("*.md")):
        if archivo.is_file() and archivo.stat().st_size < 2_000_000 and not PROHIBIDOS.search(archivo.name):
            destino.mkdir(exist_ok=True)
            shutil.copy2(archivo, destino / archivo.name)
            copiados += 1
    if copiados:
        (destino / "LEEME.txt").write_text(
            "Copia de los programitas sueltos de la carpeta de trabajo (C:\\condor en la primera computadora).\n"
            "Algunos tienen rutas fijas de esa computadora: revisarlas antes de usarlos en otra.\n", encoding="utf-8")
    decir(f"  Programitas copiados a lanzadores/: {copiados}")


def agregar_crudos():
    """`datos/crudos/` está en .gitignore; aquí se agrega a propósito, como respaldo."""
    carpeta, agregados, saltados = RAIZ / "datos" / "crudos", [], []
    if not carpeta.exists():
        decir("  No hay datos/crudos en esta computadora.")
        return
    for archivo in carpeta.rglob("*"):
        if not archivo.is_file():
            continue
        relativo = archivo.relative_to(RAIZ).as_posix()
        if PROHIBIDOS.search(relativo):
            saltados.append((relativo, "es un archivo de credenciales"))
        elif archivo.stat().st_size > TAMANO_MAXIMO:
            saltados.append((relativo, f"pesa {archivo.stat().st_size / 1e6:.0f} MB"))
        else:
            agregados.append(relativo)
    for i in range(0, len(agregados), 200):
        git("add", "-f", "--", *agregados[i:i + 200], callado=True)
    decir(f"  datos/crudos: {len(agregados)} archivos agregados como respaldo.")
    for relativo, motivo in saltados:
        decir(f"    NO se sube {relativo}: {motivo}")


def revisar_lo_preparado():
    """Quita de la subida cualquier archivo demasiado grande o que parezca una clave."""
    _, salida = git("diff", "--cached", "--name-only", "--diff-filter=AM", callado=True)
    quitados = 0
    for relativo in [x for x in salida.splitlines() if x.strip()]:
        archivo, motivo = RAIZ / relativo, None
        if not archivo.is_file():
            continue
        peso = archivo.stat().st_size
        if PROHIBIDOS.search(relativo):
            motivo = "es un archivo de credenciales"
        elif peso > TAMANO_MAXIMO:
            motivo = f"pesa {peso / 1e6:.0f} MB (GitHub no acepta 100 MB o más)"
        elif peso < 1_500_000 and archivo.name != Path(__file__).name:
            try:
                if CLAVES.search(archivo.read_text(encoding="utf-8", errors="ignore")):
                    motivo = "parece contener una clave o un token"
            except OSError:
                pass
        if motivo:
            git("reset", "-q", "--", relativo, callado=True)
            decir(f"    NO se sube {relativo}: {motivo}")
            quitados += 1
    decir(f"  Revisión de claves y tamaños: {quitados} archivos apartados.")


def principal():
    decir(f"Subir SmartSeeds a GitHub · {datetime.now():%Y-%m-%d %H:%M}")
    decir(f"Destino: {DESTINO}")
    if not GIT:
        decir("No encuentro git en esta computadora. Instala Git para Windows y vuelve a ejecutar.")
        terminar(1)
    if not (RAIZ / ".git").exists():
        decir("Esta carpeta no es un repositorio de git.")
        terminar(1)

    # El registro de este programa no se sube
    excluir = RAIZ / ".git" / "info" / "exclude"
    excluir.parent.mkdir(exist_ok=True)
    ya = excluir.read_text(encoding="utf-8", errors="ignore") if excluir.exists() else ""
    if REGISTRO.name not in ya:
        excluir.write_text(ya.rstrip("\n") + f"\n{REGISTRO.name}\n", encoding="utf-8")

    decir("\n1. Preparando los archivos")
    copiar_lanzadores()
    codigo, _ = git("add", "-A", callado=True)
    if codigo:
        decir("  git add falló.")
        terminar(1)
    agregar_crudos()
    revisar_lo_preparado()

    decir("\n2. Guardando el commit")
    _, pendiente = git("diff", "--cached", "--name-only", callado=True)
    cuantos = len([x for x in pendiente.splitlines() if x.strip()])
    if cuantos:
        # Si esta computadora no tiene firma de git configurada, se usa la del equipo solo para este repositorio
        if git("config", "user.name", callado=True)[1] == "":
            git("config", "user.name", "Condor Mission", callado=True)
        if git("config", "user.email", callado=True)[1] == "":
            git("config", "user.email", f"{CUENTA}@users.noreply.github.com", callado=True)
        mensaje = ("SmartSeeds completo: interfaz del agricultor, modelos 3D, Sierra y Costa, y respaldo de datos crudos\n\n"
                   "Incluye la interfaz nueva (app/smartseeds.py y app/interfaz/), los 26 modelos 3D de cultivos,\n"
                   "Three.js r170 en app/interfaz/vendor/, los datos procesados de las cuatro zonas y, como respaldo,\n"
                   "datos/crudos/ (normalmente fuera del repositorio).\n\n"
                   "Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>\n"
                   "Claude-Session: https://claude.ai/code/session_01U2bTnJJwifKNFaxUxbkgK4")
        codigo, _ = git("commit", "-q", "-m", mensaje)
        if codigo:
            decir("  No se pudo guardar el commit (mira el mensaje de arriba).")
            terminar(1)
        decir(f"  Commit guardado con {cuantos} archivos.")
    else:
        decir("  No había nada nuevo que guardar.")

    decir("\n3. Subiendo a GitHub")
    if git("remote", "get-url", REMOTO, callado=True)[0] == 0:
        git("remote", "set-url", REMOTO, DESTINO, callado=True)
    else:
        git("remote", "add", REMOTO, DESTINO, callado=True)
    codigo, _ = git("ls-remote", REMOTO, tope=90, callado=True)
    if codigo:
        # Si está la herramienta `gh`, se intenta crear el repositorio; si no, lo crea la persona en la página
        if shutil.which("gh"):
            decir("  El repositorio todavía no existe: intento crearlo con gh…")
            r = subprocess.run(["gh", "repo", "create", f"{CUENTA}/{REPOSITORIO}", "--public",
                                "--description", "SmartSeeds · Condor Mission · NASA Space Apps 2026"],
                               cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
            decir("    " + (r.stdout + r.stderr).strip()[:800])
            codigo, _ = git("ls-remote", REMOTO, tope=90, callado=True)
        if codigo:
            decir("  FALTA UN PASO TUYO: el repositorio todavía no existe en GitHub (o esta computadora no tiene sesión).")
            decir("    1) Abre https://github.com/new")
            decir(f"    2) Repository name: {REPOSITORIO}   ·   Public   ·   NO marques 'Add a README file'")
            decir("    3) Pulsa 'Create repository' y vuelve a ejecutar este archivo con el botón de play.")
            decir("  Tu trabajo ya quedó guardado en el commit de esta computadora; solo falta subirlo.")
            terminar(2)
    codigo, salida = git("push", REMOTO, "HEAD:refs/heads/main", tope=1800)
    if codigo:
        decir("  La subida falló. Si dice 'rejected', el repositorio de GitHub tiene algo que aquí no está:")
        decir("  créalo vacío (sin README) o avísale a Claude con este mensaje.")
        terminar(1)
    git("push", REMOTO, "--tags", tope=300, callado=True)

    decir("\n4. Comprobando")
    _, aqui = git("rev-parse", "HEAD", callado=True)
    _, alla = git("ls-remote", REMOTO, "refs/heads/main", tope=90, callado=True)
    if aqui and alla.startswith(aqui):
        decir(f"  LISTO. GitHub tiene lo mismo que esta computadora (commit {aqui[:10]}).")
        decir(f"  Página: https://github.com/{CUENTA}/{REPOSITORIO}")
        decir("\nPara trabajar desde otra computadora (en Miniforge Prompt):")
        decir(f"  git clone {DESTINO}")
        decir(f"  cd {REPOSITORIO}")
        decir("  conda env create -f environment.yml      (crea el entorno 'condor')")
        decir("  conda activate condor")
        decir("  streamlit run app/smartseeds.py")
        terminar(0)
    decir("  No pude confirmar que GitHub tenga el último commit. Revisa la página del repositorio.")
    terminar(1)


if __name__ == "__main__":
    principal()
