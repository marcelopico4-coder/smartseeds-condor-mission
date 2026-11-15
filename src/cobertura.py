"""
Tipo de terreno según el radar (modelo entrenado con las pasadas de NISAR).

Idea: cada celda se describe por CÓMO se comportó el radar en todas las pasadas
(qué tan brillante se ve, cuánto cambió de una fecha a otra, cuántas veces tuvo agua).

Hay dos formas de entrenar, y `python -m src.cobertura entrenar` elige sola:

  A. CON MAPA DE REFERENCIA (la que se usa si existe datos/procesados/referencia_worldcover_ZONA.csv,
     que crea `python recolectar_referencia.py descargar worldcover`).
     Un bosque aleatorio aprende, con el mapa ESA WorldCover de 2021, cómo se ve en el radar cada
     tipo de terreno, y luego clasifica todas las celdas con el radar de 2026. Solo aprende de las
     celdas donde un tipo ocupa al menos el 60 % de la celda. El acierto se mide en bloques de
     ~7,5 km que el modelo no vio y se guarda en datos/procesados/cobertura_evaluacion.json.
     Encima van tres reglas físicas del radar: agua en la mitad o más de las pasadas = "agua";
     agua en el 10 % o más = "inundable"; y nada con más de 10° de pendiente es "construcciones"
     (las laderas brillan en el radar como si fueran techos).

  B. SIN REFERENCIA (la primera versión). Un modelo de agrupamiento (KMeans) junta las celdas que
     se comportan parecido, sin que nadie le diga qué es cada cosa. Después cada grupo recibe un
     nombre con reglas físicas del radar:

    construcciones     HH muy alto y mucho mayor que HV, sin cambios (paredes y techos)
    agua               agua en la mayoría de las pasadas (ríos, lagunas)
    inundable          agua en varias pasadas (arrozales, bajos que se encharcan)
    cultivo_activo     la señal cambia mucho entre fechas (siembra, crecimiento, cosecha)
    vegetacion_densa   HV alto y estable (árboles, cultivos permanentes, bosque)
    vegetacion_baja    HV bajo y estable (pasto, rastrojo, suelo con poca vegetación)

    python -m src.cobertura entrenar     # entrena con todas las zonas que tengan serie
                                         # y escribe la columna `cobertura` en cada tabla

Qué es y qué NO es:
  - La referencia es un mapa hecho con satélites (2021), no visitas al campo, y tiene sus
    propios errores (exactitud mundial 76,7 %). No hay datos de campo del equipo.
  - No distingue el cultivo (papa, maíz, cacao...). Solo el tipo de cobertura. Tampoco separa
    un bosque de un cultivo de árboles (cacao, palma, banano): los dos son "árboles".
  - Con celdas de ~250 m detecta las zonas más construidas, no casas sueltas.
  - Entrenar necesita scikit-learn (entorno de desarrollo). La app NO lo necesita:
    solo lee la columna ya calculada.
"""
from __future__ import annotations

import sys
import warnings
from datetime import date

import numpy as np
import pandas as pd

import json

from .clima_relieve import ruta_celdas
from .config import DATOS_PROCESADOS, ZONAS, forma_rejilla
from .nisar import a_db, ruta_serie

RUTA_MODELO = DATOS_PROCESADOS / "modelo_cobertura.npz"
RUTA_EVALUACION = DATOS_PROCESADOS / "cobertura_evaluacion.json"
N_GRUPOS = 8

# --- Entrenamiento con mapa de referencia -----------------------------------
FUENTE_REFERENCIA = "worldcover"
NOMBRE_REFERENCIA = "ESA WorldCover 2021 v200"
# clase del mapa de referencia -> clase de la app
CLASE_DE_REFERENCIA = {"arboles": "vegetacion_densa", "manglar": "vegetacion_densa",
                       "arbustos": "vegetacion_baja", "pasto": "vegetacion_baja",
                       "suelo_desnudo": "vegetacion_baja", "cultivo": "cultivo_activo",
                       "construido": "construcciones", "agua": "agua", "humedal": "inundable"}
PUREZA_MINIMA = 0.6              # para aprender: celdas donde una clase ocupa al menos el 60 %
MINIMO_POR_CLASE = 50            # con menos celdas que estas no se aprende una clase
LADO_BLOQUE = 30                 # bloques de 30 x 30 celdas (~7,5 km) para medir el acierto
PENDIENTE_MAX_CONSTRUCCION = 10  # grados: por encima de esto una celda no se llama "construcciones"
# Decirle a un agricultor que su terreno es un pueblo es el error más molesto: solo se marca
# "construcciones" si el modelo le da al menos esta probabilidad (si no, la clase que sigue).
PROBABILIDAD_MIN_CONSTRUCCION = 0.75

# clave -> (nombre para mostrar, explicación sencilla, ¿se puede cultivar ahí?)
CLASES = {
    "construcciones": ("Zona construida",
                       "El radar ve paredes y techos: casas, galpones o un pueblo.", False),
    "agua": ("Agua casi permanente",
             "Hubo agua en la mayoría de las pasadas: río, laguna o estero.", False),
    "inundable": ("Terreno que se inunda",
                  "Tiene agua parte del tiempo: arrozal inundado, humedal o bajo que se "
                  "encharca.", True),
    "cultivo_activo": ("Cultivo de ciclo corto",
                       "Terreno de cultivos que se siembran y se cosechan dentro del año, "
                       "como el arroz o el maíz.", True),
    "vegetacion_densa": ("Árboles o vegetación densa",
                         "Árboles: puede ser bosque o un cultivo permanente como cacao, palma "
                         "o banano. Desde el radar no se distinguen.", True),
    "vegetacion_baja": ("Pasto o vegetación baja",
                        "Pasto, matorral, rastrojo o suelo con poca vegetación.", True),
}

# Umbrales para nombrar cada grupo (valores iniciales, salidos de mirar los grupos de
# Daule y Santo Domingo el 14 nov; sin calibrar con datos de campo).
AGUA_PERMANENTE = 0.5        # parte de las pasadas con agua
AGUA_INUNDABLE = 0.10
HH_CONSTRUCCION_DB = -3.5    # HH promedio por encima de esto...
HH_MENOS_HV_CONSTRUCCION = 9.0   # ...y HH mucho mayor que HV = rebote en paredes
CAMBIO_HH_DB = 2.0           # variación entre fechas que indica cultivo en actividad
CAMBIO_HV_DB = 1.5
HV_DENSA_DB = -14.5          # HV promedio de vegetación alta

RASGOS = ["hh_media", "hv_media", "hh_cambio", "hv_cambio", "hh_min", "agua", "hh_menos_hv"]


def rasgos_de_serie(hh, hv, agua) -> pd.DataFrame:
    """Rasgos de cada celda a partir de la serie [fecha, fila, columna] (una fila por celda).

    hh_media, hv_media   brillo promedio en dB
    hh_cambio, hv_cambio cuánto varió entre fechas (desviación estándar, en dB)
    hh_min               la fecha más oscura (dB)
    agua                 parte de las pasadas con agua (0 a 1)
    hh_menos_hv          diferencia HH - HV (dB): alta en construcciones
    """
    with warnings.catch_warnings(), np.errstate(invalid="ignore", divide="ignore"):
        warnings.simplefilter("ignore", RuntimeWarning)          # celdas sin ningún dato
        hh_db, hv_db = a_db(hh), a_db(hv)
        hh_db, hv_db = np.where(np.isnan(hh), np.nan, hh_db), np.where(np.isnan(hv), np.nan, hv_db)
        rasgos = {
            "hh_media": np.nanmean(hh_db, axis=0), "hv_media": np.nanmean(hv_db, axis=0),
            "hh_cambio": np.nanstd(hh_db, axis=0), "hv_cambio": np.nanstd(hv_db, axis=0),
            "hh_min": np.nanmin(hh_db, axis=0), "agua": np.nanmean(agua, axis=0),
            "hh_menos_hv": np.nanmean(hh_db - hv_db, axis=0),
        }
    return pd.DataFrame({nombre: valores.ravel() for nombre, valores in rasgos.items()})[RASGOS]


def rasgos_de_zona(clave_zona: str) -> pd.DataFrame:
    with np.load(ruta_serie(clave_zona)) as s:
        return rasgos_de_serie(s["hh"], s["hv"], s["agua"])


def nombrar(centro: dict) -> str:
    """Nombre de un grupo según el valor promedio de sus rasgos (reglas físicas del radar)."""
    if centro["agua"] >= AGUA_PERMANENTE:
        return "agua"
    if centro["agua"] >= AGUA_INUNDABLE:
        return "inundable"
    if centro["hh_media"] >= HH_CONSTRUCCION_DB and centro["hh_menos_hv"] >= HH_MENOS_HV_CONSTRUCCION:
        return "construcciones"
    if centro["hh_cambio"] >= CAMBIO_HH_DB or centro["hv_cambio"] >= CAMBIO_HV_DB:
        return "cultivo_activo"
    if centro["hv_media"] >= HV_DENSA_DB:
        return "vegetacion_densa"
    return "vegetacion_baja"


def clasificar(rasgos: pd.DataFrame, modelo: dict) -> np.ndarray:
    """Clase de cada celda con un modelo ya entrenado (solo numpy: busca el grupo más parecido).

    Devuelve un arreglo de textos; "" donde el radar no tiene datos.
    """
    con_dato = rasgos[RASGOS].notna().all(axis=1).to_numpy()
    x = (rasgos.loc[con_dato, RASGOS].to_numpy() - modelo["media"]) / modelo["escala"]
    distancia = ((x[:, None, :] - modelo["centros"][None, :, :]) ** 2).sum(axis=2)
    clases = np.full(len(rasgos), "", dtype=object)
    clases[con_dato] = np.asarray(modelo["nombres"], dtype=object)[distancia.argmin(axis=1)]
    return clases


def es_cultivable(clases: pd.Series) -> pd.Series:
    """True en las celdas donde se puede cultivar (o donde no se sabe el tipo de terreno)."""
    no_cultivables = [clave for clave, (_, _, cultivable) in CLASES.items() if not cultivable]
    return ~clases.isin(no_cultivables)


def composicion(celdas: pd.DataFrame) -> list[dict] | None:
    """De qué está hecho un terreno según el modelo: lista ordenada de mayor a menor.

    Cada elemento: {"clase", "nombre", "explicacion", "cultivable", "fraccion"}. Si la tabla
    trae la columna `peso`, cada celda cuenta según cuánto la ocupa el terreno.
    Devuelve None si las celdas no tienen tipo de terreno (zona sin modelo o sin radar).
    """
    if "cobertura" not in celdas:
        return None
    pesos = celdas["peso"] if "peso" in celdas else pd.Series(1.0, index=celdas.index)
    con_tipo = celdas["cobertura"].isin(list(CLASES))
    total = pesos[con_tipo].sum()
    if total <= 0:
        return None
    partes = pesos[con_tipo].groupby(celdas.loc[con_tipo, "cobertura"]).sum() / total
    return [{"clase": clase, "nombre": CLASES[clase][0], "explicacion": CLASES[clase][1],
             "cultivable": CLASES[clase][2], "fraccion": float(fraccion)}
            for clase, fraccion in partes.sort_values(ascending=False).items()]


def cargar_modelo() -> dict | None:
    if not RUTA_MODELO.exists():
        return None
    with np.load(RUTA_MODELO) as m:
        return {"media": m["media"], "escala": m["escala"], "centros": m["centros"],
                "nombres": [str(n) for n in m["nombres"]]}


def ruta_referencia(clave_zona: str):
    return DATOS_PROCESADOS / f"referencia_{FUENTE_REFERENCIA}_{clave_zona}.csv"


def cargar_evaluacion() -> dict | None:
    """Cómo se entrenó el modelo y cuánto acierta (None si se entrenó sin referencia)."""
    if not RUTA_EVALUACION.exists():
        return None
    return json.loads(RUTA_EVALUACION.read_text(encoding="utf-8"))


def texto_evaluacion(evaluacion: dict | None = None) -> str:
    """Frase para la app: cómo se hizo el modelo y cuánto acierta."""
    evaluacion = cargar_evaluacion() if evaluacion is None else evaluacion
    if not evaluacion:
        return ("Lo calcula un modelo automático que agrupa los terrenos por cómo se ven en las pasadas "
                "del radar. No se comprobó en el campo y no distingue qué cultivo es.")
    return (f"Lo calcula un modelo que aprendió, con el mapa {evaluacion['referencia']} de la Agencia "
            "Espacial Europea, cómo se ve cada tipo de terreno en las pasadas del radar NISAR de 2026. "
            f"En zonas que no vio al aprender coincide con ese mapa en el {evaluacion['acierto']:.0%} de "
            "los cuadros con un tipo dominante incluidos en la evaluación. "
            "No se comprobó en el campo y no distingue qué cultivo es.")


def aplicar_reglas(probabilidad: pd.DataFrame, agua: np.ndarray, pendiente: np.ndarray) -> np.ndarray:
    """Clase final de cada celda: la más probable según el modelo, corregida con reglas físicas.

    `probabilidad` tiene una columna por clase. Reglas, en este orden:
      1. Con más de PENDIENTE_MAX_CONSTRUCCION grados, o con menos probabilidad que
         PROBABILIDAD_MIN_CONSTRUCCION, no puede ser "construcciones".
      2. Agua en AGUA_PERMANENTE (la mitad) o más de las pasadas -> "agua".
      3. Agua en AGUA_INUNDABLE (10 %) o más de las pasadas -> "inundable".
    """
    probabilidad = probabilidad.copy()
    if "construcciones" in probabilidad:
        probabilidad.loc[np.asarray(pendiente) > PENDIENTE_MAX_CONSTRUCCION, "construcciones"] = 0.0
        probabilidad.loc[probabilidad["construcciones"] < PROBABILIDAD_MIN_CONSTRUCCION, "construcciones"] = 0.0
    clases = probabilidad.columns.to_numpy()[probabilidad.to_numpy().argmax(axis=1)].astype(object)
    agua = np.asarray(agua, dtype=float)
    clases[agua >= AGUA_INUNDABLE] = "inundable"
    clases[agua >= AGUA_PERMANENTE] = "agua"
    return clases


def entrenar_con_referencia(zonas=None, semilla: int = 0) -> dict:
    """Entrena con el mapa de referencia, mide el acierto y escribe la columna `cobertura`.

    Las zonas sin archivo de referencia no enseñan nada al modelo, pero también se clasifican.
    Las celdas que sirvieron para aprender reciben la clase que les dio un modelo que NO vio
    su bloque: así el acierto medido vale para todo el mapa.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import balanced_accuracy_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    zonas = [z for z in (zonas or ZONAS) if ruta_serie(z).exists() and ruta_celdas(z).exists()]
    partes = []
    for numero, z in enumerate(zonas):
        _, columnas, _ = forma_rejilla(ZONAS[z]["recuadro"])
        t = rasgos_de_zona(z)
        t["celda"] = np.arange(len(t))
        t = t.merge(pd.read_csv(ruta_celdas(z))[["celda", "pendiente"]], on="celda", how="inner")
        if ruta_referencia(z).exists():
            t = t.merge(pd.read_csv(ruta_referencia(z))[["celda", "ref_clase", "ref_pureza", "ref_estable"]],
                        on="celda", how="left")
            t["clase_ref"] = t["ref_clase"].map(CLASE_DE_REFERENCIA)
        else:
            t["clase_ref"], t["ref_pureza"], t["ref_estable"] = None, np.nan, False
        t["bloque"] = numero * 10_000 + (t["celda"] // columnas // LADO_BLOQUE) * 100 \
            + t["celda"] % columnas // LADO_BLOQUE
        t["zona"] = z
        partes.append(t)
    if not partes:
        raise RuntimeError("Ninguna zona tiene serie de radar y tabla por celda.")
    todo = pd.concat(partes, ignore_index=True)
    entradas = RASGOS + ["pendiente"]
    con_radar = todo[entradas].notna().all(axis=1)
    aprende = (con_radar & todo["clase_ref"].notna() & (todo["ref_pureza"] >= PUREZA_MINIMA)
               & todo["ref_estable"].fillna(False).astype(bool))
    cuantas = todo.loc[aprende, "clase_ref"].value_counts()
    aprende &= todo["clase_ref"].isin(cuantas[cuantas >= MINIMO_POR_CLASE].index)
    if todo.loc[aprende, "clase_ref"].nunique() < 2 or todo.loc[aprende, "bloque"].nunique() < 2:
        raise RuntimeError("No hay suficientes celdas de referencia para entrenar.")

    def nuevo_modelo():
        return RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight="balanced",
                                      n_jobs=-1, random_state=semilla)

    x, y = todo.loc[aprende, entradas], todo.loc[aprende, "clase_ref"]
    nombres = sorted(y.unique())
    cortes = GroupKFold(n_splits=min(5, todo.loc[aprende, "bloque"].nunique()))
    probabilidad = pd.DataFrame(0.0, index=todo.index, columns=nombres)
    # celdas que enseñan: probabilidad de un modelo que no vio su bloque
    probabilidad.loc[aprende] = cross_val_predict(nuevo_modelo(), x, y, groups=todo.loc[aprende, "bloque"],
                                                  cv=cortes, method="predict_proba")
    # las demás: modelo entrenado con todas las celdas de referencia
    modelo = nuevo_modelo().fit(x, y)
    resto = con_radar & ~aprende
    probabilidad.loc[resto] = modelo.predict_proba(todo.loc[resto, entradas])
    todo["cobertura"] = None
    todo.loc[con_radar, "cobertura"] = aplicar_reglas(
        probabilidad[con_radar], todo.loc[con_radar, "agua"], todo.loc[con_radar, "pendiente"])

    # Acierto, solo en las celdas de referencia (cada una vista por un modelo que no la conocía)
    real, dicho = y, todo.loc[aprende, "cobertura"]
    es_cultivo, dice_cultivo = real == "cultivo_activo", dicho == "cultivo_activo"
    evaluacion = {
        "referencia": NOMBRE_REFERENCIA, "fecha": str(date.today()), "zonas": zonas,
        "celdas_para_aprender": int(aprende.sum()), "celdas_clasificadas": int(con_radar.sum()),
        "acierto": round(float((real == dicho).mean()), 3),
        "acierto_promedio_por_clase": round(float(balanced_accuracy_score(real, dicho)), 3),
        "acierto_diciendo_siempre_lo_mas_comun": round(float(real.value_counts(normalize=True).iloc[0]), 3),
        "acierto_por_zona": {z: round(float((real[todo.loc[aprende, "zona"] == z]
                                             == dicho[todo.loc[aprende, "zona"] == z]).mean()), 3)
                             for z in zonas if (todo.loc[aprende, "zona"] == z).any()},
        "por_clase": {c: {"celdas_de_referencia": int((real == c).sum()),
                          "las_encuentra": round(float((dicho[real == c] == c).mean()), 3),
                          "acierta_cuando_la_dice": (round(float((real[dicho == c] == c).mean()), 3)
                                                     if (dicho == c).any() else None)}
                      for c in nombres},
        "cultivo_de_ciclo_corto_si_o_no": round(float((es_cultivo == dice_cultivo).mean()), 3),
        "rasgos_que_mas_pesan": {r: round(float(v), 3) for r, v in
                                 sorted(zip(entradas, modelo.feature_importances_), key=lambda par: -par[1])},
    }
    RUTA_EVALUACION.write_text(json.dumps(evaluacion, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Modelo entrenado con {int(aprende.sum())} celdas de referencia ({NOMBRE_REFERENCIA}) "
          f"de: {', '.join(zonas)}")
    print(f"Acierto en bloques que el modelo no vio: {evaluacion['acierto']:.0%} (decir siempre la clase "
          f"más común daría {evaluacion['acierto_diciendo_siempre_lo_mas_comun']:.0%}); "
          f"promedio por clase {evaluacion['acierto_promedio_por_clase']:.0%}")
    for c, d in evaluacion["por_clase"].items():
        cuando = "—" if d["acierta_cuando_la_dice"] is None else f"{d['acierta_cuando_la_dice']:.0%}"
        print(f"   {c:17s} encuentra el {d['las_encuentra']:.0%} de {d['celdas_de_referencia']} celdas; "
              f"cuando la dice, acierta el {cuando}")
    for z in zonas:
        de_zona = todo[todo["zona"] == z]
        tabla = pd.read_csv(ruta_celdas(z))
        tabla["cobertura"] = tabla["celda"].map(de_zona.set_index("celda")["cobertura"])
        tabla.to_csv(ruta_celdas(z), index=False)
        reparto = de_zona["cobertura"].dropna().value_counts(normalize=True).mul(100).round(1)
        print(f"{z}:", ", ".join(f"{c} {v} %" for c, v in reparto.items()))
    return evaluacion


def entrenar(zonas=None, n_grupos: int = N_GRUPOS, semilla: int = 0) -> dict:
    """Entrena SIN referencia (KMeans) con todas las zonas que tengan serie de radar y lo guarda.

    También escribe la columna `cobertura` en la tabla por celda de cada zona.
    Volver a ejecutarlo cuando haya pasadas nuevas o una zona nueva.
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    zonas = [z for z in (zonas or ZONAS) if ruta_serie(z).exists()]
    if not zonas:
        raise RuntimeError("Ninguna zona tiene serie de radar. Ejecuta antes `python -m src.nisar ZONA procesar`.")
    por_zona = {z: rasgos_de_zona(z) for z in zonas}
    todo = pd.concat(por_zona.values(), ignore_index=True)
    con_dato = todo.notna().all(axis=1)
    escalador = StandardScaler().fit(todo[con_dato])
    kmeans = KMeans(n_clusters=n_grupos, n_init=10, random_state=semilla).fit(
        escalador.transform(todo[con_dato]))
    centros_reales = escalador.inverse_transform(kmeans.cluster_centers_)
    nombres = [nombrar(dict(zip(RASGOS, c))) for c in centros_reales]
    modelo = {"media": escalador.mean_, "escala": escalador.scale_,
              "centros": kmeans.cluster_centers_, "nombres": nombres}
    RUTA_EVALUACION.unlink(missing_ok=True)      # este modelo no tiene medida de acierto
    np.savez_compressed(RUTA_MODELO, media=modelo["media"], escala=modelo["escala"],
                        centros=modelo["centros"], nombres=np.array(nombres),
                        rasgos=np.array(RASGOS), zonas=np.array(zonas),
                        fecha=str(date.today()), celdas=int(con_dato.sum()))

    resumen = pd.DataFrame(centros_reales, columns=RASGOS).round(2)
    resumen.insert(0, "clase", nombres)
    resumen["celdas_%"] = (pd.Series(kmeans.labels_).value_counts(normalize=True)
                           .sort_index() * 100).round(1).to_numpy()
    print(f"Modelo entrenado con {int(con_dato.sum())} celdas de: {', '.join(zonas)}")
    print(resumen.to_string(index=False))
    for z in zonas:
        clases = clasificar(por_zona[z], modelo)
        if ruta_celdas(z).exists():
            tabla = pd.read_csv(ruta_celdas(z))
            tabla["cobertura"] = np.where(clases == "", None, clases)
            tabla.to_csv(ruta_celdas(z), index=False)
        reparto = pd.Series(clases[clases != ""]).value_counts(normalize=True).mul(100).round(1)
        print(f"\n{z}:", ", ".join(f"{c} {v} %" for c, v in reparto.items()))
    return modelo


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "entrenar":
        if any(ruta_referencia(z).exists() for z in ZONAS):
            entrenar_con_referencia()
        else:
            print("No hay mapa de referencia (python recolectar_referencia.py descargar worldcover): "
                  "se entrena sin referencia.")
            entrenar()
    else:
        print("Uso: python -m src.cobertura entrenar")
