"""
Paso 1 de la subida a GitHub (pedido del usuario, 14 nov 23:32). NO sube nada todavía.

1) Crea la rama `interfaz-agricultor` en la carpeta unida (smartseeds-costa) y guarda ahí, en UN commit,
   todo el trabajo de hoy (firma: Condor Mission, con el correo oculto de GitHub).
2) Mira qué archivos cambiaron a la vez aquí y en GitHub (5 commits nuevos del equipo) y deja en
   C:\\condor\\_union\\ la versión de partida (.base) y la de GitHub (.remoto) de cada uno, para unirlos a mano
   sin perder nada. La carpeta de trabajo no se toca en este paso.
3) Revisa si ya existe la copia (fork) en la cuenta marcelopico4-coder.
Todo queda anotado en preparar_subida.txt, al lado de este archivo.
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI / "smartseeds-costa"
UNION = AQUI / "_union"
UNION.mkdir(exist_ok=True)
RAMA = "interfaz-agricultor"
COPIA = "https://github.com/marcelopico4-coder/smartseeds-costa.git"
NOTAS = open(AQUI / "preparar_subida.txt", "w", encoding="utf-8")
FIRMA = {"GIT_AUTHOR_NAME": "Condor Mission", "GIT_COMMITTER_NAME": "Condor Mission",
         "GIT_AUTHOR_EMAIL": "marcelopico4-coder@users.noreply.github.com",
         "GIT_COMMITTER_EMAIL": "marcelopico4-coder@users.noreply.github.com"}
ENTORNO = {**os.environ, **FIRMA, "PYTHONIOENCODING": "utf-8", "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}

MENSAJE = """Interfaz nueva para el agricultor, Sierra procesada y catálogos del equipo

- app/smartseeds.py, app/analisis.py y app/interfaz/: pantalla nueva para el agricultor (portada con el
  globo, marcar el terreno, preguntas opcionales, cultivos en orden con foto, ficha, vista 3D).
- app/app.py: vista técnica con la respuesta arriba y el mapa que se acerca al terreno.
- Zonas de la Sierra (Cotopaxi y Tungurahua) procesadas: celdas, radar NISAR, humedad, lluvia mensual y
  referencia WorldCover. Modelo de cobertura reentrenado con las cuatro zonas.
- src/lectura_remota.py: lectura de recuadros sin rasterio.windows.from_bounds (cerraba Python en Windows).
- Catálogo de cultivos y de mercado del equipo, heladas, perfiles productivos y pruebas.

Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Pg3QeeiaHoi9YWNm54TH1E
"""


def decir(texto=""):
    print(texto, flush=True)
    NOTAS.write(texto + "\n")
    NOTAS.flush()


def git(*orden, espera=120, crudo=False):
    try:
        p = subprocess.run(["git", *orden], cwd=REPO, env=ENTORNO, capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=espera)
    except subprocess.TimeoutExpired:
        return -1, b"" if crudo else f"(sin respuesta en {espera} s)"
    if crudo:
        return p.returncode, p.stdout
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", errors="replace").strip()


decir(f"===== preparar_subida · {datetime.now():%Y-%m-%d %H:%M:%S}")
decir(git("--version")[1] + " · autocrlf: " + (git("config", "core.autocrlf")[1] or "(sin definir)"))
rama = git("branch", "--show-current")[1]
decir(f"rama al empezar: {rama}")
if rama == "main":
    codigo, salida = git("switch", "-c", RAMA)
    decir(f"--- crear rama {RAMA} [código {codigo}]\n{salida}")
elif rama != RAMA:
    decir("La rama no es main ni la esperada: no sigo.")
    raise SystemExit(1)

if git("status", "--porcelain")[1]:
    codigo, salida = git("add", "-A")
    decir(f"--- git add -A [código {codigo}]\n{salida[-1500:]}")
    (UNION / "mensaje.txt").write_text(MENSAJE, encoding="utf-8")
    codigo, salida = git("commit", "-F", str(UNION / "mensaje.txt"))
    decir(f"--- commit [código {codigo}]\n{salida[-2500:]}")
else:
    decir("--- no había nada nuevo que guardar")
decir("--- commits de la rama que no están en GitHub:\n" + git("log", "--format=%h %an <%ae> %s", "origin/main..HEAD")[1])
decir("--- git status --short tras el commit:\n" + (git("status", "--short")[1] or "(limpio)"))

base = git("merge-base", "HEAD", "origin/main")[1]
decir(f"--- punto de partida común: {base}")
mios = set(git("diff", "--name-only", base, "HEAD")[1].splitlines())
suyos = set(git("diff", "--name-only", base, "origin/main")[1].splitlines())
ambos = sorted(mios & suyos)
decir(f"--- archivos cambiados en los dos lados: {ambos}")
for nombre in ambos:
    plano = nombre.replace("/", "__")
    for sufijo, version in ((".base", base), (".remoto", "origin/main")):
        codigo, contenido = git("show", f"{version}:{nombre}", crudo=True)
        (UNION / (plano + sufijo)).write_bytes(contenido if codigo == 0 else b"")
    decir(f"\n######## lo que cambió GitHub en {nombre}\n" + git("diff", base, "origin/main", "--", nombre)[1][:12000])

codigo, salida = git("merge-tree", "--write-tree", "--name-only", "HEAD", "origin/main")
decir(f"\n--- ensayo de unión (no toca la carpeta) [código {codigo}; 0 = sin choques, 1 = hay choques]\n{salida[:3000]}")

codigo, salida = git("ls-remote", "--heads", COPIA, espera=60)
decir(f"\n--- ¿existe la copia en marcelopico4-coder? [código {codigo}]\n{salida[:1500]}")
decir(f"===== fin · {datetime.now():%H:%M:%S}")
