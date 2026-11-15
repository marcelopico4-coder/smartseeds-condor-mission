"""
¿Puede el radar reconocer QUÉ cultivo hay? Prueba medida contra los mapas del MAG.

Es un experimento, no cambia la app ni la tabla por celda:

    python -m src.identificar_cultivo ZONA        # imprime el acierto y guarda datos/procesados/cultivo_evaluacion_ZONA.json

Cómo se mide (igual que src/cobertura.py):
  - Etiquetas: celdas donde un cultivo del mapa del MAG ocupa el 60 % o más
    (`datos/procesados/cultivos_mag_ZONA.csv`), y celdas sin ningún cultivo mapeado ("otro").
  - Rasgos: los del radar NISAR de cobertura.py + pendiente y, si la zona tiene Sentinel-1 de
    invierno (`invierno_ZONA.npz`), la señal VV de cada mes de enero a mayo.
  - Bosque aleatorio. Cada celda la clasifica un modelo que NO vio su bloque de 30 x 30 celdas.

Ojo al leer el resultado: arroz, maíz y soya del MAG son de 2025 y el radar es de 2026.
"""
from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pandas as pd

from . import cultivos_mapeados as cm
from .clima_relieve import ruta_celdas
from .cobertura import LADO_BLOQUE, RASGOS, rasgos_de_zona
from .config import DATOS_PROCESADOS, ZONAS, forma_rejilla

PUREZA = 0.6             # parte mínima de la celda para tomarla como ejemplo de un cultivo
SIN_CULTIVO = 0.05       # por debajo de esto en todos los cultivos, la celda es "otro"
MINIMO_POR_CLASE = 100   # con menos celdas no se intenta reconocer ese cultivo


def rasgos_invierno(clave_zona: str) -> pd.DataFrame | None:
    """Señal VV de Sentinel-1 por mes (enero a mayo), en dB, y cuánto cambia. None si no hay serie."""
    ruta = DATOS_PROCESADOS / f"invierno_{clave_zona}.npz"
    if not ruta.exists():
        return None
    with np.load(ruta) as s, warnings.catch_warnings(), np.errstate(invalid="ignore", divide="ignore"):
        warnings.simplefilter("ignore", RuntimeWarning)
        fechas, vv, agua = s["fechas"].astype(str), s["vv"], s["agua"]
        vv_db = 10 * np.log10(np.clip(vv, 1e-6, None)) if np.nanmax(vv) > 0 and np.nanmin(vv) >= 0 else vv
        meses = np.array([f[5:7] for f in fechas])
        datos = {f"vv_mes_{m}": np.nanmean(vv_db[meses == m], axis=0).ravel()
                 for m in ("01", "02", "03", "04", "05") if (meses == m).any()}
        datos["vv_cambio"] = np.nanstd(vv_db, axis=0).ravel()
        datos["vv_min"] = np.nanmin(vv_db, axis=0).ravel()
        datos["agua_inv"] = np.nanmean(agua, axis=0).ravel()
    return pd.DataFrame(datos)


def preparar(clave_zona: str) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Tabla con rasgos, etiqueta y bloque. Devuelve (tabla, rasgos NISAR, rasgos Sentinel-1)."""
    _, columnas, _ = forma_rejilla(ZONAS[clave_zona]["recuadro"])
    t = rasgos_de_zona(clave_zona)
    t["celda"] = np.arange(len(t))
    t = t.merge(pd.read_csv(ruta_celdas(clave_zona))[["celda", "pendiente"]], on="celda")
    de_nisar = RASGOS + ["pendiente"]
    de_s1 = []
    inv = rasgos_invierno(clave_zona)
    if inv is not None:
        de_s1 = list(inv.columns)
        t = t.join(inv)
    ref = cm.cargar(clave_zona)
    partes = ref[[f"ref_{c}" for c in cm.CAPAS]]
    etiqueta = partes.idxmax(axis=1).str.replace("ref_", "", regex=False)
    etiqueta = etiqueta.where(partes.max(axis=1) >= PUREZA)
    etiqueta = etiqueta.mask(partes.max(axis=1) < SIN_CULTIVO, "otro")
    t = t.merge(pd.DataFrame({"celda": ref["celda"], "etiqueta": etiqueta}), on="celda")
    t["bloque"] = (t["celda"] // columnas // LADO_BLOQUE) * 100 + t["celda"] % columnas // LADO_BLOQUE
    return t, de_nisar, de_s1


def medir(t: pd.DataFrame, entradas: list[str], semilla: int = 0) -> dict:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import balanced_accuracy_score
    from sklearn.model_selection import GroupKFold, cross_val_predict
    sirve = t[entradas].notna().all(axis=1) & t["etiqueta"].notna()
    cuantas = t.loc[sirve, "etiqueta"].value_counts()
    sirve &= t["etiqueta"].isin(cuantas[cuantas >= MINIMO_POR_CLASE].index)
    x, y = t.loc[sirve, entradas], t.loc[sirve, "etiqueta"]
    modelo = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight="balanced",
                                    n_jobs=-1, random_state=semilla)
    dicho = pd.Series(cross_val_predict(modelo, x, y, groups=t.loc[sirve, "bloque"],
                                        cv=GroupKFold(n_splits=5)), index=y.index)
    pesos = modelo.fit(x, y).feature_importances_
    return {
        "celdas": int(len(y)),
        "acierto": round(float((y == dicho).mean()), 3),
        "acierto_promedio_por_clase": round(float(balanced_accuracy_score(y, dicho)), 3),
        "acierto_diciendo_siempre_lo_mas_comun": round(float(y.value_counts(normalize=True).iloc[0]), 3),
        "por_clase": {c: {"celdas": int((y == c).sum()),
                          "las_encuentra": round(float((dicho[y == c] == c).mean()), 3),
                          "acierta_cuando_la_dice": (round(float((y[dicho == c] == c).mean()), 3)
                                                     if (dicho == c).any() else None),
                          "se_confunde_con": (dicho[(y == c) & (dicho != c)].value_counts(normalize=True)
                                              .round(2).head(2).to_dict())}
                      for c in sorted(y.unique())},
        "rasgos_que_mas_pesan": {r: round(float(v), 3) for r, v in
                                 sorted(zip(entradas, pesos), key=lambda par: -par[1])[:6]},
    }


def probar(clave_zona: str) -> dict:
    t, de_nisar, de_s1 = preparar(clave_zona)
    resultado = {"zona": clave_zona, "etiquetas": "MAG, Estimaciones de cultivos 1:25.000 (2022 y 2025)",
                 "solo_nisar": medir(t, de_nisar)}
    if de_s1:
        resultado["nisar_y_sentinel1"] = medir(t, de_nisar + de_s1)
    ruta = DATOS_PROCESADOS / f"cultivo_evaluacion_{clave_zona}.json"
    ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    for nombre in ("solo_nisar", "nisar_y_sentinel1"):
        if nombre not in resultado:
            continue
        r = resultado[nombre]
        print(f"\n[{clave_zona}] {nombre}: {r['celdas']} celdas | acierto {r['acierto']:.0%} "
              f"(siempre lo más común: {r['acierto_diciendo_siempre_lo_mas_comun']:.0%}) | "
              f"promedio por clase {r['acierto_promedio_por_clase']:.0%}")
        for c, d in r["por_clase"].items():
            cuando = "—" if d["acierta_cuando_la_dice"] is None else f"{d['acierta_cuando_la_dice']:.0%}"
            print(f"   {c:15s} {d['celdas']:6d} celdas | las encuentra {d['las_encuentra']:.0%} | "
                  f"cuando lo dice acierta {cuando} | se confunde con {d['se_confunde_con']}")
        print("   rasgos que más pesan:", r["rasgos_que_mas_pesan"])
    return resultado


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ZONAS:
        print("Uso: python -m src.identificar_cultivo ZONA     Zonas:", ", ".join(ZONAS))
        sys.exit(1)
    probar(sys.argv[1])
