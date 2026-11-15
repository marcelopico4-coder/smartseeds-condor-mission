# Unión Sierra + Costa · estado al 14-nov-2026, 18:10

Carpetas en esta computadora:
- `C:\condor\smartseeds`        trabajo de la Sierra. ES EL RESPALDO: no se toca.
- `C:\condor\smartseeds-costa`  clon de https://github.com/JotaCenfe/smartseeds-costa (rama main, commit ccb1d9d). Con cambios SIN commit ni subida (ver abajo).

## Hallazgo principal
Las dos carpetas NO son dos versiones del mismo código: son dos programas distintos que comparten 8 nombres de
archivo. Ningún archivo de la Sierra coincide con ninguna versión del historial del repositorio, y los que se
llaman igual se parecen entre 5 % y 16 %. No hay "versión más vieja" que actualizar ni diferencias línea a línea
que unir: hay que pasar las ideas de la Sierra al diseño del repositorio.

Diferencias de fondo:
- Tabla por celda: repositorio `datos/procesados/celdas_ZONA.csv`, cuadros de ~250 m. Sierra
  `datos/procesados/<zona>/celdas.csv`, cuadros de ~1 km (y radar a ~110 m). No son intercambiables: las zonas de
  la Sierra hay que procesarlas de nuevo con los comandos del repositorio.
- Puntaje: repositorio = aptitud 0–100 graduada + mercado como etiqueta (alta / media / saturado). Sierra = 50 %
  terreno + 50 % oportunidad con oferta y demanda de DEMOSTRACIÓN.
- Cultivos: repositorio 15 (5 de la Sierra "para probar"). Sierra 26, con rangos del catálogo del equipo v1.1.

## a) Solo de la Sierra (105 archivos)
- Zonas Cotopaxi y Tungurahua (órbita 76 ascendente), en el formato de la Sierra.
- Catálogos del equipo: `tablas/catalogo/` (agronómico v1.1) y `tablas/mercado/` (mercado v1.0), ~12 MB.
- Tablas derivadas: `cultivos.csv`, `perfiles_productivos.csv`, `mercado_precios.csv`, `mercado_rendimiento.csv`,
  `mercado_comercio.csv`, `sitios_verificacion_tungurahua.csv`.
- Módulos sin equivalente en el repositorio: heladas, catálogo, firmas y análisis del radar por pixel, extracción
  GCOV, motor con oferta y demanda, base de datos, lanzadores, 32 pruebas, documentos.
- Datos procesados de la Sierra (formato propio, no los lee la app del repositorio).

## b) Mismo nombre en los dos lados, contenido distinto (8)
`src/config.py`, `src/aptitud.py`, `src/mercado.py`, `src/nisar.py`, `src/clima_relieve.py`, `app/app.py`,
`README.md`, y los pequeños `.gitignore` / `requirements.txt`. Propuesta: se queda SIEMPRE la versión del
repositorio; de la Sierra solo se agregan piezas nuevas (zonas, cultivos, heladas).

## c) Versión de la Sierra simplemente más vieja
Ninguno.

## Lo que ya se trajo al clon (14-nov 18:10; detalle en la sección "Unión con la Sierra" de su CLAUDE.md)
- Zonas `cotopaxi` y `tungurahua` en `src/config.py` (cuadros de 0,4°). SIN PROCESAR todavía.
- Heladas: `src/heladas.py` y factor opcional en `src/aptitud.py`.
- 10 cultivos de la Sierra desde el catálogo v1.1 (`src/catalogo_equipo.py`, `tablas/catalogo/`,
  `tablas/perfiles_productivos.csv`). El fréjol quedó fuera porque cambia los resultados de la Costa.
- Mercado: 5 cultivos nuevos en el diccionario de `src/preparar_mercado.py` (sin probar con los Excel),
  claves en `siembra_provincias.csv` y una fila de cebolla blanca en Tungurahua en `mercado.csv`.
- Pruebas: `python tests/prueba_rapida.py` pasa en esta computadora (▷ `C:\condor\probar_union.py`).
- Los 6 terrenos de prueba de la Costa dan lo mismo que antes.

## Pendiente
1. Permiso para procesar las dos zonas (lecturas remotas de NISAR con Earthdata, WorldCover, SoilGrids, CHELSA).
2. Papa: usar o no 9–11 °C del INIAP.
3. Fréjol: agregarlo o no (cambia Santo Domingo).
4. Volver a correr `python -m src.preparar_mercado` donde estén los Excel.
5. Probar la app en un punto de cada zona de la Sierra. Commit y subida: solo cuando el usuario lo pida.

## Estado al 14-nov-2026, 21:35 (detalle en "Sierra procesada" del CLAUDE.md del clon)
- Las dos zonas de la Sierra quedaron PROCESADAS en el clon (relieve, heladas, radar, humedad, suelo, lluvia local,
  vecinos, mapa de referencia) y el tipo de terreno se reentrenó con las cuatro zonas. Pruebas: pasan (21:24).
- Lo que trabó la tarde: `rasterio.windows.from_bounds` tumbaba Python en esta computadora y el servidor de CHELSA
  se colgaba. Resuelto con `src/lectura_remota.py` (nuevo).
- Al reentrenar cambió el tipo de terreno de la Costa: 9,5 % de las celdas en Santo Domingo y 19,2 % en Daule.
  El acierto general pasó de 79 % a 76 % (ahora con cuatro zonas). No entra en el puntaje.
- App probada en pantalla en Píllaro y Saquisilí con el enlace `?lat=&lon=`. Falta en pantalla: tocar el mapa,
  dibujar, capas del radar y gráfico de pasadas en la Sierra; y volver a mirar la Costa.
- Decididos antes por el usuario (otra sesión): heladas apagadas en el puntaje, papa con 9–11 °C del INIAP,
  brócoli agregado, zanahoria no.
- Sigue pendiente: fréjol; `actualizar_mercado.py` / `python -m src.preparar_mercado` con los Excel del SIPA;
  precios mayoristas para dos filas más; radar de época lluviosa (Sentinel-1, ~25 min por zona, preguntar antes);
  MapBiomas para separar el páramo; datos de campo. Commit y subida: solo cuando el usuario lo pida.
- Para lanzar desde VS Code: ▷ `C:\condor\probar_union.py` (procesa la Sierra) y ▷ `C:\condor\abrir_app_union.py`
  (prueba cuatro puntos y abre la app en `localhost:8765`, solo en esta computadora).
