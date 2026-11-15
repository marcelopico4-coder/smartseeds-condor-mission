"""
Radar de la época lluviosa: Sentinel-1 (producto OPERA RTC-S1 de la NASA).

NISAR solo tiene pasadas desde junio de 2026 (época seca). Para ver dónde se acumula el agua en
invierno se usa otro radar, Sentinel-1 de la ESA, en el producto OPERA RTC-S1 que procesa el
JPL de la NASA y distribuye ASF: banda C, polarizaciones VV y VH, 30 m.

    Es banda C, no banda L: ve el agua abierta igual de bien, pero atraviesa menos la vegetación.
    Por eso se guarda como una serie APARTE y no se mezcla con los rasgos de NISAR.
    NISAR sigue siendo el dato central del proyecto.

Uso (pide el login de Earthdata ya guardado, igual que NISAR):
    python -m src.sentinel daule procesar     # enero a mayo -> datos/procesados/_s1_tmp/ (se puede repetir)
    python -m src.sentinel daule procesar --vh  # además lee VH de las ráfagas que la ofrecen
    python -m src.sentinel daule calibrar     # elige el umbral de agua comparando con NISAR
    python -m src.sentinel daule tabla        # invierno_daule.npz y columna `agua_invierno`

Cómo se detecta el agua: el agua quieta refleja el radar hacia otro lado y se ve oscura. Un píxel
cuenta como agua si VV queda por debajo de un umbral en dB. El umbral no se inventa: `calibrar`
lee Sentinel-1 en fechas pegadas a las de NISAR (época seca) y elige el que da el agua más
parecida a la que vio NISAR. Como cada fecha guarda el agua para varios umbrales, cambiar de
umbral no obliga a leer otra vez.

`agua_invierno` = parte de los píxeles de la celda con agua, promediada en las pasadas de enero
a mayo. Es la misma definición de `encharcamiento` (NISAR, época seca). VH se conserva como rasgo
opcional en potencia lineal; la detección de agua sigue usando VV.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

from .config import DATOS_PROCESADOS, ZONAS, forma_rejilla
from .nisar import PENDIENTE_MAX_AGUA, _wkt, a_db, sesion_remota

UMBRALES_DB = [-14, -15, -16, -17, -18, -19, -20, -21, -22]   # candidatos a umbral de agua en VV
UMBRAL_AGUA_VV_DB = -19.0      # elegido con `calibrar` en Daule el 14 nov (ver README); repetirlo en cada zona
VENTANA_SUAVIZADO = 3          # promedio de 3 x 3 píxeles (~90 m) contra el ruido granulado
INVIERNO = ("2026-01-01", "2026-05-31")
DIAS_CERCA_DE_NISAR = 2        # para calibrar: pasadas de Sentinel-1 a esta distancia de una de NISAR


def ruta_invierno(clave_zona: str) -> Path:
    return DATOS_PROCESADOS / f"invierno_{clave_zona}.npz"


def _ruta_parcial(clave_zona: str, fecha: str) -> Path:
    return DATOS_PROCESADOS / "_s1_tmp" / f"{clave_zona}_{fecha}.npz"


def buscar(clave_zona: str, inicio: str, fin: str) -> list:
    """Productos OPERA RTC-S1 que tocan la zona entre dos fechas."""
    import asf_search as asf
    return list(asf.search(dataset="OPERA-S1", processingLevel="RTC",
                           intersectsWith=_wkt(ZONAS[clave_zona]["recuadro"]),
                           start=inicio, end=fin + "T23:59:59", maxResults=5000))


def _url(producto, sufijo: str) -> str | None:
    """Dirección del archivo VV, VH o de máscara de un producto."""
    for url in producto.properties.get("additionalUrls") or []:
        if url.endswith(sufijo):
            return url
    return None


def _bajar(fs, url: str, intentos: int = 4) -> bytes:
    """Trae un archivo pequeño completo a la memoria (no se guarda en el disco)."""
    ultimo = None
    for n in range(intentos):
        try:
            return fs.cat_file(url)
        except Exception as error:  # noqa: BLE001
            ultimo = error
            time.sleep(5 * (n + 1))
            fs = sesion_remota()
    raise ultimo


def _suavizar(potencia: np.ndarray, tam: int = VENTANA_SUAVIZADO) -> np.ndarray:
    """Promedio de tam x tam píxeles en potencia lineal, sin contar los píxeles sin dato."""
    from scipy.ndimage import uniform_filter
    valido = np.isfinite(potencia)
    suma = uniform_filter(np.where(valido, potencia, 0.0), size=tam, mode="constant")
    cuenta = uniform_filter(valido.astype("float32"), size=tam, mode="constant")
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(valido & (cuenta > 0), suma / cuenta, np.nan)


def _leer_bandas_rafaga(fs, producto, recuadro, incluir_vh: bool):
    """Potencias VV y VH opcional, coordenadas y EPSG de la ventana de una ráfaga."""
    from pyproj import Transformer
    from rasterio.io import MemoryFile
    from rasterio.windows import Window, from_bounds

    url_vv, url_mascara = _url(producto, "_VV.tif"), _url(producto, "_mask.tif")
    if url_vv is None:
        return None
    lon_min, lat_min, lon_max, lat_max = recuadro
    with MemoryFile(_bajar(fs, url_vv)) as memoria, memoria.open() as src:
        epsg = src.crs.to_epsg()
        lons, lats = np.meshgrid(np.linspace(lon_min, lon_max, 5), np.linspace(lat_min, lat_max, 5))
        xs, ys = Transformer.from_crs(4326, epsg, always_xy=True).transform(lons.ravel(), lats.ravel())
        ventana = from_bounds(min(xs), min(ys), max(xs), max(ys), src.transform)
        ventana = ventana.round_offsets().round_lengths().intersection(Window(0, 0, src.width, src.height)) \
            if _se_tocan(ventana, src) else None
        if ventana is None or ventana.width < 1 or ventana.height < 1:
            return None
        vv = src.read(1, window=ventana).astype("float32")
        t = src.window_transform(ventana)
    mascara = np.ones(vv.shape, dtype=bool)
    if url_mascara is not None:     # 0 = dato bueno; 1 a 3 = sombra o inversión del relieve; 255 = sin dato
        with MemoryFile(_bajar(fs, url_mascara)) as memoria, memoria.open() as src:
            mascara = src.read(1, window=ventana) == 0
    vv[~(mascara & np.isfinite(vv) & (vv > 0))] = np.nan
    vh = None
    url_vh = _url(producto, "_VH.tif") if incluir_vh else None
    if url_vh is not None:
        with MemoryFile(_bajar(fs, url_vh)) as memoria, memoria.open() as src:
            vh = src.read(1, window=ventana).astype("float32")
            if vh.shape != vv.shape or src.crs.to_epsg() != epsg or src.window_transform(ventana) != t:
                raise ValueError("Las bandas VV y VH de la ráfaga tienen rejillas distintas.")
        vh[~(mascara & np.isfinite(vh) & (vh > 0))] = np.nan
    x = t.c + (np.arange(vv.shape[1]) + 0.5) * t.a
    y = t.f + (np.arange(vv.shape[0]) + 0.5) * t.e
    return vv, vh, x, y, epsg


def leer_rafaga(fs, producto, recuadro):
    """VV de una ráfaga, solo en la ventana de la zona: (potencia, x, y, epsg) o None."""
    rafaga = _leer_bandas_rafaga(fs, producto, recuadro, incluir_vh=False)
    if rafaga is None:
        return None
    vv, _, x, y, epsg = rafaga
    return vv, x, y, epsg


def _se_tocan(ventana, src) -> bool:
    return (ventana.col_off < src.width and ventana.row_off < src.height
            and ventana.col_off + ventana.width > 0 and ventana.row_off + ventana.height > 0)


def _celda_de_cada_pixel(x, y, epsg, recuadro):
    """Número de celda de cada píxel (-1 si cae fuera de la zona)."""
    from pyproj import Transformer
    filas, columnas, paso = forma_rejilla(recuadro)
    lon_min, _, _, lat_max = recuadro
    xx, yy = np.meshgrid(x, y)
    lon, lat = Transformer.from_crs(epsg, 4326, always_xy=True).transform(xx.ravel(), yy.ravel())
    i = np.floor((lat_max - lat) / paso).astype(int)
    j = np.floor((lon - lon_min) / paso).astype(int)
    dentro = (i >= 0) & (i < filas) & (j >= 0) & (j < columnas)
    return np.where(dentro, i * columnas + j, -1)


def procesar_fecha(clave_zona: str, fecha: str, incluir_vh: bool = False) -> Path | None:
    """Guarda por celda el promedio de VV, el agua por umbral y, si se solicita, el promedio de VH."""
    recuadro = ZONAS[clave_zona]["recuadro"]
    filas, columnas, _ = forma_rejilla(recuadro)
    n_celdas = filas * columnas
    productos = [p for p in buscar(clave_zona, fecha, fecha) if str(p.properties["startTime"])[:10] == fecha]
    if not productos:
        raise RuntimeError(f"No hay productos de Sentinel-1 el {fecha}")
    fs = sesion_remota()
    suma_vv, cuenta = np.zeros(n_celdas), np.zeros(n_celdas)
    suma_agua = np.zeros((len(UMBRALES_DB), n_celdas))
    suma_vh, cuenta_vh = np.zeros(n_celdas), np.zeros(n_celdas)
    for p in productos:
        t0 = time.time()
        rafaga = _leer_bandas_rafaga(fs, p, recuadro, incluir_vh)
        if rafaga is None:
            continue
        vv, vh, x, y, epsg = rafaga
        vv = _suavizar(vv)
        celda = _celda_de_cada_pixel(x, y, epsg, recuadro)
        ok = (celda >= 0) & np.isfinite(vv.ravel())
        k, valores = celda[ok], vv.ravel()[ok]
        suma_vv += np.bincount(k, weights=valores, minlength=n_celdas)
        cuenta += np.bincount(k, minlength=n_celdas)
        if vh is not None:
            vh = _suavizar(vh).ravel()
            ok_vh = (celda >= 0) & np.isfinite(vh)
            suma_vh += np.bincount(celda[ok_vh], weights=vh[ok_vh], minlength=n_celdas)
            cuenta_vh += np.bincount(celda[ok_vh], minlength=n_celdas)
        en_db = a_db(valores)
        for n, umbral in enumerate(UMBRALES_DB):
            suma_agua[n] += np.bincount(k, weights=(en_db < umbral).astype("float64"), minlength=n_celdas)
        print(f"  {fecha} {p.properties['operaBurstID']}: ventana {vv.shape}, "
              f"{(np.bincount(k, minlength=n_celdas) > 0).mean():.0%} de las celdas, {time.time() - t0:.0f} s",
              flush=True)
    if cuenta.sum() == 0:
        return None
    with np.errstate(invalid="ignore", divide="ignore"):
        vv_medio = np.where(cuenta > 0, suma_vv / cuenta, np.nan).astype("float32").reshape(filas, columnas)
        agua = np.where(cuenta > 0, suma_agua / cuenta, np.nan).astype("float32").reshape(-1, filas, columnas)
    parcial = _ruta_parcial(clave_zona, fecha)
    parcial.parent.mkdir(parents=True, exist_ok=True)
    bandas = {"vv": vv_medio}
    if incluir_vh:
        vh_medio = np.full(n_celdas, np.nan, dtype="float32")
        np.divide(suma_vh, cuenta_vh, out=vh_medio, where=cuenta_vh > 0)
        bandas["vh"] = vh_medio.reshape(filas, columnas)
    np.savez_compressed(parcial, agua=agua, umbrales=np.array(UMBRALES_DB),
                        orbita=int(productos[0].properties["pathNumber"]), **bandas)
    return parcial


def _parcial_listo(parcial: Path, incluir_vh: bool) -> bool:
    if not parcial.exists():
        return False
    if not incluir_vh:
        return True
    with np.load(parcial) as datos:
        return "vh" in datos.files


def procesar_fechas(clave_zona: str, fechas: list[str], segundos_por_fecha: int = 420, intentos: int = 3,
                    incluir_vh: bool = False):
    """Procesa cada fecha por separado. Con VH, repite las fechas guardadas solo con VV."""
    import subprocess

    from .config import RAIZ
    for numero, fecha in enumerate(fechas, start=1):
        parcial = _ruta_parcial(clave_zona, fecha)
        comando = [sys.executable, "-W", "ignore", "-m", "src.sentinel", clave_zona, "fecha", fecha]
        if incluir_vh:
            comando.append("--vh")
        for intento in range(1, intentos + 1):
            if _parcial_listo(parcial, incluir_vh):
                break
            try:
                subprocess.run(comando, cwd=RAIZ, timeout=segundos_por_fecha)
            except subprocess.TimeoutExpired:
                print(f"  {fecha}: se colgó (intento {intento} de {intentos})", flush=True)
        estado = "lista" if _parcial_listo(parcial, incluir_vh) else "NO se pudo leer"
        print(f"[{numero}/{len(fechas)}] {fecha}: {estado}", flush=True)


def fechas_de(clave_zona: str, inicio: str, fin: str) -> list[str]:
    return sorted({str(p.properties["startTime"])[:10] for p in buscar(clave_zona, inicio, fin)})


def fechas_para_calibrar(clave_zona: str) -> dict[str, str]:
    """{fecha de Sentinel-1: fecha de NISAR más cercana}, solo las que están a pocos días."""
    from datetime import date

    from .nisar import ruta_serie
    with np.load(ruta_serie(clave_zona)) as s:
        de_nisar = [str(f) for f in s["fechas"]]
    de_s1 = fechas_de(clave_zona, min(de_nisar), max(de_nisar))
    pares = {}
    for f in de_s1:
        cercana = min(de_nisar, key=lambda n: abs((date.fromisoformat(n) - date.fromisoformat(f)).days))
        if abs((date.fromisoformat(cercana) - date.fromisoformat(f)).days) <= DIAS_CERCA_DE_NISAR:
            pares[f] = cercana
    return pares


def calibrar(clave_zona: str) -> dict:
    """Compara el agua de Sentinel-1, con cada umbral, con la de NISAR en fechas cercanas.

    Para cada umbral: diferencia media (por celda) entre las dos fracciones de agua, y cuánto se
    parecen las celdas "con agua" (al menos un cuarto de la celda) de los dos radares.
    Devuelve {"umbral": el mejor, "tabla": DataFrame con todos, "pares": fechas usadas}.
    """
    import pandas as pd

    from .nisar import ruta_serie
    pares = fechas_para_calibrar(clave_zona)
    procesar_fechas(clave_zona, list(pares))
    with np.load(ruta_serie(clave_zona)) as s:
        de_nisar = {str(f): s["agua"][n] for n, f in enumerate(s["fechas"])}
    filas = []
    for n, umbral in enumerate(UMBRALES_DB):
        diferencia, ambos, alguno, solo_s1, solo_nisar, usados = [], 0, 0, 0, 0, 0
        for f_s1, f_nisar in pares.items():
            if not _ruta_parcial(clave_zona, f_s1).exists():
                continue
            with np.load(_ruta_parcial(clave_zona, f_s1)) as p:
                s1 = p["agua"][n]
            nisar = de_nisar[f_nisar]
            comun = np.isfinite(s1) & np.isfinite(nisar)
            if comun.mean() < 0.3:          # esa pasada casi no cubre la zona
                continue
            usados += 1
            diferencia.append(np.abs(s1[comun] - nisar[comun]).mean())
            a, b = s1[comun] >= 0.25, nisar[comun] >= 0.25
            ambos, alguno = ambos + int((a & b).sum()), alguno + int((a | b).sum())
            solo_s1, solo_nisar = solo_s1 + int((a & ~b).sum()), solo_nisar + int((~a & b).sum())
        if usados:
            filas.append({"umbral_dB": umbral, "fechas": usados,
                          "diferencia_media": round(float(np.mean(diferencia)), 4),
                          "coincidencia": round(ambos / alguno, 3) if alguno else np.nan,
                          "celdas_con_agua_los_dos": ambos, "solo_sentinel": solo_s1, "solo_nisar": solo_nisar})
    tabla = pd.DataFrame(filas)
    if tabla.empty:
        raise RuntimeError("No hay fechas de Sentinel-1 cerca de las de NISAR para calibrar.")
    mejor = int(tabla.loc[tabla["coincidencia"].idxmax(), "umbral_dB"])
    print(tabla.to_string(index=False))
    print(f"Umbral que más se parece a NISAR: {mejor} dB (coincidencia = celdas con agua para los dos radares "
          "entre celdas con agua para alguno)")
    return {"umbral": mejor, "tabla": tabla, "pares": pares}


def serie_y_tabla(clave_zona: str, umbral_db: float = UMBRAL_AGUA_VV_DB, inicio: str = INVIERNO[0],
                  fin: str = INVIERNO[1]):
    """Junta las fechas ya leídas en invierno_ZONA.npz y escribe la columna `agua_invierno`."""
    import warnings

    import pandas as pd

    from .clima_relieve import ruta_celdas
    n = UMBRALES_DB.index(int(umbral_db))
    fechas = sorted(p.stem.split("_")[-1] for p in (DATOS_PROCESADOS / "_s1_tmp").glob(f"{clave_zona}_*.npz"))
    fechas = [f for f in fechas if inicio <= f <= fin]
    if not fechas:
        raise RuntimeError(f"No hay fechas leídas de {clave_zona}. Ejecuta antes `procesar`.")
    agua, vv, vh = [], [], []
    for f in fechas:
        with np.load(_ruta_parcial(clave_zona, f)) as p:
            agua.append(p["agua"][n])
            vv.append(p["vv"])
            vh.append(p["vh"] if "vh" in p.files else None)
    agua, vv = np.array(agua, dtype="float32"), np.array(vv, dtype="float32")
    bandas = {"vv": vv}
    if any(v is not None for v in vh):
        bandas["vh"] = np.array([v if v is not None else np.full_like(vv[0], np.nan) for v in vh])
    np.savez_compressed(ruta_invierno(clave_zona), fechas=np.array(fechas), agua=agua,
                        umbral_db=float(umbral_db), **bandas)
    tabla = pd.read_csv(ruta_celdas(clave_zona))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)          # celdas sin ningún dato
        invierno = np.nanmean(agua, axis=0)
    pendiente = tabla["pendiente"].to_numpy().reshape(invierno.shape)
    invierno = np.where(pendiente > PENDIENTE_MAX_AGUA, 0.0, invierno)    # en laderas lo oscuro es sombra
    tabla["agua_invierno"] = invierno.ravel()[tabla["celda"].to_numpy()].round(3)
    tabla.to_csv(ruta_celdas(clave_zona), index=False)
    con = tabla["agua_invierno"]
    print(f"{clave_zona}: {len(fechas)} fechas ({fechas[0]} a {fechas[-1]}), umbral {umbral_db:g} dB. "
          f"Celdas con agua en invierno (5 % o más): {(con >= 0.05).mean():.1%}; "
          f"10 % o más: {(con >= 0.10).mean():.1%}; 30 % o más: {(con >= 0.30).mean():.1%}")
    return tabla


def cargar_invierno(clave_zona: str) -> dict | None:
    """Serie ya procesada con fechas, agua, vv, umbral_db y vh cuando está disponible."""
    if not ruta_invierno(clave_zona).exists():
        return None
    with np.load(ruta_invierno(clave_zona)) as s:
        serie = {"fechas": [str(f) for f in s["fechas"]], "agua": s["agua"], "vv": s["vv"],
                 "umbral_db": float(s["umbral_db"])}
        if "vh" in s.files:
            serie["vh"] = s["vh"]
        return serie


def agua_del_terreno(invierno: dict, celdas, pesos=None):
    """Parte del terreno con agua en cada pasada de la época lluviosa (Serie de pandas, de 0 a 1)."""
    import pandas as pd

    from .nisar import _media_por_fecha
    celdas = np.asarray(list(celdas), dtype=int)
    pesos = np.ones(len(celdas)) if pesos is None else np.asarray(list(pesos), dtype="float64")
    columnas = invierno["agua"].shape[2]
    valores = _media_por_fecha(invierno["agua"][:, celdas // columnas, celdas % columnas], pesos)
    return pd.Series(valores, index=pd.to_datetime(invierno["fechas"]), name="agua").dropna()


if __name__ == "__main__":
    uso = "Uso: python -m src.sentinel ZONA [procesar [--vh] | calibrar | tabla [UMBRAL]]"
    if len(sys.argv) < 3 or sys.argv[1] not in ZONAS:
        raise SystemExit(uso)
    zona, accion = sys.argv[1], sys.argv[2]
    if accion == "fecha":                       # uso interno: una fecha en su propio proceso
        procesar_fecha(zona, sys.argv[3], incluir_vh="--vh" in sys.argv[4:])
    elif accion == "procesar":
        procesar_fechas(zona, fechas_de(zona, *INVIERNO), incluir_vh="--vh" in sys.argv[3:])
    elif accion == "calibrar":
        calibrar(zona)
    elif accion == "tabla":
        serie_y_tabla(zona, float(sys.argv[3]) if len(sys.argv) > 3 else UMBRAL_AGUA_VV_DB)
    else:
        raise SystemExit(uso)
