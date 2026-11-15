"""
SmartSeeds · interfaz en Streamlit.

Ejecutar desde la raíz del repositorio (con el entorno `condor` activado):
    streamlit run app/app.py

La app NO procesa radar en vivo: lee las tablas de `datos/procesados/` y solo
consulta en línea el clima de NASA POWER (es una consulta liviana).
"""
import re
import sys
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from branca.element import MacroElement
from folium.plugins import Draw
from jinja2 import Template
from streamlit_folium import st_folium

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.clima_relieve import cargar_celdas, celda_mas_cercana, clima_power, ruta_celdas  # noqa: E402
from src.config import (CAPITALES, ZONAS, en_ecuador, forma_rejilla, provincia_sugerida,  # noqa: E402
                        zona_de_punto)
from src.nisar import cargar_series, ruta_serie, serie_del_terreno  # noqa: E402
from src.cobertura import CLASES, composicion, es_cultivable, texto_evaluacion  # noqa: E402
from src.mercado import ETIQUETAS, ETIQUETAS_EVIDENCIA, mas_sembrados  # noqa: E402
from src.aptitud import AGUA_VISIBLE  # noqa: E402
from src.recomendar import (BANDA_PUNTOS, PUNTAJE_MINIMO, empatados, evaluar_todos,  # noqa: E402
                            reparto_mejor_cultivo)
from src.suelo_lluvia import (cargar_lluvia_mensual, con_lluvia_mensual, lluvia_mensual_de,  # noqa: E402
                              ruta_lluvia_mensual, suelo_texto)
from src.vecindad import resumen_vecinos  # noqa: E402
from src.sentinel import agua_del_terreno, cargar_invierno, ruta_invierno  # noqa: E402
from src.terreno import (area_texto, celda_promedio, celdas_del_terreno, media_con_peso,  # noqa: E402
                         vertices_de_geojson)
from src.terreno import centro as centro_terreno  # noqa: E402  (aquí `centro` es el centro del mapa)

st.set_page_config(page_title="SmartSeeds", page_icon="🌱", layout="wide")

CENTRO_ECUADOR, ZOOM_ECUADOR = (-1.4, -78.6), 7
# Acercamiento del mapa cuando se marca un terreno: en una zona detallada se alcanza a ver el
# cuadro de datos (~250 m); fuera de ellas el dato es de ~50 km y basta ver los alrededores.
ZOOM_TERRENO, ZOOM_TERRENO_NACIONAL = 15, 12
# Terrenos de ejemplo (un toque y se analizan): nombre del botón -> (latitud, longitud)
EJEMPLOS = {"Santo Domingo": (-0.33, -79.12), "Daule (arrozal)": (-1.9356, -79.6511),
            "Píllaro": (-1.18556, -78.54778), "Saquisilí": (-0.83889, -78.64)}
ICONO_MERCADO = {"alta": "🟢", "media": "🟡", "saturado": "🔴", "sin_datos": "⚪"}
EVIDENCIA_CORTA = {"fuerte": "Sí, y rinde bien", "presente": "Sí, pero rinde menos",
                   "poca": "Casi no", "sin_datos": "Sin datos"}
MODO_PUNTO, MODO_DIBUJO = "📍 Tocar un punto", "✏️ Dibujar mi terreno"
RIEGO_NO, RIEGO_SI = "No, solo lluvia", "Sí, tengo riego"

# Fondos del mapa. El primero es el que se ve al abrir; se cambian con el cuadro de la
# esquina superior derecha del mapa.
FONDO_CROQUIS = "Croquis"
FONDO_FOTO = "Foto satelital"
FONDO_NASA = "NASA 31 oct (óptico)"
URL_FOTO = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/"
            "tile/{z}/{y}/{x}")
CREDITO_FOTO = "Imágenes &copy; Esri, Maxar, Earthstar Geographics y la comunidad GIS"
# Imagen diaria del satélite Suomi NPP (sensor VIIRS) servida por NASA GIBS. Es la fecha de
# la última pasada de NISAR sobre Daule: sirve para comparar lo que ve un satélite óptico
# (nubes) con lo que ve el radar. Su detalle máximo es de ~250 m (nivel 9).
URL_NASA = ("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
            "VIIRS_SNPP_CorrectedReflectance_TrueColor/default/2026-10-31/"
            "GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg")
CREDITO_NASA = "NASA EOSDIS GIBS · VIIRS (Suomi NPP)"

# Capas del radar que se pueden pintar sobre el mapa: nombre -> columna de la tabla por celda.
# Cada capa usa UN solo color, de claro (poco) a oscuro (mucho).
CAPAS_RADAR = {"Nada": None, "Tipo de terreno (modelo del radar)": "cobertura",
               "Agua en la época seca (NISAR)": "encharcamiento",
               "Agua en invierno (Sentinel-1)": "agua_invierno",
               "Vegetación": "vegetacion", "Humedad del suelo": "humedad"}
# Un color por tipo de terreno, siempre el mismo y en este orden (paleta de categorías).
COLOR_TIPO = {"agua": (0x2A, 0x78, 0xD6), "construcciones": (0xEB, 0x68, 0x34),
              "inundable": (0x1B, 0xAF, 0x7A), "cultivo_activo": (0xED, 0xA1, 0x00),
              "vegetacion_baja": (0xE8, 0x7B, 0xA4), "vegetacion_densa": (0x00, 0x83, 0x00)}
RAMPA_AZUL = ((0x86, 0xB6, 0xEF), (0x0D, 0x36, 0x6B))
RAMPA_VERDE = ((0xC8, 0xE6, 0xC0), (0x00, 0x63, 0x00))
RAMPAS = {"encharcamiento": RAMPA_AZUL, "agua_invierno": RAMPA_AZUL, "humedad": RAMPA_AZUL,
          "vegetacion": RAMPA_VERDE}
GRIS_SIN_RADAR = (137, 135, 129, 110)     # celdas que el radar no cubre
OPACIDAD_CAPA = 170                       # de 0 (invisible) a 255 (tapa el mapa)
AGUA_MUCHA = 0.5                          # agua en la mitad de las pasadas = azul más oscuro
COLOR_LINEA = {"light": "#2a78d6", "dark": "#3987e5"}

# Gráficos de la serie del radar: columna -> (título, cómo leerlo)
GRAFICOS_RADAR = {
    "vegetacion": ("Vegetación (0 = suelo desnudo, 100 = vegetación densa)",
                   "Si la línea sube, las plantas están creciendo. Si baja de golpe, suele ser "
                   "cosecha o preparación del terreno. No hay dato en las pasadas en que el "
                   "terreno estaba cubierto de agua."),
    "agua": ("Agua sobre el terreno (% del terreno)",
             "Parte del terreno que el radar vio cubierta de agua en cada pasada."),
    "humedad": ("Humedad del suelo (100 = suelo saturado)",
                "Humedad que midió el radar (producto SME2 de NISAR). Bajo vegetación muy "
                "densa es poco confiable."),
}
PREFERENCIAS = {"Cosechar pronto": "pronto", "Un cultivo para muchos años": "largo"}

# Textos en español de la herramienta de dibujo del mapa (vienen en inglés)
DIBUJO_EN_ESPANOL = """
if (window.L && L.drawLocal) {
    var d = L.drawLocal;
    d.draw.toolbar.buttons.polygon = 'Dibujar mi terreno (esquina por esquina)';
    d.draw.toolbar.buttons.rectangle = 'Dibujar un terreno rectangular';
    d.draw.toolbar.actions.text = 'Cancelar';
    d.draw.toolbar.actions.title = 'Cancelar el dibujo';
    d.draw.toolbar.finish.text = 'Terminar';
    d.draw.toolbar.finish.title = 'Terminar el dibujo';
    d.draw.toolbar.undo.text = 'Borrar la última esquina';
    d.draw.toolbar.undo.title = 'Borrar la última esquina marcada';
    d.draw.handlers.polygon.tooltip.start = 'Toca la primera esquina de tu terreno';
    d.draw.handlers.polygon.tooltip.cont = 'Toca la siguiente esquina';
    d.draw.handlers.polygon.tooltip.end = 'Toca la primera esquina otra vez para cerrar';
    d.draw.handlers.rectangle.tooltip.start = 'Mantén apretado y arrastra para dibujar';
    d.draw.handlers.simpleshape.tooltip.end = 'Suelta para terminar';
    d.edit.toolbar.buttons.edit = 'Corregir el dibujo';
    d.edit.toolbar.buttons.editDisabled = 'No hay nada que corregir';
    d.edit.toolbar.buttons.remove = 'Borrar el dibujo';
    d.edit.toolbar.buttons.removeDisabled = 'No hay nada que borrar';
    d.edit.toolbar.actions.save.text = 'Guardar';
    d.edit.toolbar.actions.cancel.text = 'Cancelar';
    d.edit.toolbar.actions.clearAll.text = 'Borrar todo';
    d.edit.handlers.edit.tooltip.text = 'Arrastra las esquinas para corregir';
    d.edit.handlers.edit.tooltip.subtext = 'Luego toca Guardar';
    d.edit.handlers.remove.tooltip.text = 'Toca el dibujo que quieres borrar';
}
"""


class TextosDibujo(MacroElement):
    """Elemento del mapa que solo traduce al español los textos de la herramienta de dibujo."""
    _template = Template("{% macro script(this, kwargs) %}" + DIBUJO_EN_ESPANOL + "{% endmacro %}")


# --- Datos (con caché para no repetir consultas) ----------------------------
@st.cache_data(ttl=24 * 3600, show_spinner="Consultando el clima en NASA POWER…")
def clima(lat: float, lon: float) -> dict:
    return clima_power(lat, lon)


# `modificado` es la fecha del archivo: si el archivo cambia, la caché se renueva sola.
@st.cache_data(show_spinner=False)
def celdas(clave_zona: str, modificado: float) -> pd.DataFrame:
    return cargar_celdas(clave_zona)


@st.cache_data(show_spinner=False)
def lluvia_de_cada_mes(clave_zona: str, modificado: float) -> dict | None:
    return cargar_lluvia_mensual(clave_zona)


@st.cache_data(show_spinner=False)
def radar_de_invierno(clave_zona: str, modificado: float) -> dict | None:
    return cargar_invierno(clave_zona)


@st.cache_data(show_spinner=False)
def series_radar(clave_zona: str, modificado: float) -> dict | None:
    return cargar_series(clave_zona)


@st.cache_data(show_spinner=False)
def imagen_capa(clave_zona: str, columna: str, modificado: float) -> np.ndarray | None:
    """Imagen (fila, columna, RGBA) de una capa del radar, lista para ponerla sobre el mapa."""
    tabla = cargar_celdas(clave_zona)
    if tabla is None or columna not in tabla:
        return None
    filas, columnas, _ = forma_rejilla(ZONAS[clave_zona]["recuadro"])
    sin_radar = tabla["vegetacion"].isna().to_numpy().reshape(filas, columnas)
    if columna == "cobertura":                # categorías: un color fijo por tipo de terreno
        tipo = tabla[columna].to_numpy(dtype=object).reshape(filas, columnas)
        imagen = np.zeros((filas, columnas, 4), dtype="uint8")
        for clase, color in COLOR_TIPO.items():
            imagen[tipo == clase] = (*color, OPACIDAD_CAPA)
        imagen[sin_radar] = GRIS_SIN_RADAR
        return imagen
    valor = tabla[columna].to_numpy(dtype="float64").reshape(filas, columnas)
    if columna == "agua_invierno":            # es de otro radar: su propia cobertura
        sin_radar = np.isnan(valor)
    if columna in ("encharcamiento", "agua_invierno"):     # solo se pinta donde hubo agua
        visible, tono = valor >= AGUA_VISIBLE, np.clip(valor / AGUA_MUCHA, 0, 1)
    else:
        visible, tono = ~np.isnan(valor), np.clip(valor, 0, 1)
    tono = np.nan_to_num(tono)
    claro, oscuro = RAMPAS[columna]
    imagen = np.zeros((filas, columnas, 4), dtype="uint8")
    for i in range(3):
        imagen[..., i] = (claro[i] + (oscuro[i] - claro[i]) * tono).astype("uint8")
    imagen[..., 3] = np.where(visible, OPACIDAD_CAPA, 0)
    imagen[sin_radar] = GRIS_SIN_RADAR
    return imagen


def leyenda_capa(columna: str) -> str:
    """Explica los colores de la capa pintada en el mapa (barrita o lista de categorías)."""
    if columna == "cobertura":
        cuadros = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px">'
            f'<span style="width:12px;height:12px;border-radius:3px;'
            f'background:rgb{COLOR_TIPO[clase]}"></span>{CLASES[clase][0]}</span>'
            for clase in COLOR_TIPO)
        return (f'<div style="font-size:0.85rem;line-height:1.9">{cuadros}'
                f'<span style="display:inline-flex;align-items:center;gap:5px">'
                f'<span style="width:12px;height:12px;border-radius:3px;'
                f'background:rgb(137,135,129)"></span>sin datos del radar</span></div>')
    claro, oscuro = ("#%02x%02x%02x" % c for c in RAMPAS[columna])
    return (f'<div style="display:flex;align-items:center;gap:8px;font-size:0.85rem">'
            f'<span>poco</span><div style="flex:1;max-width:220px;height:10px;border-radius:4px;'
            f'background:linear-gradient(90deg,{claro},{oscuro})"></div><span>mucho</span>'
            f'<span style="margin-left:12px;display:inline-block;width:12px;height:12px;'
            f'border-radius:3px;background:rgb(137,135,129)"></span><span>sin datos del radar</span>'
            f'</div>')


def datos_del_terreno(lat: float, lon: float, contorno=None):
    """Devuelve (celda, clima, clave_zona, celdas_del_contorno, tipos_de_terreno, vecinos).

    La celda sigue el formato acordado. Si se dibujó un contorno dentro de una zona
    detallada, la celda es el PROMEDIO de las celdas que el terreno toca y
    `celdas_del_contorno` es la tabla con esas celdas (None en los demás casos).
    Las celdas que el modelo del radar ve como construcciones o agua permanente no
    entran en el promedio (salvo que todo el terreno sea así).
    `tipos_de_terreno` dice de qué está hecho el terreno según ese modelo (o None).
    `vecinos` resume qué vio el radar alrededor del terreno, a menos de 1 km (o None).
    La celda lleva además `lluvia_mensual` (12 números) cuando hay ese dato.
    """
    c = clima(round(lat, 2), round(lon, 2))
    clave = zona_de_punto(lat, lon)
    if clave and ruta_celdas(clave).exists():
        tabla = celdas(clave, ruta_celdas(clave).stat().st_mtime)
        mensual = (lluvia_de_cada_mes(clave, ruta_lluvia_mensual(clave).stat().st_mtime)
                   if ruta_lluvia_mensual(clave).exists() else None)
        if contorno:
            dentro = celdas_del_terreno(tabla, contorno)
            tipos = composicion(dentro)
            vecinos = resumen_vecinos(tabla, lat, lon, dentro["celda"].tolist())
            if "cobertura" in dentro and es_cultivable(dentro["cobertura"]).any():
                dentro = dentro[es_cultivable(dentro["cobertura"])]
            dentro = con_lluvia_mensual(dentro, mensual)
            celda = celda_promedio(dentro, contorno)
            celda["lluvia_mensual"] = lluvia_mensual_de(mensual, dentro["celda"].tolist(),
                                                        dentro["peso"].tolist())
            return celda, c, clave, dentro, tipos, vecinos
        celda = celda_mas_cercana(tabla, lat, lon)
        celda["lluvia_mensual"] = lluvia_mensual_de(mensual, celda["celda"])
        return (celda, c, clave, None, composicion(pd.DataFrame([celda])),
                resumen_vecinos(tabla, lat, lon))
    celda = {"lat": lat, "lon": lon, "altura": c["altura_power"], "pendiente": None,
             "temp": c["temp"], "lluvia": c["lluvia"], "lluvia_mensual": c.get("lluvia_mensual"),
             "humedad": None, "encharcamiento": None, "vegetacion": None}
    return celda, c, None, None, None, None


def tiene(valor) -> bool:
    return valor is not None and not pd.isna(valor)


def cuadro_de_datos(lat: float, lon: float):
    """Esquinas [(sur, oeste), (norte, este)] del cuadro de datos (~250 m) que contiene el punto.

    None si el punto está fuera de las zonas detalladas. Es el mismo cuadro que elige
    `celda_mas_cercana`: los centros de las celdas están en la mitad de cada cuadro.
    """
    clave = zona_de_punto(lat, lon)
    if not clave:
        return None
    lon_min, _, _, lat_max = ZONAS[clave]["recuadro"]
    filas, columnas, paso = forma_rejilla(ZONAS[clave]["recuadro"])
    fila = min(max(int((lat_max - lat) / paso), 0), filas - 1)
    columna = min(max(int((lon - lon_min) / paso), 0), columnas - 1)
    norte, oeste = lat_max - fila * paso, lon_min + columna * paso
    return [(norte - paso, oeste), (norte, oeste + paso)]


def enfocar_terreno(lat: float, lon: float) -> None:
    """Anota que el mapa debe centrarse en ese terreno y acercarse a él.

    Nunca aleja el mapa: si ya estaba más cerca (por un terreno marcado antes), se queda así.
    """
    acercamiento = ZOOM_TERRENO if zona_de_punto(lat, lon) else ZOOM_TERRENO_NACIONAL
    anterior = st.session_state.get("enfoque", (None, 0))[1]
    st.session_state["enfoque"] = ((lat, lon), max(acercamiento, anterior))


def rendimiento_corto(texto: str | None) -> tuple[str | None, str | None]:
    """(quintales por cuadra, ámbito) sacados de la frase de rendimiento de `src.mercado`.

    Esa frase dice "En el país rinde en promedio unas 1.4 toneladas ... (cerca de 21 quintales
    por cuadra)." Devuelve ("21", "el país"), o (None, None) si no hay dato de rendimiento.
    """
    hallado = re.search(r"^En (.+?) rinde .*cerca de ([\d.,]+) quintales por cuadra", texto or "")
    return (hallado.group(2), hallado.group(1)) if hallado else (None, None)


def resumen_de_condiciones(factores: list[dict]) -> str:
    """Una línea que cuenta las condiciones del terreno a favor, a medias y en contra del cultivo."""
    notas = [f["nota"] for f in factores if f["nota"] is not None]
    a_favor = sum(n >= 1 for n in notas)
    a_medias = sum(0 < n < 1 for n in notas)
    en_contra = sum(n <= 0 for n in notas)
    partes = [f"✅ {a_favor} a favor"]
    if a_medias:
        partes.append(f"⚠️ {a_medias} a medias")
    if en_contra:
        partes.append(f"❌ {en_contra} en contra")
    return "Condiciones de tu terreno para este cultivo: " + " · ".join(partes)


# --- Barra lateral ----------------------------------------------------------
with st.sidebar:
    st.title("🌱 SmartSeeds")
    st.caption("Equipo Condor Mission · NASA Space Apps 2026")
    opciones = {"Todo Ecuador": None} | {z["nombre"]: k for k, z in ZONAS.items()}
    vista = st.selectbox("Ir a", list(opciones))
    st.markdown(
        "**Cómo usarla**\n"
        "1. Toca tu terreno en el mapa, o dibuja su contorno esquina por esquina.\n"
        "2. Mira qué cultivos le convienen y por qué.\n\n"
        "Los recuadros verdes son las zonas con detalle del radar **NISAR**."
    )
    st.divider()
    st.caption(
        "Datos: NASA POWER (clima), NASADEM (relieve), NISAR (radar), "
        "FAO EcoCrop (cultivos), INEC-ESPAC y MAG (mercado).\n\n"
        "⚠️ Versión en desarrollo: los requisitos de los cultivos son preliminares. "
        "Es una recomendación orientativa, no una orden."
    )

# --- Mapa -------------------------------------------------------------------
st.title("¿Qué me conviene sembrar?")

if opciones[vista]:
    lon_min, lat_min, lon_max, lat_max = ZONAS[opciones[vista]]["recuadro"]
    centro, zoom = ((lat_min + lat_max) / 2, (lon_min + lon_max) / 2), 11
else:
    centro, zoom = CENTRO_ECUADOR, ZOOM_ECUADOR

# Hacia dónde mira el mapa ("enfoque"): la vista elegida en "Ir a" o el terreno marcado, lo que
# haya pasado de último. Así, al marcar un terreno el mapa se acerca a él en vez de quedarse lejos.
if st.session_state.get("vista_mostrada") != vista:
    st.session_state["vista_mostrada"] = vista
    st.session_state["enfoque"] = (centro, zoom)

col_mapa, col_resultado = st.columns([5, 4], gap="large")

with col_mapa:
    modo = st.radio("¿Cómo quieres marcar tu terreno?", [MODO_PUNTO, MODO_DIBUJO], horizontal=True)
    capa = CAPAS_RADAR[st.selectbox(
        "Pintar sobre el mapa lo que vio el radar", list(CAPAS_RADAR),
        help="Pinta las zonas detalladas (recuadros verdes) con lo que midió el radar "
             "entre junio y octubre de 2026.")]
    if capa:
        st.markdown(leyenda_capa(capa), unsafe_allow_html=True)
    mapa = folium.Map(location=centro, zoom_start=zoom, control_scale=True, tiles=None,
                      max_zoom=19)
    folium.TileLayer("OpenStreetMap", name=FONDO_CROQUIS, max_zoom=19).add_to(mapa)
    folium.TileLayer(URL_FOTO, attr=CREDITO_FOTO, name=FONDO_FOTO, max_native_zoom=17,
                     max_zoom=19, show=False).add_to(mapa)
    folium.TileLayer(URL_NASA, attr=CREDITO_NASA, name=FONDO_NASA, max_native_zoom=9,
                     max_zoom=19, show=False).add_to(mapa)
    folium.LayerControl(collapsed=False, position="topright").add_to(mapa)
    for clave, z in ZONAS.items():
        lon_min, lat_min, lon_max, lat_max = z["recuadro"]
        if capa and ruta_celdas(clave).exists():
            imagen = imagen_capa(clave, capa, ruta_celdas(clave).stat().st_mtime)
            if imagen is not None:
                folium.raster_layers.ImageOverlay(
                    imagen, bounds=[[lat_min, lon_min], [lat_max, lon_max]], origin="upper",
                    pixelated=True, interactive=False, control=False).add_to(mapa)
        # El letrero queda fijo en el centro de la zona (sticky=False): si siguiera al cursor
        # taparía justo el lugar donde se va a tocar el terreno.
        folium.Rectangle([(lat_min, lon_min), (lat_max, lon_max)], color="#2e7d32", weight=2,
                         fill=True, fill_opacity=0.05,
                         tooltip=folium.Tooltip(f"Zona detallada: {z['nombre']}", sticky=False),
                         interactive=False).add_to(mapa)
    punto, contorno = None, None

    if modo == MODO_DIBUJO:
        # Herramienta de dibujo: solo polígono, con todas las esquinas que haga falta
        st.caption("1. Acerca el mapa a tu terreno (con la **foto satelital** se ven mejor los "
                   "linderos).  \n"
                   "2. Toca el botón ⬟ y marca el borde punto por punto. Puedes poner todos "
                   "los puntos que necesites para seguir curvas y esquinas.  \n"
                   "3. Para cerrar, toca otra vez el primer punto.  \n"
                   "4. ¿Quedó mal un punto? Toca ✎, arrástralo a su lugar y toca **Guardar**.")
        TextosDibujo().add_to(mapa)         # antes de Draw: así los botones nacen en español
        Draw(draw_options={"polyline": False, "circle": False, "marker": False,
                           "circlemarker": False, "rectangle": False,
                           "polygon": {"allowIntersection": False, "showArea": False,
                                       "shapeOptions": {"color": "#e65100"}}},
             # Ojo: NO pasar {"edit": True}. Con eso el botón de corregir se activa pero no
             # aparecen las esquinas para arrastrar (falla interna de Leaflet.draw 1.0).
             edit_options={"poly": {"allowIntersection": False}}).add_to(mapa)
        centro_mapa, zoom_mapa = st.session_state["enfoque"]
        salida = st_folium(mapa, height=560, use_container_width=True, center=centro_mapa,
                           zoom=zoom_mapa, returned_objects=["all_drawings"], key="mapa_dibujo")
        dibujos = [v for v in map(vertices_de_geojson, (salida or {}).get("all_drawings") or [])
                   if v]
        if dibujos:
            contorno = dibujos[-1]          # si hay varios dibujos, se analiza el último
            if len(dibujos) > 1:
                st.caption("Hay varios dibujos: se analiza el último. Borra los demás con 🗑.")
    else:
        marcador = folium.FeatureGroup(name="terreno")
        # Enlace directo a un terreno (útil para la demo): …/?lat=-0.33&lon=-79.12
        if "punto" not in st.session_state and {"lat", "lon"} <= set(st.query_params):
            try:
                st.session_state["punto"] = (float(st.query_params["lat"]),
                                             float(st.query_params["lon"]))
                enfocar_terreno(*st.session_state["punto"])
            except ValueError:
                pass
        # Terrenos de ejemplo: un toque y se analiza (sirven para probar la app sin buscar en el mapa)
        st.caption("Toca tu terreno en el mapa, o prueba con un terreno de ejemplo:")
        anchos = [len(nombre) + 4 for nombre in EJEMPLOS]       # botón más ancho si el nombre es largo
        for columna_boton, (nombre_ejemplo, lugar) in zip(st.columns(anchos), EJEMPLOS.items()):
            if columna_boton.button(nombre_ejemplo, key=f"ejemplo_{nombre_ejemplo}",
                                    use_container_width=True):
                st.session_state["punto"] = lugar
                enfocar_terreno(*lugar)
        punto = st.session_state.get("punto")
        if punto:
            # Punto dibujado (no una imagen de alfiler): la imagen a veces no carga y sale un ícono roto
            folium.CircleMarker(punto, radius=7, color="#ffffff", weight=2, fill=True,
                                fill_color="#e65100", fill_opacity=1, tooltip="Tu terreno").add_to(marcador)
            cuadro = cuadro_de_datos(*punto)
            if cuadro:          # el cuadro de ~250 m cuyos datos se usan para este terreno
                folium.Rectangle(cuadro, color="#e65100", weight=2, fill=False,
                                 interactive=False).add_to(marcador)
        centro_mapa, zoom_mapa = st.session_state["enfoque"]
        salida = st_folium(mapa, height=560, use_container_width=True, center=centro_mapa,
                           zoom=zoom_mapa, feature_group_to_add=marcador,
                           returned_objects=["last_clicked"], key="mapa")
        if punto and cuadro_de_datos(*punto):
            st.caption("🟧 El cuadro naranja es la parte del mapa cuyos datos se analizan (~250 m de lado, "
                       "unas 6 hectáreas). Si tu terreno es más grande, usa **Dibujar mi terreno**.")
        clic = (salida or {}).get("last_clicked")
        if clic:
            nuevo = (round(clic["lat"], 5), round(clic["lng"], 5))
            # El mapa sigue recordando el último toque: cada toque se atiende una sola vez, para
            # que no le gane a un terreno de ejemplo elegido después.
            if nuevo != st.session_state.get("clic_atendido"):
                st.session_state["clic_atendido"] = nuevo
                if nuevo != punto:
                    st.session_state["punto"] = nuevo
                    enfocar_terreno(*nuevo)
                    st.rerun()

# --- Resultados -------------------------------------------------------------
# Orden en pantalla: primero la respuesta (qué sembrar) y después, plegado, el detalle del terreno.
with col_resultado:
    if modo == MODO_DIBUJO and not contorno:
        st.info("👈 Dibuja el contorno de tu terreno en el mapa para analizarlo.")
        st.stop()
    if modo == MODO_PUNTO and not punto:
        st.info("👈 Toca un punto del mapa para analizar ese terreno, o prueba con uno de los "
                "terrenos de ejemplo.")
        st.stop()

    lat, lon = centro_terreno(contorno) if contorno else punto
    if not en_ecuador(lat, lon):
        st.warning("Ese punto está fuera del Ecuador continental. Elige otro terreno.")
        st.stop()

    try:
        celda, c, clave_zona, celdas_contorno, tipos, vecinos = datos_del_terreno(lat, lon, contorno)
    except Exception as error:  # noqa: BLE001
        st.error(f"No se pudo consultar el clima de NASA POWER. Revisa tu internet.\n\n{error}")
        st.stop()

    # --- 1. Tu terreno, en pocas líneas ---
    st.subheader("Tu terreno")
    if contorno:
        st.caption(f"Terreno dibujado · centro en latitud {lat:.4f}, longitud {lon:.4f}")
        st.metric("Tamaño de tu terreno", area_texto(contorno))
        if celdas_contorno is not None and len(celdas_contorno) > 1:
            st.caption(f"Tu terreno toca {len(celdas_contorno)} cuadros de datos de ~250 m. Cada "
                       "cuadro cuenta según la parte que tu terreno ocupa de él, así el "
                       "resultado sigue la forma que dibujaste.")
        elif celdas_contorno is not None:
            st.caption("Tu terreno cabe dentro de un solo cuadro de datos (~250 m, unas 6 ha): "
                       "se usan los datos de ese cuadro. Los datos del radar no tienen más "
                       "detalle que eso.")
    else:
        st.caption(f"Latitud {lat:.4f}, longitud {lon:.4f}")
    if clave_zona:
        st.success(f"Nivel detallado · {ZONAS[clave_zona]['nombre']}")
    elif zona_de_punto(lat, lon):
        st.warning("Zona detallada, pero todavía no se ha generado su tabla de celdas "
                   "(`python -m src.clima_relieve`). Se muestra el nivel nacional.")
    else:
        st.info("Nivel nacional: clima y altura aproximados (promedio de ~50 km).")

    # Los cuatro datos principales en una sola línea (no se cortan en pantallas angostas)
    resumen = [texto for texto in (
        f"⛰️ **{celda['altura']:.0f} m** de altura" if tiene(celda["altura"]) else None,
        f"🌡️ **{celda['temp']:.1f} °C**" if tiene(celda["temp"]) else None,
        f"🌧️ **{celda['lluvia']:.0f} mm** de lluvia al año" if tiene(celda["lluvia"]) else None,
        f"📐 pendiente de **{celda['pendiente']:.0f}°**" if tiene(celda["pendiente"]) else None) if texto]
    if resumen:
        st.markdown(" · ".join(resumen))

    # Parte del terreno que el radar ve como construcciones o agua (no cultivable)
    fuera = sum(t["fraccion"] for t in tipos if not t["cultivable"]) if tipos else 0.0
    if fuera >= 0.995:
        st.warning("El radar ve este lugar como zona construida o agua, no como "
                   "terreno de cultivo. Toma la recomendación solo como referencia "
                   "o marca otro lugar.")

    # --- 2. Dos preguntas sencillas al agricultor. No dependen del terreno elegido: se conservan ---
    p1, p2 = st.columns(2)
    riego = p1.radio("¿Tienes riego en tu terreno?", [RIEGO_NO, RIEGO_SI], horizontal=True,
                     key="riego",
                     help="Con riego, la falta de lluvia resta menos puntos, pero no desaparece: "
                          "mientras más agua haya que regar, menos puntos. El riego no cambia "
                          "el clima, la pendiente ni las inundaciones.") == RIEGO_SI
    preferencia = PREFERENCIAS[p2.radio(
        "¿Qué buscas?", list(PREFERENCIAS), horizontal=True, key="preferencia",
        help="No cambia el puntaje. Solo decide el orden entre cultivos con aptitud parecida.")]
    celda["riego"] = riego

    provincias = sorted(CAPITALES)
    sugerida = provincia_sugerida(lat, lon)
    provincia = st.selectbox("Provincia (para el mercado)", provincias,
                             index=provincias.index(sugerida), key=f"prov_{lat}_{lon}",
                             help="Se sugiere la más cercana; corrígela si no es la tuya.")

    todos = evaluar_todos(celda, provincia, preferencia=preferencia)
    mejores = [x for x in todos if x["puntaje"] >= PUNTAJE_MINIMO][:3]

    # --- 3. La respuesta: cultivos recomendados ---
    st.subheader("Cultivos recomendados")
    if not mejores:
        st.warning("Ningún cultivo de la lista alcanza una aptitud suficiente en este terreno.")
    for i, cultivo in enumerate(mejores, start=1):
        with st.container(border=True):
            a, b = st.columns([5, 2])
            a.markdown(f"### {i}. {cultivo['nombre']}")
            a.caption(f"*{cultivo['nombre_cientifico']}* · {str(cultivo['tipo']).replace('_', ' ')}")
            # El puntaje en una sola línea que no se parte ni se corta en columnas angostas
            b.markdown(f'<div style="text-align:right;white-space:nowrap;line-height:1.2">'
                       f'<span style="font-size:0.85rem;opacity:0.7">Aptitud</span><br>'
                       f'<span style="font-size:1.9rem;font-weight:700">{cultivo["puntaje"]:.0f}</span>'
                       f'<span style="opacity:0.7"> /100</span></div>', unsafe_allow_html=True)
            st.progress(min(1.0, cultivo["puntaje"] / 100))

            # Lo que más le importa al agricultor, de un vistazo: cuánto rinde, cuándo cosecha y el mercado
            d1, d2 = st.columns(2)
            quintales, ambito = rendimiento_corto(cultivo.get("rendimiento_texto"))
            if quintales:
                d1.markdown(f"📦 **{quintales} quintales por cuadra**")
                d1.caption(f"Lo que rinde en promedio en {ambito}")
            else:
                d1.markdown("📦 **Rendimiento: sin dato**")
                d1.caption("Todavía no hay dato de cuánto rinde")
            if tiene(cultivo.get("meses")):
                d2.markdown(f"⏱️ **{cultivo['meses']:.0f} meses**")
                d2.caption("hasta la primera cosecha")
            linea = f"{ICONO_MERCADO[cultivo['mercado']]} **{ETIQUETAS[cultivo['mercado']]}**"
            if cultivo.get("evidencia") and cultivo["evidencia"] != "sin_datos":
                linea += f" · ¿Se siembra en tu provincia? **{EVIDENCIA_CORTA[cultivo['evidencia']]}**"
            st.markdown(linea)
            st.caption(resumen_de_condiciones(cultivo["factores"]))

            with st.expander("¿Por qué? Ver el detalle"):
                st.markdown(f"{ICONO_MERCADO[cultivo['mercado']]} **{ETIQUETAS[cultivo['mercado']]}** — "
                            f"{cultivo['mercado_texto']}")
                if cultivo.get("evidencia") and cultivo["evidencia"] != "sin_datos":
                    st.markdown(f"🌾 **{ETIQUETAS_EVIDENCIA[cultivo['evidencia']]}** — "
                                f"{cultivo['evidencia_texto']}")
                if cultivo.get("rendimiento_texto"):
                    st.markdown(f"📦 {cultivo['rendimiento_texto']}")
                if cultivo.get("tiempo_texto"):
                    st.markdown(f"⏱️ {cultivo['tiempo_texto']}")
                st.markdown("**Condiciones de tu terreno para este cultivo**")
                for f in cultivo["factores"]:
                    icono = "•" if f["nota"] is None else "✅" if f["nota"] >= 1 else \
                            "⚠️" if f["nota"] > 0 else "❌"
                    st.markdown(f"{icono} {f['texto']}")
                if cultivo.get("mercado_fuente"):
                    st.caption(f"Mercado y rendimiento: se compara 2024 con 2025, con datos de tu provincia "
                               f"si los hay y, si no, del país. Fuente: {cultivo['mercado_fuente']}")
                if cultivo.get("suelo"):
                    st.markdown(f"🧪 **Suelo que prefiere:** {cultivo['suelo']['texto']}")
                    st.caption(f"Dato de referencia del catálogo del equipo. En el puntaje solo cuenta la "
                               f"acidez (pH) de tu terreno, cuando el mapa de suelos la tiene. "
                               f"Fuente: {cultivo['suelo']['fuente']}")

    # Empates: se avisa cuáles otros cultivos tienen la misma aptitud que el tercero
    iguales = empatados(todos) if len(mejores) == 3 else []
    if iguales:
        st.info(f"**Con una aptitud parecida (menos de {BANDA_PUNTOS} puntos de diferencia) también están:** "
                + ", ".join(f"{x['nombre']} ({x['puntaje']:.0f})" for x in iguales)
                + ". Entre cultivos de aptitud parecida van primero los que se siembran y rinden bien "
                  "en tu provincia, luego los de mejor mercado y al final lo que elegiste en "
                  "\"¿Qué buscas?\".")

    siembras = mas_sembrados(provincia)
    if siembras:
        st.caption(f"Lo que más se siembra en {provincia} (INEC, ESPAC {siembras[0]['anio']}): "
                   + ", ".join(f"{x['nombre'].lower()} ({x['superficie_ha']:,.0f} ha)".replace(",", ".")
                               for x in siembras) + ".")

    # Terreno grande: no todo el terreno es igual, se muestra qué conviene en cada parte
    if celdas_contorno is not None and len(celdas_contorno) > 1:
        reparto = reparto_mejor_cultivo(celdas_contorno, riego=riego, preferencia=preferencia)
        if len(reparto) > 1:
            st.subheader("Tu terreno no es igual en todas partes")
            st.caption("Mejor cultivo en cada parte del terreno, mirando cuadro por cuadro:")
            for r in reparto:
                nombre = ("Ningún cultivo de la lista alcanza la aptitud mínima"
                          if r["cultivo"] == "ninguno" else r["nombre"])
                st.markdown(f"- **{r['fraccion']:.0%} del terreno:** {nombre}")

    # --- 4. El detalle del terreno, plegado: clima, suelo, radar y vecinos ---
    hay_radar = bool(clave_zona) and tiene(celda.get("vegetacion"))
    with st.expander("🔎 Ver el detalle de tu terreno: clima, suelo, radar y vecinos"):
        (m1, m2), (m3, m4) = st.columns(2), st.columns(2)
        m1.metric("Altura", f"{celda['altura']:.0f} m" if tiene(celda["altura"]) else "—")
        m2.metric("Temperatura", f"{celda['temp']:.1f} °C" if tiene(celda["temp"]) else "—")
        m3.metric("Lluvia", f"{celda['lluvia']:.0f} mm" if tiene(celda["lluvia"]) else "—",
                  help="Milímetros de lluvia por año (promedio de muchos años)")
        m4.metric("Pendiente", f"{celda['pendiente']:.0f}°" if tiene(celda["pendiente"]) else "—")

        # Detalle local: lluvia a 1 km y suelo a 250 m (solo en las zonas detalladas)
        if clave_zona and tiene(celda.get("lluvia_power")):
            st.caption(f"Lluvia de tu terreno según el mapa CHELSA (cuadros de 1 km, promedio 1981–2010). "
                       f"NASA POWER, que solo da un valor para toda la zona, marca {celda['lluvia_power']:.0f} mm.")
        if clave_zona and suelo_texto(celda):
            st.markdown(f"🧪 **Suelo de tu terreno:** {suelo_texto(celda)}.")
            st.caption("Según el mapa mundial SoilGrids (cuadros de 250 m). Es una orientación: "
                       "no reemplaza un análisis de suelo hecho en tu terreno.")

        if hay_radar:
            st.markdown("**Lo que vio el radar NISAR** (pasadas cada 12 días, a través de las nubes)")
            n1, n2, n3 = st.columns(3)
            n1.metric("Vegetación", f"{celda['vegetacion']:.2f}",
                      help="Índice de vegetación del radar: 0 = suelo desnudo, 1 = vegetación densa")
            n2.metric("Encharcamiento", f"{celda['encharcamiento']:.0%}",
                      help="Parte de las pasadas en que el radar vio agua acumulada")
            n3.metric("Humedad", f"{celda['humedad']:.0%}" if tiene(celda.get("humedad")) else "—",
                      help="Humedad del suelo (producto SME2 de NISAR): 100 % = suelo saturado")
            if celdas_contorno is not None and len(celdas_contorno) > 1:
                con_agua = media_con_peso(
                    (celdas_contorno["encharcamiento"] >= AGUA_VISIBLE).astype(float),
                    celdas_contorno["peso"]) or 0.0
                st.caption(f"El radar vio agua acumulada en el {con_agua:.0%} de tu terreno "
                           "en alguna de sus pasadas.")
            if tiene(celda.get("agua_invierno")):
                st.markdown(f"**Época lluviosa (enero a mayo):** el radar Sentinel-1 vio agua en el "
                            f"**{celda['agua_invierno']:.0%}** de tu terreno, en promedio.")
                st.caption("NISAR empezó a medir en junio. Para el invierno se usa Sentinel-1, otro radar "
                           "(producto OPERA RTC-S1 de la NASA). Ve bien el agua abierta, pero menos a "
                           "través de las plantas.")
            # Tipo de terreno según el modelo entrenado con las pasadas del radar
            if tipos:
                st.markdown("**Qué hay en tu terreno, según el radar**")
                for t in tipos:
                    parte = f"{t['fraccion']:.0%} · " if len(tipos) > 1 else ""
                    st.markdown(f"- {parte}**{t['nombre']}**. {t['explicacion']}")
                if 0 < fuera < 0.995:
                    st.caption(f"El {fuera:.0%} que el radar ve como zona construida o agua "
                               "no entra en el análisis de tu terreno.")
                st.caption(texto_evaluacion())

            # Los terrenos vecinos: qué vio el radar a menos de 1 km
            if vecinos:
                st.markdown(f"**Qué hay alrededor de tu terreno** (a menos de 1 km, {vecinos['n']} cuadros vecinos)")
                if vecinos["tipos"]:
                    partes = [f"{parte:.0%} {CLASES[clase][0].lower()}"
                              for clase, parte in vecinos["tipos"].items() if clase in CLASES and parte >= 0.05]
                    st.markdown("- Tipo de terreno de los vecinos: " + ", ".join(partes) + ".")
                if vecinos["con_agua"] is not None:
                    if vecinos["con_agua"] >= 0.05:
                        st.markdown(f"- En la época seca el radar vio agua en el **{vecinos['con_agua']:.0%}** "
                                    "de los terrenos vecinos.")
                    else:
                        st.markdown("- El radar casi no vio agua en los terrenos vecinos.")
                diferencia = vecinos.get("diferencia_altura")
                if diferencia is not None and abs(diferencia) >= 3:
                    st.markdown(f"- Tu terreno está unos **{abs(diferencia):.0f} m más "
                                f"{'alto' if diferencia > 0 else 'bajo'}** que sus vecinos.")
        elif clave_zona:
            st.caption("Este punto queda fuera de la franja que cubre el radar en esta órbita.")

    # --- 5. Serie del radar: lo que vio en cada pasada sobre este terreno (otro desplegable) ---
    if hay_radar:
        numeros = (celdas_contorno["celda"].tolist() if celdas_contorno is not None
                   else [int(celda["celda"])])
        series = (series_radar(clave_zona, ruta_serie(clave_zona).stat().st_mtime)
                  if ruta_serie(clave_zona).exists() else None)
        pesos = celdas_contorno["peso"].tolist() if celdas_contorno is not None else None
        serie = serie_del_terreno(series, numeros, pesos) if series else None
        if serie is not None:
            with st.expander("📈 Ver lo que vio el radar en cada pasada"):
                tema = getattr(getattr(st.context, "theme", None), "type", None) or "light"
                for columna, (titulo, ayuda) in GRAFICOS_RADAR.items():
                    datos = (serie[columna] * 100).dropna() if columna in serie else None
                    if datos is None or datos.empty:
                        continue
                    st.markdown(f"**{titulo}**")
                    st.line_chart(datos.rename("valor"), height=170,
                                  x_label="Fecha de la pasada",
                                  color=COLOR_LINEA.get(tema, COLOR_LINEA["light"]))
                    st.caption(ayuda)
                invierno = (radar_de_invierno(clave_zona, ruta_invierno(clave_zona).stat().st_mtime)
                            if ruta_invierno(clave_zona).exists() else None)
                if invierno:
                    agua_inv = agua_del_terreno(invierno, numeros, pesos) * 100
                    if not agua_inv.empty:
                        st.markdown("**Agua sobre el terreno en la época lluviosa (% del terreno)**")
                        st.line_chart(agua_inv.rename("valor"), height=170, x_label="Fecha de la pasada",
                                      color=COLOR_LINEA.get(tema, COLOR_LINEA["light"]))
                        st.caption("Pasadas de enero a mayo del radar Sentinel-1 (otro satélite, banda C). "
                                   "Se muestra aparte porque no es NISAR.")

# --- Tabla completa ---------------------------------------------------------
with st.expander("Ver todos los cultivos evaluados"):
    st.dataframe(
        pd.DataFrame([{"Cultivo": x["nombre"], "Aptitud": x["puntaje"],
                       "Primera cosecha (meses)": x["meses"],
                       "Tipo": str(x["tipo"]).replace("_", " "),
                       "Se siembra en tu provincia": EVIDENCIA_CORTA.get(x["evidencia"], "Sin datos"),
                       "Mercado": ETIQUETAS[x["mercado"]]} for x in todos]),
        hide_index=True, use_container_width=True,
        column_config={
            "Aptitud": st.column_config.ProgressColumn(
                "Aptitud (0–100)", min_value=0, max_value=100, format="%.0f"),
            "Primera cosecha (meses)": st.column_config.NumberColumn(format="%d")},
    )
