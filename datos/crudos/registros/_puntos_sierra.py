
import pandas as pd
from src.clima_relieve import cargar_celdas, celda_mas_cercana
from src.cobertura import composicion
from src.config import provincia_sugerida, zona_de_punto
from src.recomendar import PUNTAJE_MINIMO, evaluar_todos
from src.suelo_lluvia import cargar_lluvia_mensual, lluvia_mensual_de, suelo_texto
from src.vecindad import resumen_vecinos

PUNTOS = [("Píllaro, Tungurahua", -1.170, -78.540), ("Quero, Tungurahua", -1.380, -78.610),
          ("Salcedo, Cotopaxi", -1.020, -78.570), ("Saquisilí, Cotopaxi", -0.840, -78.660)]
for nombre, lat, lon in PUNTOS:
    clave = zona_de_punto(lat, lon)
    tabla = cargar_celdas(clave)
    celda = celda_mas_cercana(tabla, lat, lon)
    celda["lluvia_mensual"] = lluvia_mensual_de(cargar_lluvia_mensual(clave), celda["celda"])
    provincia = provincia_sugerida(lat, lon)
    print(f"\n=== {nombre} ({lat}, {lon}) · zona {clave} · provincia sugerida {provincia}")
    print("   terreno:", {k: celda.get(k) for k in ("altura", "pendiente", "temp", "lluvia", "lluvia_power", "ph",
                                                  "arcilla", "arena", "materia_organica", "humedad", "vegetacion",
                                                  "temp_minima", "helada", "cobertura")})
    print("   suelo:", suelo_texto(celda), "· tipo de terreno:", composicion(pd.DataFrame([celda])))
    print("   vecinos:", resumen_vecinos(tabla, lat, lon))
    for riego in (False, True):
        celda["riego"] = riego
        todos = evaluar_todos(celda, provincia, preferencia="pronto")
        mejores = [x for x in todos if x["puntaje"] >= PUNTAJE_MINIMO]
        print(f"   {'CON' if riego else 'SIN'} riego · {len(mejores)} de {len(todos)} cultivos pasan de {PUNTAJE_MINIMO}:")
        for x in mejores[:6]:
            print(f"      {x['puntaje']:5.0f}  {x['nombre']:<22} mercado: {x['mercado']:<10} evidencia: {x.get('evidencia')}")
        if not riego:
            print("      los 4 de más abajo:", ", ".join(f"{x['nombre']} {x['puntaje']:.0f}" for x in todos[-4:]))
