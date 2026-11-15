"""
Prueba la carpeta unida (smartseeds-costa) en un punto de cada zona de la Sierra y abre la app.

1) Sin pantalla: arma el terreno igual que la app (celda más cercana + lluvia de cada mes + vecinos)
   en un punto de Tungurahua y otro de Cotopaxi, y anota los cultivos recomendados en
   probar_puntos_sierra.txt, al lado de este archivo.
2) Abre la app (Streamlit) en http://localhost:8765 para verla en el navegador.
   Para cerrarla: cierra la terminal donde quedó corriendo.
No hace commit, no sube nada y no publica la app (solo se ve en esta computadora).
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI / "smartseeds-costa"
_env = Path(sys.executable).parent
ENTORNO = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(REPO)}
if (_env / "Library" / "bin").exists():
    ENTORNO["PATH"] = os.pathsep.join(str(r) for r in (_env, _env / "Library" / "mingw-w64" / "bin",
                                                       _env / "Library" / "usr" / "bin", _env / "Library" / "bin",
                                                       _env / "Scripts")) + os.pathsep + ENTORNO.get("PATH", "")

PUNTOS = '''
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
    print(f"\\n=== {nombre} ({lat}, {lon}) · zona {clave} · provincia sugerida {provincia}")
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
'''
notas = open(AQUI / "probar_puntos_sierra.txt", "a", encoding="utf-8")
notas.write(f"\n===== puntos de la Sierra · {datetime.now():%Y-%m-%d %H:%M:%S}\n")
archivo = REPO / "datos" / "crudos" / "registros" / "_puntos_sierra.py"
archivo.parent.mkdir(parents=True, exist_ok=True)
archivo.write_text(PUNTOS, encoding="utf-8")
p = subprocess.run([sys.executable, str(archivo)], cwd=REPO, env=ENTORNO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
print(p.stdout + p.stderr)
notas.write(p.stdout + p.stderr + f"\n[código de salida {p.returncode}]\n")
notas.close()

print("Abriendo la app en http://localhost:8765 (cierra esta terminal para apagarla) ...", flush=True)
subprocess.run([sys.executable, "-m", "streamlit", "run", "app/app.py", "--server.headless", "true",
                "--server.port", "8765", "--server.address", "localhost", "--browser.gatherUsageStats", "false"], cwd=REPO, env=ENTORNO,
               stdin=subprocess.DEVNULL)
