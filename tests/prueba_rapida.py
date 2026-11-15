"""
Prueba rápida de la lógica (sin internet y sin datos descargados).

    python tests/prueba_rapida.py

Usa terrenos y matrices INVENTADOS solo para comprobar que las fórmulas se
comportan como se espera. No son datos del proyecto.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import cobertura, nisar, sentinel, terreno  # noqa: E402
from src.aptitud import aptitud, aptitud_detalle, cargar_requisitos  # noqa: E402
from src.clima_relieve import corregir_temp_por_altura, nombre_tile, pendiente_grados  # noqa: E402
from src.config import provincia_sugerida, zona_de_punto  # noqa: E402
from src.mercado import clasificar, evidencia_local, mas_sembrados, mercado, mercado_detalle  # noqa: E402
from src.preparar_mercado import variacion_precio  # noqa: E402
from src.recomendar import (banda, empatados, evaluar_todos, recomendar, reparto_mejor_cultivo,  # noqa: E402
                            suelo_detalle, tiempo_texto)
from src.suelo_lluvia import clase_textura, con_lluvia_mensual, lluvia_mensual_de, suelo_texto  # noqa: E402
from src.vecindad import agua_en_vecinos, resumen_vecinos  # noqa: E402

req = cargar_requisitos().set_index("cultivo")

# --- Aptitud: un terreno de Costa y uno de Sierra ---------------------------
costa = {"altura": 420, "pendiente": 4, "temp": 24.3, "lluvia": 1560,
         "humedad": None, "encharcamiento": None, "vegetacion": None}
sierra = {"altura": 3000, "pendiente": 8, "temp": 12.0, "lluvia": 900,
          "humedad": None, "encharcamiento": None, "vegetacion": None}

assert aptitud(costa, req.loc["cacao"].to_dict()) == 100
assert aptitud(costa, req.loc["papa"].to_dict()) < 40
# Papa con el rango del INIAP (9 a 11 °C, aplicado el 14 nov): a 12 °C pierde unos puntos, ya no saca 100
assert 90 <= aptitud(sierra, req.loc["papa"].to_dict()) < 100
assert aptitud(dict(sierra, altura=3400, temp=10.0), req.loc["papa"].to_dict()) == 100
assert aptitud(sierra, req.loc["cacao"].to_dict()) < 40
assert aptitud({}, req.loc["cacao"].to_dict()) is None            # sin datos -> sin puntaje

# El encharcamiento castiga al cacao pero no al arroz
inundado = dict(costa, encharcamiento=0.5, pendiente=1)
assert aptitud(inundado, req.loc["cacao"].to_dict()) < aptitud(costa, req.loc["cacao"].to_dict())
assert aptitud(inundado, req.loc["arroz"].to_dict()) == 100

# La humedad poco confiable (vegetación densa) se informa pero no cambia el puntaje
mojado = dict(costa, humedad=0.95)
assert aptitud(dict(mojado, humedad_confiable=0.9), req.loc["cacao"].to_dict()) < 100
assert aptitud(dict(mojado, humedad_confiable=0.1), req.loc["cacao"].to_dict()) == 100

# --- Puntaje graduado: no es lo mismo estar en lo ideal que en lo que el cultivo aguanta ---
cacao = req.loc["cacao"].to_dict()                    # ideal 21–32 °C, aguanta desde 10 °C
assert 40 < aptitud(dict(costa, temp=19), cacao) < aptitud(costa, cacao)
# Llover de más resta, pero como máximo la mitad de la nota (el daño llega por el drenaje)
assert aptitud(dict(costa, lluvia=2000), cacao) > aptitud(dict(costa, lluvia=5000), cacao) > \
    aptitud(dict(costa, lluvia=9000), cacao) > 60
# Acidez del suelo (pH de SoilGrids): cuenta solo si la celda la trae
assert aptitud(dict(costa, ph=4.3), cacao) < aptitud(dict(costa, ph=5.5), cacao) == aptitud(costa, cacao)
# Agua en los terrenos vecinos: castiga al cacao, no al arroz
assert aptitud(dict(costa, agua_vecinos=0.3), cacao) < 70
assert aptitud(dict(costa, agua_vecinos=0.3, pendiente=1), req.loc["arroz"].to_dict()) == 100
assert aptitud(dict(costa, agua_vecinos=0.02), cacao) == 100                 # menos del 5 %: no cuenta
# Agua en invierno (radar Sentinel-1, enero a mayo): mismos límites que el encharcamiento
assert aptitud(dict(costa, agua_invierno=0.15), cacao) < aptitud(dict(costa, agua_invierno=0.0), cacao) == 100
assert aptitud(dict(costa, agua_invierno=0.4), cacao) < 40                   # se inunda: no sirve para cacao
assert aptitud(dict(costa, agua_invierno=0.4, pendiente=1), req.loc["arroz"].to_dict()) == 100
# Con el invierno medido, los vecinos ya no cuentan (servían para suponerlo)
assert aptitud(dict(costa, agua_invierno=0.0, agua_vecinos=0.3), cacao) == 100
con_invierno = [f["factor"] for f in aptitud_detalle(dict(costa, agua_invierno=0.0, agua_vecinos=0.3), cacao)["factores"]]
assert "Invierno" in con_invierno and "Alrededores" not in con_invierno
# La papa no usa la temperatura mundial de EcoCrop (15 a 25 °C) sino la del INIAP para la franja andina
assert (req.loc["papa", "temp_opt_min_C"], req.loc["papa", "temp_opt_max_C"]) == (9, 11)
assert req.loc["haba", "temp_opt_max_C"] == 14

top = recomendar(costa, "Santo Domingo de los Tsáchilas")
assert len(top) == 3 and all(c["puntaje"] >= 40 for c in top)
assert not {"papa", "quinua", "haba"} & {c["cultivo"] for c in top}

# --- Riego: reduce la falta de agua, pero no la borra ni arregla otras cosas ---
seco = {"altura": 5, "pendiente": 2, "temp": 27.7, "lluvia": 770,           # como Daule
        "humedad": None, "encharcamiento": None, "vegetacion": None}
regado = dict(seco, riego=True)
for nombre in ("arroz", "banano", "cacao"):
    c = req.loc[nombre].to_dict()
    assert aptitud(seco, c) < aptitud(regado, c) < 100                       # mejora, pero no llega a 100
assert aptitud(regado, req.loc["arroz"].to_dict()) < aptitud(regado, req.loc["banano"].to_dict())  # al arroz le falta más agua
assert aptitud(regado, req.loc["maiz_duro"].to_dict()) == aptitud(seco, req.loc["maiz_duro"].to_dict()) == 100
assert aptitud(dict(costa, riego=True), req.loc["cacao"].to_dict()) == 100   # si llueve bastante, no cambia nada
assert aptitud(dict(sierra, riego=True), req.loc["cacao"].to_dict()) < 40    # el riego no quita el frío
assert aptitud(dict(inundado, riego=True), req.loc["cacao"].to_dict()) ==     aptitud(inundado, req.loc["cacao"].to_dict())                            # ni la inundación

# Si el radar vio agua en el terreno, al arroz no se le dice que "se seca rápido"
arrozal = dict(costa, pendiente=1, encharcamiento=0.37, humedad=0.25, humedad_confiable=0.9)
assert aptitud(arrozal, req.loc["arroz"].to_dict()) == 100

# Cultivos de ciclo corto: se comparan con la lluvia de los meses del cultivo, no con la del año
LLUVIA_DAULE = [212, 365, 335, 224, 85, 30, 18, 4, 7, 5, 30, 74]            # mm por mes, enero a diciembre
daule = dict(seco, lluvia=1389, lluvia_mensual=LLUVIA_DAULE)
maiz = req.loc["maiz_duro"].to_dict()
assert aptitud(daule, maiz) == 100                                            # 4 meses de invierno: 1.136 mm
assert aptitud(dict(daule, lluvia_mensual=[10] * 12), maiz) < 60             # 40 mm en el ciclo: no alcanza
arroz = req.loc["arroz"].to_dict()
assert aptitud(daule, arroz) < aptitud(dict(daule, riego=True), arroz) < 100
assert aptitud(dict(daule, agua_invierno=0.2, pendiente=1), arroz) == 100     # agua vista en invierno
# ...y si el radar vio agua en el terreno, al arroz no le falta agua aunque llueva poco
assert aptitud(dict(daule, encharcamiento=0.37, pendiente=1), arroz) == 100
assert aptitud(dict(daule, encharcamiento=0.37, pendiente=1), maiz) < 40
# El cacao (permanente) sigue con la lluvia del año
assert aptitud(daule, cacao) == aptitud(dict(daule, lluvia_mensual=None), cacao) == 100

# --- Orden: franja de aptitud, luego la provincia, el mercado y la preferencia ---
assert banda(97.4) == 95 and banda(97.6) == 100 and banda(100) == 100
pronto = evaluar_todos(costa, "Guayas", preferencia="pronto")
largo = evaluar_todos(costa, "Guayas", preferencia="largo")
# Los siete primeros tienen 100. Van primero los que se siembran y rinden bien en Guayas, y
# entre esos el de mejor mercado: palma ("alta"), luego arroz y banano ("media")
assert [c["cultivo"] for c in pronto[:3]] == ["palma_aceitera", "arroz", "banano"]   # el más rápido primero
assert [c["cultivo"] for c in largo[:3]] == ["palma_aceitera", "banano", "arroz"]    # permanente primero
cien = [c for c in pronto if c["puntaje"] == 100]
assert [c["evidencia"] for c in cien] == ["fuerte"] * 5 + ["presente", "poca"]       # la yuca casi no se siembra en Guayas
assert cien[3]["mercado"] == cien[4]["mercado"] == "saturado"                        # maíz y cacao: después de los de "media"
assert {c["cultivo"]: c["puntaje"] for c in pronto} == {c["cultivo"]: c["puntaje"] for c in largo}
assert {c["cultivo"] for c in empatados(pronto)} == {"maiz_duro", "cacao", "pina", "yuca"}   # misma franja, fuera del top 3
# Un punto menos de aptitud no cambia de franja: el plátano (95) queda detrás de los de 100
assert pronto[7]["cultivo"] == "platano" and banda(pronto[7]["puntaje"]) == 95
assert "4 meses" in tiempo_texto(req.loc["maiz_duro"].to_dict())
assert "3 años" in tiempo_texto(req.loc["cacao"].to_dict()) and tiempo_texto({}) is None

# --- Suelo (catálogo del equipo): se informa, pero no cambia el puntaje -------
suelo_cacao = suelo_detalle("cacao")
assert suelo_cacao and "pH entre 6 y 7" in suelo_cacao["texto"] and "Agrocalidad" in suelo_cacao["fuente"]
assert "pH" not in suelo_detalle("papa")["texto"]                  # pH de la papa: pendiente en el catálogo
assert suelo_detalle("banano") is None                             # no está en el catálogo -> sin dato
assert any(c["suelo"] for c in pronto if c["cultivo"] == "cacao")

# --- Mercado ----------------------------------------------------------------
assert clasificar(15, -3) == "saturado"
assert clasificar(2, 8) == "alta"
assert clasificar(2, 1) == "media"
assert mercado("cultivo_que_no_existe", "Guayas") == "sin_datos"
# Datos reales 2024-2025 (ESPAC y SIPA), por provincia: se sembró más cacao y papa y el precio bajó
assert mercado("cacao", "Guayas") == "saturado" and mercado("papa", "Cotopaxi") == "saturado"
assert mercado("arroz", "Guayas") == "media" and mercado("banano", "Los Ríos") == "media"
det = mercado_detalle("maiz_duro", "Guayas")
assert det["nivel"] == "saturado" and "En Guayas" in det["texto"]
assert "quintales por cuadra" in det["rendimiento"] and "INEC" in det["fuente"]
# La provincia manda sobre el país: el cacao está saturado en el país pero no en Santo Domingo
assert mercado("cacao", "Santo Domingo de los Tsáchilas") == "media" and mercado("cacao", "Azuay") == "saturado"
assert mercado("cacao", "santo domingo de los tsachilas") == "media"   # sin tildes ni mayúsculas también
# Sin fila de la provincia se usa la nacional, y el texto lo dice
assert "En el país" in mercado_detalle("platano", "Guayas")["texto"]
# Haba y quinua: el SIPA no tiene precios suficientes -> sin datos, no se inventa
assert mercado("haba", "Cotopaxi") == mercado("quinua", "Cotopaxi") == "sin_datos"
assert mercado_detalle("haba", "Cotopaxi")["rendimiento"] is None

# Cómo se arma la tabla: el precio solo se compara con los meses que están en los dos años
meses = [(2024, m, 1.0) for m in range(1, 13)] + [(2025, m, 1.5) for m in range(1, 7)]
precios = pd.DataFrame([{"anio": a, "mes": m, "prov": "GUAYAS", "producto": "yuca", "usd_kg": v} for a, m, v in meses])
cambio = variacion_precio(precios, "Yuca", "GUAYAS")
assert cambio["meses"] == 6 and abs(cambio["var"] - 50) < 1e-6
assert variacion_precio(precios[precios["mes"] != 6], "Yuca", "GUAYAS") is None   # 5 meses: no alcanza
assert variacion_precio(precios, "Yuca", "MANABI") is None

# --- Lo que se siembra en la provincia (ESPAC) -------------------------------
assert evidencia_local("cacao", "Guayas")["nivel"] == "fuerte"            # 104.939 ha y rinde más que el país
assert evidencia_local("pina", "Guayas")["nivel"] == "presente"           # se siembra, pero rinde menos
assert evidencia_local("maracuya", "Guayas")["nivel"] == "poca"           # 220 ha
assert evidencia_local("papa", "Guayas")["nivel"] == "poca" and "no registra" in evidencia_local("papa", "Guayas")["texto"]
assert evidencia_local("cultivo_que_no_existe", "Guayas")["nivel"] == "sin_datos"
assert [x["nombre"] for x in mas_sembrados("guayas", 3)] == ["Arroz", "Cacao", "Banano"]
assert mas_sembrados("Provincia inventada") == []

# --- Suelo y lluvia con detalle local ----------------------------------------
assert clase_textura(40, 20) == "franco" and clase_textura(20, 60) == "arcilloso"
assert clase_textura(80, 5) == "arenoso franco" and clase_textura(33, 30) == "franco arcilloso"
assert clase_textura(None, 30) is None and clase_textura(float("nan"), 30) is None
assert suelo_texto({"ph": 5.4, "arena": 33, "arcilla": 30}) == "suelo franco arcilloso, pH 5.4"
assert suelo_texto({"ph": None}) is None
mensual = {"celda": np.array([7, 8, 9]), "lluvia": np.array([[10.0] * 12, [30.0] * 12, [50.0] * 12])}
assert lluvia_mensual_de(mensual, 8) == [30.0] * 12
assert lluvia_mensual_de(mensual, [7, 9], [3, 1]) == [20.0] * 12          # promedio con pesos
assert lluvia_mensual_de(mensual, 99) is None and lluvia_mensual_de(None, 8) is None
assert con_lluvia_mensual(pd.DataFrame({"celda": [9, 7]}), mensual)["lluvia_mensual"].tolist() == [[50.0] * 12, [10.0] * 12]

# --- Los terrenos vecinos (rejilla de Daule, 180 x 180, con un solo cuadro con agua) ---
filas_d = columnas_d = 180
zona_falsa = pd.DataFrame({"celda": np.arange(filas_d * columnas_d)})
zona_falsa["lat"] = -1.65 - (zona_falsa["celda"] // columnas_d + 0.5) * 8 / 3600
zona_falsa["lon"] = -80.05 + (zona_falsa["celda"] % columnas_d + 0.5) * 8 / 3600
zona_falsa["altura"], zona_falsa["encharcamiento"], zona_falsa["cobertura"] = 10.0, 0.0, "vegetacion_baja"
charco = 90 * columnas_d + 90
zona_falsa.loc[charco, ["encharcamiento", "cobertura", "altura"]] = [0.6, "agua", 4.0]
vec = agua_en_vecinos(zona_falsa, "daule")
assert vec[charco] == 0                                   # el propio cuadro no cuenta como vecino
assert 0 < vec[charco + 1] < 0.05 and vec[charco + 3 * columnas_d] > 0     # sus vecinos sí lo ven
assert vec[charco + 6] == 0 and vec[0] == 0               # a más de 1 km ya no
resumen = resumen_vecinos(zona_falsa, zona_falsa.loc[charco + 1, "lat"], zona_falsa.loc[charco + 1, "lon"])
assert 40 <= resumen["n"] <= 60 and 0 < resumen["con_agua"] < 0.05 and resumen["tipos"]["vegetacion_baja"] > 0.9
assert resumen["diferencia_altura"] == 0
en_el_charco = resumen_vecinos(zona_falsa, zona_falsa.loc[charco, "lat"], zona_falsa.loc[charco, "lon"])
assert en_el_charco["con_agua"] == 0 and en_el_charco["diferencia_altura"] == -6    # está 6 m más bajo

# --- Radar de la época lluviosa (Sentinel-1) ----------------------------------
suave = sentinel._suavizar(np.array([[1.0, 1.0, 1.0], [1.0, 10.0, 1.0], [1.0, np.nan, 1.0]], dtype="float32"))
assert abs(suave[1, 1] - 17 / 8) < 1e-5 and np.isnan(suave[2, 1])        # promedia sin contar el hueco
assert abs(suave[0, 0] - 13 / 4) < 1e-5                                   # en la esquina, solo lo que hay
serie_inv = {"fechas": ["2026-01-06", "2026-02-11", "2026-03-07"],
             "agua": np.stack([np.full((180, 180), v, dtype="float32") for v in (0.0, 0.5, np.nan)])}
serie_inv["agua"][1, 0, 1] = 1.0
del_terreno = sentinel.agua_del_terreno(serie_inv, [0, 1], [1, 3])
assert del_terreno.round(3).tolist() == [0.0, 0.875] and len(del_terreno) == 2      # la fecha sin dato no sale
assert sentinel._url(type("P", (), {"properties": {"additionalUrls": ["a_VH.tif", "a_VV.tif"]}})(), "_VV.tif") == "a_VV.tif"

# --- Clima y relieve --------------------------------------------------------
assert abs(corregir_temp_por_altura(24.0, 500, 1500) - 17.5) < 1e-6   # 1000 m más alto = 6,5 °C menos
assert nombre_tile(-1, -80) == "s01w080" and nombre_tile(0, -79) == "n00w079"
plano = np.zeros((20, 20), dtype="float32")
rampa = np.tile(np.arange(20, dtype="float32") * 30.87, (20, 1)).T    # sube ~45° de fila en fila
assert pendiente_grados(plano, 0).max() == 0
assert abs(pendiente_grados(rampa, 0)[10, 10] - 45) < 0.5

# --- Zonas ------------------------------------------------------------------
assert zona_de_punto(-0.25, -79.2) == "santo_domingo"
assert zona_de_punto(-1.85, -79.85) == "daule"
assert zona_de_punto(-2.9, -79.0) is None
assert provincia_sugerida(-2.19, -79.9) == "Guayas"

# --- Terreno dibujado (contorno) --------------------------------------------
# Cuadrado de 0,01° x 0,01° en el ecuador: ~1112 m de lado -> ~123,6 hectáreas
cuadrado = [(-79.20, -0.01), (-79.19, -0.01), (-79.19, 0.0), (-79.20, 0.0)]
assert abs(terreno.area_m2(cuadrado) / 10_000 - 123.6) < 0.5
assert terreno.area_texto(cuadrado).endswith("cuadras)")
assert terreno.dentro([-79.195, -79.185], [-0.005, -0.005], cuadrado).tolist() == [True, False]
ele = [(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]              # terreno irregular en forma de L
assert terreno.dentro([0.5, 1.5, 1.5], [1.5, 0.5, 1.5], ele).tolist() == [True, True, False]
geo = {"geometry": {"type": "Polygon", "coordinates": [[[p[0], p[1]] for p in cuadrado + cuadrado[:1]]]}}
assert terreno.vertices_de_geojson(geo) == cuadrado
assert terreno.vertices_de_geojson({"geometry": {"type": "Point", "coordinates": [0, 0]}}) is None
tabla_inv = pd.DataFrame({"celda": [0, 1, 2], "lat": [-0.005, -0.006, -0.5], "lon": [-79.195, -79.194, -79.195],
                          "altura": [400.0, 440.0, 900.0], "pendiente": [2.0, 6.0, 30.0],
                          "temp": [24.0, 24.0, 20.0], "lluvia": [1560, 1560, 1560],
                          "humedad": [np.nan, np.nan, np.nan], "encharcamiento": [0.5, 0.0, 0.0],
                          "vegetacion": [0.5, 0.7, 0.9]})
adentro = terreno.celdas_del_terreno(tabla_inv, cuadrado)
assert adentro["celda"].tolist() == [0, 1]                           # la celda lejana queda fuera
prom = terreno.celda_promedio(adentro, cuadrado)
assert prom["altura"] == 420 and prom["encharcamiento"] == 0.25 and prom["humedad"] is None
assert adentro["peso"].tolist() == [1.0, 1.0]                        # las dos celdas quedan enteras dentro
# Un terreno que cubre solo la mitad oeste de la celda 0 y una esquina de la celda 1
paso = 8 / 3600
medio = [(-79.195 - paso / 2, -0.005 - paso / 2), (-79.195, -0.005 - paso / 2),
         (-79.195, -0.005 + paso / 2), (-79.195 - paso / 2, -0.005 + paso / 2)]
mitad = terreno.celdas_del_terreno(tabla_inv, medio)
assert mitad["celda"].tolist() == [0] and abs(mitad["peso"].iloc[0] - 0.5) < 1e-9
dos = terreno.celdas_del_terreno(tabla_inv, [(-79.1965, -0.0045), (-79.1935, -0.0045),
                                             (-79.1935, -0.0065), (-79.1965, -0.0065)])
assert dos["celda"].tolist() == [0, 1] and dos["peso"].iloc[0] > dos["peso"].iloc[1] > 0
prom2 = terreno.celda_promedio(dos, medio)
assert 400 < prom2["altura"] < 420                                   # pesa más la celda más ocupada (400 m)
chico = [(-79.3001, -0.4001), (-79.3000, -0.4001), (-79.3000, -0.4000)]   # más pequeño que una celda
assert len(terreno.celdas_del_terreno(tabla_inv, chico)) == 1        # usa la celda más cercana
partes = reparto_mejor_cultivo(adentro)
assert {p["cultivo"] for p in partes} == {"arroz", "maiz_duro"}      # la mitad inundada -> arroz
assert {p["cultivo"] for p in reparto_mejor_cultivo(adentro, preferencia="largo")} == {"arroz", "banano"}
assert abs(sum(p["fraccion"] for p in partes) - 1) < 1e-9

# --- Capas NISAR con matrices de prueba -------------------------------------
hh = np.full((4, 3, 3), 0.10, dtype="float32")     # 4 fechas, 3x3 píxeles, -10 dB
hv = np.full((4, 3, 3), 0.02, dtype="float32")
hh[:2, 0, 0] = 0.005                                # un píxel con agua en 2 de 4 fechas (-23 dB)
ench = nisar.capa_encharcamiento(hh)
assert ench[0, 0] == 0.5 and ench[1, 1] == 0
veg = nisar.capa_vegetacion(hh, hv)
assert abs(veg[1, 1] - 4 * 0.02 / 0.12) < 1e-5
rel = nisar.humedad_relativa(hh)
assert rel[0, 0, 0] == 0 and rel[3, 0, 0] == 1      # seco al inicio, húmedo al final
assert abs(nisar.a_db(np.array([0.1]))[0] + 10) < 1e-5

# Serie del radar de un terreno (lo que dibuja el gráfico de la app): 4 fechas, rejilla 3x3
agua = np.zeros((4, 3, 3), dtype="float32")
agua[:2, 0, 0] = 1.0                                # la celda 0 estuvo cubierta de agua 2 fechas
series = {"fechas": ["2026-06-21", "2026-07-03", "2026-07-15", "2026-07-27"],
          "hh": hh, "hv": hv, "agua": agua,
          "fechas_humedad": ["2026-06-21", "2026-07-03"],
          "sm": np.full((2, 3, 3), 0.25, dtype="float32")}
st0 = nisar.serie_del_terreno(series, [0])
assert st0["agua"].tolist() == [1, 1, 0, 0]
assert st0["vegetacion"].isna().tolist() == [True, True, False, False]   # sobre el agua no vale
assert st0["humedad"].iloc[0] == 0.5 and st0["humedad"].isna().sum() == 2   # 0,25 m³/m³ = 50 %
st2 = nisar.serie_del_terreno(series, [0, 4])       # terreno dibujado: promedio de 2 celdas
assert st2["agua"].tolist() == [0.5, 0.5, 0, 0]
vacio = dict(series, hh=np.full_like(hh, np.nan), hv=np.full_like(hv, np.nan))
assert nisar.serie_del_terreno(vacio, [0]) is None  # fuera de la franja del radar

# --- Tipo de terreno según el radar (modelo de agrupamiento) -----------------
# Reglas que le ponen nombre a cada grupo, con valores parecidos a los que salieron al entrenar
base = {"hh_media": -8, "hv_media": -16, "hh_cambio": 0.6, "hv_cambio": 0.5, "hh_min": -9,
        "agua": 0.0, "hh_menos_hv": 8}
assert cobertura.nombrar(base) == "vegetacion_baja"
assert cobertura.nombrar(dict(base, hv_media=-11)) == "vegetacion_densa"
assert cobertura.nombrar(dict(base, hh_cambio=2.9)) == "cultivo_activo"
assert cobertura.nombrar(dict(base, hh_media=0, hh_menos_hv=10.6)) == "construcciones"
assert cobertura.nombrar(dict(base, agua=0.27)) == "inundable"
assert cobertura.nombrar(dict(base, agua=0.8)) == "agua"
# Rasgos de una serie inventada: la celda (0,0) tiene agua en 2 de 4 fechas y cambia mucho
ras = cobertura.rasgos_de_serie(hh, hv, agua)
assert len(ras) == 9 and ras["agua"].iloc[0] == 0.5 and ras["hh_cambio"].iloc[0] > 5
assert abs(ras["hh_media"].iloc[4] + 10) < 1e-4 and ras["hh_cambio"].iloc[4] < 1e-4
# Clasificar con un modelo de dos grupos (sin scikit-learn): el más parecido gana
modelo = {"media": np.zeros(7), "escala": np.ones(7), "nombres": ["vegetacion_baja", "inundable"],
          "centros": np.array([ras.iloc[4].to_numpy(), ras.iloc[0].to_numpy()])}
clases = cobertura.clasificar(ras, modelo)
assert clases[0] == "inundable" and clases[4] == "vegetacion_baja"
# De qué está hecho un terreno: pesa cada celda por lo que ocupa; lo construido no es cultivable
mezcla = pd.DataFrame({"cobertura": ["cultivo_activo", "construcciones", None], "peso": [0.75, 0.25, 1.0]})
comp = cobertura.composicion(mezcla)
assert [(c["clase"], c["fraccion"], c["cultivable"]) for c in comp] ==     [("cultivo_activo", 0.75, True), ("construcciones", 0.25, False)]
assert cobertura.es_cultivable(mezcla["cobertura"]).tolist() == [True, False, True]
assert cobertura.composicion(pd.DataFrame({"altura": [1.0]})) is None

# Modelo con mapa de referencia: las reglas físicas corrigen lo que dice el modelo
prob = pd.DataFrame({"construcciones": [0.9, 0.9, 0.7, 0.2, 0.9, 0.9],
                     "vegetacion_baja": [0.1, 0.1, 0.3, 0.8, 0.1, 0.1]})
reglas = cobertura.aplicar_reglas(prob, agua=[0, 0, 0, 0, 0.2, 0.6], pendiente=[2, 15, 2, 2, 2, 2])
assert reglas.tolist() == ["construcciones",      # seguro y en plano
                           "vegetacion_baja",     # en ladera no puede ser un pueblo
                           "vegetacion_baja",     # no está bastante seguro (menos de 0,75)
                           "vegetacion_baja",
                           "inundable",           # agua en el 20 % de las pasadas
                           "agua"]                # agua en la mitad o más de las pasadas
assert set(cobertura.CLASE_DE_REFERENCIA.values()) <= set(cobertura.CLASES)
assert "ESA WorldCover" in cobertura.texto_evaluacion({"referencia": "ESA WorldCover 2021 v200", "acierto": 0.79})
assert "79%" in cobertura.texto_evaluacion({"referencia": "ESA WorldCover 2021 v200", "acierto": 0.79})

# --- Sierra: zonas, heladas y cultivos del catálogo del equipo -----------------
from src import catalogo_equipo, heladas  # noqa: E402

assert zona_de_punto(-0.93, -78.62) == "cotopaxi" and zona_de_punto(-1.24, -78.63) == "tungurahua"
assert provincia_sugerida(-1.17, -78.54) == "Tungurahua"                      # Píllaro
# Heladas: riesgo según la mínima media del mes más frío
assert list(heladas.riesgo_de_helada([5, 2, -1, -4])) == [0, 0.5, 1, 1]
alturas = np.full((11, 11), 2900.0)
alturas[5, 5] = 2840.0                                                        # un fondo plano 60 m más bajo
hond = heladas.indice_hondonada(alturas, np.zeros((11, 11)))
assert hond[5, 5] > 0.9 and hond[0, 0] == 0
assert heladas.indice_hondonada(alturas, np.full((11, 11), 20.0))[5, 5] == 0  # en ladera el aire frío no se queda
minima = heladas.minima_por_celda(4.0, 2900, np.array([2900, 3400]), np.array([0.0, 0.0]))
assert abs(minima[0] - 4.0) < 1e-9 and abs(minima[1] - 0.75) < 1e-9           # 500 m más arriba: 3,25 °C menos
assert heladas.minima_por_celda(4.0, 2900, 2900, 1.0) == 2.5                  # hondonada: 1,5 °C más frío
# La helada solo cuenta si la celda trae el dato y la tabla dice cuánto aguanta el cultivo
papa, quinua, haba = (req.loc[c].to_dict() for c in ("papa", "quinua", "haba"))
fria = dict(sierra, helada=0.8, temp_minima=0.2)
import src.aptitud as _apt  # noqa: E402
# El factor está APAGADO (14 nov): la helada se muestra como aviso y no cambia ningún puntaje
assert _apt.HELADAS_EN_PUNTAJE is False
for _c in (papa, quinua, haba):
    assert aptitud(fria, _c) == aptitud(sierra, _c)
    _aviso = [f for f in aptitud_detalle(fria, _c)["factores"] if f["factor"] == "Heladas"][0]
    assert _aviso["nota"] is None and "riesgo de 80%" in _aviso["texto"] and "no cuenta en el puntaje" in _aviso["texto"]
assert "no las aguanta" in [f["texto"] for f in aptitud_detalle(fria, papa)["factores"] if f["factor"] == "Heladas"][0]
# Encendido (para cuando haya fuente para todos): la helada solo cuenta si la tabla dice cuánto aguanta el cultivo
_apt.HELADAS_EN_PUNTAJE = True
assert aptitud(fria, papa) < aptitud(sierra, papa) and aptitud(fria, quinua) < aptitud(sierra, quinua)
assert aptitud(sierra, papa) - aptitud(fria, papa) > aptitud(sierra, quinua) - aptitud(fria, quinua)  # la papa pierde más
assert aptitud(fria, haba) == aptitud(sierra, haba)                           # haba: sin dato, no cuenta
assert "no cuenta en el puntaje" in [f["texto"] for f in aptitud_detalle(fria, haba)["factores"] if f["factor"] == "Heladas"][0]
assert aptitud(dict(sierra, helada=0.02), papa) == aptitud(sierra, papa)      # menos del 5 %: sin heladas
_apt.HELADAS_EN_PUNTAJE = False
assert not [f for f in aptitud_detalle(costa, papa)["factores"] if f["factor"] == "Heladas"]   # la Costa no cambia
# Cultivos de la Sierra traídos del catálogo del equipo (v1.1): no cambian nada en la Costa
nuevos = set(catalogo_equipo.CULTIVOS_NUEVOS)
assert nuevos <= set(req.index) and "frejol" not in req.index
assert all((aptitud(costa, req.loc[c].to_dict()) or 0) < 40 for c in nuevos)
assert aptitud(sierra, req.loc["cebada"].to_dict()) > 80 and aptitud(sierra, req.loc["chocho"].to_dict()) > 80
assert req.loc["cebada", "temp_opt_min_C"] == 8 and req.loc["cebada", "temp_abs_min_C"] <= 8   # rango andino del Ecuador
assert pd.isna(req.loc["amaranto", "pendiente_max_grados"])                   # lo que el catálogo no trae queda vacío
seca = dict(sierra, humedad=0.2, humedad_confiable=0.9)
assert aptitud(seca, req.loc["amaranto"].to_dict()) == aptitud(sierra, req.loc["amaranto"].to_dict())  # sin dato de drenaje
fila, fila_eco, _ = catalogo_equipo.filas_del_cultivo("chocho")
assert (fila["altitud_min_m"], fila["altitud_max_m"], fila["ciclo_meses"], fila["tolera_heladas"]) == (2600, 3200, 6, "no")
assert fila_eco["temp_opt_min_ecuador_C"] == 7 and "Basantes" in fila_eco["fuente_ecuador"]

print("TODO BIEN: aptitud graduada, riego, lluvia del ciclo, orden, suelo, mercado, provincia, vecinos, "
      "clima/relieve, zonas, terreno dibujado, "
      "capas NISAR, tipo de terreno, heladas y cultivos de la Sierra.")
