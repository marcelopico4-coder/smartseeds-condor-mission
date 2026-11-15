# Cultivos mapeados por el MAG · nota para la sesión principal

Hecho el sábado 14 de noviembre de 2026 (18:00–18:30) en una sesión de apoyo, a partir de
`RECURSOS_IDENTIFICAR_CULTIVOS.md` (la búsqueda de la sesión del navegador, que no pudo abrir
ni descargar los recursos). Aquí está lo que sí se pudo abrir, descargar y medir.

**Esta sesión solo creó archivos nuevos.** No tocó `app/app.py`, `celdas_ZONA.csv`, `CLAUDE.md`,
`README.md`, `.gitignore` ni `tests/`. No hizo ningún commit. `python tests/prueba_rapida.py` sigue pasando.

## 1. Archivos nuevos

| Archivo | Qué es |
|---|---|
| `src/cultivos_mapeados.py` | Descarga los polígonos del MAG de una zona y calcula qué parte de cada celda ocupa cada cultivo |
| `src/identificar_cultivo.py` | Experimento: ¿reconoce el radar el cultivo? Medido contra el mapa del MAG |
| `src/validar_campo.py` | Validación: puntaje de la app en terrenos visitados por el MAG |
| `datos/procesados/cultivos_mag_santo_domingo.csv`, `cultivos_mag_daule.csv` | Tabla por celda (1,0 y 1,3 MB) |
| `datos/procesados/cultivo_evaluacion_ZONA.json` | Resultado del experimento |
| `datos/procesados/validacion_campo_ZONA.json` | Resultado de la validación |
| `datos/crudos/cultivos_mag/ZONA/` | Polígonos y puntos descargados (25 MB, ya ignorados por git) |

Comandos (piden `rasterio`, solo desarrollo; fuera de Miniforge Prompt hay que poner
`envs/condor/Library/bin` en el PATH):

```
python -m src.cultivos_mapeados ZONA descargar   # ~1 min en Daule
python -m src.cultivos_mapeados ZONA tabla
python -m src.cultivos_mapeados ZONA comparar
python -m src.identificar_cultivo ZONA
python -m src.validar_campo ZONA descargar
python -m src.validar_campo ZONA medir
```

## 2. Lo que la sesión del navegador no pudo abrir y sí responde

- **Geoportal del MAG, "Estimaciones de cultivos 1:25.000"** (WFS
  `http://geoportal.agricultura.gob.ec/cobertura/E25k/wfs`): 56 capas. Más de lo que se esperaba:
  - **arroz 2024 y 2025**, por los tres períodos del año;
  - **maíz amarillo duro 2024 y 2025**, dos períodos;
  - **soya 2024 y 2025**;
  - **banano 2018–2022**, **palma aceitera 2018–2022**, **caña de azúcar industrial 2018–2022**;
  - "cultivo por período" 2014–2023 (varios cultivos de ciclo corto en una capa).
- **SIGTIERRAS** (WFS `.../sigtierras/cobertura_tierra/wfs`): no es el mapa de uso de la tierra, son
  **8.913 puntos visitados en campo** (2014–2015) con el cultivo anotado, más encuestas a productores.
- **Catálogo de la FAO** (`https://data.apps.fao.org/map/gsrv/edit/rlc_ecuador/wfs`): las mismas capas
  del MAG por `https` (`rlc_ecuador:ea010_cultivo_banano`, `..._palma_aceitera`, `..._cana_azucar_industrial`,
  `..._periodo1/2/3`). Sirve si la app publicada en `https` bloquea el servicio `http` del MAG.
- Shapefile de palma del catálogo FAO: existe, 15,6 MB. No hizo falta: el WFS da lo mismo por zona.

Detalles del servicio del MAG: no acepta pedir por páginas (`startIndex` da error); se pide con
`version=1.1.0`, `bbox=lon0,lat0,lon1,lat1,EPSG:4326` y `maxFeatures` alto, y se comprueba contra
`totalFeatures`. Las coordenadas vienen en lon, lat. Cada polígono dice "no se realizó la fase de
validación en campo". **No se comprobó la licencia del geoservicio**: la ficha de la FAO da
CC BY-NC-SA 4.0 para la palma; citar al MAG y no usar con fines comerciales.

**No se abrieron** (quedan como en el archivo de recursos): HLS de la NASA, AlphaEarth, TESSERA,
altura de árboles de Meta, WorldCereal, MapBiomas (pide cuenta de Google), Forest Data Partnership
(cacao; pide Earth Engine), el mapa de cobertura 2020 de Datos Abiertos y Sentinel-1 VH.

## 3. Tabla por celda: `cultivos_mag_ZONA.csv`

Una fila por celda, mismo número de `celda` que `celdas_ZONA.csv`. No es una predicción.

| Columna | Significado |
|---|---|
| `ref_arroz`, `ref_maiz_duro`, `ref_soya` | Parte de la celda (0 a 1) dentro de los polígonos de 2025 (cualquier período) |
| `ref_banano`, `ref_palma_aceitera`, `ref_cana_azucar` | Lo mismo, polígonos de 2022 |
| `arroz_ciclos` | En cuántos de los tres períodos de 2025 hubo arroz (promedio de la parte arrocera) |
| `cultivo_mapeado` | El cultivo que más ocupa, si pasa del 25 % (`PARTE_MINIMA`, sin calibrar); vacío si ninguno |

| Zona | Arroz | Banano | Maíz duro | Soya | Palma | Caña |
|---|---|---|---|---|---|---|
| Daule (ha aprox.) | 99.811 | 5.259 | 2.054 | 2.055 | 102 | 0 |
| Daule (celdas con más del 5 %) | 73,2 % | 4,5 % | 3,0 % | 3,5 % | 0,1 % | 0 % |
| Santo Domingo (ha aprox.) | 0 | 221 | 2 | 0 | 2.797 | 0 |
| Santo Domingo (celdas con más del 5 %) | 0 % | 0,2 % | 0 % | 0 % | 3,0 % | 0 % |

Los tres terrenos de demostración de Daule caen en arroz según el MAG: inundado 100 % (1,0 siembras
al año), seco 84 % (1,7 siembras), agua en invierno 100 %. El de Santo Domingo no tiene cultivo mapeado.

Cuidados: solo cubre seis cultivos, así que **una celda vacía no significa "sin cultivo"** (cacao,
plátano, pasto y yuca no están). En Santo Domingo casi no aporta. Arroz, maíz y soya son de 2025.

## 4. ¿Reconoce el radar el cultivo? (medido, bloques que el modelo no vio)

Etiquetas: celdas con un cultivo del MAG en el 60 % o más, y "otro" donde no hay ninguno.

| Daule | Celdas | Solo NISAR: lo encuentra / acierta al decirlo | NISAR + Sentinel-1 de invierno |
|---|---|---|---|
| Arroz | 15.533 | 91 % / 94 % | 94 % / 95 % |
| Banano | 734 | 92 % / 77 % | 96 % / 92 % |
| Maíz duro | 147 | 37 % / 16 % | 29 % / 36 % |
| Otro | 6.452 | 82 % / 81 % | 87 % / 86 % |
| **Acierto total** | 22.866 | **88 %** | **92 %** |

Decir siempre "arroz" daría 68 %. El promedio por clase es 76 % en los dos casos.

- **Arroz y banano sí se reconocen** con el radar. **El maíz duro no**: se confunde con arroz.
- La soya no entró: quedaron menos de 100 celdas puras.
- **Santo Domingo, palma: el radar no la reconoce** (0 % de 152 celdas; se confunde con el resto de
  árboles). Ahí el mapa del MAG es la única fuente.
- Ojo: arroz y maíz son de 2025 y el radar de 2026.

## 5. Validación con terrenos visitados por el MAG (2014–2015)

Puntos donde el MAG anotó un cultivo que la app evalúa: 374 en Santo Domingo y 543 en Daule.

| | Santo Domingo | Daule |
|---|---|---|
| La app lo considera apto (puntaje ≥ 40) | 100 % | 100 % |
| Puntaje ≥ 70 | 98 % | 50 % |
| Está entre los 3 primeros | 34 % | 25 % |
| Puntaje mediano | 87,9 | 69,6 |

**Lo bueno:** la app nunca descarta un cultivo que de verdad estaba sembrado.

**El problema, en Daule:** de 376 terrenos con arroz, la app le da al arroz un puntaje mediano de
56,5 y lo pone entre los tres primeros solo en el 20 %; en esos terrenos pone primero plátano (297
veces) o banano (154). El 78 % de esos terrenos sigue mapeado como arroz por el MAG en 2025.
- Con "sí, tengo riego" el puntaje mediano del arroz sube a 92,4 (99 % con 70 o más), pero sigue entre
  los tres primeros solo en el 34 %, porque plátano, banano y palma sacan 100 y van delante.
- En Santo Domingo pasa algo parecido con el plátano: 154 terrenos, apto en todos, top 3 en el 1 %.
  La app pone primero maíz duro en 215 de los 374 terrenos, y solo 19 tenían maíz.

## 6. Propuesta de integración (decide la sesión principal)

1. **Mostrar el dato en la app**, separado de lo que dice el modelo: en la ficha del terreno,
   `cultivos_mapeados.texto_del_terreno(fila)` devuelve frases como "Arroz: 84 % del cuadro, según el
   mapa del MAG de 2025 (unas 1,7 siembras en el año)". `cultivos_mapeados.cargar(zona)` solo usa pandas.
2. **Capa en el mapa** "Cultivo mapeado (MAG)" con `cultivo_mapeado`, igual que las de `CAPAS_RADAR`.
3. **Usarlo como evidencia local en el orden**, antes que la evidencia de la provincia: si el MAG mapea
   el cultivo en el cuadro o en los vecinos, es la mejor señal de "aquí se siembra y funciona". Es lo
   que arreglaría el caso del arroz en Daule. Cambia el orden de `evaluar_todos()`: decisión del equipo.
4. **Riego:** donde `arroz_ciclos` es 2 o más hay riego casi seguro; se podría sugerir "sí" por defecto.
5. **Tipo de terreno:** el experimento muestra que se puede añadir un segundo nivel (arroz / banano /
   otro) en Daule con 88–92 % de acierto. No se integró en `src/cobertura.py`.
6. Para la **Sierra**: los mismos comandos con la zona nueva. El servicio tiene caña y el "cultivo por
   período" de años anteriores; no se revisó qué cultivos trae en Cotopaxi y Tungurahua. Los puntos de
   campo sí cubren la Sierra (el ejemplo del servicio es maíz suave en Bolívar).
7. Si se suben los `cultivos_mag_ZONA.csv`, añadir la cita del MAG en las referencias.

## 7. Correcciones de la revisión del navegador que NO se aplicaron (tocan archivos compartidos)

- `recolectar_referencia.py`: poner `rasterio.Env(GDAL_HTTP_TIMEOUT=30, GDAL_HTTP_MAX_RETRY=1)` para que
  MapBiomas no deje el script colgado, y sacar el código 74 (banano) del grupo "agropecuario".
- Frase de la app: "coincide en el 79 % de los cuadros" → añadir "con un tipo dominante" (en Daule el
  37 % de las celdas son mezcladas y no tienen medida).
- `CLAUDE.md`: las horas (19:10, 18:00, 19:00) no cuadran con el commit de las 17:23.
- `src/sentinel.py` solo usa VV; los mismos archivos traen VH.

## 8. Fuentes para citar

- MAG, Geoportal del Agro Ecuatoriano. Estimaciones de cultivos, escala 1:25.000 (arroz, maíz amarillo
  duro y soya 2025; banano y palma aceitera 2022). http://geoportal.agricultura.gob.ec/geoservicios/cartografia.html
- MAG – SIGTIERRAS. Datos de campo de cobertura y uso de la tierra, escala 1:25.000 (2014–2015). Mismo geoportal.
