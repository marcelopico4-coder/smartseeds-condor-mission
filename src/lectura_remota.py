"""
Leer SOLO el recuadro que hace falta de un mapa GeoTIFF que está en internet (o en el disco).

Lo usan `src.suelo_lluvia` (lluvia de CHELSA) y `recolectar_referencia.py` (WorldCover, MapBiomas).
Hay dos formas de leer; se elige con la variable de entorno SMARTSEEDS_LECTURA:

  "directa"  (por defecto) el mismo proceso abre el mapa con rasterio/GDAL, como siempre.
  "aparte"   la lectura se hace en un proceso de Python nuevo, que solo lee el recuadro y lo
             guarda en un archivo temporal; el proceso principal lo recoge.

"aparte" sirve cuando la conexión es inestable: el 14 nov el servidor de CHELSA dejó varias veces la
lectura colgada más de 2 minutos; con "aparte" cada lectura tiene un tiempo máximo y, si no responde,
se corta y se reintenta (hasta 6 veces). El resultado es idéntico: solo cambia en qué proceso se lee.

La ventana del recuadro se calcula aquí (`ventana_del_recuadro`) y no con `rasterio.windows.from_bounds`:
el 14 nov esa función tumbaba el proceso sin mensaje en una computadora con Windows (ver la nota ahí).

Uso:
    from src.lectura_remota import leer_recuadro
    r = leer_recuadro(url_o_ruta, (lon_min, lat_min, lon_max, lat_max))
    r["datos"]            matriz con los valores tal como vienen en el archivo (fila 0 = norte)
    r["transformacion"]   posición de la matriz (objeto Affine: .c y .f esquina, .a y .e tamaño del cuadro)
    r["escala"], r["desfase"]   para pasar a la unidad real: valor * escala + desfase
    r["en_grados"]        False si el mapa no está en latitud y longitud
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
OPCIONES_GDAL = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
                 "GDAL_HTTP_TIMEOUT": "120", "GDAL_HTTP_MAX_RETRY": "3"}
ESPERA_APARTE = 90           # segundos que se le da a cada proceso aparte antes de cortarlo (lo normal son ~10)
INTENTOS_APARTE = 6


def forma_de_leer() -> str:
    return "aparte" if os.environ.get("SMARTSEEDS_LECTURA", "directa").strip().lower() == "aparte" else "directa"


def es_remoto(origen: str) -> bool:
    return str(origen).startswith(("http://", "https://"))


def ventana_del_recuadro(recuadro, t):
    """Ventana (columnas y filas) del mapa que cubre el recuadro; `t` es la transformación del mapa.

    Es la misma cuenta que hace `rasterio.windows.from_bounds`, escrita aquí con aritmética simple.
    Motivo: el 14 nov, en una computadora con Windows (rasterio 1.4.4, GDAL 3.12.3, entorno conda),
    `from_bounds` tumbaba el proceso sin mensaje (código 3228369023, dentro de rasterio/transform.py),
    y por eso `suelo_lluvia` no pasaba de la lectura de la lluvia. Abrir y leer el mapa sí funcionaba.
    """
    from rasterio.windows import Window

    if t.b != 0 or t.d != 0:
        raise ValueError("El mapa está girado: esta lectura solo sirve para mapas alineados con el norte.")
    oeste, sur, este, norte = recuadro

    def exacto(v):          # un valor a menos de una millonésima de cuadro de un entero se toma como ese entero
        return float(round(v)) if abs(v - round(v)) < 1e-6 else v

    columnas = [exacto((oeste - t.c) / t.a), exacto((este - t.c) / t.a)]
    filas = [exacto((norte - t.f) / t.e), exacto((sur - t.f) / t.e)]
    return Window(col_off=min(columnas), row_off=min(filas), width=max(columnas) - min(columnas),
                  height=max(filas) - min(filas)).round_offsets().round_lengths()


def _leer_directo(origen: str, recuadro, relleno=None) -> dict:
    """Abre el mapa en este mismo proceso y lee la ventana del recuadro."""
    import rasterio

    ruta = "/vsicurl/" + origen if es_remoto(origen) else str(origen)
    with rasterio.Env(**OPCIONES_GDAL), rasterio.open(ruta) as mapa:
        ventana = ventana_del_recuadro(recuadro, mapa.transform)
        if relleno is None:
            datos = mapa.read(1, window=ventana)
        else:                                   # la ventana puede salirse del mapa: se completa con `relleno`
            datos = mapa.read(1, window=ventana, boundless=True, fill_value=relleno)
        t = mapa.window_transform(ventana)
        return {"datos": datos, "transformacion": t, "escala": float(mapa.scales[0]),
                "desfase": float(mapa.offsets[0]),
                "en_grados": bool(mapa.crs is None or mapa.crs.is_geographic)}


def _leer_aparte(origen: str, recuadro, relleno=None) -> dict:
    """Lanza un Python nuevo que lee el recuadro y lo deja en un archivo temporal; aquí se recoge.

    Si el proceso no termina en ESPERA_APARTE segundos (el servidor a veces deja la conexión colgada)
    o termina con error, se vuelve a intentar con otro proceso, hasta INTENTOS_APARTE veces.
    """
    from affine import Affine

    ultimo = ""
    for intento in range(1, INTENTOS_APARTE + 1):
        with tempfile.TemporaryDirectory() as carpeta:
            salida = Path(carpeta) / "recuadro.npz"
            orden = [sys.executable, "-m", "src.lectura_remota", str(origen),
                     *[repr(float(v)) for v in recuadro], "nada" if relleno is None else repr(relleno),
                     str(salida)]
            entorno = {**os.environ, "SMARTSEEDS_LECTURA": "directa", "PYTHONIOENCODING": "utf-8"}
            try:
                p = subprocess.run(orden, cwd=RAIZ, env=entorno, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=ESPERA_APARTE,
                                   stdin=subprocess.DEVNULL)
                ultimo = f"código {p.returncode}\n{(p.stdout + p.stderr)[-1500:]}"
                bien = p.returncode == 0 and salida.exists()
            except subprocess.TimeoutExpired:
                ultimo, bien = f"no respondió en {ESPERA_APARTE} segundos", False
            if bien:
                with np.load(salida) as guardado:
                    return {"datos": guardado["datos"], "transformacion": Affine(*guardado["transformacion"]),
                            "escala": float(guardado["escala"]), "desfase": float(guardado["desfase"]),
                            "en_grados": bool(guardado["en_grados"])}
        print(f"  (lectura de {str(origen).rsplit('/', 1)[-1]}: intento {intento} de {INTENTOS_APARTE} "
              f"falló: {ultimo.splitlines()[0]})", flush=True)
        time.sleep(5)
    raise OSError(f"No se pudo leer {origen} en un proceso aparte tras {INTENTOS_APARTE} intentos.\n{ultimo}")


def leer_recuadro(origen: str, recuadro, relleno=None) -> dict:
    """Lee la parte del mapa que cubre `recuadro` = (lon_min, lat_min, lon_max, lat_max).

    `relleno`: si se da, la ventana puede salirse del mapa y lo que falte se completa con ese valor.
    Un archivo del disco siempre se lee de forma directa.
    """
    if es_remoto(origen) and forma_de_leer() == "aparte":
        return _leer_aparte(origen, recuadro, relleno)
    return _leer_directo(origen, recuadro, relleno)


if __name__ == "__main__":
    # Uso interno: python -m src.lectura_remota ORIGEN LON_MIN LAT_MIN LON_MAX LAT_MAX RELLENO|nada SALIDA.npz
    if len(sys.argv) != 8:
        raise SystemExit("Uso interno (lo lanza leer_recuadro): ORIGEN LON_MIN LAT_MIN LON_MAX LAT_MAX "
                         "RELLENO|nada SALIDA.npz")
    _origen, _recuadro = sys.argv[1], tuple(float(v) for v in sys.argv[2:6])
    _relleno = None if sys.argv[6] == "nada" else float(sys.argv[6])
    _r = _leer_directo(_origen, _recuadro, _relleno)
    np.savez(sys.argv[7], datos=_r["datos"], transformacion=np.array(tuple(_r["transformacion"])[:6]),
             escala=_r["escala"], desfase=_r["desfase"], en_grados=_r["en_grados"])
    print(f"recuadro leído: {_r['datos'].shape[0]} x {_r['datos'].shape[1]} cuadros")
