"""
SmartSeeds · interfaz nueva (pantalla completa, pensada para el agricultor).

Ejecutar desde la raíz del repositorio (con el entorno `condor` activado):
    streamlit run app/smartseeds.py

Cómo está hecha:
  - Toda la pantalla es UNA pieza propia (`app/interfaz/index.html`): el globo, el mapa donde se
    marca el terreno, las tarjetas de cultivos y la ficha de cada uno. Streamlit solo la aloja.
  - Cuando el agricultor termina de marcar su terreno, la pieza manda un "pedido" a Python;
    `app/analisis.py` hace el cálculo con el motor de siempre (`src/`) y devuelve la respuesta.
  - `app/app.py` sigue existiendo: es la vista técnica, con las capas del radar y los gráficos.
"""
import mimetypes
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# En Windows, Python a veces sirve los .js como "texto" y el navegador se niega a cargarlos como
# módulos (los modelos 3D de las plantas usan módulos). Se fija el tipo correcto antes de servir nada.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("model/gltf-binary", ".glb")

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
for carpeta in (RAIZ, AQUI):
    if str(carpeta) not in sys.path:
        sys.path.insert(0, str(carpeta))

from analisis import analizar, lista_de_cultivos  # noqa: E402
from src.clima_relieve import clima_power  # noqa: E402
from src.config import ECUADOR, ZONAS  # noqa: E402

st.set_page_config(page_title="SmartSeeds", page_icon="🌱", layout="wide",
                   initial_sidebar_state="collapsed")

# La pieza ocupa toda la ventana: se esconden la barra y los márgenes de Streamlit.
st.markdown("""
<style>
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], [data-testid="stStatusWidget"], footer { display: none !important; }
[data-testid="stAppViewContainer"], .stApp { background: #12081C; }
.block-container, [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
iframe { display: block; width: 100%; border: 0; }
</style>
""", unsafe_allow_html=True)

interfaz = components.declare_component("smartseeds_interfaz", path=str(AQUI / "interfaz"))


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def clima(lat: float, lon: float) -> dict:
    return clima_power(lat, lon)


@st.cache_data(show_spinner=False)
def configuracion() -> dict:
    """Lo que la pieza necesita saber antes de empezar (no cambia mientras la app corre)."""
    return {"zonas": [list(z["recuadro"]) for z in ZONAS.values()],     # (lon_min, lat_min, lon_max, lat_max)
            "ecuador": list(ECUADOR), "cultivos": lista_de_cultivos()}


valor = interfaz(resultado=st.session_state.get("resultado"), configuracion=configuracion(),
                 key="interfaz", default=None)

# La pieza manda {"accion": "analizar", "pedido": número, ...}. Cada pedido se calcula una sola vez.
if valor and valor.get("accion") == "analizar" and valor.get("pedido") != st.session_state.get("pedido_hecho"):
    st.session_state["resultado"] = analizar(valor, clima)
    st.session_state["pedido_hecho"] = valor.get("pedido")
    st.rerun()
