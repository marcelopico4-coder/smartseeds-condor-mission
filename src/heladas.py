"""
Riesgo de helada por celda (para las zonas de la Sierra).

    python -m src.heladas ZONA      # agrega `temp_minima` y `helada` a datos/procesados/celdas_ZONA.csv

Ejecutarlo DESPUÉS de `python -m src.clima_relieve ZONA` (ese comando escribe la tabla de nuevo).

Cómo se calcula:
  - NASA POWER da la temperatura mínima media de cada mes (T2M_MIN) para un cuadro de ~50 km.
  - Se lleva a la altura real de cada celda con el mismo gradiente que la temperatura media
    (6,5 °C por cada 1.000 m).
  - En los fondos planos más bajos que su entorno ("hondonadas") el aire frío se queda de noche:
    ahí se resta hasta ENFRIAMIENTO_HONDONADA grados.
  - `temp_minima` = esa temperatura en el mes más frío del año.
  - `helada` = riesgo de 0 a 1: 0 si la mínima media es de 5 °C o más, 1 si es de -1 °C o menos.
    (Una mínima MEDIA de 3 °C ya quiere decir varias noches bajo cero en el mes.)

Límites que hay que declarar: es el promedio de varios años de un modelo mundial, no una medición;
vale para el mes más frío aunque un cultivo corto se pueda sembrar esquivando ese mes; y los
números de abajo (5 °C, 6 °C, 1,5 °C, 60 m, 15°, 9 cuadros) son valores iniciales sin calibrar.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
import requests

from .clima_relieve import GRADIENTE_C_POR_M, MESES, URL_POWER, cargar_celdas, ruta_celdas
from .config import ZONAS, forma_rejilla

MINIMA_SIN_HELADAS_C = 5.0       # mínima media del mes desde la cual casi no hay heladas
GRADOS_HASTA_RIESGO_TOTAL = 6.0  # el riesgo llega a 1 cuando la mínima media baja a 5 - 6 = -1 °C
ENFRIAMIENTO_HONDONADA = 1.5     # °C de frío extra en el fondo plano de una hondonada
DESNIVEL_HONDONADA_M = 60        # metros por debajo del entorno para contar como hondonada completa
PENDIENTE_SIN_HONDONADA = 15     # grados: en una ladera así el aire frío escurre y no se queda
VENTANA_HONDONADA = 9            # cuadros de lado del "entorno" (9 x ~250 m ≈ 2 km)


def minimas_power(lat: float, lon: float) -> dict:
    """Temperatura mínima media de cada mes (NASA POWER) y la altura media de su cuadro."""
    params = {"parameters": "T2M_MIN", "community": "AG",
              "longitude": round(lon, 3), "latitude": round(lat, 3), "format": "JSON"}
    r = requests.get(URL_POWER, params=params, timeout=60)
    r.raise_for_status()
    datos = r.json()
    par = datos["properties"]["parameter"]["T2M_MIN"]
    coords = datos.get("geometry", {}).get("coordinates", [])
    return {"minimas": [float(par[m]) for m in MESES],
            "altura_power": float(coords[2]) if len(coords) > 2 else None}


def indice_hondonada(altura: np.ndarray, pendiente: np.ndarray, ventana: int = VENTANA_HONDONADA) -> np.ndarray:
    """De 0 a 1 por cuadro: 1 = fondo plano claramente más bajo que lo que tiene alrededor.

    `altura` y `pendiente` son matrices (filas x columnas) de la zona.
    """
    medio = ventana // 2
    relleno = np.pad(altura, medio, mode="edge")
    suma = np.zeros_like(altura, dtype=float)
    for df in range(ventana):                       # promedio del entorno, solo con numpy
        for dc in range(ventana):
            suma += relleno[df:df + altura.shape[0], dc:dc + altura.shape[1]]
    desnivel = suma / ventana ** 2 - altura          # positivo si el cuadro está más bajo que su entorno
    return np.clip(desnivel / DESNIVEL_HONDONADA_M, 0, 1) * np.clip(1 - pendiente / PENDIENTE_SIN_HONDONADA, 0, 1)


def riesgo_de_helada(temp_minima):
    """Riesgo de 0 a 1 a partir de la mínima media del mes más frío (número o arreglo)."""
    return np.clip((MINIMA_SIN_HELADAS_C - np.asarray(temp_minima, dtype=float)) / GRADOS_HASTA_RIESGO_TOTAL, 0, 1)


def minima_por_celda(minima_mes_mas_frio: float, altura_power: float, altura, hondonada):
    """Mínima del mes más frío llevada a la altura de cada celda y enfriada en las hondonadas."""
    return (minima_mes_mas_frio - GRADIENTE_C_POR_M * (np.asarray(altura, dtype=float) - altura_power)
            - ENFRIAMIENTO_HONDONADA * np.asarray(hondonada, dtype=float))


def agregar_a_tabla(clave_zona: str, clima: dict | None = None) -> pd.DataFrame:
    """Escribe `temp_minima` y `helada` en la tabla por celda de la zona."""
    tabla = cargar_celdas(clave_zona)
    if tabla is None:
        raise SystemExit(f"Falta la tabla de {clave_zona}: ejecuta antes python -m src.clima_relieve {clave_zona}")
    lon_min, lat_min, lon_max, lat_max = ZONAS[clave_zona]["recuadro"]
    clima = clima or minimas_power((lat_min + lat_max) / 2, (lon_min + lon_max) / 2)
    filas, columnas, _ = forma_rejilla(ZONAS[clave_zona]["recuadro"])
    altura = tabla["altura"].to_numpy(float).reshape(filas, columnas)
    pendiente = tabla["pendiente"].to_numpy(float).reshape(filas, columnas)
    hondonada = indice_hondonada(altura, pendiente)
    minima = minima_por_celda(min(clima["minimas"]), clima["altura_power"], altura, hondonada)
    tabla["temp_minima"] = minima.ravel().round(1)
    tabla["helada"] = riesgo_de_helada(minima).ravel().round(2)
    tabla.to_csv(ruta_celdas(clave_zona), index=False)
    return tabla


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ZONAS:
        raise SystemExit(f"Uso: python -m src.heladas ZONA   (zonas: {', '.join(ZONAS)})")
    t = agregar_a_tabla(sys.argv[1])
    con_riesgo = (t["helada"] >= 0.3).mean()
    print(f"Listo: mínima del mes más frío entre {t['temp_minima'].min():.1f} y {t['temp_minima'].max():.1f} °C; "
          f"{con_riesgo:.0%} de las celdas con riesgo de helada de 30 % o más -> {ruta_celdas(sys.argv[1])}")
