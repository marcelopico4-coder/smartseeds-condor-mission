"""
Datos de referencia para comprobar y entrenar el analizador de terreno (tipo de terreno).

El modelo actual (src/cobertura.py) agrupa las celdas por cómo se ve el radar, pero nadie le
dice qué hay de verdad en cada celda. Este script trae mapas de cobertura ya hechos, para
tener con qué comparar y con qué entrenar. Hay dos fuentes:

  mapbiomas   MapBiomas Ecuador, Colección 3.0 (Fundación EcoCiencia y red MapBiomas).
              Mapas anuales 1985-2024 hechos para el Ecuador con imágenes Landsat.
              Separa lo AGROPECUARIO (cultivos y pastos) del bosque natural, de los herbazales
              y páramos, de lo urbano y del agua. Se deja fuera la clase beta de banano.
              Se leen 2022, 2023 y 2024: la referencia es 2024 y se marca como "estable"
              la celda que no cambió de clase en esos tres años.
              https://ecuador.mapbiomas.org/en/mapas-de-cobertura-y-uso/

  worldcover  ESA WorldCover 2021 v200, 10 m, 11 clases, exactitud global 76,7 %.
              Agencia Espacial Europea (agencia socia de Space Apps). Licencia CC BY 4.0.
              Zanaga, D. et al. (2022). ESA WorldCover 10 m 2021 v200.
              https://doi.org/10.5281/zenodo.7254221
              © ESA WorldCover project / Contains modified Copernicus Sentinel data (2021),
              processed by ESA WorldCover consortium.

Citar en las referencias del proyecto la fuente que se use.

No se descarga el archivo completo: se lee por internet solo la ventana de cada zona. No pide
usuario ni clave. Si la lectura por internet falla, se puede bajar el archivo con el navegador
y guardarlo en datos/crudos/referencia/ con su mismo nombre: el script lo usa desde ahí.

Uso (desde la raíz del repositorio, con el entorno `condor` activado):

    python recolectar_referencia.py descargar mapbiomas   # -> datos/procesados/referencia_mapbiomas_ZONA.csv
    python recolectar_referencia.py comparar mapbiomas    # modelo actual contra la referencia
    python recolectar_referencia.py probar mapbiomas      # prueba un modelo entrenado CON la referencia

(lo mismo con `worldcover`). Ninguno de los comandos cambia los archivos que ya existen:
`descargar` crea un archivo nuevo por zona y los otros dos solo muestran resultados.

Qué es y qué NO es la referencia:
  - Son mapas hechos con satélites, no visitas al campo, y tienen sus propios errores.
  - El último año de MapBiomas es 2024; el radar es de 2026. Por eso se usan para entrenar
    solo las celdas "estables" y donde una clase ocupa la mayor parte de la celda.
  - "Agropecuario" junta cultivos y pastos. Ninguna de las dos fuentes dice qué cultivo es
    (MapBiomas solo separa el banano, y lo marca como versión beta).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.config import DATOS_CRUDOS, DATOS_PROCESADOS, ZONAS, forma_rejilla  # noqa: E402

CARPETA_LOCAL = DATOS_CRUDOS / "referencia"     # archivos bajados a mano (opcional)

# Cada fuente: de dónde se lee y cómo se agrupan sus códigos de píxel en clases con nombre.
FUENTES = {
    "mapbiomas": {
        "url": ("https://storage.googleapis.com/mapbiomas-public/initiatives/ecuador/"
                "collection_3/coverage/ecuador_coverage_{anio}.tif"),
        "anios": [2022, 2023, 2024],            # el último es la referencia; los tres dan la estabilidad
        "clases": {
            "agropecuario": [14, 21],            # mosaico de agricultura y/o pastos; excluye banano beta (74)
            "plantacion_forestal": [9],          # silvicultura
            "bosque": [1, 3, 4, 5, 6],           # bosque, bosque abierto, manglar, bosque inundable
            "natural_abierto": [10, 11, 12, 13, 29, 81, 82],   # herbazales, páramo, roca
            "urbano": [24],
            "sin_vegetacion": [22, 23, 25, 30, 68],            # minería, playas, otras áreas
            "agua": [26, 31, 33],                # río, lago u océano; acuicultura
            "glaciar": [34],
        },
        # (nombre, clases del modelo del radar, columnas de la referencia que deberían coincidir)
        "aciertos": [("construcciones", ["construcciones"], ["urbano"]),
                     ("agua o inundable", ["agua", "inundable"], ["agua"]),
                     ("árboles o vegetación densa", ["vegetacion_densa"], ["bosque", "plantacion_forestal"])],
        "pregunta": ("¿es terreno agropecuario?", ["agropecuario"]),
    },
    "worldcover": {
        "url": ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
                "ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"),
        "anios": [2021],
        "clases": {"arboles": [10], "arbustos": [20], "pasto": [30], "cultivo": [40],
                   "construido": [50], "suelo_desnudo": [60], "nieve": [70], "agua": [80],
                   "humedal": [90], "manglar": [95], "musgo": [100]},
        "aciertos": [("construcciones", ["construcciones"], ["construido"]),
                     ("agua o inundable", ["agua", "inundable"], ["agua", "humedal"]),
                     ("árboles o vegetación densa", ["vegetacion_densa"], ["arboles"])],
        "pregunta": ("¿es cultivo de ciclo corto?", ["cultivo"]),
    },
}
GRADOS_TILE = 3            # WorldCover: cada archivo cubre 3 x 3 grados
PUREZA_MINIMA = 0.6        # para entrenar: celdas donde una clase ocupa al menos el 60 %
LADO_BLOQUE = 30           # bloques de 30 x 30 celdas (~7,5 km) para separar entrenamiento y prueba


def ruta_referencia(clave_zona: str, fuente: str) -> Path:
    return DATOS_PROCESADOS / f"referencia_{fuente}_{clave_zona}.csv"


# ---------------------------------------------------------------------------
# 1. Recolectar: leer la ventana de la zona y resumirla por celda
# ---------------------------------------------------------------------------
def tiles_del_recuadro(recuadro) -> list[tuple[str, tuple]]:
    """Archivos de WorldCover que tocan el recuadro: [(código, recuadro del archivo)].

    El código es la esquina inferior izquierda del archivo, por ejemplo S03W081
    (de 3° sur a 0° y de 81° a 78° oeste).
    """
    lon_min, lat_min, lon_max, lat_max = recuadro
    tiles = []
    lat0 = math.floor(lat_min / GRADOS_TILE) * GRADOS_TILE
    while lat0 < lat_max:
        lon0 = math.floor(lon_min / GRADOS_TILE) * GRADOS_TILE
        while lon0 < lon_max:
            codigo = (f"{'N' if lat0 >= 0 else 'S'}{abs(lat0):02d}"
                      f"{'E' if lon0 >= 0 else 'W'}{abs(lon0):03d}")
            tiles.append((codigo, (lon0, lat0, lon0 + GRADOS_TILE, lat0 + GRADOS_TILE)))
            lon0 += GRADOS_TILE
        lat0 += GRADOS_TILE
    return tiles


def archivos_de(fuente: str, anio: int, recuadro) -> list[tuple[str, tuple]]:
    """[(dirección del archivo, parte del recuadro que cubre)] para una fuente y un año."""
    url = FUENTES[fuente]["url"]
    if "{tile}" not in url:                       # un solo archivo para todo el país
        return [(url.format(anio=anio), tuple(recuadro))]
    archivos = []
    for codigo, limites in tiles_del_recuadro(recuadro):
        parte = (max(recuadro[0], limites[0]), max(recuadro[1], limites[1]),
                 min(recuadro[2], limites[2]), min(recuadro[3], limites[3]))
        archivos.append((url.format(tile=codigo), parte))
    return archivos


def leer_ventana(url: str, recuadro):
    """Lee solo la parte del archivo que cubre el recuadro (por internet o de una copia local).

    Devuelve (matriz de códigos, longitud del borde oeste, latitud del borde norte, ancho
    y alto del píxel en grados). La fila 0 de la matriz es el norte.
    """
    from src.lectura_remota import leer_recuadro   # lee solo la ventana (ver ahí la forma "aparte")

    local = CARPETA_LOCAL / url.rsplit("/", 1)[-1]
    origen = str(local) if local.exists() else url
    # Unión del 14 nov: GitHub ponía aquí GDAL_HTTP_TIMEOUT=30 y un solo reintento. La lectura ahora pasa por
    # `leer_recuadro`, que trae sus propios límites (ver OPCIONES_GDAL y ESPERA_APARTE en src/lectura_remota.py).
    try:
        leido = leer_recuadro(origen, recuadro, relleno=0)
        if not leido["en_grados"]:
            raise SystemExit(f"{origen} no está en grados (latitud y longitud). "
                             "Avisa antes de seguir: hay que convertirlo.")
        datos, t = leido["datos"], leido["transformacion"]
    except OSError as error:      # incluye el error de lectura de rasterio (RasterioIOError)
        raise SystemExit(
            f"No se pudo leer {origen}\n   {error}\n"
            f"Baja el archivo con el navegador desde\n   {url}\n"
            f"guárdalo en {CARPETA_LOCAL} con el mismo nombre y vuelve a ejecutar.") from error
    return datos, t.c, t.f, t.a, -t.e


def a_grupos(datos: np.ndarray, clases: dict[str, list[int]]) -> np.ndarray:
    """Cambia cada código de píxel por el número de su clase (1, 2, 3…); 0 = sin dato u otro."""
    tabla = np.zeros(int(max(datos.max(), max(max(c) for c in clases.values()))) + 1, dtype="uint8")
    for numero, codigos in enumerate(clases.values(), start=1):
        tabla[codigos] = numero
    return tabla[datos]


def contar_por_celda(grupos, lon_oeste, lat_norte, ancho, alto, recuadro, n_clases) -> np.ndarray:
    """Cuántos píxeles de cada clase caen en cada celda de la rejilla de la zona.

    Devuelve una matriz [clase, fila, columna]. Los píxeles sin dato (0) o fuera del
    recuadro no se cuentan.
    """
    filas, columnas, paso = forma_rejilla(recuadro)
    lon_min, _, _, lat_max = recuadro
    lats = lat_norte - (np.arange(grupos.shape[0]) + 0.5) * alto
    lons = lon_oeste + (np.arange(grupos.shape[1]) + 0.5) * ancho
    i = np.floor((lat_max - lats) / paso).astype("int64")
    j = np.floor((lons - lon_min) / paso).astype("int64")
    dentro = ((i >= 0) & (i < filas))[:, None] & ((j >= 0) & (j < columnas))[None, :]
    celda = np.clip(i, 0, filas - 1)[:, None] * columnas + np.clip(j, 0, columnas - 1)[None, :]
    conteos = np.zeros((n_clases, filas, columnas), dtype="int64")
    for numero in range(1, n_clases + 1):
        elegido = dentro & (grupos == numero)
        conteos[numero - 1] = np.bincount(celda[elegido], minlength=filas * columnas).reshape(
            filas, columnas)
    return conteos


def _clase_mayor(conteos: np.ndarray, nombres: list[str]):
    """(clase principal por celda, parte de la celda que ocupa); vacío donde no hay dato."""
    total = conteos.sum(axis=0)
    sin_dato = (total == 0).ravel()
    partes = (conteos / np.where(total > 0, total, 1)).reshape(len(nombres), -1)
    mayor = np.where(sin_dato, None, np.asarray(nombres, dtype=object)[partes.argmax(axis=0)])
    pureza = np.where(sin_dato, np.nan, partes.max(axis=0))
    return mayor, pureza, partes, sin_dato


def tabla_referencia(conteos_por_anio: dict[int, np.ndarray], nombres: list[str]) -> pd.DataFrame:
    """Una fila por celda, con el último año como referencia.

    ref_NOMBRE   parte de la celda con esa clase (0 a 1)
    ref_clase    clase que más ocupa la celda
    ref_pureza   parte de la celda que ocupa esa clase
    ref_estable  True si la clase principal fue la misma en todos los años leídos
    """
    anios = sorted(conteos_por_anio)
    mayor, pureza, partes, sin_dato = _clase_mayor(conteos_por_anio[anios[-1]], nombres)
    tabla = pd.DataFrame({"celda": np.arange(mayor.size)})
    for numero, nombre in enumerate(nombres):
        tabla[f"ref_{nombre}"] = np.where(sin_dato, np.nan, partes[numero]).round(3)
    tabla["ref_clase"] = mayor
    tabla["ref_pureza"] = np.round(pureza, 3)
    estable = ~sin_dato
    for anio in anios[:-1]:
        estable &= _clase_mayor(conteos_por_anio[anio], nombres)[0] == mayor
    tabla["ref_estable"] = estable
    return tabla


def descargar(fuente: str, zonas=None) -> None:
    clases = FUENTES[fuente]["clases"]
    nombres = list(clases)
    for clave in (zonas or ZONAS):
        recuadro = ZONAS[clave]["recuadro"]
        filas, columnas, _ = forma_rejilla(recuadro)
        por_anio = {}
        for anio in FUENTES[fuente]["anios"]:
            conteos = np.zeros((len(nombres), filas, columnas), dtype="int64")
            for url, parte in archivos_de(fuente, anio, recuadro):
                datos, lon_oeste, lat_norte, ancho, alto = leer_ventana(url, parte)
                print(f"  {clave} {anio}: {url.rsplit('/', 1)[-1]}, ventana de "
                      f"{datos.shape[0]} x {datos.shape[1]} píxeles", flush=True)
                conteos += contar_por_celda(a_grupos(datos, clases), lon_oeste, lat_norte,
                                            ancho, alto, recuadro, len(nombres))
            por_anio[anio] = conteos
        tabla = tabla_referencia(por_anio, nombres)
        DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
        tabla.to_csv(ruta_referencia(clave, fuente), index=False)
        reparto = tabla["ref_clase"].value_counts(normalize=True).mul(100).round(1)
        print(f"{clave}: {len(tabla)} celdas -> {ruta_referencia(clave, fuente)}")
        print("   clase principal por celda:", ", ".join(f"{c} {v} %" for c, v in reparto.items()))
        if len(por_anio) > 1:
            print(f"   celdas que no cambiaron de clase entre {min(por_anio)} y {max(por_anio)}: "
                  f"{tabla['ref_estable'].mean():.0%}")


# ---------------------------------------------------------------------------
# 2. Comparar: ¿qué dice la referencia en las celdas de cada clase del modelo?
# ---------------------------------------------------------------------------
def _unir(clave_zona: str, fuente: str) -> pd.DataFrame | None:
    from src.clima_relieve import cargar_celdas
    celdas = cargar_celdas(clave_zona)
    if celdas is None or not ruta_referencia(clave_zona, fuente).exists():
        return None
    return celdas.merge(pd.read_csv(ruta_referencia(clave_zona, fuente)), on="celda", how="inner")


def _acierto(nombre, del_modelo: pd.Series, de_referencia: pd.Series) -> str:
    """Cuánto coincide una clase del modelo con la referencia, en los dos sentidos."""
    ambos = int((del_modelo & de_referencia).sum())
    confirma = f"{ambos / del_modelo.sum():.0%}" if del_modelo.sum() else "—"
    encuentra = f"{ambos / de_referencia.sum():.0%}" if de_referencia.sum() else "—"
    return (f"   {nombre}: de {int(del_modelo.sum())} celdas que el modelo marca, la referencia "
            f"confirma el {confirma}; de {int(de_referencia.sum())} celdas de la referencia, "
            f"el modelo encuentra el {encuentra}")


def comparar(fuente: str, zonas=None) -> None:
    columnas = [f"ref_{n}" for n in FUENTES[fuente]["clases"]]
    for clave in (zonas or ZONAS):
        t = _unir(clave, fuente)
        if t is None or "cobertura" not in t:
            print(f"{clave}: falta la referencia o la columna `cobertura` "
                  f"(ejecuta antes `descargar {fuente}`).")
            continue
        t = t[t["cobertura"].notna() & t["ref_clase"].notna()]
        print(f"\n=== {clave}: {len(t)} celdas con modelo y con referencia ({fuente})")
        print("Qué hay, según la referencia, dentro de las celdas de cada clase del modelo (%):")
        resumen = t.groupby("cobertura")[columnas].mean().mul(100).round(0)
        resumen = resumen.loc[:, resumen.max() >= 1]                     # sin columnas vacías
        resumen.columns = [c.removeprefix("ref_") for c in resumen.columns]
        resumen.insert(0, "celdas", t["cobertura"].value_counts())
        print(resumen.to_string())
        print("Coincidencias (la referencia cuenta si la clase ocupa la mitad de la celda o más):")
        for nombre, del_modelo, de_referencia in FUENTES[fuente]["aciertos"]:
            print(_acierto(nombre, t["cobertura"].isin(del_modelo),
                           t[[f"ref_{c}" for c in de_referencia]].sum(axis=1) >= 0.5))
        en_ladera = t[(t["cobertura"] == "construcciones") & (t["pendiente"] > 10)]
        if len(en_ladera):
            columna = f"ref_{FUENTES[fuente]['aciertos'][0][2][0]}"
            print(f"   construcciones en laderas de más de 10°: {len(en_ladera)} celdas, con "
                  f"{en_ladera[columna].mean():.0%} de zona construida según la referencia")


# ---------------------------------------------------------------------------
# 3. Probar un modelo entrenado con la referencia (no escribe nada)
# ---------------------------------------------------------------------------
def probar(fuente: str, zonas=None) -> None:
    """Entrena un bosque aleatorio con los rasgos del radar y la referencia, y mide el acierto.

    La prueba es honesta: cada zona se parte en bloques de ~7,5 km y el modelo se prueba
    siempre en bloques que NO vio al entrenar (celdas vecinas se parecen demasiado).
    Solo se usan celdas estables y donde una clase ocupa la mayor parte de la celda.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import balanced_accuracy_score, classification_report
    from sklearn.model_selection import GroupKFold, cross_val_predict

    from src.cobertura import RASGOS, rasgos_de_zona
    from src.nisar import ruta_serie

    partes = []
    for numero, clave in enumerate(zonas or ZONAS):
        t = _unir(clave, fuente)
        if t is None or not ruta_serie(clave).exists():
            continue
        _, n_columnas, _ = forma_rejilla(ZONAS[clave]["recuadro"])
        rasgos = rasgos_de_zona(clave).add_prefix("radar_")
        rasgos["celda"] = np.arange(len(rasgos))
        t = t.merge(rasgos, on="celda", how="inner")
        fila, columna = t["celda"] // n_columnas, t["celda"] % n_columnas
        t["bloque"] = numero * 10_000 + (fila // LADO_BLOQUE) * 100 + columna // LADO_BLOQUE
        t["zona"] = clave
        partes.append(t)
    if not partes:
        print(f"No hay zonas con serie de radar y referencia. Ejecuta antes `descargar {fuente}`.")
        return
    todo = pd.concat(partes, ignore_index=True)
    entradas = [f"radar_{r}" for r in RASGOS] + ["pendiente"]
    util = todo[todo[entradas].notna().all(axis=1) & (todo["ref_pureza"] >= PUREZA_MINIMA)
                & todo["ref_estable"].astype(bool)]
    cuantas = util["ref_clase"].value_counts()
    util = util[util["ref_clase"].isin(cuantas[cuantas >= 50].index)]   # con muy pocas celdas no se aprende
    print(f"Celdas para entrenar y probar: {len(util)} de {len(todo)} (con radar, estables y con "
          f"una clase que ocupa al menos el {PUREZA_MINIMA:.0%} de la celda)")
    print("Clases:", ", ".join(f"{c} {n}" for c, n in util["ref_clase"].value_counts().items()))
    if util["ref_clase"].nunique() < 2 or util["bloque"].nunique() < 2:
        print("No hay suficientes clases o bloques para hacer la prueba.")
        return

    def nuevo_modelo():
        return RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight="balanced",
                                      n_jobs=-1, random_state=0)

    cortes = GroupKFold(n_splits=min(5, util["bloque"].nunique()))
    prediccion = cross_val_predict(nuevo_modelo(), util[entradas], util["ref_clase"],
                                   groups=util["bloque"], cv=cortes)
    acierto = (prediccion == util["ref_clase"]).mean()
    siempre_la_mayor = util["ref_clase"].value_counts(normalize=True).iloc[0]
    print(f"\nAcierto en bloques que el modelo no vio: {acierto:.0%} "
          f"(decir siempre la clase más común daría {siempre_la_mayor:.0%})")
    print(f"Acierto promedio por clase (cada clase pesa igual): "
          f"{balanced_accuracy_score(util['ref_clase'], prediccion):.0%}")
    print(classification_report(util["ref_clase"], prediccion, digits=2, zero_division=0))
    for clave, grupo in util.assign(prediccion=prediccion).groupby("zona"):
        print(f"   {clave}: acierto {(grupo['prediccion'] == grupo['ref_clase']).mean():.0%} "
              f"en {len(grupo)} celdas")

    # La pregunta que más le importa a la recomendación, como sí o no
    pregunta, positivas = FUENTES[fuente]["pregunta"]
    real, dicho = util["ref_clase"].isin(positivas), pd.Series(prediccion, index=util.index).isin(positivas)
    if real.any() and (~real).any():
        print(f"\n{pregunta}  Acierto {(real == dicho).mean():.0%}. "
              + _acierto("sí", dicho, real).strip())

    importancia = pd.Series(nuevo_modelo().fit(util[entradas], util["ref_clase"]).feature_importances_,
                            index=[e.removeprefix("radar_") for e in entradas])
    print("Qué rasgos pesan más:", ", ".join(f"{r} {v:.2f}" for r, v in
                                              importancia.sort_values(ascending=False).items()))
    print("\nEsto es solo una prueba: no se guardó ningún modelo ni se cambió ninguna tabla.")


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else ""
    fuente_pedida = sys.argv[2] if len(sys.argv) > 2 else "mapbiomas"
    zonas_pedidas = sys.argv[3:] or None
    acciones = {"descargar": descargar, "comparar": comparar, "probar": probar}
    if accion not in acciones or fuente_pedida not in FUENTES:
        print("Uso: python recolectar_referencia.py [descargar|comparar|probar] "
              "[mapbiomas|worldcover] [ZONA ...]")
        sys.exit(1)
    acciones[accion](fuente_pedida, zonas_pedidas)
