"""
SmartSeeds · arma la respuesta completa para un terreno, lista para mostrarla en la interfaz nueva.

No dibuja nada y no usa Streamlit: recibe el terreno marcado y devuelve un diccionario sencillo
(texto y números) que `app/interfaz/index.html` convierte en pantalla. El cálculo es el mismo de
siempre: `src.recomendar.evaluar_todos` sobre la celda del terreno. Aquí solo se junta y se explica.

Lo que SÍ sale de datos: aptitud, condiciones del terreno, superficie sembrada y precios
(ESPAC y SIPA), rendimiento y tiempo a la cosecha.
Lo que NO se calcula todavía y por eso no se afirma: cuánta demanda habrá el mes de la cosecha.
La nota de rotación de cultivos es una orientación general por familia botánica, sin fuente
del equipo todavía: se muestra marcada como orientación.
"""
from __future__ import annotations

import math
import re
from datetime import date

import pandas as pd

from src.aptitud import PESO_PEOR_FACTOR, cargar_requisitos
from src.clima_relieve import cargar_celdas, celda_mas_cercana, clima_power, ruta_celdas
from src.cobertura import composicion, es_cultivable
from src.config import en_ecuador, provincia_sugerida, zona_de_punto
from src.mercado import ETIQUETAS, ETIQUETAS_EVIDENCIA
from src.recomendar import BANDA_PUNTOS, PUNTAJE_MINIMO, evaluar_todos
from src.suelo_lluvia import (cargar_lluvia_mensual, con_lluvia_mensual, lluvia_mensual_de,
                              ruta_lluvia_mensual, suelo_texto)
from src.terreno import area_texto, celda_promedio, celdas_del_terreno
from src.terreno import centro as centro_terreno
from src.vecindad import resumen_vecinos

CUANTOS_MOSTRAR = 5          # cultivos que se muestran como recomendación (los mejores)
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]

# Familia botánica de cada cultivo de la tabla (dato de botánica, no del terreno).
FAMILIAS = {
    "papa": "solanáceas", "tomate_de_arbol": "solanáceas", "uvilla": "solanáceas",
    "maiz_duro": "gramíneas", "maiz_suave": "gramíneas", "arroz": "gramíneas", "trigo": "gramíneas",
    "cebada": "gramíneas",
    "haba": "leguminosas", "arveja": "leguminosas", "lenteja": "leguminosas", "chocho": "leguminosas",
    "quinua": "amarantáceas", "amaranto": "amarantáceas",
    "cebolla_blanca": "aliáceas", "brocoli": "crucíferas", "yuca": "euforbiáceas",
    "cacao": "malváceas", "banano": "musáceas", "platano": "musáceas", "palma_aceitera": "palmas",
    "cafe_robusta": "rubiáceas", "maracuya": "pasifloráceas", "pina": "bromeliáceas",
    "mora_de_castilla": "rosáceas", "aguacate": "lauráceas",
}


def _limpio(valor):
    """Deja el valor listo para viajar al navegador: sin NaN ni tipos de numpy."""
    if isinstance(valor, dict):
        return {str(k): _limpio(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_limpio(v) for v in valor]
    if hasattr(valor, "item") and not isinstance(valor, (str, bytes)):
        try:
            valor = valor.item()
        except (ValueError, AttributeError):
            return None
    if isinstance(valor, float) and (math.isnan(valor) or math.isinf(valor)):
        return None
    return valor


def _tiene(valor) -> bool:
    return valor is not None and not pd.isna(valor)


def terreno_completo(lat: float, lon: float, contorno=None, clima=clima_power):
    """(celda, clave_zona, celdas_del_contorno, tipos_de_terreno, vecinos) del terreno marcado.

    Es el mismo armado que hace `app/app.py` en `datos_del_terreno` (se repite aquí porque aquel
    está atado a la pantalla de Streamlit). `contorno` es una lista de vértices (lon, lat) o None.
    `clima` es la función que consulta NASA POWER (se puede cambiar por una con caché).
    """
    clave = zona_de_punto(lat, lon)
    if clave and ruta_celdas(clave).exists():
        tabla = cargar_celdas(clave)
        mensual = cargar_lluvia_mensual(clave) if ruta_lluvia_mensual(clave).exists() else None
        if contorno:
            dentro = celdas_del_terreno(tabla, contorno)
            if len(dentro):
                tipos = composicion(dentro)
                vecinos = resumen_vecinos(tabla, lat, lon, dentro["celda"].tolist())
                if "cobertura" in dentro and es_cultivable(dentro["cobertura"]).any():
                    dentro = dentro[es_cultivable(dentro["cobertura"])]
                dentro = con_lluvia_mensual(dentro, mensual)
                celda = celda_promedio(dentro, contorno)
                celda["lluvia_mensual"] = lluvia_mensual_de(mensual, dentro["celda"].tolist(),
                                                            dentro["peso"].tolist())
                return celda, clave, dentro, tipos, vecinos
        celda = celda_mas_cercana(tabla, lat, lon)
        celda["lluvia_mensual"] = lluvia_mensual_de(mensual, celda["celda"])
        return (celda, clave, None, composicion(pd.DataFrame([celda])),
                resumen_vecinos(tabla, lat, lon))
    # NASA POWER solo se consulta aquí, fuera de las zonas detalladas: dentro de ellas todo sale de
    # la tabla ya procesada, y así el análisis no depende de que ese servidor conteste en el momento.
    c = clima(round(lat, 2), round(lon, 2))
    celda = {"lat": lat, "lon": lon, "altura": c["altura_power"], "pendiente": None,
             "temp": c["temp"], "lluvia": c["lluvia"], "lluvia_mensual": c.get("lluvia_mensual"),
             "humedad": None, "encharcamiento": None, "vegetacion": None}
    return celda, None, None, None, None


def rendimiento_corto(texto: str | None):
    """(quintales por cuadra, ámbito) sacados de la frase de rendimiento de `src.mercado`."""
    hallado = re.search(r"^En (.+?) rinde .*cerca de ([\d.,]+) quintales por cuadra", texto or "")
    return (hallado.group(2), hallado.group(1)) if hallado else (None, None)


def cosecha_estimada(meses, hoy: date | None = None) -> str | None:
    """Mes y año en que llegaría la primera cosecha si se siembra este mes (cuenta simple)."""
    if not _tiene(meses):
        return None
    hoy = hoy or date.today()
    total = hoy.month - 1 + int(round(float(meses)))
    return f"{MESES[total % 12]} de {hoy.year + total // 12}"


def nota_de_rotacion(cultivo: str, nombre: str, anterior: str | None, nombre_anterior: str | None):
    """Orientación general según lo que se sembró antes (por familia botánica). None si no aplica."""
    if not anterior or anterior not in FAMILIAS or cultivo not in FAMILIAS:
        return None
    familia, familia_anterior = FAMILIAS[cultivo], FAMILIAS[anterior]
    antes = (nombre_anterior or anterior).lower()
    if anterior == cultivo:
        return (f"Aquí sembraste {antes} la última vez. Repetir el mismo cultivo en el mismo suelo "
                "favorece sus plagas y enfermedades y gasta los mismos nutrientes: conviene alternar.")
    if familia == familia_anterior:
        return (f"{nombre} y {antes} son de la misma familia ({familia}) y comparten plagas y "
                "enfermedades. Es mejor dejar pasar un ciclo con otro cultivo entre los dos.")
    if familia_anterior == "leguminosas":
        return (f"Antes sembraste {antes}, que es una leguminosa: suele dejar nitrógeno en el suelo, "
                "y este cultivo lo aprovecha.")
    return (f"Va bien después de {antes}: son de familias distintas, y alternar familias ayuda a "
            "cortar plagas y enfermedades.")


def _resumen_condiciones(factores: list[dict]) -> dict:
    notas = [f["nota"] for f in factores if f["nota"] is not None]
    return {"a_favor": sum(n >= 1 for n in notas), "a_medias": sum(0 < n < 1 for n in notas),
            "en_contra": sum(n <= 0 for n in notas)}


def lista_de_cultivos() -> list[dict]:
    """Cultivos de la tabla (clave y nombre), para la pregunta opcional "¿qué sembraste antes?"."""
    from src.recomendar import NOMBRES
    claves = cargar_requisitos()["cultivo"].tolist()
    return sorted(({"clave": c, "nombre": NOMBRES.get(c, str(c).replace("_", " ").capitalize())}
                   for c in claves), key=lambda x: x["nombre"])


def analizar(pedido: dict, clima=clima_power, hoy: date | None = None) -> dict:
    """Respuesta completa para el terreno del `pedido` que manda la interfaz.

    pedido = {"pedido": número, "contorno": [[lon, lat], ...] o None, "punto": [lat, lon] o None,
              "riego": bool, "preferencia": "pronto" | "largo", "anterior": clave o None,
              "ph": número o None}
    """
    numero = pedido.get("pedido")
    contorno = [(float(x), float(y)) for x, y in (pedido.get("contorno") or [])]
    contorno = contorno if len(contorno) >= 3 else None
    if contorno:
        lat, lon = centro_terreno(contorno)
    elif pedido.get("punto"):
        lat, lon = (float(v) for v in pedido["punto"])
    else:
        return {"pedido": numero, "error": "Falta marcar el terreno en el mapa."}
    if not en_ecuador(lat, lon):
        return {"pedido": numero, "error": "Ese lugar está fuera del Ecuador continental. "
                                           "Por ahora SmartSeeds solo analiza terrenos del Ecuador."}
    try:
        celda, clave_zona, dentro, tipos, vecinos = terreno_completo(lat, lon, contorno, clima)
    except Exception as error:  # noqa: BLE001
        return {"pedido": numero, "error": "No se pudo consultar el clima de NASA POWER. "
                                           f"Revisa tu internet y vuelve a intentar. ({error})"}

    celda["riego"] = bool(pedido.get("riego"))
    ph_propio = pedido.get("ph")
    if _tiene(ph_propio) and 3 <= float(ph_propio) <= 10:      # análisis de suelo del agricultor
        celda["ph"] = float(ph_propio)
    else:
        ph_propio = None
    preferencia = "largo" if pedido.get("preferencia") == "largo" else "pronto"
    provincia = provincia_sugerida(lat, lon)
    todos = evaluar_todos(celda, provincia, preferencia=preferencia)
    mejores = [x for x in todos if x["puntaje"] >= PUNTAJE_MINIMO][:CUANTOS_MOSTRAR]
    nombres = {x["cultivo"]: x["nombre"] for x in todos}
    anterior = pedido.get("anterior") or None

    cultivos = []
    for puesto, x in enumerate(mejores, start=1):
        quintales, ambito = rendimiento_corto(x.get("rendimiento_texto"))
        cultivos.append({
            "puesto": puesto, "clave": x["cultivo"], "nombre": x["nombre"],
            "nombre_cientifico": x.get("nombre_cientifico") or "",
            "tipo": str(x.get("tipo") or "").replace("_", " "),
            "familia": FAMILIAS.get(x["cultivo"]),
            "puntaje": round(float(x["puntaje"])),
            "quintales": quintales, "ambito": ambito,
            "meses": x.get("meses"), "cosecha": cosecha_estimada(x.get("meses"), hoy),
            "mercado": x["mercado"], "mercado_etiqueta": ETIQUETAS[x["mercado"]],
            "mercado_texto": x["mercado_texto"], "mercado_fuente": x.get("mercado_fuente"),
            "evidencia": x.get("evidencia"),
            "evidencia_etiqueta": ETIQUETAS_EVIDENCIA.get(x.get("evidencia")),
            "evidencia_texto": x.get("evidencia_texto"),
            "rendimiento_texto": x.get("rendimiento_texto"), "tiempo_texto": x.get("tiempo_texto"),
            "factores": [{"factor": f.get("factor"), "nota": f["nota"], "texto": f["texto"]} for f in x["factores"]],
            "condiciones": _resumen_condiciones(x["factores"]),
            "suelo_prefiere": (x["suelo"] or {}).get("texto") if x.get("suelo") else None,
            "suelo_fuente": (x["suelo"] or {}).get("fuente") if x.get("suelo") else None,
            "rotacion": nota_de_rotacion(x["cultivo"], x["nombre"], anterior, nombres.get(anterior)),
        })

    fuera = sum(t["fraccion"] for t in tipos if not t["cultivable"]) if tipos else 0.0
    hay_radar = bool(clave_zona) and _tiene(celda.get("vegetacion"))
    terreno = {
        "lat": lat, "lon": lon, "provincia": provincia,
        "area": area_texto(contorno) if contorno else None,
        "detallado": bool(clave_zona), "con_radar": hay_radar,
        "cuadros": int(len(dentro)) if dentro is not None else 1,
        "altura": celda.get("altura"), "pendiente": celda.get("pendiente"),
        "temp": celda.get("temp"), "lluvia": celda.get("lluvia"),
        "suelo": suelo_texto(celda) if clave_zona else None, "ph_propio": ph_propio,
        "vegetacion": celda.get("vegetacion") if hay_radar else None,
        "humedad": celda.get("humedad") if hay_radar else None,
        "encharcamiento": celda.get("encharcamiento") if hay_radar else None,
        "helada": celda.get("helada"), "temp_minima": celda.get("temp_minima"),
        "tipos": [{"nombre": t["nombre"], "fraccion": t["fraccion"], "cultivable": t["cultivable"]}
                  for t in (tipos or [])],
        "no_cultivable": fuera >= 0.995,
        "vecinos_agua": (vecinos or {}).get("con_agua"),
        "diferencia_altura": (vecinos or {}).get("diferencia_altura"),
    }
    return _limpio({
        "pedido": numero, "terreno": terreno, "cultivos": cultivos,
        "banda": BANDA_PUNTOS, "minimo": PUNTAJE_MINIMO, "peso_peor": PESO_PEOR_FACTOR,
        "otros": [{"nombre": x["nombre"], "puntaje": round(float(x["puntaje"]))}
                  for x in todos if x["puntaje"] >= PUNTAJE_MINIMO][CUANTOS_MOSTRAR:],
        "anterior": nombres.get(anterior), "riego": celda["riego"], "preferencia": preferencia,
        "mes_siembra": MESES[(hoy or date.today()).month - 1],
    })
