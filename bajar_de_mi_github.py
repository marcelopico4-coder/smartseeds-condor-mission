# -*- coding: utf-8 -*-
"""
Baja a esta computadora lo último que hay en GitHub (repositorio personal).

Se lanza con el botón ▷. Se puede repetir las veces que haga falta.
No borra nada: si aquí hay cambios sin guardar que chocan con lo de GitHub,
se detiene y lo dice, sin tocar los archivos.

Deja el resultado en bajar_de_mi_github.txt (ese archivo no se sube).
"""
import datetime
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
DESTINO = "https://github.com/marcelopico4-coder/smartseeds-condor-mission.git"
REMOTO = "personal"
RAMA_REMOTA = "main"
REGISTRO = os.path.join(RAIZ, "bajar_de_mi_github.txt")

lineas = []


def decir(texto=""):
    """Muestra en pantalla y guarda en el registro."""
    print(texto)
    lineas.append(texto)


def git(*argumentos):
    """Ejecuta git en la raíz del repositorio. Devuelve (código, salida)."""
    entorno = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    hecho = subprocess.run(
        ["git", *argumentos], cwd=RAIZ, env=entorno,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return hecho.returncode, (hecho.stdout + hecho.stderr).strip()


def guardar_registro():
    with open(REGISTRO, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas) + "\n")


def no_subir_el_registro():
    """Anota el registro en la lista de archivos que git no mira."""
    ruta = os.path.join(RAIZ, ".git", "info", "exclude")
    try:
        actual = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else ""
        if "bajar_de_mi_github.txt" not in actual:
            with open(ruta, "a", encoding="utf-8") as archivo:
                archivo.write("\nbajar_de_mi_github.txt\n")
    except OSError:
        pass


def principal():
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    decir(f"Bajar SmartSeeds de GitHub · {ahora}")
    decir(f"Origen: {DESTINO}")
    decir()
    no_subir_el_registro()

    # El remoto 'personal' ya existe en esta computadora; si no, se crea.
    codigo, salida = git("remote", "get-url", REMOTO)
    if codigo != 0:
        git("remote", "add", REMOTO, DESTINO)

    decir("1. Consultando GitHub")
    codigo, salida = git("fetch", REMOTO, RAMA_REMOTA)
    if codigo != 0:
        decir("  NO SE PUDO consultar GitHub. Revisa el internet.")
        decir("  " + salida.replace("\n", "\n  "))
        return 1

    _, aqui = git("rev-parse", "HEAD")
    _, alla = git("rev-parse", f"{REMOTO}/{RAMA_REMOTA}")
    decir(f"  Esta computadora: {aqui[:10]}")
    decir(f"  GitHub:           {alla[:10]}")

    if aqui == alla:
        decir()
        decir("LISTO. Esta computadora ya tiene lo último. No había nada que bajar.")
        return 0

    _, nuevos = git("log", "--format=  %h %ad  %s", "--date=format:%d-%m %H:%M",
                    f"HEAD..{REMOTO}/{RAMA_REMOTA}")
    decir()
    decir("2. Lo nuevo que hay en GitHub")
    decir(nuevos or "  (nada nuevo)")
    _, archivos = git("diff", "--stat", f"HEAD...{REMOTO}/{RAMA_REMOTA}")
    if archivos:
        decir("  " + archivos.replace("\n", "\n  "))

    decir()
    decir("3. Trayendo los cambios")
    # Primero el camino simple: esta computadora no tiene commits propios nuevos.
    codigo, salida = git("merge", "--ff-only", f"{REMOTO}/{RAMA_REMOTA}")
    if codigo != 0:
        # Hay trabajo propio aquí: se intenta juntar las dos partes.
        codigo, salida = git("merge", "--no-edit", f"{REMOTO}/{RAMA_REMOTA}")
        if codigo != 0:
            git("merge", "--abort")
            decir("  NO SE BAJÓ NADA. Los cambios de GitHub chocan con cambios de esta")
            decir("  computadora. No se tocó ningún archivo. Mensaje de git:")
            decir("  " + salida.replace("\n", "\n  "))
            return 1
    decir("  " + salida.replace("\n", "\n  "))

    _, ahora_aqui = git("rev-parse", "HEAD")
    decir()
    if ahora_aqui == alla:
        decir(f"LISTO. Esta computadora tiene lo mismo que GitHub (commit {alla[:10]}).")
    else:
        decir(f"LISTO. Se unió lo de GitHub con lo de esta computadora (commit {ahora_aqui[:10]}).")
        decir("Esta computadora tiene además cambios propios que GitHub todavía no tiene.")
    decir("Recarga el navegador para ver la app con los cambios.")
    return 0


if __name__ == "__main__":
    try:
        resultado = principal()
    except Exception as error:  # que el registro quede aunque algo falle
        decir(f"ERROR inesperado: {error}")
        resultado = 1
    guardar_registro()
    sys.exit(resultado)
