"""
Uso de la tierra por parcela y registros oficiales del MAG, por zona.

Completa lo que `src/cultivos_mapeados.py` no cubre: ese módulo solo tiene seis cultivos y nada
en la Sierra. Aquí se usa el mapa "Cobertura y uso de la tierra y sistemas productivos
agropecuarios 1:25.000" (todo el país, con el cultivo de cada parcela) y cinco registros:

    python -m src.uso_tierra_mag ZONA descargar   # -> datos/crudos/uso_tierra_mag/ZONA/
    python -m src.uso_tierra_mag ZONA contar      # parcelas y hectáreas por cultivo (solo imprime)
    python -m src.uso_tierra_mag ZONA tabla       # -> datos/procesados/uso_tierra_mag_ZONA.csv

ZONA es una clave de `src/config.py` o una de RECUADROS_EXTRA (recuadros de la Sierra tomados
del archivo de datos del equipo, mientras no estén en config).

Tabla por celda (mismo número de `celda` y misma rejilla que celdas_ZONA.csv):
    uso_dominante      nombre de la cobertura que ocupa más de la celda (texto del MAG)
    uso_parte          parte de la celda que ocupa (0 a 1)
    uso_<cultivo>      parte de la celda con cada cultivo que la app evalúa, con pasto y con páramo
    uso_maiz           "maíz" a secas, sin decir si es duro o suave
    riego_mapeado      parte de la celda cuyas parcelas figuran "con riego"
    paramo_mapeado     parte de la celda dentro del páramo cartografiado (1:100.000)
    helada_riesgo      nivel de riesgo por helada del subsector agrícola en la parroquia

Cuidados:
  - El mapa de cobertura se levantó entre 2009 y 2015 (programa SIGTIERRAS): dice qué se sembraba
    entonces. Sirve como experiencia histórica del lugar, no como "qué hay hoy".
  - El riesgo por helada es un índice por parroquia, no por terreno.
  - Pide rasterio (solo desarrollo). La app solo leería el CSV.

Fuente: MAG, Geoportal del Agro Ecuatoriano, http://geoportal.agricultura.gob.ec/geoservicios/cartografia.html
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from .config import DATOS_CRUDOS, DATOS_PROCESADOS, PASO_CELDA_SEG, ZONAS, forma_rejilla

BASE = "http://geoportal.agricultura.gob.ec/"
MAXIMO_POR_PEDIDO = 20000

# Recuadros de la Sierra del manifest del archivo del equipo (lon_min, lat_min, lon_max, lat_max)
RECUADROS_EXTRA = {"tungurahua": (-78.80, -1.50, -78.40, -1.10),
                   "cotopaxi": (-78.85, -1.10, -78.45, -0.70)}

# nombre corto -> (servicio, capa, atributos que se conservan)
CAPAS = {
    "cobertura": ("cobertura/E25k_asociacion_objetos/wfs", "E25k_asociacion_objetos:vw_sc_cobertura_tierra",
                  ("nivel_I", "nivel_II", "nombre_cobertura_de_la_tierra", "temporalidad", "riego",
                   "sistema_de_producción", "tamaño_de_parcela", "superficie_calculada")),
    "catastro_bananero": ("registros/E5k/wfs", "E5k:vw_catastro_bananero", ("var", "rie", "sce", "ppg", "pep")),
    "catastro_floricola": ("registros/E5k/wfs", "E5k:vw_catastro_floricola", ("var", "rie", "sce")),
    "censo_palmicultor": ("registros/E50k/wfs", "E50k:vw_censo_palmicultor", ("ets", "asi", "sci")),
    "riego_parcelario": ("demarcacion/E5k/wfs", "E5k:vw_hf001_area_riego_parcelario",
                         ("método_de_riego_tecnificado", "nombre_cultivos_regados", "superficie_calculada")),
    "paramo": ("cobertura/E100k/wfs", "E100k:vw_paramo", ("sce",)),
    "helada_agricola": ("agroestadistica/riesgos_agroclimaticos/wfs",
                        "riesgos_agroclimaticos:vw_01a9_riesgo_helada_agricola",
                        ("nombre_provincia", "nombre_cantón", "nombre_parroquia", "nivel_de_amenaza",
                         "nivel_de_riesgo", "índice_de_riesgo", "subíndice_de_amenaza")),
}

# Cómo llama el mapa del MAG a los cultivos que la app evalúa (texto sin tildes, en mayúsculas)
CULTIVOS = {
    "cacao": ("CACAO",), "banano": ("BANANO",), "platano": ("PLATANO",),
    "palma_aceitera": ("PALMA AFRICANA", "PALMA ACEITERA"), "cafe_robusta": ("CAFE",),
    "maracuya": ("MARACUYA",), "maiz_duro": ("MAIZ DURO", "MAIZ AMARILLO"), "arroz": ("ARROZ",),
    "yuca": ("YUCA",), "pina": ("PINA",), "papa": ("PAPA",), "maiz_suave": ("MAIZ SUAVE",),
    "haba": ("HABA",), "quinua": ("QUINUA",), "tomate_de_arbol": ("TOMATE DE ARBOL",),
    "pasto": ("PASTO", "PASTIZAL"), "paramo": ("PARAMO",),
}
# El mapa dice casi siempre "MAIZ" a secas. No se reparte entre duro y suave: va en `uso_maiz`
# y quien lo use decide por la zona (en la Costa es maíz duro; sobre ~2.000 m, maíz suave).
SOLO_NOMBRE_EXACTO = {"maiz": ("MAIZ",)}
NIVELES_HELADA = {"MUY BAJO": 1, "BAJO": 2, "MEDIO": 3, "ALTO": 4, "MUY ALTO": 5}


def recuadro_de(clave_zona: str):
    if clave_zona in ZONAS:
        return ZONAS[clave_zona]["recuadro"]
    return RECUADROS_EXTRA[clave_zona]


def sin_tildes(texto) -> str:
    limpio = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in limpio if unicodedata.category(c) != "Mn").upper().strip()


def carpeta(clave_zona: str) -> Path:
    return DATOS_CRUDOS / "uso_tierra_mag" / clave_zona


def ruta_tabla(clave_zona: str) -> Path:
    return DATOS_PROCESADOS / f"uso_tierra_mag_{clave_zona}.csv"


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------
def _pedir(servicio: str, capa: str, recuadro, nivel: int = 0) -> dict:
    """Elementos de una capa dentro del recuadro. Si el servidor corta, parte el recuadro en cuatro."""
    a, b, c, d = recuadro
    r = requests.get(BASE + servicio, timeout=900, params={
        "service": "WFS", "version": "1.1.0", "request": "GetFeature", "typeName": capa,
        "outputFormat": "application/json", "srsName": "EPSG:4326",
        "bbox": f"{a},{b},{c},{d},EPSG:4326", "maxFeatures": MAXIMO_POR_PEDIDO})
    r.raise_for_status()
    datos = r.json()
    hallados = {f["id"]: f for f in datos.get("features", [])}
    if len(hallados) >= datos.get("totalFeatures", 0) or nivel >= 4:
        return hallados
    lon_m, lat_m = (a + c) / 2, (b + d) / 2
    for parte in ((a, b, lon_m, lat_m), (lon_m, b, c, lat_m), (a, lat_m, lon_m, d), (lon_m, lat_m, c, d)):
        hallados.update(_pedir(servicio, capa, parte, nivel + 1))
    return hallados


def descargar(clave_zona: str, solo=None) -> None:
    destino = carpeta(clave_zona)
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, (servicio, capa, atributos) in CAPAS.items():
        if solo and nombre not in solo:
            continue
        try:
            elementos = _pedir(servicio, capa, recuadro_de(clave_zona)).values()
        except Exception as error:  # noqa: BLE001
            print(f"  {nombre}: FALLÓ ({type(error).__name__}: {str(error)[:90]})", flush=True)
            continue
        # Solo la geometría y los atributos útiles: sin nombres de predios ni de personas
        limpio = [{"type": "Feature", "geometry": f["geometry"],
                   "properties": {k: f["properties"].get(k) for k in atributos}}
                  for f in elementos if f.get("geometry")]
        ruta = destino / f"{nombre}.geojson"
        ruta.write_text(json.dumps({"type": "FeatureCollection", "features": limpio}, ensure_ascii=False),
                        encoding="utf-8")
        print(f"  {nombre:20s} {len(limpio):6d} elementos, {ruta.stat().st_size / 1e6:6.1f} MB", flush=True)


def leer(clave_zona: str, nombre: str) -> list:
    ruta = carpeta(clave_zona) / f"{nombre}.geojson"
    return json.loads(ruta.read_text(encoding="utf-8"))["features"] if ruta.exists() else []


def cultivo_de(nombre_cobertura) -> str | None:
    """Clave del cultivo de la app que corresponde a un nombre de cobertura del MAG, o None."""
    texto = sin_tildes(nombre_cobertura)
    for clave, palabras in SOLO_NOMBRE_EXACTO.items():
        if texto in palabras:
            return clave
    for clave, palabras in CULTIVOS.items():
        if any(texto == p or texto.startswith(p + " ") or texto.startswith(p + "-") for p in palabras):
            return clave
    return None


# ---------------------------------------------------------------------------
# Conteo por cultivo (para saber cuántas parcelas hay)
# ---------------------------------------------------------------------------
def contar(clave_zona: str, cuantos: int = 30) -> pd.DataFrame:
    filas = [{"cobertura": sin_tildes(f["properties"].get("nombre_cobertura_de_la_tierra")),
              "nivel_I": f["properties"].get("nivel_I"),
              "riego": sin_tildes(f["properties"].get("riego")),
              "ha": pd.to_numeric(f["properties"].get("superficie_calculada"), errors="coerce")}
             for f in leer(clave_zona, "cobertura")]
    t = pd.DataFrame(filas)
    resumen = (t.groupby("cobertura").agg(parcelas=("ha", "size"), hectareas=("ha", "sum"))
               .sort_values("hectareas", ascending=False))
    print(f"\n[{clave_zona}] cobertura y uso de la tierra: {len(t)} parcelas, {t['ha'].sum():,.0f} ha")
    print(resumen.head(cuantos).round(0).to_string())
    print("  riego:", t["riego"].value_counts().head(6).to_dict())
    for nombre in ("catastro_bananero", "catastro_floricola", "censo_palmicultor", "riego_parcelario", "paramo",
                   "helada_agricola"):
        print(f"  {nombre}: {len(leer(clave_zona, nombre))} elementos")
    return resumen


# ---------------------------------------------------------------------------
# Tabla por celda
# ---------------------------------------------------------------------------
def _fino(pares, recuadro, tipo="uint16"):
    """Pinta (geometría, número) en la rejilla fina de 1 segundo de arco."""
    from rasterio.features import rasterize
    from rasterio.transform import from_origin
    filas, columnas, _ = forma_rejilla(recuadro)
    p = PASO_CELDA_SEG
    forma = (filas * p, columnas * p)
    pares = [(g, v) for g, v in pares if g]
    if not pares:
        return np.zeros(forma, dtype=tipo)
    return rasterize(pares, out_shape=forma, fill=0, dtype=tipo,
                     transform=from_origin(recuadro[0], recuadro[3], 1 / 3600, 1 / 3600))


def _por_celda(fino, recuadro):
    filas, columnas, _ = forma_rejilla(recuadro)
    p = PASO_CELDA_SEG
    return fino.reshape(filas, p, columnas, p).transpose(0, 2, 1, 3).reshape(filas * columnas, p * p)


def construir_tabla(clave_zona: str) -> pd.DataFrame:
    recuadro = recuadro_de(clave_zona)
    filas, columnas, _ = forma_rejilla(recuadro)
    parcelas = leer(clave_zona, "cobertura")
    if not parcelas:
        raise FileNotFoundError(f"Falta la descarga: python -m src.uso_tierra_mag {clave_zona} descargar")
    nombres = sorted({sin_tildes(f["properties"].get("nombre_cobertura_de_la_tierra")) for f in parcelas})
    codigo = {n: i + 1 for i, n in enumerate(nombres)}
    # Las parcelas grandes primero: si dos se solapan, queda la más pequeña (más detallada)
    orden = sorted(parcelas, key=lambda f: -(pd.to_numeric(f["properties"].get("superficie_calculada"),
                                                           errors="coerce") or 0))
    usos = _por_celda(_fino(((f["geometry"], codigo[sin_tildes(f["properties"].get("nombre_cobertura_de_la_tierra"))])
                             for f in orden), recuadro), recuadro)
    tabla = pd.DataFrame({"celda": np.arange(filas * columnas)})
    cuenta = np.stack([(usos == c).sum(axis=1) for c in range(len(nombres) + 1)], axis=1)
    mayor = cuenta[:, 1:].argmax(axis=1)
    parte = cuenta[np.arange(len(cuenta)), mayor + 1] / usos.shape[1]
    tabla["uso_dominante"] = np.where(parte > 0, np.array(nombres)[mayor], "")
    tabla["uso_parte"] = parte.round(3)
    for clave in list(CULTIVOS) + list(SOLO_NOMBRE_EXACTO):
        codigos = [c for n, c in codigo.items() if cultivo_de(n) == clave]
        tabla[f"uso_{clave}"] = np.isin(usos, codigos).mean(axis=1).round(3) if codigos else 0.0
    con_riego = _por_celda(_fino(((f["geometry"], 1) for f in orden
                                  if sin_tildes(f["properties"].get("riego")) in ("CON RIEGO", "SI", "VERDADERO")),
                                 recuadro, "uint8"), recuadro)
    tabla["riego_mapeado"] = con_riego.mean(axis=1).round(3)
    paramo = _por_celda(_fino(((f["geometry"], 1) for f in leer(clave_zona, "paramo")), recuadro, "uint8"), recuadro)
    tabla["paramo_mapeado"] = paramo.mean(axis=1).round(3)
    helada = _por_celda(_fino(((f["geometry"], NIVELES_HELADA.get(sin_tildes(f["properties"].get("nivel_de_riesgo")), 0))
                               for f in leer(clave_zona, "helada_agricola")), recuadro, "uint8"), recuadro)
    nivel = np.array([np.bincount(fila, minlength=6).argmax() for fila in helada])
    tabla["helada_riesgo"] = pd.Series(nivel).map({v: k for k, v in NIVELES_HELADA.items()}).fillna("")
    DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta_tabla(clave_zona), index=False)
    return tabla


def cargar(clave_zona: str) -> pd.DataFrame | None:
    ruta = ruta_tabla(clave_zona)
    return pd.read_csv(ruta, keep_default_na=False, na_values=[""]) if ruta.exists() else None


if __name__ == "__main__":
    zonas = list(ZONAS) + [z for z in RECUADROS_EXTRA if z not in ZONAS]
    if len(sys.argv) < 3 or sys.argv[1] not in zonas:
        print("Uso: python -m src.uso_tierra_mag ZONA [descargar|contar|tabla]   Zonas:", ", ".join(zonas))
        sys.exit(1)
    zona, accion = sys.argv[1], sys.argv[2]
    if accion == "descargar":
        descargar(zona, solo=sys.argv[3:] or None)
    elif accion == "contar":
        contar(zona)
    elif accion == "tabla":
        tb = construir_tabla(zona)
        print(f"Guardado {ruta_tabla(zona)} ({len(tb)} celdas)")
        print(tb["uso_dominante"].replace("", "(sin dato)").value_counts().head(15).to_string())
