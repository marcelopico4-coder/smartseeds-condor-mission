"""
Aptitud física de un terreno para cada cultivo (0 a 100) y sus razones.

Contrato:  aptitud(fila_celda, fila_cultivo) -> 0..100

Cómo se calcula (regla inicial, fácil de explicar y de ajustar):
  - Cada factor (altura, temperatura, lluvia, pendiente, acidez del suelo, encharcamiento,
    agua en invierno o en los terrenos vecinos, heladas, humedad) recibe una nota de 0 a 1.
  - Temperatura, lluvia y acidez (pH) usan DOS rangos por cultivo (tablas/ecocrop_cultivos.csv):
    el IDEAL, donde la nota es 1, y el que el cultivo AGUANTA, donde la nota llega a 0.
    Entre uno y otro la nota baja en línea recta. Así dos terrenos parecidos ya no reciben
    los dos un 100: recibe más el que está más cerca de lo ideal.
  - Altura y pendiente: nota 1 dentro del rango y baja al alejarse (los MARGENES de abajo).
    Si un cultivo no tiene los dos rangos, temperatura y lluvia también se calculan así.
  - Puntaje = 100 x (0,6 x la peor nota + 0,4 x el promedio).
    Así manda el factor limitante: de nada sirve la lluvia perfecta si hace frío.
  - Si falta un dato (por ejemplo, NISAR fuera de las zonas detalladas), ese
    factor no cuenta y se avisa en las razones.
"""
from __future__ import annotations

import math

import pandas as pd

from .config import TABLAS

MARGEN_ALTURA_M = 300      # metros fuera del rango hasta llegar a nota 0
MARGEN_TEMP_C = 3          # grados fuera del rango
MARGEN_LLUVIA = 0.30       # 30 % por debajo del mínimo / por encima del máximo
MARGEN_PENDIENTE = 15      # grados por encima de la pendiente máxima
PESO_PEOR_FACTOR = 0.6
HUMEDAD_CONFIABLE_MIN = 0.5   # mínimo de datos "recomendados" para usar la humedad en el puntaje
AGUA_VISIBLE = 0.05           # el terreno "tuvo agua" si el radar la vio en al menos el 5 % de las pasadas

# Riego. El agricultor dice si tiene riego (celda["riego"] = True). Regla:
#   - El riego SOLO arregla la FALTA de agua (poca lluvia, suelo que se seca).
#     No cambia la altura, la temperatura, la pendiente, el exceso de lluvia ni la inundación.
#   - Tampoco borra la falta de agua: la reduce. Mientras más agua haya que poner
#     con el riego, menos puntos. Así "tengo riego" no pone a todos los cultivos en 100.
#   - Nota de lluvia con riego = 1 - PESO_FALTA_AGUA_CON_RIEGO x (parte del agua que falta).
#     Ejemplo: si la lluvia cubre el 77 % de lo que pide el cultivo, falta el 23 % y la
#     nota es 1 - 0,5 x 0,23 = 0,89. Si no lloviera nada, la nota sería 0,5.
# El 0,5 es un valor inicial sin calibrar (declararlo como limitación).
PESO_FALTA_AGUA_CON_RIEGO = 0.5

# Lluvia de más. La lluvia del año por encima de lo ideal no mata al cultivo como la falta de agua:
# el daño llega por el mal drenaje y las enfermedades, y eso ya se mide aparte (pendiente,
# encharcamiento y humedad del radar). Por eso llover de más resta, como máximo, la mitad de la nota.
# Valor inicial sin calibrar (declararlo como limitación).
PESO_EXCESO_LLUVIA = 0.5

# Cultivos de CICLO CORTO: ocupan el terreno pocos meses, así que no se comparan con la lluvia de
# todo el año sino con la de los meses del cultivo (`ciclo_meses`), sembrando en el mes que más
# conviene. Hace falta la lluvia de cada mes: celda["lluvia_mensual"], una lista de 12 números
# (en las zonas detalladas viene de CHELSA; en el resto del país, de NASA POWER).
# Si no está, se usa la lluvia del año y llover de más no resta (no se puede saber si sobra agua).
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

# Agua en los terrenos vecinos (columna `agua_vecinos`, de src/vecindad.py): parte de los cuadros a
# menos de 1 km donde el radar vio agua. Con la mitad de los vecinos con agua, un cultivo que no
# soporta el encharcamiento recibe nota 0. Valor inicial sin calibrar.
AGUA_VECINOS_MAX = 0.5
AGUA_VECINOS_MINIMA = 0.05    # menos del 5 % de vecinos con agua se cuenta como "nada"
# Agua en invierno (columna `agua_invierno`, de src/sentinel.py): parte del terreno con agua entre
# enero y mayo según el radar Sentinel-1. Se evalúa con los mismos límites del encharcamiento.
# Cuando la celda trae este dato, los vecinos NO cuentan en el puntaje: servían para suponer si el
# terreno se moja en invierno, y aquí eso ya está medido.

# Heladas (columna `helada`, de src/heladas.py; solo en las zonas de la Sierra): riesgo de 0 a 1 en el
# mes más frío del año. Cuánto resta depende de lo que aguanta el cultivo (columna `tolera_heladas` de
# requisitos_cultivos.csv: "no", "parcial" o "si"). Nota = 1 - riesgo x (1 - aguante).
# Si el cultivo no tiene ese dato, la helada se muestra pero NO cuenta en el puntaje.
# Los tres aguantes son valores iniciales sin calibrar (declararlo como limitación).
AGUANTE_HELADA = {"no": 0.1, "parcial": 0.4, "si": 0.7}
# APAGADO el 14 nov (decisión del equipo): solo 6 cultivos tienen dato de cuánto aguantan la helada
# (papa, chocho, amaranto, trigo, cebada y quinua). Con el factor encendido la papa bajaba y el maíz
# suave, el haba y la arveja no, solo porque les falta la fuente, y quedaban por encima sin merecerlo.
# Mientras esté en False la helada se MUESTRA como aviso en cada cultivo pero no cambia ningún puntaje.
# Volver a True cuando `tolera_heladas` tenga fuente para todos los cultivos de la Sierra.
HELADAS_EN_PUNTAJE = False
RIESGO_HELADA_MINIMO = 0.05   # menos del 5 % de riesgo se cuenta como "sin heladas"

ALTURA_CULTIVO_ANDINO_M = 1500   # un cultivo cuya altura mínima es esta o más se trata como andino

COLUMNAS_RANGOS = ["temp_opt_min_C", "temp_opt_max_C", "temp_abs_min_C", "temp_abs_max_C",
                   "lluvia_opt_min_mm", "lluvia_opt_max_mm", "lluvia_abs_min_mm", "lluvia_abs_max_mm",
                   "ph_opt_min", "ph_opt_max", "ph_abs_min", "ph_abs_max"]


def cargar_requisitos(ruta=None) -> pd.DataFrame:
    """Lee tablas/requisitos_cultivos.csv y le une los rangos ideal y tolerable de cada cultivo.

    Los rangos vienen de tablas/ecocrop_cultivos.csv (fichas de FAO EcoCrop). En los cultivos
    andinos que tienen un rango de temperatura del Ecuador (columnas `..._ecuador_C`, del catálogo
    del equipo), ese rango reemplaza al ideal de EcoCrop, que es mundial.
    """
    requisitos = pd.read_csv(ruta or TABLAS / "requisitos_cultivos.csv")
    ruta_rangos = TABLAS / "ecocrop_cultivos.csv"
    if ruta is not None or not ruta_rangos.exists():
        return requisitos
    rangos = pd.read_csv(ruta_rangos)
    if "temp_opt_min_ecuador_C" in rangos:
        andino = rangos["temp_opt_min_ecuador_C"].notna() & rangos["temp_opt_max_ecuador_C"].notna()
        rangos.loc[andino, "temp_opt_min_C"] = rangos.loc[andino, "temp_opt_min_ecuador_C"]
        rangos.loc[andino, "temp_opt_max_C"] = rangos.loc[andino, "temp_opt_max_ecuador_C"]
        # el rango que aguanta nunca puede ser más angosto que el ideal
        rangos["temp_abs_min_C"] = rangos[["temp_abs_min_C", "temp_opt_min_C"]].min(axis=1)
        rangos["temp_abs_max_C"] = rangos[["temp_abs_max_C", "temp_opt_max_C"]].max(axis=1)
    else:
        andino = pd.Series(False, index=rangos.index)
    unidos = requisitos.merge(rangos[["cultivo"] + COLUMNAS_RANGOS], on="cultivo", how="left")
    # Cultivos de altura (desde ALTURA_CULTIVO_ANDINO_M) SIN rango de temperatura del Ecuador:
    # la temperatura de EcoCrop no se usa, porque es mundial y deja mal a la papa en los Andes
    # (su ideal es 15–25 °C). Siguen con el rango de requisitos_cultivos.csv hasta tener una
    # fuente ecuatoriana (INIAP).
    con_rango_ecuador = set(rangos.loc[andino, "cultivo"])
    de_altura = (pd.to_numeric(unidos["altitud_min_m"], errors="coerce") >= ALTURA_CULTIVO_ANDINO_M)
    sin_fuente = de_altura & ~unidos["cultivo"].isin(con_rango_ecuador)
    unidos.loc[sin_fuente, [c for c in COLUMNAS_RANGOS if c.startswith("temp_")]] = float("nan")
    return unidos


def _num(x):
    """Convierte a número; vacío o NaN -> None."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def _nota_rango(valor, minimo, maximo, margen_bajo, margen_alto):
    """1 dentro de [minimo, maximo]; baja a 0 al alejarse. None si falta el dato."""
    if valor is None or (minimo is None and maximo is None):
        return None
    if minimo is not None and valor < minimo:
        return max(0.0, 1 - (minimo - valor) / margen_bajo)
    if maximo is not None and valor > maximo:
        return max(0.0, 1 - (valor - maximo) / margen_alto)
    return 1.0


def _factor_rango(nombre, unidad, valor, minimo, maximo, margen_bajo, margen_alto,
                  bajo, alto, decimales=0):
    """Evalúa un factor con rango y redacta la razón en lenguaje sencillo."""
    if valor is None:
        return {"factor": nombre, "nota": None, "texto": f"{nombre}: sin dato para este punto"}
    nota = _nota_rango(valor, minimo, maximo, margen_bajo, margen_alto)
    if nota is None:
        return {"factor": nombre, "nota": None,
                "texto": f"{nombre}: falta el requisito del cultivo en la tabla"}
    v = f"{valor:.{decimales}f} {unidad}"
    if minimo is not None and maximo is not None:
        rango = f"{minimo:g}–{maximo:g} {unidad}"
    elif minimo is not None:
        rango = f"mínimo {minimo:g} {unidad}"
    else:
        rango = f"máximo {maximo:g} {unidad}"
    if nota >= 1:
        texto = f"{nombre} {v}: adecuada (necesita {rango})"
    elif minimo is not None and valor < minimo:
        texto = f"{nombre} {v}: {bajo} (necesita {rango})"
    else:
        texto = f"{nombre} {v}: {alto} (necesita {rango})"
    return {"factor": nombre, "nota": nota, "texto": texto}


def _nota_optimo(valor, opt_min, opt_max, abs_min, abs_max, piso_alto=0.0):
    """1 dentro del rango ideal; baja en línea recta hasta 0 en el límite que el cultivo aguanta.

    `piso_alto` es la nota mínima cuando el valor se pasa por arriba (se usa en la lluvia de más).
    """
    if valor < opt_min:
        return 0.0 if valor <= abs_min else (valor - abs_min) / (opt_min - abs_min)
    if valor > opt_max:
        if valor >= abs_max:
            return piso_alto
        return 1 - (1 - piso_alto) * (valor - opt_max) / (abs_max - opt_max)
    return 1.0


def _factor_optimo(nombre, unidad, valor, rango, palabras, decimales=0, piso_alto=0.0, consejo_alto=""):
    """Factor con rango ideal y rango que aguanta. `rango` = (opt_min, opt_max, abs_min, abs_max).

    `palabras` = (poco, muy poco, mucho, demasiado): cómo se dice cada caso en lenguaje sencillo.
    """
    if valor is None:
        return {"factor": nombre, "nota": None, "texto": f"{nombre}: sin dato para este punto"}
    opt_min, opt_max, abs_min, abs_max = rango
    nota = _nota_optimo(valor, opt_min, opt_max, abs_min, abs_max, piso_alto)
    poco, muy_poco, mucho, demasiado = palabras
    v = f"{valor:.{decimales}f} {unidad}".strip()
    ideal = f"lo mejor es {opt_min:g}–{opt_max:g} {unidad}".strip()
    if opt_min <= valor <= opt_max:
        texto = f"{nombre} {v}: ideal para este cultivo ({ideal})"
    elif valor < opt_min and valor > abs_min:
        texto = f"{nombre} {v}: {poco}. El cultivo se da, pero no en su mejor condición ({ideal}; aguanta desde {abs_min:g})"
    elif valor < opt_min:
        texto = f"{nombre} {v}: {muy_poco} para este cultivo (aguanta desde {abs_min:g} {unidad})".replace(" )", ")")
    elif valor < abs_max:
        texto = f"{nombre} {v}: {mucho}. El cultivo se da, pero no en su mejor condición ({ideal}; aguanta hasta {abs_max:g})"
        texto += consejo_alto
    else:
        texto = f"{nombre} {v}: {demasiado} para este cultivo (aguanta hasta {abs_max:g} {unidad})".replace(" )", ")")
        texto += consejo_alto
    return {"factor": nombre, "nota": nota, "texto": texto}


def _lluvia_del_ciclo(celda: dict, cultivo: dict, rango, riego: bool) -> dict | None:
    """Factor de lluvia de un cultivo de ciclo corto: la lluvia de sus meses, en la mejor época.

    Prueba sembrar en cada uno de los 12 meses, suma la lluvia de los meses que dura el cultivo
    y se queda con el mes de siembra que da la mejor nota. Devuelve None si no aplica (el cultivo
    no es de ciclo corto o falta la lluvia mensual): entonces se usa la lluvia del año.
    """
    if str(cultivo.get("tipo", "")).strip().lower() != "ciclo_corto":
        return None
    mensual, meses = celda.get("lluvia_mensual"), _num(cultivo.get("ciclo_meses"))
    if not isinstance(mensual, (list, tuple)) or len(mensual) != 12 or meses is None:
        return None
    mensual, meses = [_num(v) for v in mensual], int(round(meses))
    if None in mensual or not 1 <= meses <= 11:
        return None
    opt_min, opt_max, abs_min, abs_max = rango
    mejor = None
    for inicio in range(12):
        total = sum(mensual[(inicio + k) % 12] for k in range(meses))
        nota = _nota_optimo(total, opt_min, opt_max, abs_min, abs_max)
        if riego and total < opt_min:     # con riego la falta de agua resta menos (regla del riego)
            nota = 1 - PESO_FALTA_AGUA_CON_RIEGO * (opt_min - total) / opt_min
        if mejor is None or nota > mejor[0] + 1e-9:
            mejor = (nota, inicio, total)
    nota, inicio, total = mejor
    cuando = f"Lluvia: sembrando en {MESES[inicio]}, en los {meses} meses del cultivo caen unos {total:.0f} mm"
    ideal = f"lo mejor es {opt_min:g}–{opt_max:g} mm en el ciclo"
    if opt_min <= total <= opt_max:
        texto = f"{cuando}: ideal para este cultivo ({ideal})"
    elif total < opt_min and riego:
        texto = (f"{cuando}: no alcanza ({ideal}). Con tu riego sí se puede, pero tendrás que regar "
                 f"lo que falta: unos {opt_min - total:.0f} mm en el ciclo")
    elif total < opt_min and total > abs_min:
        texto = f"{cuando}: llueve menos de lo ideal ({ideal}; aguanta desde {abs_min:g}). Con riego mejoraría"
    elif total < opt_min:
        texto = f"{cuando}: llueve demasiado poco para este cultivo sin riego (aguanta desde {abs_min:g} mm)"
    else:
        texto = (f"{cuando}: llueve más de lo ideal incluso en la mejor época ({ideal}; aguanta hasta "
                 f"{abs_max:g}). Hace falta buen drenaje")
    return {"factor": "Lluvia", "nota": nota, "texto": texto}


def _rango_graduado(cultivo: dict, prefijo: str, sufijo: str):
    """(opt_min, opt_max, abs_min, abs_max) de un cultivo, o None si falta alguno de los cuatro."""
    valores = tuple(_num(cultivo.get(f"{prefijo}_{parte}{sufijo}"))
                    for parte in ("opt_min", "opt_max", "abs_min", "abs_max"))
    return None if None in valores else valores


def aptitud_detalle(celda: dict, cultivo: dict) -> dict:
    """Puntaje y explicación. Devuelve {"puntaje": 0..100 o None, "factores": [...]}."""
    alt_min, alt_max = _num(cultivo.get("altitud_min_m")), _num(cultivo.get("altitud_max_m"))
    t_min, t_max = _num(cultivo.get("temp_min_C")), _num(cultivo.get("temp_max_C"))
    ll_min, ll_max = _num(cultivo.get("lluvia_min_mm_anio")), _num(cultivo.get("lluvia_max_mm_anio"))
    pen_max = _num(cultivo.get("pendiente_max_grados"))
    tolera = str(cultivo.get("tolera_encharcamiento", "")).strip().lower()
    drenaje = str(cultivo.get("necesita_drenaje", "")).strip().lower()

    rango_temp = _rango_graduado(cultivo, "temp", "_C")
    rango_lluvia = _rango_graduado(cultivo, "lluvia", "_mm")
    rango_ph = _rango_graduado(cultivo, "ph", "")

    factores = [_factor_rango("Altura", "m", _num(celda.get("altura")), alt_min, alt_max,
                              MARGEN_ALTURA_M, MARGEN_ALTURA_M, "muy baja", "muy alta")]
    if rango_temp:
        factores.append(_factor_optimo(
            "Temperatura", "°C", _num(celda.get("temp")), rango_temp,
            ("algo fría", "demasiado fría", "algo caliente", "demasiado caliente"), decimales=1))
    else:
        factores.append(_factor_rango("Temperatura", "°C", _num(celda.get("temp")), t_min, t_max,
                                      MARGEN_TEMP_C, MARGEN_TEMP_C, "muy frío", "muy caliente", decimales=1))
    riego = celda.get("riego") is True
    lluvia = _num(celda.get("lluvia"))
    lluvia_del_ciclo = _lluvia_del_ciclo(celda, cultivo, rango_lluvia, riego) if rango_lluvia else None
    if lluvia_del_ciclo:
        factores.append(lluvia_del_ciclo)
    elif rango_lluvia:
        ciclo_corto = str(cultivo.get("tipo", "")).strip().lower() == "ciclo_corto"
        factores.append(_factor_optimo(
            "Lluvia", "mm/año", _num(celda.get("lluvia")), rango_lluvia,
            ("llueve menos de lo ideal", "llueve demasiado poco", "llueve más de lo ideal",
             "llueve mucho más de lo que conviene"),
            piso_alto=1.0 if ciclo_corto else 1 - PESO_EXCESO_LLUVIA,
            consejo_alto=(". Como es de ciclo corto, se puede sembrar en los meses menos lluviosos" if ciclo_corto
                          else ". Hace falta buen drenaje y hay más riesgo de enfermedades")))
        ll_min = rango_lluvia[0]      # con riego, la falta de agua se mide contra la lluvia ideal
    else:
        factores.append(_factor_rango("Lluvia", "mm/año", _num(celda.get("lluvia")), ll_min, ll_max,
                                      (ll_min or 1) * MARGEN_LLUVIA, (ll_max or 1) * MARGEN_LLUVIA,
                                      "llueve poco", "llueve demasiado"))

    # Riego: si la lluvia no alcanza pero hay riego, la falta resta menos (ver regla arriba)
    if not lluvia_del_ciclo and riego and lluvia is not None and ll_min is not None and lluvia < ll_min:
        falta = ll_min - lluvia
        factores[-1] = {
            "factor": "Lluvia", "nota": 1 - PESO_FALTA_AGUA_CON_RIEGO * falta / ll_min,
            "texto": f"Lluvia {lluvia:.0f} mm/año: no alcanza (necesita mínimo {ll_min:g} mm/año). "
                     f"Con tu riego sí se puede, pero tendrás que regar lo que falta: "
                     f"unos {falta:.0f} mm al año"}

    # Si la lluvia no alcanza pero el radar vio agua sobre el terreno y el cultivo vive en el agua
    # (arroz), el agua ya está ahí: la falta de lluvia no resta.
    aguas = [a for a in (_num(celda.get("encharcamiento")), _num(celda.get("agua_invierno"))) if a is not None]
    agua_vista = max(aguas) if aguas else None
    if (tolera == "si" and agua_vista is not None and agua_vista >= AGUA_VISIBLE
            and factores[-1]["nota"] is not None and factores[-1]["nota"] < 1):
        factores[-1] = {"factor": "Lluvia", "nota": 1.0,
                        "texto": "Lluvia: la lluvia sola no alcanza para este cultivo, pero el radar vio agua "
                                 f"sobre el {agua_vista:.0%} del terreno: el agua ya está ahí"}

    # Pendiente: solo tiene máximo
    pendiente = _num(celda.get("pendiente"))
    if pendiente is None:
        factores.append({"factor": "Pendiente", "nota": None,
                         "texto": "Pendiente: sin dato (solo en zonas detalladas)"})
    elif pen_max is not None:
        nota = _nota_rango(pendiente, None, pen_max, 1, MARGEN_PENDIENTE)
        texto = (f"Pendiente {pendiente:.0f}°: adecuada (máximo {pen_max:g}°)" if nota >= 1 else
                 f"Pendiente {pendiente:.0f}°: terreno muy inclinado (máximo {pen_max:g}°)")
        factores.append({"factor": "Pendiente", "nota": nota, "texto": texto})

    # Acidez del suelo (pH del mapa SoilGrids, columna `ph`): rango ideal y rango que aguanta
    ph = _num(celda.get("ph"))
    if rango_ph and ph is not None:
        factores.append(_factor_optimo(
            "Suelo: pH", "", ph, rango_ph,
            ("algo ácido", "demasiado ácido", "algo alcalino", "demasiado alcalino"), decimales=1))
    elif rango_ph:
        factores.append({"factor": "Suelo: pH", "nota": None,
                         "texto": "Suelo: sin dato de acidez (pH) para este punto"})

    # Encharcamiento (NISAR): fracción de fechas en que el terreno tuvo agua
    ench = _num(celda.get("encharcamiento"))
    if ench is None:
        factores.append({"factor": "Encharcamiento", "nota": None,
                         "texto": "Encharcamiento: sin dato de radar NISAR para este punto"})
    else:
        limite = {"si": None, "parcial": 0.6}.get(tolera, 0.3)   # "no" o vacío -> 0.3
        nota = 1.0 if limite is None else max(0.0, 1 - ench / limite)
        if ench < 0.005:   # menos del 0,5 %: se redondea a "nada" (en un terreno dibujado es un promedio)
            texto = "Encharcamiento: el radar no vio agua acumulada en el terreno"
        elif limite is None:
            texto = f"Encharcamiento: se inunda {ench:.0%} de las fechas, y este cultivo lo tolera"
        else:
            texto = f"Encharcamiento: el radar vio agua {ench:.0%} de las fechas; este cultivo no lo soporta bien"
        factores.append({"factor": "Encharcamiento", "nota": nota, "texto": texto})

    # Agua en los terrenos vecinos (NISAR): parte de los cuadros a menos de 1 km con agua.
    # Los datos del radar son de la época seca: si los vecinos tuvieron agua entonces,
    # en invierno el terreno también puede mojarse.
    invierno = _num(celda.get("agua_invierno"))
    if invierno is not None:
        limite = {"si": None, "parcial": 0.6}.get(tolera, 0.3)      # igual que el encharcamiento
        if invierno < 0.005:
            nota, texto = 1.0, "Invierno: el radar no vio agua acumulada en el terreno entre enero y mayo"
        elif limite is None:
            nota, texto = 1.0, (f"Invierno: entre enero y mayo el radar vio agua en el {invierno:.0%} del "
                                "terreno, y este cultivo la aprovecha")
        else:
            nota, texto = max(0.0, 1 - invierno / limite), (
                f"Invierno: entre enero y mayo el radar vio agua en el {invierno:.0%} del terreno; "
                "este cultivo no lo soporta bien")
        factores.append({"factor": "Invierno", "nota": nota, "texto": texto})

    vecinos = _num(celda.get("agua_vecinos"))
    if vecinos is not None and invierno is None:
        if vecinos < AGUA_VECINOS_MINIMA:
            factores.append({"factor": "Alrededores", "nota": 1.0,
                             "texto": "Alrededores: el radar casi no vio agua en los terrenos vecinos (a menos de 1 km)"})
        elif tolera == "si":
            factores.append({"factor": "Alrededores", "nota": 1.0,
                             "texto": f"Alrededores: el radar vio agua en {vecinos:.0%} de los terrenos vecinos; "
                                      "es zona de agua, buena para este cultivo"})
        else:
            limite_vecinos = AGUA_VECINOS_MAX * (2 if tolera == "parcial" else 1)
            factores.append({"factor": "Alrededores", "nota": max(0.0, 1 - vecinos / limite_vecinos),
                             "texto": f"Alrededores: el radar vio agua en {vecinos:.0%} de los terrenos vecinos "
                                      "(a menos de 1 km). En invierno tu terreno también puede mojarse"})

    # Heladas (Sierra): riesgo en el mes más frío y lo que aguanta el cultivo
    helada = _num(celda.get("helada"))
    if helada is not None:
        aguante = AGUANTE_HELADA.get(str(cultivo.get("tolera_heladas", "")).strip().lower())
        minima = _num(celda.get("temp_minima"))
        frio = "" if minima is None else f" (en el mes más frío la temperatura baja en promedio a {minima:.1f} °C)"
        if helada < RIESGO_HELADA_MINIMO:
            # sin nota: un "1" aquí subiría el promedio de los cultivos que no llegan a 100
            factores.append({"factor": "Heladas", "nota": None,
                             "texto": f"Heladas: casi no hay riesgo en este terreno{frio}"})
        elif not HELADAS_EN_PUNTAJE:
            sabe = {0.1: " Este cultivo no las aguanta.", 0.4: " Este cultivo las aguanta en parte.",
                    0.7: " Este cultivo las aguanta bastante."}.get(aguante, "")
            factores.append({"factor": "Heladas", "nota": None,
                             "texto": f"Heladas: riesgo de {helada:.0%} en el mes más frío{frio}.{sabe} Es un aviso: "
                                      "todavía no cuenta en el puntaje, porque falta ese dato para varios cultivos"})
        elif aguante is None:
            factores.append({"factor": "Heladas", "nota": None,
                             "texto": f"Heladas: riesgo de {helada:.0%} en el mes más frío{frio}. No hay dato de cuánto "
                                      "aguanta este cultivo: no cuenta en el puntaje"})
        else:
            como = {0.1: "este cultivo no las aguanta", 0.4: "este cultivo las aguanta en parte",
                    0.7: "este cultivo las aguanta bastante"}[aguante]
            factores.append({"factor": "Heladas", "nota": 1 - helada * (1 - aguante),
                             "texto": f"Heladas: riesgo de {helada:.0%} en el mes más frío{frio}; {como}"})

    # Humedad del suelo (NISAR): 0 = seco, 1 = saturado
    # `humedad_confiable` = fracción de los datos que la NASA marca como recomendados.
    # En vegetación densa casi ninguno lo es: se muestra el dato pero NO cuenta en el puntaje.
    hum = _num(celda.get("humedad"))
    confiable = _num(celda.get("humedad_confiable"))
    if hum is None:
        factores.append({"factor": "Humedad", "nota": None,
                         "texto": "Humedad del suelo: sin dato de radar NISAR para este punto"})
    elif confiable is not None and confiable < HUMEDAD_CONFIABLE_MIN:
        factores.append({"factor": "Humedad", "nota": None,
                         "texto": f"Humedad del suelo según NISAR: {hum:.0%} de saturación "
                                  "(poco confiable por la vegetación densa; no cuenta en el puntaje)"})
    elif drenaje not in ("si", "no"):
        # El cultivo no tiene dato de drenaje en la tabla: no se supone ni una cosa ni la otra
        factores.append({"factor": "Humedad", "nota": None,
                         "texto": f"Humedad del suelo según NISAR: {hum:.0%} de saturación (falta el dato de "
                                  "drenaje de este cultivo; no cuenta en el puntaje)"})
    elif drenaje == "si":
        nota = 1.0 if hum <= 0.7 else max(0.0, 1 - (hum - 0.7) / 0.3)
        texto = ("Humedad del suelo: adecuada para un cultivo que necesita buen drenaje" if nota >= 1
                 else "Humedad del suelo: muy húmedo para un cultivo que necesita buen drenaje")
        factores.append({"factor": "Humedad", "nota": nota, "texto": texto})
    else:
        nota = 1.0 if hum >= 0.5 else max(0.0, hum / 0.5)
        if nota >= 1:
            texto = "Humedad del suelo: el terreno retiene agua, bueno para este cultivo"
        elif ench is not None and ench >= AGUA_VISIBLE:
            # El radar vio agua sobre el terreno: no tiene sentido decir que "se seca rápido"
            nota = 1.0
            texto = "Humedad del suelo: el radar vio agua acumulada en el terreno, bueno para este cultivo"
        elif riego:
            nota = 1 - PESO_FALTA_AGUA_CON_RIEGO * (1 - nota)
            texto = ("Humedad del suelo: el terreno se seca rápido para este cultivo; "
                     "con tu riego se compensa en parte")
        else:
            texto = "Humedad del suelo: el terreno se seca rápido para este cultivo"
        factores.append({"factor": "Humedad", "nota": nota, "texto": texto})

    notas = [f["nota"] for f in factores if f["nota"] is not None]
    if not notas:
        return {"puntaje": None, "factores": factores}
    puntaje = 100 * (PESO_PEOR_FACTOR * min(notas) + (1 - PESO_PEOR_FACTOR) * sum(notas) / len(notas))
    return {"puntaje": round(puntaje, 1), "factores": factores}


def aptitud(fila_celda: dict, fila_cultivo: dict) -> float | None:
    """Puntaje de aptitud 0..100 (None si no hay ningún dato para calcularlo)."""
    return aptitud_detalle(fila_celda, fila_cultivo)["puntaje"]
