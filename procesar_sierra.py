"""
SmartSeeds · procesar las dos zonas de la Sierra (cotopaxi y tungurahua) de punta a punta.
En VS Code: abre este archivo y pulsa "Run Python File". Se puede volver a lanzar: el radar
retoma las fechas que falten. La salida queda en datos/crudos/registros/procesar_sierra.txt

Orden por zona (el de CLAUDE.md): clima_relieve -> heladas -> nisar procesar / humedad / capas
-> suelo_lluvia -> vecindad -> mapa de referencia WorldCover. Al final, tipo de terreno.
Si un paso falla en una zona se salta el resto de ESA zona y se sigue con la otra.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
REGISTRO = RAIZ / "datos" / "crudos" / "registros" / "procesar_sierra.txt"
REGISTRO.parent.mkdir(parents=True, exist_ok=True)
ENTORNO = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
# VS Code lanza python.exe SIN activar el entorno conda. Para que las librerías de mapas (GDAL, que usa
# rasterio) encuentren sus archivos, se ponen las carpetas del entorno en el PATH, como hace "conda activate".
_env = Path(sys.executable).parent
if (_env / "Library" / "bin").exists():
    ENTORNO["PATH"] = os.pathsep.join(str(r) for r in (_env, _env / "Library" / "mingw-w64" / "bin",
                                                       _env / "Library" / "usr" / "bin", _env / "Library" / "bin",
                                                       _env / "Scripts")) + os.pathsep + ENTORNO.get("PATH", "")
    ENTORNO.setdefault("GDAL_DATA", str(_env / "Library" / "share" / "gdal"))
    ENTORNO.setdefault("PROJ_DATA", str(_env / "Library" / "share" / "proj"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
registro = open(REGISTRO, "a", encoding="utf-8")


def decir(texto):
    print(texto, flush=True)
    registro.write(texto + "\n")
    registro.flush()


PYTHON = [sys.executable]


def en_archivo(codigo, nombre):
    """Guarda un trozo de código en un archivo dentro de la carpeta de registros y devuelve su ruta."""
    ruta = REGISTRO.parent / nombre
    ruta.write_text(codigo, encoding="utf-8")
    return str(ruta)


def correr(*args):
    if args[0] == "-c":
        args = (en_archivo(args[1], f"_paso_{abs(hash(args[1])) % 10000}.py"),)
        ENTORNO["PYTHONPATH"] = str(RAIZ)
    decir(f"\n>>> [{datetime.now():%H:%M:%S}] python {' '.join(args)}")
    p = subprocess.Popen([*PYTHON, *args], cwd=RAIZ, env=ENTORNO, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace")
    for linea in p.stdout:
        decir(linea.rstrip("\n"))
    if p.wait() != 0:
        decir(f"!!! terminó con error (código {p.returncode})")
    return p.returncode == 0


def carpeta_mb(ruta):
    return sum(f.stat().st_size for f in Path(ruta).rglob("*") if f.is_file()) / 1e6 if Path(ruta).exists() else 0


decir(f"\n########## procesar_sierra · {datetime.now():%Y-%m-%d %H:%M:%S} · {sys.executable}")

# --- Lectura de mapas por internet (CHELSA, WorldCover) en esta computadora ---------------------------------
# Dos tropiezos del 14 nov, ya resueltos en src/lectura_remota.py:
#   1) `rasterio.windows.from_bounds` tumbaba el proceso (código 3228369023): la ventana se calcula ahora a mano.
#   2) el servidor de CHELSA a veces deja la conexión colgada varios minutos: con la forma "aparte" cada lectura
#      va en un proceso nuevo con tiempo máximo y se reintenta. El resultado es el mismo.
# Antes de procesar se prueba con un recuadro mínimo, para fallar pronto y con un mensaje claro si no hay internet.
ENTORNO["SMARTSEEDS_LECTURA"] = "aparte"
ENTORNO["PYTHONPATH"] = str(RAIZ)      # para que los archivos sueltos de prueba encuentren `src`
PRUEBA = ("from src.lectura_remota import forma_de_leer, leer_recuadro\n"
          "from src.suelo_lluvia import URL_CHELSA\n"
          "r = leer_recuadro(URL_CHELSA, (-78.62, -1.32, -78.58, -1.28))\n"
          "print('forma:', forma_de_leer(), '· recuadro de', r['datos'].shape, '· lluvia del año en Ambato:',\n"
          "      round(float(r['datos'].mean() * r['escala'] + r['desfase'])), 'mm')\n")
try:
    r = subprocess.run([sys.executable, en_archivo(PRUEBA, "_prueba_lectura.py")], cwd=RAIZ, env=ENTORNO,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900,
                       stdin=subprocess.DEVNULL)
    decir(f"Prueba de lectura remota: código {r.returncode} · "
          f"{' | '.join((r.stdout + r.stderr).strip().splitlines()[-6:])}")
    lectura_bien = r.returncode == 0
except Exception as error:  # noqa: BLE001
    decir(f"Prueba de lectura remota: {error!r}")
    lectura_bien = False
if not lectura_bien:
    decir("No se pudo leer un mapa por internet: no se procesa nada.")
    decir(f"########## FIN · {datetime.now():%H:%M:%S}")
    raise SystemExit(1)
PASOS = [["-m", "src.clima_relieve", "{z}"], ["-m", "src.heladas", "{z}"],
         ["-m", "src.nisar", "{z}", "procesar"], ["-m", "src.nisar", "{z}", "humedad"],
         ["-m", "src.nisar", "{z}", "capas"], ["-m", "src.suelo_lluvia", "{z}"],
         ["-m", "src.vecindad", "{z}"], ["recolectar_referencia.py", "descargar", "worldcover", "{z}"]]
resultado = {}
for zona in ("tungurahua", "cotopaxi"):
    resultado[zona] = "completa"
    for paso in PASOS:
        if not correr(*[a.format(z=zona) for a in paso]):
            resultado[zona] = "FALLÓ en: " + " ".join(a.format(z=zona) for a in paso)
            break

# tipo de terreno: se guarda cómo estaba la Costa para decir cuánto cambia al reentrenar
codigo_antes = ("import pandas as pd, pathlib\n"
                "for z in ('santo_domingo','daule'):\n"
                "    pd.read_csv(f'datos/procesados/celdas_{z}.csv', usecols=['celda','cobertura'])"
                ".to_csv(f'datos/crudos/registros/cobertura_antes_{z}.csv', index=False)\n")
codigo_despues = ("import pandas as pd\n"
                  "for z in ('santo_domingo','daule'):\n"
                  "    a = pd.read_csv(f'datos/crudos/registros/cobertura_antes_{z}.csv')['cobertura'].fillna('sin radar').astype(str)\n"
                  "    d = pd.read_csv(f'datos/procesados/celdas_{z}.csv')['cobertura'].fillna('sin radar').astype(str)\n"
                  "    print(z, '| celdas cuyo tipo de terreno cambió al reentrenar:', f'{(a != d).mean():.1%}')\n"
                  "for z in ('tungurahua','cotopaxi'):\n"
                  "    t = pd.read_csv(f'datos/procesados/celdas_{z}.csv')\n"
                  "    print(z, len(t), 'celdas | columnas:', list(t.columns))\n"
                  "    print(t.describe().loc[['min','50%','max']].round(2).T.to_string())\n"
                  "    print((t['cobertura'].value_counts(normalize=True, dropna=False) * 100).round(1).to_dict())\n")
if any(v == "completa" for v in resultado.values()):
    correr("-c", codigo_antes)
    correr("-m", "src.cobertura", "entrenar")
    correr("-c", codigo_despues)
correr("tests/prueba_rapida.py")
decir(f"\nRESULTADO POR ZONA: {resultado}")
decir(f"Tamaño en disco: datos/crudos {carpeta_mb(RAIZ / 'datos' / 'crudos'):.0f} MB · "
      f"datos/procesados {carpeta_mb(RAIZ / 'datos' / 'procesados'):.0f} MB")
decir(f"########## FIN · {datetime.now():%H:%M:%S}")
