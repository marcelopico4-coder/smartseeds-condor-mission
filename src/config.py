"""
Configuración común de SmartSeeds (rutas, zonas de demostración y formatos).

Todo lo que el equipo acuerde el sábado se cambia AQUÍ, en un solo lugar.
"""
from pathlib import Path

# --- Rutas (siempre relativas a la raíz del repositorio) --------------------
RAIZ = Path(__file__).resolve().parents[1]
DATOS_CRUDOS = RAIZ / "datos" / "crudos"          # descargas pesadas (no van a GitHub)
DATOS_PROCESADOS = RAIZ / "datos" / "procesados"  # capas pequeñas que lee la app
TABLAS = RAIZ / "tablas"

# --- Zonas de demostración --------------------------------------------------
# recuadro = (lon_min, lat_min, lon_max, lat_max) en grados
ZONAS = {
    "santo_domingo": {
        "nombre": "Santo Domingo de los Tsáchilas (Costa)",
        "recuadro": (-79.40, -0.45, -79.00, -0.05),
        "provincia": "Santo Domingo de los Tsáchilas",
        # Serie NISAR GCOV verificada el 13 nov: 11 fechas, misma geometría
        "nisar_path": 76,
        "nisar_direccion": "ASCENDING",
    },
    "daule": {
        "nombre": "Daule – Salitre – Samborondón (Costa, zona arrocera)",
        "recuadro": (-80.05, -2.05, -79.65, -1.65),
        # La mayor parte del recuadro es Guayas; el borde este toca Los Ríos.
        "provincia": "Guayas",
        # Elegida el 14 nov por ser la candidata con más agua visible en el radar.
        # Órbita 112 descendente (frames 89 y 90): 10 fechas GCOV, 21 jun – 31 oct 2026.
        "nisar_path": 112,
        "nisar_direccion": "DESCENDING",
    },
    # --- Sierra (agregadas el 14 nov al unir el trabajo de Cotopaxi y Tungurahua) ---
    # Cuadros de 0,4° como los de la Costa, puestos sobre los valles agrícolas. El trabajo de la
    # Sierra usaba recuadros más grandes (toda la provincia); se achicaron para que procesar el
    # radar tarde lo mismo que en la Costa. Si se cambian, hay que volver a procesar la zona.
    "cotopaxi": {
        "nombre": "Latacunga – Salcedo – Pujilí – Saquisilí (Sierra, Cotopaxi)",
        "recuadro": (-78.85, -1.10, -78.45, -0.70),
        "provincia": "Cotopaxi",
        # Misma órbita que Santo Domingo. En el trabajo de la Sierra se confirmaron 11 fechas GCOV
        # (19 jun – 29 oct 2026) sobre la provincia; falta comprobarlo con este recuadro.
        "nisar_path": 76,
        "nisar_direccion": "ASCENDING",
    },
    "tungurahua": {
        "nombre": "Ambato – Píllaro – Pelileo – Quero (Sierra, Tungurahua)",
        "recuadro": (-78.80, -1.50, -78.40, -1.10),
        "provincia": "Tungurahua",
        "nisar_path": 76,
        "nisar_direccion": "ASCENDING",
    },
}

# --- Tabla por celda (contrato entre módulos) -------------------------------
# altura (m), pendiente (grados), temp (°C media anual), lluvia (mm/año),
# humedad (0 = seco … 1 = saturado), encharcamiento (0 … 1 = fracción de fechas
# con agua), vegetacion (0 … 1, índice de vegetación del radar)
COLUMNAS_CELDA = ["celda", "lat", "lon", "altura", "pendiente", "temp", "lluvia",
                  "humedad", "encharcamiento", "vegetacion"]

# Tamaño de cada celda de la tabla, en segundos de arco (8" ≈ 250 m).
# NASADEM viene a 1" (≈ 30 m); se promedia para que la tabla sea liviana.
PASO_CELDA_SEG = 8



def forma_rejilla(recuadro) -> tuple[int, int, float]:
    """(filas, columnas, paso en grados) de la rejilla de celdas de una zona.

    La celda número k está en la fila k // columnas (desde el NORTE) y en la
    columna k % columnas (desde el OESTE). Es el mismo orden de la tabla por celda.
    """
    lon_min, lat_min, lon_max, lat_max = recuadro
    filas = round((lat_max - lat_min) * 3600) // PASO_CELDA_SEG
    columnas = round((lon_max - lon_min) * 3600) // PASO_CELDA_SEG
    return filas, columnas, PASO_CELDA_SEG / 3600


# Límites aproximados del Ecuador continental (para validar el punto elegido)
ECUADOR = (-81.1, -5.1, -75.1, 1.5)

# Capitales de provincia (lat, lon): sirven para SUGERIR la provincia del punto.
# Es una aproximación; en la app el usuario puede corregirla.
CAPITALES = {
    "Azuay": (-2.90, -79.00), "Bolívar": (-1.59, -79.00), "Cañar": (-2.74, -78.85),
    "Carchi": (0.81, -77.72), "Chimborazo": (-1.67, -78.65), "Cotopaxi": (-0.93, -78.62),
    "El Oro": (-3.26, -79.96), "Esmeraldas": (0.97, -79.65), "Guayas": (-2.19, -79.89),
    "Imbabura": (0.35, -78.12), "Loja": (-4.00, -79.20), "Los Ríos": (-1.80, -79.53),
    "Manabí": (-1.05, -80.45), "Morona Santiago": (-2.31, -78.12), "Napo": (-0.99, -77.81),
    "Orellana": (-0.46, -76.99), "Pastaza": (-1.49, -78.00), "Pichincha": (-0.22, -78.51),
    "Santa Elena": (-2.23, -80.86), "Santo Domingo de los Tsáchilas": (-0.25, -79.17),
    "Sucumbíos": (0.08, -76.89), "Tungurahua": (-1.24, -78.63),
    "Zamora Chinchipe": (-4.07, -78.95),
}


def zona_de_punto(lat: float, lon: float) -> str | None:
    """Devuelve la clave de la zona de demostración que contiene el punto (o None)."""
    for clave, zona in ZONAS.items():
        lon_min, lat_min, lon_max, lat_max = zona["recuadro"]
        if lon_min <= lon <= lon_max and lat_min <= lat <= lat_max:
            return clave
    return None


def provincia_sugerida(lat: float, lon: float) -> str:
    """Provincia cuya capital está más cerca del punto (aproximación)."""
    clave = zona_de_punto(lat, lon)
    if clave:
        return ZONAS[clave]["provincia"]
    return min(CAPITALES, key=lambda p: (CAPITALES[p][0] - lat) ** 2 + (CAPITALES[p][1] - lon) ** 2)


def en_ecuador(lat: float, lon: float) -> bool:
    lon_min, lat_min, lon_max, lat_max = ECUADOR
    return lon_min <= lon <= lon_max and lat_min <= lat <= lat_max
