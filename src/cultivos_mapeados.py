"""
Cultivos ya mapeados por el Ministerio de Agricultura (MAG), por celda.

No es una predicción: son los polígonos oficiales de "Estimaciones de cultivos" a
escala 1:25.000 del geoportal del MAG (hechos sobre imágenes PlanetScope y Sentinel-2).
Sirven para dos cosas:
  1. Mostrar en la app un dato con fuente y año: "según el MAG (2025), aquí hay arroz".
  2. Dar etiquetas para entrenar o comprobar el modelo de tipo de terreno.

    python -m src.cultivos_mapeados ZONA descargar   # polígonos de la zona -> datos/crudos/cultivos_mag/ZONA/
    python -m src.cultivos_mapeados ZONA tabla       # -> datos/procesados/cultivos_mag_ZONA.csv
    python -m src.cultivos_mapeados ZONA comparar    # contra el radar y el tipo de terreno (solo imprime)

La tabla tiene una fila por celda (mismo número de `celda` que celdas_ZONA.csv) y, por
cultivo, la parte de la celda que cae dentro de los polígonos (0 a 1):
    ref_arroz, ref_maiz_duro, ref_soya, ref_banano, ref_palma_aceitera, ref_cana_azucar
más `arroz_ciclos` (en cuántos de los tres períodos del año hubo arroz, promedio de la
parte arrocera) y `cultivo_mapeado` (el cultivo que ocupa más, si pasa de PARTE_MINIMA).

Cuidados:
  - Arroz, maíz y soya son de 2025 y cambian cada temporada: leerlo como "aquí se sembró
    en 2025", no como "aquí hay arroz hoy". Banano, palma y caña son de 2022.
  - El MAG indica en cada polígono que no se hizo la validación en campo.
  - Solo cubre estos seis cultivos: una celda sin dato NO significa "sin cultivo".
  - Pide rasterio (solo desarrollo). La app solo lee el CSV.

Fuente: MAG, Geoportal del Agro Ecuatoriano, geoservicio "Estimaciones de cultivos 1:25.000"
(http://geoportal.agricultura.gob.ec/geoservicios/cartografia.html).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from .config import DATOS_CRUDOS, DATOS_PROCESADOS, PASO_CELDA_SEG, ZONAS, forma_rejilla

WFS = "http://geoportal.agricultura.gob.ec/cobertura/E25k/wfs"
MAXIMO_POR_PEDIDO = 20000
PARTE_MINIMA = 0.25      # parte de la celda para nombrar un "cultivo mapeado" (sin calibrar)

# cultivo (misma clave que tablas/requisitos_cultivos.csv cuando existe) -> capas del MAG y año
CAPAS = {
    "arroz": {"anio": 2025, "capas": ["vw_ea010_arroz_periodo1_2025", "vw_ea010_arroz_periodo2_2025",
                                      "vw_ea010_arroz_periodo3_2025"]},
    "maiz_duro": {"anio": 2025, "capas": ["vw_ea010_maiz_amarillo_duro_periodo1_2025",
                                          "vw_ea010_maiz_amarillo_duro_periodo2_2025"]},
    "soya": {"anio": 2025, "capas": ["vw_ea010_soya_2025"]},
    "banano": {"anio": 2022, "capas": ["vw_ea010_cultivo_banano_2022"]},
    "palma_aceitera": {"anio": 2022, "capas": ["vw_ea010_cultivo_palma_aceitera_2022"]},
    "cana_azucar": {"anio": 2022, "capas": ["vw_ea010_cultivo_cazucar_industrial_2022"]},
}
NOMBRES = {"arroz": "Arroz", "maiz_duro": "Maíz duro", "soya": "Soya", "banano": "Banano",
           "palma_aceitera": "Palma aceitera", "cana_azucar": "Caña de azúcar"}


def carpeta_cruda(clave_zona: str) -> Path:
    return DATOS_CRUDOS / "cultivos_mag" / clave_zona


def ruta_tabla(clave_zona: str) -> Path:
    return DATOS_PROCESADOS / f"cultivos_mag_{clave_zona}.csv"


# ---------------------------------------------------------------------------
# Descarga (solo los polígonos que tocan el recuadro de la zona)
# ---------------------------------------------------------------------------
def _pedir(capa: str, recuadro) -> dict:
    """Polígonos de una capa dentro del recuadro, como {id: polígono}.

    El servidor no deja pedir por páginas. Si corta la respuesta (devuelve menos de los
    que dice tener), se parte el recuadro en cuatro y se vuelve a pedir cada parte.
    """
    lon0, lat0, lon1, lat1 = recuadro
    r = requests.get(WFS, timeout=600, params={
        "service": "WFS", "version": "1.1.0", "request": "GetFeature",
        "typeName": f"E25k:{capa}", "outputFormat": "application/json", "srsName": "EPSG:4326",
        "bbox": f"{lon0},{lat0},{lon1},{lat1},EPSG:4326", "maxFeatures": MAXIMO_POR_PEDIDO})
    r.raise_for_status()
    datos = r.json()
    encontrados = {f["id"]: f for f in datos.get("features", [])}
    if len(encontrados) >= datos.get("totalFeatures", 0):
        return encontrados
    lon_m, lat_m = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    for parte in ((lon0, lat0, lon_m, lat_m), (lon_m, lat0, lon1, lat_m),
                  (lon0, lat_m, lon_m, lat1), (lon_m, lat_m, lon1, lat1)):
        encontrados.update(_pedir(capa, parte))
    return encontrados


def descargar(clave_zona: str) -> None:
    lon0, lat0, lon1, lat1 = ZONAS[clave_zona]["recuadro"]
    destino = carpeta_cruda(clave_zona)
    destino.mkdir(parents=True, exist_ok=True)
    for cultivo, info in CAPAS.items():
        for capa in info["capas"]:
            poligonos = list(_pedir(capa, (lon0, lat0, lon1, lat1)).values())
            # Se guarda solo la geometría y tres datos: los archivos quedan mucho más livianos
            limpio = [{"type": "Feature", "geometry": f["geometry"],
                       "properties": {k: f["properties"].get(k) for k in
                                      ("nombre_cantón", "período_de_monitoreo", "insumo_ráster")}}
                      for f in poligonos if f.get("geometry")]
            ruta = destino / f"{capa}.geojson"
            ruta.write_text(json.dumps({"type": "FeatureCollection", "features": limpio}),
                            encoding="utf-8")
            print(f"  {cultivo:15s} {capa}: {len(limpio)} polígonos, "
                  f"{ruta.stat().st_size / 1e6:.1f} MB", flush=True)


# ---------------------------------------------------------------------------
# Parte de cada celda cubierta por cada cultivo
# ---------------------------------------------------------------------------
def _parte_por_celda(geometrias, recuadro) -> np.ndarray:
    """Pinta los polígonos en una rejilla fina (1 segundo de arco) y promedia por celda."""
    from rasterio.features import rasterize
    from rasterio.transform import from_origin
    filas, columnas, _ = forma_rejilla(recuadro)
    lon_min, _, _, lat_max = recuadro
    p = PASO_CELDA_SEG
    if not geometrias:
        return np.zeros((filas, columnas), dtype="float32")
    fino = rasterize(((g, 1) for g in geometrias), out_shape=(filas * p, columnas * p),
                     transform=from_origin(lon_min, lat_max, 1 / 3600, 1 / 3600),
                     fill=0, dtype="uint8")
    return fino.reshape(filas, p, columnas, p).mean(axis=(1, 3)).astype("float32")


def _leer(clave_zona: str, capa: str) -> list:
    ruta = carpeta_cruda(clave_zona) / f"{capa}.geojson"
    if not ruta.exists():
        raise FileNotFoundError(f"Falta {ruta}. Ejecuta: python -m src.cultivos_mapeados {clave_zona} descargar")
    return [f["geometry"] for f in json.loads(ruta.read_text(encoding="utf-8"))["features"]]


def construir_tabla(clave_zona: str) -> pd.DataFrame:
    recuadro = ZONAS[clave_zona]["recuadro"]
    filas, columnas, _ = forma_rejilla(recuadro)
    tabla = pd.DataFrame({"celda": np.arange(filas * columnas)})
    for cultivo, info in CAPAS.items():
        por_capa = [_parte_por_celda(_leer(clave_zona, capa), recuadro) for capa in info["capas"]]
        # Varias capas = varios períodos del mismo año: la celda cuenta si hubo cultivo en alguno
        junto = _parte_por_celda([g for capa in info["capas"] for g in _leer(clave_zona, capa)], recuadro)
        tabla[f"ref_{cultivo}"] = junto.ravel().round(3)
        if cultivo == "arroz":
            with np.errstate(invalid="ignore", divide="ignore"):
                ciclos = np.where(junto > 0.01, sum(por_capa) / junto, np.nan)
            tabla["arroz_ciclos"] = ciclos.ravel().round(2)
    partes = tabla[[f"ref_{c}" for c in CAPAS]]
    mayor = partes.idxmax(axis=1).str.replace("ref_", "", regex=False)
    tabla["cultivo_mapeado"] = mayor.where(partes.max(axis=1) >= PARTE_MINIMA, "")
    DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta_tabla(clave_zona), index=False)
    return tabla


# ---------------------------------------------------------------------------
# Lectura para la app (solo pandas)
# ---------------------------------------------------------------------------
def cargar(clave_zona: str) -> pd.DataFrame | None:
    ruta = ruta_tabla(clave_zona)
    return pd.read_csv(ruta, keep_default_na=False, na_values=[""]) if ruta.exists() else None


def resumen_del_terreno(tabla: pd.DataFrame, celdas: pd.DataFrame) -> dict | None:
    """Combina las fracciones del MAG según cuánto ocupa el terreno de cada celda."""
    cruce = celdas[["celda", "peso"]].merge(tabla, on="celda", how="left", validate="one_to_one")
    pesos = cruce["peso"]
    resultado = {}
    for cultivo in CAPAS:
        columna = f"ref_{cultivo}"
        partes = cruce[columna]
        validas = partes.notna()
        if validas.any():
            resultado[columna] = float(np.average(partes[validas], weights=pesos[validas]))
    if not resultado:
        return None

    con_ciclos = cruce["arroz_ciclos"].notna() & cruce["ref_arroz"].gt(0)
    if con_ciclos.any():
        peso_arroz = pesos[con_ciclos] * cruce.loc[con_ciclos, "ref_arroz"]
        resultado["arroz_ciclos"] = float(np.average(cruce.loc[con_ciclos, "arroz_ciclos"],
                                                     weights=peso_arroz))
    return resultado


def texto_del_terreno(fila: dict, minimo: float = 0.05, superficie: str = "del cuadro") -> list[str]:
    """Frases para la pantalla: qué cultivos tiene mapeados el MAG en la superficie analizada."""
    frases = []
    for cultivo, info in CAPAS.items():
        parte = pd.to_numeric(fila.get(f"ref_{cultivo}"), errors="coerce")
        if pd.isna(parte) or parte < minimo:
            continue
        frase = f"{NOMBRES[cultivo]}: {parte:.0%} {superficie}, según el mapa del MAG de {info['anio']}"
        ciclos = pd.to_numeric(fila.get("arroz_ciclos"), errors="coerce")
        if cultivo == "arroz" and not pd.isna(ciclos):
            frase += f" ({ciclos:.1f} períodos con arroz mapeado, en promedio)"
        frases.append(frase + ".")
    return frases


# ---------------------------------------------------------------------------
# Comparación con lo que ya tiene la tabla por celda (solo imprime)
# ---------------------------------------------------------------------------
def comparar(clave_zona: str) -> None:
    from .clima_relieve import cargar_celdas
    ref, celdas = cargar(clave_zona), cargar_celdas(clave_zona)
    t = celdas.merge(ref, on="celda")
    print(f"Zona {clave_zona}: {len(t)} celdas")
    for cultivo in CAPAS:
        parte = t[f"ref_{cultivo}"]
        print(f"  {NOMBRES[cultivo]:15s} en alguna parte: {(parte > 0.05).mean():6.1%} de las celdas | "
              f"en más de la mitad: {(parte >= 0.5).mean():6.1%} | hectáreas aprox.: "
              f"{parte.sum() * (PASO_CELDA_SEG * 30.87) ** 2 / 1e4:,.0f}")
    for cultivo in CAPAS:
        puras = t[t[f"ref_{cultivo}"] >= 0.6]
        if len(puras) < 30:
            continue
        print(f"\n  Celdas con {NOMBRES[cultivo]} en el 60 % o más ({len(puras)}):")
        if "cobertura" in puras:
            reparto = puras["cobertura"].value_counts(normalize=True).head(4)
            print("    tipo de terreno del modelo:", ", ".join(f"{k} {v:.0%}" for k, v in reparto.items()))
        for col in ("vegetacion", "encharcamiento", "agua_invierno", "humedad"):
            if col in puras and puras[col].notna().any():
                print(f"    {col:15s} mediana {puras[col].median():.3f}   (toda la zona: {t[col].median():.3f})")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ZONAS:
        print("Uso: python -m src.cultivos_mapeados ZONA [descargar|tabla|comparar]   Zonas:", ", ".join(ZONAS))
        sys.exit(1)
    zona, accion = sys.argv[1], sys.argv[2]
    if accion == "descargar":
        descargar(zona)
    elif accion == "tabla":
        tb = construir_tabla(zona)
        print(f"Guardado {ruta_tabla(zona)} ({len(tb)} celdas)")
        print(tb["cultivo_mapeado"].replace("", "(ninguno)").value_counts().to_string())
    elif accion == "comparar":
        comparar(zona)
