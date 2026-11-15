"""
Catálogo agronómico del equipo (tablas/catalogo/SMARTSEEDS_catalogo_final_v1.1.json).

Para qué sirve aquí: sacar del catálogo los rangos documentados de los cultivos de la SIERRA
(temperatura, lluvia, altura, acidez del suelo, drenaje, helada, tiempo hasta la cosecha) y
escribirlos en las dos tablas que usa el puntaje:
    tablas/requisitos_cultivos.csv   y   tablas/ecocrop_cultivos.csv
Solo AGREGA filas de cultivos que todavía no están; nunca cambia una fila existente.

    python -m src.catalogo_equipo            # muestra lo que agregaría (no escribe nada)
    python -m src.catalogo_equipo escribir   # agrega las filas que falten

Reglas del catálogo que se respetan (el catálogo es referencia documental, no reglas validadas):
  - No se promedian rangos de fuentes distintas: se ELIGE una fuente por cultivo. En la Sierra manda
    la fuente andina, y entre ellas la ecuatoriana (INIAP, Basantes 2015); FAO EcoCrop queda como
    el rango que el cultivo aguanta. No se pasa un rango andino a un cultivo de la Costa ni al revés.
  - Lo que el catálogo no trae se deja VACÍO (no se inventa): ese factor no cuenta en el puntaje.
  - Tiempo hasta la cosecha: el catálogo no da un valor general. Se elige UN perfil por cultivo en
    tablas/perfiles_productivos.csv (con su motivo) y se usa el punto medio de SU intervalo.
Decisiones tomadas aquí, sin calibrar (declararlas): el orden de fuentes de arriba; un margen de
1 unidad de pH cuando no hay límite absoluto; cómo se traduce la temperatura de daño por helada a
"tolera / parcial / no" (0 a -1 °C no tolera, -1 a -3 °C parcial, menos de -3 °C tolera).
Los valores de EcoCrop de estas filas se tomaron del catálogo del equipo (que cita cada ficha);
no se volvieron a comprobar uno por uno en la página de la FAO.
"""
import json
from functools import lru_cache

import numpy as np
import pandas as pd

from .config import TABLAS

MARGEN_PH = 1.0
LITORAL = {"S02", "S03", "S23", "PROD03", "PROD04", "PROD05", "PROD06"}   # fuentes de contexto tropical
EXCLUIR_TIPO = ("Hass", "Russet", "sarna", "flor_de_corte", "jardineria", "sintesis_1989",
                "nutricional", "tolerancia_reportada", "experimental", "LT50", "foliolos", "modelo",
                "ambiente_observado_no_requisito")
TEXTURA_ECOCROP = {"heavy": ["arcilloso", "franco arcilloso"], "medium": ["franco"],
                   "light": ["franco arenoso", "arenoso"]}
HELADA_OK = ("tolerancia_general", "dano_por_helada_reportado", "temperatura_critica_dano_visible")
ALIAS = {"temperatura_adaptacion": ("temperatura_adaptacion", "temperatura_media_anual", "temperatura_contexto_andino"),
         "altitud": ("altitud", "altitud_adaptacion", "altitud_zona_produccion")}
TEXTURA_FICHA = {"franca": "franco", "franco_limosa": "franco", "limosa": "franco",
                 "franco_arcillosa": "franco arcilloso", "franco_arcillo_limosa": "franco arcilloso",
                 "franco_arcillo_arenosa": "franco arcilloso", "arcillo_arenosa": "arcilloso",
                 "arcillosa": "arcilloso", "franco_arenosa": "franco arenoso", "arenosa": "arenoso"}
SUELO_VIGENTE = ("activo", "documentado_con_alcance")
A_DIAS = {"dia": 1.0, "mes": 30.4, "año": 365.0}


@lru_cache(maxsize=2)
def cargar(ruta=None):
    ruta = ruta or TABLAS / "catalogo" / "SMARTSEEDS_catalogo_final_v1.1.json"
    with open(ruta, encoding="utf-8") as f:
        cat = json.load(f)
    return cat


def _local(e, region):
    """¿La evidencia es de una fuente del contexto del cultivo (no ECOCROP)?"""
    f = e["fuente_id"]
    if f.startswith("ECO") or any(x in e["tipo"] for x in EXCLUIR_TIPO):
        return False
    return (f in LITORAL) if region == "tropico" else (f not in LITORAL)


def _rango(v):
    if isinstance(v, dict) and v.get("min") is not None and v.get("max") is not None and v["min"] < v["max"]:
        return float(v["min"]), float(v["max"])
    if isinstance(v, dict) and v.get("favorable_min") is not None and v.get("favorable_max") is not None:
        return float(v["favorable_min"]), float(v["favorable_max"])
    return None


def _ref(fuentes, fid):
    r = fuentes.get(fid, fid)
    return r.split(". http")[0][:95]


def perfil(cid, region, cat=None):
    """Rangos elegidos para un cultivo del catálogo en una región, con su fuente."""
    cat = cat or cargar()
    fuentes = {f["id"]: (f.get("referencia") or f.get("titulo") or f["id"]) for f in cat["fuentes"]}
    clima = [e for e in cat["evidencias_agroclimaticas"] if e["cultivo_id"] == cid]
    suelo = [e for e in cat["evidencias_suelo"]
             if e["cultivo_id"] == cid and e.get("estado_documental") in SUELO_VIGENTE]
    p, refs = {}, []
    ecuador = {f["id"] for f in cat["fuentes"]
               if any(t in ((f.get("alcance") or "") + " " + (f.get("referencia") or "")) for t in ("Ecuador", "INIAP", "ecuatorian"))}

    def eco(var):
        return next((e["valor"] for e in clima if e["variable"] == var and e["fuente_id"].startswith("ECO")
                     and isinstance(e["valor"], dict) and "optimo_min" in e["valor"]), None), \
               next((e["fuente_id"] for e in clima if e["variable"] == var and e["fuente_id"].startswith("ECO")), None)

    def local(var, lista=clima):
        cand = [e for e in lista if e["variable"] in ALIAS.get(var, (var,)) and _local(e, region) and _rango(e["valor"])]
        if not cand:
            return None, None
        e = next((x for x in cand if x["fuente_id"] in ecuador), cand[0])     # primero la fuente ecuatoriana
        return _rango(e["valor"]), e["fuente_id"]

    # --- temperatura media
    e, fe = eco("temperatura_adaptacion")
    loc, fl = local("temperatura_adaptacion")
    if not loc and e:        # fuente local que solo da el mínimo: el máximo óptimo se toma de ECOCROP
        ab_local = next((x for x in clima if x["variable"] == "temperatura_adaptacion" and _local(x, region)
                         and isinstance(x["valor"], dict) and x["valor"].get("min") is not None
                         and x["valor"].get("max") is None), None)
        if ab_local and ab_local["valor"]["min"] < e["optimo_max"]:
            loc, fl = (float(ab_local["valor"]["min"]), float(e["optimo_max"])), ab_local["fuente_id"]
    mejor = next((x for x in clima if x["variable"] == "temperatura_optima" and _local(x, region)
                  and x["tipo"] == "rango_media_asociado_mayor_produccion" and _rango(x["valor"])), None)
    if e or loc:
        opt = loc or (e["optimo_min"], e["optimo_max"])
        ab = (e["absoluto_min"], e["absoluto_max"]) if e else (opt[0] - 5, opt[1] + 5)
        if mejor and loc:        # la fuente local da el rango de crecimiento Y el de mayor producción
            ab, opt = loc, _rango(mejor["valor"])
        p.update(temp_opt_min=opt[0], temp_opt_max=opt[1], temp_min=min(ab[0], opt[0]), temp_max=max(ab[1], opt[1]))
        refs.append(f"temperatura {opt[0]:g}–{opt[1]:g} °C: {_ref(fuentes, fl or fe)}"
                    + (f" (ECOCROP mundial da {e['optimo_min']:g}–{e['optimo_max']:g})" if loc and e else ""))
    # --- lluvia anual
    e, fe = eco("precipitacion_anual")
    loc, fl = local("precipitacion_anual")
    if e or loc:
        opt = loc or (e["optimo_min"], e["optimo_max"])
        ab = (e["absoluto_min"], e["absoluto_max"]) if e else (opt[0] * 0.6, opt[1] * 1.5)
        p.update(lluvia_anual_opt_min=opt[0], lluvia_anual_opt_max=opt[1],
                 lluvia_anual_min=min(ab[0], opt[0]), lluvia_anual_max=max(ab[1], opt[1]))
        refs.append(f"lluvia anual {opt[0]:g}–{opt[1]:g} mm: {_ref(fuentes, fl or fe)}")
    # --- agua del ciclo (lluvia del ciclo reportada; si no, necesidad de agua estacional FAO)
    for var in ("precipitacion_ciclo", "demanda_hidrica"):
        ev = next((x for x in clima if x["variable"] == var and _rango(x["valor"])
                   and (x["fuente_id"] not in LITORAL or region == "tropico")
                   and (var == "demanda_hidrica" or _local(x, region))), None)
        if ev:
            p["agua_ciclo_min"] = _rango(ev["valor"])[0]
            refs.append(f"agua en el ciclo {_rango(ev['valor'])[0]:g}–{_rango(ev['valor'])[1]:g} mm: {_ref(fuentes, ev['fuente_id'])}")
            break
    # --- altura
    e, fe = eco("altitud")
    loc, fl = local("altitud")
    tope = e.get("absoluto_max") if e else None
    if loc:
        p.update(altura_min=loc[0], altura_max=loc[1], altura_tope=max(tope or 0, loc[1] + 300))
        refs.append(f"altura {loc[0]:g}–{loc[1]:g} m: {_ref(fuentes, fl)}")
    elif tope:
        p.update(altura_min=0.0, altura_max=float(tope), altura_tope=float(tope) + 300)
        refs.append(f"altura hasta {tope:g} m: {_ref(fuentes, fe)}")
    # --- pH
    ph_eco = next((_rango(x["valor"]) for x in suelo if x["variable"] == "ph" and x["tipo"] == "optimo"), None)
    ph_abs = next((_rango(x["valor"]) for x in suelo if x["variable"] == "ph" and x["tipo"] == "absoluto_segun_ECOCROP"), None)
    loc, fl = local("ph", suelo)
    f_eco = next((x["fuente_id"] for x in suelo if x["variable"] == "ph" and x["tipo"] == "optimo"), None)
    if loc or ph_eco:
        opt = loc or ph_eco
        ab = ph_abs or (opt[0] - MARGEN_PH, opt[1] + MARGEN_PH)
        p.update(ph_opt_min=opt[0], ph_opt_max=opt[1], ph_min=min(ab[0], opt[0]), ph_max=max(ab[1], opt[1]))
        otras = [f"{x['fuente_id']} {_rango(x['valor'])[0]:g}–{_rango(x['valor'])[1]:g}" for x in suelo
                 if x["variable"] == "ph" and _rango(x["valor"]) and x["tipo"] != "absoluto_segun_ECOCROP"
                 and x["fuente_id"] != (fl or f_eco)]
        refs.append(f"pH {opt[0]:g}–{opt[1]:g}: {_ref(fuentes, fl or f_eco)}"
                    + (f" (otras fuentes: {'; '.join(otras)})" if otras else ""))
    # --- textura y drenaje (clases de ECOCROP)
    tx = next((x["valor"] for x in suelo if x["variable"] == "textura_categoria" and x["tipo"] == "optimo"), None)
    if isinstance(tx, str):
        aptas = [t for clase in TEXTURA_ECOCROP if clase in tx for t in TEXTURA_ECOCROP[clase]]
        if aptas:
            p["texturas_aptas"] = ";".join(aptas)
            refs.append(f"textura {tx}: ECOCROP")
    if "texturas_aptas" not in p:      # fichas nuevas: lista de texturas con nombre
        ev = next((x for x in suelo if x["variable"] == "textura" and _local(x, region)
                   and isinstance(x["valor"], (list, str)) and x["tipo"].startswith("referencia")), None)
        if ev:
            nombres = ev["valor"] if isinstance(ev["valor"], list) else [ev["valor"]]
            aptas = list(dict.fromkeys(TEXTURA_FICHA[n] for n in nombres if n in TEXTURA_FICHA))
            if aptas:
                p["texturas_aptas"] = ";".join(aptas)
                refs.append(f"textura {', '.join(n.replace('_', ' ') for n in nombres)}: {_ref(fuentes, ev['fuente_id'])}")
    dr = next((x["valor"] for x in suelo if x["variable"] == "drenaje_categoria" and x["tipo"] == "optimo"), None)
    if isinstance(dr, str):
        p["tolerancia_encharcamiento"] = 0.1 if dr.startswith("well") else 0.5
        refs.append(f"drenaje {dr}: ECOCROP")
    else:
        ev = next((x for x in suelo if x["variable"] == "drenaje" and _local(x, region)
                   and x["tipo"].startswith("referencia")), None)
        if ev:
            txt = " ".join(ev["valor"]) if isinstance(ev["valor"], list) else str(ev["valor"])
            p["tolerancia_encharcamiento"] = 0.5 if "moderad" in txt else 0.1
            refs.append(f"drenaje {txt.replace('_', ' ')}: {_ref(fuentes, ev['fuente_id'])}")
    # --- pendiente máxima del terreno, si la ficha la da (en %; el motor trabaja en grados)
    ev = next((x for x in suelo if x["variable"] == "pendiente_terreno" and _local(x, region)
               and isinstance(x["valor"], dict) and x["valor"].get("max") is not None), None)
    if ev:
        p["pendiente_max"] = round(float(np.degrees(np.arctan(ev["valor"]["max"] / 100))), 1)
        refs.append(f"pendiente hasta {ev['valor']['max']:g} % (~{p['pendiente_max']:g}°): {_ref(fuentes, ev['fuente_id'])}")
    # --- materia orgánica: solo si la fuente da un porcentaje
    mo = next((x["valor"] for x in suelo if x["variable"] == "materia_organica"
               and isinstance(x["valor"], str) and "%" in x["valor"] and _local(x, region)), None)
    if mo:
        p["mo_min"] = float(mo.split("%")[0].split()[-1])
        refs.append(f"materia orgánica: {mo}")
    # --- helada: temperatura de daño documentada -> clase de tolerancia (decisión del motor)
    for x in clima:
        if x["variable"] != "helada":
            continue
        if isinstance(x["valor"], dict) and any(t in x["tipo"] for t in HELADA_OK):
            t = float(next(iter(x["valor"].values())))
            p.update(helada_dano_c=t, tolerancia_helada=0.1 if t >= -1 else 0.4 if t >= -3 else 0.7)
            refs.append(f"helada: daño reportado hacia {t:g} °C"
                        + (f" en {x['etapa'].replace('_', ' ')}" if x.get("etapa") else "") + f": {_ref(fuentes, x['fuente_id'])}")
            break
        if x["valor"] is None and "cualitativa" in x["tipo"]:
            p["tolerancia_helada"] = 0.1
            refs.append(f"helada: sensible (sin temperatura){' en ' + x['etapa'] if x.get('etapa') else ''}: {_ref(fuentes, x['fuente_id'])}")
            break
    p["referencias"] = refs
    return p


def _dias(e):
    v, k = e["valor"], A_DIAS.get(e["unidad"])
    if k is None or not isinstance(v, dict) or v.get("min") is None or v.get("max") is None:
        return None
    return v["min"] * k, v["max"] * k


@lru_cache(maxsize=2)
def _seleccion(ruta=None):
    ruta = ruta or TABLAS / "perfiles_productivos.csv"
    if not ruta.exists():
        return {}
    t = pd.read_csv(ruta, keep_default_na=False)
    return {f["cultivo"]: f for _, f in t.iterrows()}


def produccion(cultivo, cat=None):
    """Ciclo y rendimiento técnico del perfil que el motor eligió para un cultivo
    (tablas/perfiles_productivos.csv). Solo lo que el catálogo documenta; lo demás queda ausente."""
    cat = cat or cargar()
    sel = _seleccion().get(cultivo)
    if sel is None:
        return {}
    ev = {e["id"]: e for e in cat["evidencias_productivas"]}
    fuentes = {f["id"]: (f.get("referencia") or f.get("titulo") or f["id"]) for f in cat["fuentes"]}
    r = {"perfil_motivo": sel["motivo"]}
    ids = [i for i in sel["evidencias_ciclo"].split("+") if i]
    tramos = [(ev[i], _dias(ev[i])) for i in ids if i in ev]
    if tramos and all(d for _, d in tramos):
        lo, hi = sum(d[0] for _, d in tramos), sum(d[1] for _, d in tramos)
        e0, e1 = tramos[0][0], tramos[-1][0]
        r.update(ciclo_min=round(lo), ciclo_max=round(hi), ciclo_dias=int(round((lo + hi) / 2)),
                 ciclo_evento=f"{e0['evento_inicio']} → {e1['evento_fin']}".replace("_", " "),
                 ciclo_fuente=f"{e0.get('perfil', '').replace('_', ' ')} ({', '.join(ids)}): {_ref(fuentes, e0['fuente_id'])}")
    e = ev.get(sel["evidencia_rendimiento"])
    if e is not None and e.get("operador") in ("intervalo_reportado", "valor_puntual_reportado") \
            and e["unidad"] in ("t/ha", "kg/ha") and isinstance(e["valor"], dict) and e["valor"].get("min") is not None:
        k = 0.001 if e["unidad"] == "kg/ha" else 1.0
        r.update(rend_tecnico_min=round(e["valor"]["min"] * k, 2), rend_tecnico_max=round(e["valor"]["max"] * k, 2),
                 rend_tecnico_nota=f"{e['tipo'].replace('_', ' ')}, {(e.get('perfil') or '').replace('_', ' ')}, "
                                   f"{(e.get('producto') or '').replace('_', ' ')} ({e['id']}): {_ref(fuentes, e['fuente_id'])}")
    return r




# ---------------------------------------------------------------------------
# Del catálogo a las tablas del puntaje
# ---------------------------------------------------------------------------
# clave en las tablas -> (id en el catálogo, región de sus fuentes, tipo, nombre científico)
CULTIVOS_NUEVOS = {
    "arveja": ("C002", "sierra", "ciclo_corto", "Pisum sativum"),
    "lenteja": ("C004", "sierra", "ciclo_corto", "Lens culinaris"),
    "chocho": ("C005", "sierra", "ciclo_corto", "Lupinus mutabilis"),
    "trigo": ("C006", "sierra", "ciclo_corto", "Triticum aestivum"),
    "cebada": ("C007", "sierra", "ciclo_corto", "Hordeum vulgare"),
    "amaranto": ("C010", "sierra", "ciclo_corto", "Amaranthus caudatus"),
    "cebolla_blanca": ("C022", "sierra", "ciclo_corto", "Allium fistulosum"),
    "uvilla": ("C020", "sierra", "semipermanente", "Physalis peruviana"),
    "mora_de_castilla": ("C019", "sierra", "permanente", "Rubus glaucus"),
    "aguacate": ("C018", "sierra", "permanente", "Persea americana"),
}
# Cultivos de la Sierra muy sembrados que NO se pueden agregar todavía: el catálogo v1.1 solo trae
# su tiempo de cultivo y su rendimiento, no su clima ni su suelo (sin esos rangos no hay puntaje).
SIN_CLIMA_EN_EL_CATALOGO = ["brócoli", "zanahoria"]
# El fréjol (C001) NO se agrega solo: el catálogo solo trae para él la ficha mundial de EcoCrop (sin franja de
# altura del Ecuador), y con eso saca entre 75 y 100 puntos en la Costa y cambia el orden de Santo Domingo
# y Daule. Es una decisión de los dos programadores. Para agregarlo, poner esta línea en CULTIVOS_NUEVOS:
#     "frejol": ("C001", "sierra", "ciclo_corto", "Phaseolus vulgaris"),


def _ecocrop(cid, cat):
    """Valores de la ficha de FAO EcoCrop que guarda el catálogo para un cultivo ({} si no hay)."""
    clima = [e for e in cat["evidencias_agroclimaticas"] if e["cultivo_id"] == cid and e["fuente_id"].startswith("ECO")]
    suelo = [e for e in cat["evidencias_suelo"] if e["cultivo_id"] == cid and e["fuente_id"].startswith("ECO")]
    if not clima:
        return {}
    por = {e["variable"]: e["valor"] for e in clima if isinstance(e["valor"], dict) and "optimo_min" in e["valor"]}
    codigo = clima[0]["fuente_id"][3:]
    fila = {"codigo_ecocrop": codigo, "url": f"https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id={codigo}"}
    t, ll, alt = por.get("temperatura_adaptacion"), por.get("precipitacion_anual"), por.get("altitud")
    if t:
        fila.update(temp_opt_min_C=t["optimo_min"], temp_opt_max_C=t["optimo_max"],
                    temp_abs_min_C=t["absoluto_min"], temp_abs_max_C=t["absoluto_max"])
    if ll:
        fila.update(lluvia_opt_min_mm=ll["optimo_min"], lluvia_opt_max_mm=ll["optimo_max"],
                    lluvia_abs_min_mm=ll["absoluto_min"], lluvia_abs_max_mm=ll["absoluto_max"])
    if alt and alt.get("absoluto_max") is not None:
        fila["altitud_max_m"] = alt["absoluto_max"]
    ph_opt = next((_rango(e["valor"]) for e in suelo if e["variable"] == "ph" and e["tipo"] == "optimo"), None)
    ph_abs = next((_rango(e["valor"]) for e in suelo if e["variable"] == "ph" and e["tipo"] == "absoluto_segun_ECOCROP"), None)
    if ph_opt and ph_abs:
        fila.update(ph_opt_min=ph_opt[0], ph_opt_max=ph_opt[1], ph_abs_min=ph_abs[0], ph_abs_max=ph_abs[1])
    dr = next((e["valor"] for e in suelo if e["variable"] == "drenaje_categoria" and e["tipo"] == "optimo"), None)
    if isinstance(dr, str):
        fila["drenaje_optimo"] = dr
    return fila


def filas_del_cultivo(clave, cat=None):
    """(fila para requisitos_cultivos.csv, fila para ecocrop_cultivos.csv o None, avisos)."""
    cat = cat or cargar()
    cid, region, tipo, cientifico = CULTIVOS_NUEVOS[clave]
    p, pr, eco = perfil(cid, region, cat), produccion(clave, cat), _ecocrop(cid, cat)
    ref = {r.split(":")[0].split(" ")[0]: r for r in p["referencias"]}      # "temperatura", "altura", "pH"...
    avisos = []

    def fuente_de(factor):
        r = ref.get(factor, "")
        return r.split(": ", 1)[1].split(" (ECOCROP mundial")[0].split(" (otras fuentes")[0] if ": " in r else ""

    req = {"cultivo": clave, "nombre_cientifico": cientifico, "tipo": tipo,
           "altitud_min_m": p.get("altura_min"), "altitud_max_m": p.get("altura_max"),
           "temp_min_C": p.get("temp_opt_min"), "temp_max_C": p.get("temp_opt_max"),
           "lluvia_min_mm_anio": p.get("lluvia_anual_opt_min"), "lluvia_max_mm_anio": p.get("lluvia_anual_opt_max"),
           "pendiente_max_grados": p.get("pendiente_max"),
           "tolera_encharcamiento": {0.1: "no", 0.5: "parcial"}.get(p.get("tolerancia_encharcamiento"), ""),
           "necesita_drenaje": "si" if p.get("tolerancia_encharcamiento") in (0.1, 0.5) else "",
           "ciclo_meses": round(pr["ciclo_dias"] / 30.4) if "ciclo_dias" in pr else None}
    partes = [f"{f}: {fuente_de(f)}" for f in ("temperatura", "lluvia", "altura") if fuente_de(f)]
    if "ciclo_fuente" in pr:
        partes.append("tiempo de cultivo: " + pr["ciclo_fuente"].split("): ", 1)[-1])
    req["fuente"] = "Catálogo del equipo v1.1 · " + " · ".join(partes)
    faltan = [n for n, c in (("altura", "altitud_max_m"), ("temperatura", "temp_min_C"), ("lluvia del año", "lluvia_min_mm_anio"),
                             ("pendiente máxima", "pendiente_max_grados"), ("drenaje", "necesita_drenaje"),
                             ("tiempo de cultivo", "ciclo_meses")) if req[c] in (None, "")]
    req["notas"] = ("Referencia documental sin validación local (Sierra)."
                    + (f" El catálogo no trae: {', '.join(faltan)}." if faltan else ""))
    # Helada: solo si el catálogo documenta la temperatura de daño o la sensibilidad
    if "tolerancia_helada" in p:
        req["tolera_heladas"] = {0.1: "no", 0.4: "parcial", 0.7: "si"}[p["tolerancia_helada"]]
        req["helada_fuente"] = ref.get("helada:", ref.get("helada", "")).replace("helada: ", "")
    else:
        avisos.append("sin dato de helada")
    if faltan:
        avisos.append("sin " + ", ".join(faltan))

    fila_eco = None
    if eco:
        fila_eco = {"cultivo": clave, "nombre_ecocrop": cientifico, **eco}
        local = "temperatura" in ref and ("ECOCROP mundial da" in ref["temperatura"] or "ECOCROP" not in ref["temperatura"].upper())
        if local and p.get("temp_opt_min") is not None:
            fila_eco.update(temp_opt_min_ecuador_C=p["temp_opt_min"], temp_opt_max_ecuador_C=p["temp_opt_max"],
                            fuente_ecuador=fuente_de("temperatura") + ". Tomado del catálogo del equipo v1.1")
    return req, fila_eco, avisos


def _texto(v):
    """Número sin decimales de sobra ("2600", no "2600.0"); vacío si no hay dato."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    return f"{v:g}" if isinstance(v, (int, float, np.integer, np.floating)) else str(v)


def _agregar_filas(ruta, filas_nuevas, columnas_nuevas=(), valores=None):
    """Agrega filas (y columnas vacías) a un CSV SIN reescribir las filas que ya estaban.

    `valores` = {cultivo: {columna: valor}} para llenar columnas nuevas en filas existentes.
    """
    import csv
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    cabecera = filas[0]
    for col in columnas_nuevas:
        if col not in cabecera:
            cabecera.append(col)
    for fila in filas[1:]:
        fila += [""] * (len(cabecera) - len(fila))
        for col, v in (valores or {}).get(fila[0], {}).items():
            fila[cabecera.index(col)] = v
    ya = {fila[0] for fila in filas[1:]}
    for nueva in filas_nuevas:
        if nueva["cultivo"] not in ya:
            filas.append([_texto(nueva.get(col)) for col in cabecera])
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(filas)


# Helada de los cultivos andinos que YA estaban en la tabla (lo que el catálogo v1.1 documenta)
HELADA_DE_LOS_QUE_YA_ESTABAN = {"papa": "C011", "quinua": "C009", "haba": "C003", "maiz_suave": "C008"}


def agregar_a_las_tablas(escribir=False):
    """Agrega a las dos tablas los cultivos de CULTIVOS_NUEVOS que todavía no estén."""
    cat = cargar()
    ya_req = set(pd.read_csv(TABLAS / "requisitos_cultivos.csv")["cultivo"])
    ya_eco = set(pd.read_csv(TABLAS / "ecocrop_cultivos.csv")["cultivo"])
    nuevas_req, nuevas_eco = [], []
    for clave in CULTIVOS_NUEVOS:
        req, eco, avisos = filas_del_cultivo(clave, cat)
        if clave not in ya_req:
            nuevas_req.append(req)
        if eco and clave not in ya_eco:
            nuevas_eco.append(eco)
        print(f"{clave:17} altura {_texto(req['altitud_min_m'])}–{_texto(req['altitud_max_m'])} m · "
              f"temp {_texto(req['temp_min_C'])}–{_texto(req['temp_max_C'])} °C · "
              f"lluvia {_texto(req['lluvia_min_mm_anio']) or '?'}–{_texto(req['lluvia_max_mm_anio']) or '?'} mm · "
              f"{_texto(req['ciclo_meses'])} meses · helada: {req.get('tolera_heladas', '—')}"
              + (f"   [{'; '.join(avisos)}]" if avisos else ""))
    helada = {}
    for clave, cid in HELADA_DE_LOS_QUE_YA_ESTABAN.items():
        p = perfil(cid, "sierra", cat)
        if "tolerancia_helada" in p:
            fuente = next(r for r in p["referencias"] if r.startswith("helada")).replace("helada: ", "")
            helada[clave] = {"tolera_heladas": {0.1: "no", 0.4: "parcial", 0.7: "si"}[p["tolerancia_helada"]],
                             "helada_fuente": fuente + " (catálogo del equipo v1.1)"}
    print("Helada documentada en cultivos que ya estaban:", {k: v["tolera_heladas"] for k, v in helada.items()})
    if not escribir:
        print(f"\nSe agregarían {len(nuevas_req)} filas a requisitos_cultivos.csv y {len(nuevas_eco)} a "
              "ecocrop_cultivos.csv. Para escribir: python -m src.catalogo_equipo escribir")
        return nuevas_req, nuevas_eco
    _agregar_filas(TABLAS / "requisitos_cultivos.csv", nuevas_req, ("tolera_heladas", "helada_fuente"), helada)
    _agregar_filas(TABLAS / "ecocrop_cultivos.csv", nuevas_eco)
    print(f"\nAgregadas {len(nuevas_req)} filas a requisitos_cultivos.csv y {len(nuevas_eco)} a ecocrop_cultivos.csv.")
    return nuevas_req, nuevas_eco


if __name__ == "__main__":
    import sys
    agregar_a_las_tablas(escribir="escribir" in sys.argv[1:])
