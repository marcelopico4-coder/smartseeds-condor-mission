"""
Suelo y lluvia con detalle local, para que el análisis cambie de un terreno a otro.

Con NASA POWER la lluvia es UN solo número para toda una zona (su celda mide ~50 km) y la app no
sabía nada del suelo: por eso casi todos los terrenos de una zona recibían el mismo resultado.
Este módulo agrega a la tabla por celda dos fuentes de uso libre (no son de la NASA: citarlas):

  SoilGrids 2.0 (ISRIC)   suelo a 250 m: pH, arcilla, arena y carbono orgánico de 0 a 30 cm.
                          Licencia CC BY 4.0.  https://soilgrids.org
  CHELSA V2.1             lluvia promedio 1981-2010 a ~1 km: la del año (variable bio12) y la de
                          cada mes (variable pr).  https://chelsa-climate.org

Uso (una vez por zona, después de `clima_relieve` y de `nisar ZONA capas`):
    python -m src.suelo_lluvia daule

Columnas que escribe en datos/procesados/celdas_ZONA.csv (las demás no se tocan):
    ph                 pH del suelo en agua, 0-30 cm
    arcilla, arena     porcentaje de arcilla y de arena, 0-30 cm
    materia_organica   porcentaje de materia orgánica, 0-30 cm (carbono orgánico x 1,724)
    lluvia             mm por año según CHELSA (es la que usa el puntaje)
    lluvia_power       mm por año según NASA POWER (el valor que había antes; se conserva)
Además guarda datos/procesados/lluvia_mensual_ZONA.npz: la lluvia de cada mes en cada celda. El
puntaje la usa en los cultivos de ciclo corto, que se comparan con la lluvia de los meses del
cultivo y no con la de todo el año.

No se baja ningún archivo grande: de SoilGrids se pide solo el recuadro de la zona (~12 KB por
capa) y de CHELSA se lee en remoto solo la ventana de la zona (el archivo mundial pesa 655 MB).
Las respuestas de SoilGrids quedan en datos/crudos/suelo/ZONA/ por si hay que revisarlas.

Límites que hay que declarar: SoilGrids es un mapa mundial hecho con un modelo, no un análisis
de suelo del terreno; CHELSA es un promedio de 30 años, no la lluvia de este año. Cada valor se
toma del cuadro más cercano de su mapa, sin suavizar, para no aparentar más detalle del que hay.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
import requests

from .clima_relieve import cargar_celdas, ruta_celdas
from .config import DATOS_CRUDOS, DATOS_PROCESADOS, ZONAS

URL_SOILGRIDS = "https://maps.isric.org/mapserv"
URL_CHELSA = ("https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/"
              "CHELSA_bio12_1981-2010_V.2.1.tif")
URL_CHELSA_MES = ("https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/pr/"
                  "CHELSA_pr_{mes:02d}_1981-2010_V.2.1.tif")

# capa de SoilGrids -> (columna de la tabla, número por el que se divide para tener la unidad final)
#   phh2o viene en pH x 10; clay y sand en g/kg (entre 10 = %); soc en dg/kg (entre 100 = %)
CAPAS_SUELO = {"phh2o": ("ph", 10), "clay": ("arcilla", 10), "sand": ("arena", 10), "soc": ("carbono", 100)}
PROFUNDIDADES = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15}   # capa -> grosor en cm (peso del promedio)
CARBONO_A_MATERIA_ORGANICA = 1.724                          # factor de Van Bemmelen
MARGEN_GRADOS = 0.01                                        # se pide un poco más que el recuadro

COLUMNAS_NUEVAS = ["ph", "arcilla", "arena", "materia_organica", "lluvia_power"]


# ---------------------------------------------------------------------------
# Textura del suelo (triángulo de texturas del USDA), con nombres en español
# ---------------------------------------------------------------------------
def clase_textura(arena, arcilla) -> str | None:
    """Nombre de la textura según el porcentaje de arena y de arcilla (el resto es limo)."""
    try:
        arena, arcilla = float(arena), float(arcilla)
    except (TypeError, ValueError):
        return None
    if np.isnan(arena) or np.isnan(arcilla):
        return None
    limo = 100 - arena - arcilla
    if limo + 1.5 * arcilla < 15:
        return "arenoso"
    if limo + 2 * arcilla < 30:
        return "arenoso franco"
    if (7 <= arcilla < 20 and arena > 52 and limo + 2 * arcilla >= 30) or (arcilla < 7 and limo < 50):
        return "franco arenoso"
    if 7 <= arcilla < 27 and 28 <= limo < 50 and arena <= 52:
        return "franco"
    if (limo >= 50 and 12 <= arcilla < 27) or (50 <= limo < 80 and arcilla < 12):
        return "franco limoso"
    if limo >= 80 and arcilla < 12:
        return "limoso"
    if 20 <= arcilla < 35 and limo < 28 and arena > 45:
        return "franco arcillo arenoso"
    if 27 <= arcilla < 40 and 20 < arena <= 45:
        return "franco arcilloso"
    if 27 <= arcilla < 40 and arena <= 20:
        return "franco arcillo limoso"
    if arcilla >= 35 and arena > 45:
        return "arcillo arenoso"
    if arcilla >= 40 and limo >= 40:
        return "arcillo limoso"
    if arcilla >= 40:
        return "arcilloso"
    return "franco"


def suelo_texto(celda: dict) -> str | None:
    """Frase corta del suelo de una celda, o None si no hay dato."""
    ph, textura = celda.get("ph"), clase_textura(celda.get("arena"), celda.get("arcilla"))
    partes = []
    if textura:
        partes.append(f"suelo {textura}")
    if ph is not None and not pd.isna(ph):
        partes.append(f"pH {float(ph):.1f}")
    # La materia orgánica queda en la tabla pero no se muestra: SoilGrids suele dar de más en el trópico.
    return ", ".join(partes) if partes else None


# ---------------------------------------------------------------------------
# Lectura de los dos mapas
# ---------------------------------------------------------------------------
def _valor_mas_cercano(geo, banda: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Valor del cuadro del mapa que contiene cada punto (sin interpolar).

    `geo` es la transformación del mapa: geo.c y geo.f son la esquina superior izquierda,
    geo.a el ancho de un cuadro y geo.e su alto (negativo, porque las filas bajan).
    """
    columnas = np.clip(((lon - geo.c) / geo.a).astype(int), 0, banda.shape[1] - 1)
    filas = np.clip(((lat - geo.f) / geo.e).astype(int), 0, banda.shape[0] - 1)
    return banda[filas, columnas]


def leer_suelo(clave_zona: str, lat: np.ndarray, lon: np.ndarray) -> dict[str, np.ndarray]:
    """Pide a SoilGrids el recuadro de la zona y devuelve ph, arcilla, arena y carbono por celda."""
    from rasterio.io import MemoryFile   # solo hace falta para preparar la tabla, no para la app

    lon_min, lat_min, lon_max, lat_max = ZONAS[clave_zona]["recuadro"]
    carpeta = DATOS_CRUDOS / "suelo" / clave_zona
    carpeta.mkdir(parents=True, exist_ok=True)
    resultado = {}
    for capa, (columna, divisor) in CAPAS_SUELO.items():
        suma = np.zeros(len(lat))
        peso_total = np.zeros(len(lat))
        for profundidad, grosor in PROFUNDIDADES.items():
            archivo = carpeta / f"{capa}_{profundidad}.tif"
            if not archivo.exists():
                consulta = [
                    ("map", f"/map/{capa}.map"), ("SERVICE", "WCS"), ("VERSION", "2.0.1"),
                    ("REQUEST", "GetCoverage"), ("COVERAGEID", f"{capa}_{profundidad}_mean"),
                    ("FORMAT", "image/tiff"),
                    ("SUBSET", f"long({lon_min - MARGEN_GRADOS},{lon_max + MARGEN_GRADOS})"),
                    ("SUBSET", f"lat({lat_min - MARGEN_GRADOS},{lat_max + MARGEN_GRADOS})"),
                    ("SUBSETTINGCRS", "http://www.opengis.net/def/crs/EPSG/0/4326"),
                    ("OUTPUTCRS", "http://www.opengis.net/def/crs/EPSG/0/4326"),
                ]
                r = requests.get(URL_SOILGRIDS, params=consulta, timeout=120)
                r.raise_for_status()
                if "tiff" not in r.headers.get("content-type", ""):
                    raise RuntimeError(f"SoilGrids no devolvió una imagen para {capa} {profundidad}: {r.text[:200]}")
                archivo.write_bytes(r.content)
            with MemoryFile(archivo.read_bytes()) as memoria, memoria.open() as src:
                valores = _valor_mas_cercano(src.transform, src.read(1).astype(float), lat, lon)
            valido = valores > 0          # 0 y negativos = sin dato (ciudades, agua)
            suma += np.where(valido, valores, 0) * grosor
            peso_total += np.where(valido, grosor, 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            resultado[columna] = np.where(peso_total > 0, suma / peso_total / divisor, np.nan)
        print(f"  SoilGrids {capa}: mediana {np.nanmedian(resultado[columna]):.2f}, "
              f"sin dato en {np.isnan(resultado[columna]).mean():.1%} de las celdas")
    return resultado


def leer_lluvia(clave_zona: str, lat: np.ndarray, lon: np.ndarray, url: str = URL_CHELSA,
                nombre: str = "lluvia del año") -> np.ndarray:
    """Lee en remoto la ventana de la zona de un mapa de lluvia de CHELSA (mm)."""
    from src.lectura_remota import leer_recuadro   # lee solo la ventana (ver ahí la forma "aparte")

    lon_min, lat_min, lon_max, lat_max = ZONAS[clave_zona]["recuadro"]
    leido = leer_recuadro(url, (lon_min - MARGEN_GRADOS, lat_min - MARGEN_GRADOS,
                                lon_max + MARGEN_GRADOS, lat_max + MARGEN_GRADOS))
    banda = leido["datos"].astype(float) * leido["escala"] + leido["desfase"]
    origen = leido["transformacion"]
    lluvia = _valor_mas_cercano(origen, banda, lat, lon)
    print(f"  CHELSA {nombre}: de {lluvia.min():.0f} a {lluvia.max():.0f} mm (mediana {np.median(lluvia):.0f})")
    return lluvia


def ruta_lluvia_mensual(clave_zona: str):
    return DATOS_PROCESADOS / f"lluvia_mensual_{clave_zona}.npz"


def cargar_lluvia_mensual(clave_zona: str) -> dict | None:
    """{"celda": números de celda, "lluvia": matriz (celdas x 12 meses) en mm}, o None si no existe."""
    ruta = ruta_lluvia_mensual(clave_zona)
    if not ruta.exists():
        return None
    with np.load(ruta) as datos:
        return {"celda": datos["celda"], "lluvia": datos["lluvia"].astype(float)}


def lluvia_mensual_de(mensual: dict | None, celdas, pesos=None) -> list[float] | None:
    """Lluvia de cada mes (12 números) de una celda o del promedio de varias (con sus pesos)."""
    if mensual is None:
        return None
    celdas = np.atleast_1d(np.asarray(celdas))
    posicion = {int(c): i for i, c in enumerate(mensual["celda"])}
    indices = [posicion[int(c)] for c in celdas if int(c) in posicion]
    if not indices:
        return None
    if pesos is None or len(indices) != len(celdas):
        pesos = np.ones(len(indices))
    promedio = np.average(mensual["lluvia"][indices], axis=0, weights=np.asarray(pesos, dtype=float))
    return [round(float(v), 1) for v in promedio]


def con_lluvia_mensual(celdas: pd.DataFrame, mensual: dict | None) -> pd.DataFrame:
    """Copia de una tabla de celdas con la columna `lluvia_mensual` (lista de 12) en cada fila."""
    if mensual is None or celdas is None or celdas.empty:
        return celdas
    celdas = celdas.copy()
    celdas["lluvia_mensual"] = [lluvia_mensual_de(mensual, c) for c in celdas["celda"]]
    return celdas


def agregar_a_tabla(clave_zona: str) -> pd.DataFrame:
    """Agrega suelo y lluvia local a la tabla por celda de la zona y la guarda."""
    tabla = cargar_celdas(clave_zona)
    if tabla is None:
        raise SystemExit(f"Falta la tabla de {clave_zona}: ejecuta primero python -m src.clima_relieve {clave_zona}")
    lat, lon = tabla["lat"].to_numpy(), tabla["lon"].to_numpy()

    suelo = leer_suelo(clave_zona, lat, lon)
    tabla["ph"] = np.round(suelo["ph"], 1)
    tabla["arcilla"] = np.round(suelo["arcilla"], 0)
    tabla["arena"] = np.round(suelo["arena"], 0)
    tabla["materia_organica"] = np.round(suelo["carbono"] * CARBONO_A_MATERIA_ORGANICA, 1)

    if "lluvia_power" not in tabla:            # la primera vez se guarda el valor de NASA POWER
        tabla["lluvia_power"] = tabla["lluvia"]
    tabla["lluvia"] = np.round(leer_lluvia(clave_zona, lat, lon), 0)

    tabla.to_csv(ruta_celdas(clave_zona), index=False)
    print(f"Tabla actualizada: {ruta_celdas(clave_zona)}")

    meses = np.column_stack([leer_lluvia(clave_zona, lat, lon, URL_CHELSA_MES.format(mes=m), f"mes {m:02d}")
                             for m in range(1, 13)])
    np.savez_compressed(ruta_lluvia_mensual(clave_zona), celda=tabla["celda"].to_numpy(),
                        lluvia=np.round(meses).astype(np.int16))
    print(f"Lluvia mensual guardada: {ruta_lluvia_mensual(clave_zona)} "
          f"(suma de los 12 meses, mediana {np.median(meses.sum(axis=1)):.0f} mm; "
          f"mapa del año, mediana {tabla['lluvia'].median():.0f} mm)")
    return tabla


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ZONAS:
        raise SystemExit(f"Uso: python -m src.suelo_lluvia ZONA   (zonas: {', '.join(ZONAS)})")
    agregar_a_tabla(sys.argv[1])
