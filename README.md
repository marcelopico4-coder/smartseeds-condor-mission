# SmartSeeds · Equipo Condor Mission
### NASA Space Apps Challenge 2026 · Sede Sangolquí · Reto: Dancing with the SARs

**SmartSeeds** es una app donde el agricultor marca su terreno y recibe qué cultivos le convienen,
explicando por qué: lo que su suelo permite (según el radar NISAR y datos de la NASA) y lo que el
mercado necesita (según datos agrícolas del Ecuador).

> **Regla del concurso:** el desarrollo empieza el **sábado 14 a las 9:00**. Antes solo se preparan
> herramientas, cuentas, lectura y verificación de datos.
> **Envío:** domingo 15 antes de las **23:59** (meta del equipo: 21:00).

---

## 1. La idea en una página

### Por qué NISAR
En las zonas agrícolas del Ecuador casi siempre hay nubes y los satélites ópticos fallan.
NISAR (NASA-ISRO) es un radar que **ve a través de las nubes**, de día y de noche, cada 12 días y gratis.
Su banda L atraviesa la vegetación.

### Qué aporta el radar al agricultor

| Capa NISAR | Pregunta que responde |
|---|---|
| Humedad del suelo | ¿Tu terreno retiene agua o se seca rápido? |
| Encharcamiento / inundación | ¿Se te inunda en época de lluvia? |
| Actividad de la vegetación | ¿Qué se cultiva alrededor, cuándo se cosecha, hubo tala? |
| Estabilidad del terreno (opcional) | ¿La ladera es estable para cultivos permanentes? |

### Cómo recomienda
1. **Aptitud física (0–100) por cultivo:** altura y pendiente (NASADEM) + clima (NASA POWER) + capas NISAR + requisitos de cada cultivo (FAO EcoCrop / INIAP).
2. **Indicador de mercado:** tendencias de producción (ESPAC del INEC) + precios (MAG) → oportunidad alta / media / mercado saturado. Es una **recomendación**, no una orden.
3. **Resultado:** los 3 mejores cultivos, cada uno con sus razones en lenguaje sencillo.

### Escala: nacional + zonas detalladas

| Nivel | Cobertura | Datos |
|---|---|---|
| **Nacional** | Todo Ecuador | Clima, relieve, suelo, mercado por provincia (datos livianos) |
| **Detallado con NISAR** | 2 zonas de demostración | Humedad, encharcamiento y vegetación a 20–30 m (precalculado) |

Cada pasada de NISAR pesa varios GB, por eso el detalle se procesa por zonas.
**Zonas propuestas:** una de la **Costa** (Santo Domingo de los Tsáchilas) y una de la **Sierra** (por definir).

**Validación:** ¿la app recomienda los cultivos que ya prosperan en cada zona?

---

## 2. Datos ya verificados (13 nov) – Santo Domingo de los Tsáchilas

Recuadro: lon −79.40 a −79.00, lat −0.45 a −0.05

- **NISAR GCOV:** serie de **11 fechas** (path 76, ascendente), del 19 jun al 29 oct 2026, cada 12 días.
  También series descendentes de 10 fechas (path 112) y otra ascendente (path 4).
  Cada serie se analiza por separado (no se mezclan geometrías).
- **NISAR SME2:** 52 productos. Parece ser la **humedad de suelo nivel 3 de NISAR** → confirmar en la NISAR Data User Guide.
- **NASA POWER:** 24,3 °C media anual, ~1.560 mm/año. Celdas de ~50 km: comparar con INAMHI y declararlo como limitación.
- **SMAP:** 36 archivos en octubre 2026 (respaldo de humedad).

⚠️ Las fechas NISAR disponibles son de **época seca** (jun–oct). Para encharcamiento conviene buscar
datos BETA de la época lluviosa (ene–may): cambiar `INICIO` en `verificar_instalacion.py` a `"2025-10-01"`.

---

## 3. Recursos

### Cultivos mapeados y observaciones de campo

- **Ministerio de Agricultura y Ganadería del Ecuador (MAG), Dirección de Análisis de Información Agropecuaria.** [Estimaciones de superficie sembrada y plantada a escala 1:25.000](http://geoportal.agricultura.gob.ec/geoservicios/cartografia.html), [geoservicio WFS E25k](http://geoportal.agricultura.gob.ec/cobertura/E25k/wfs). SmartSeeds convirtió polígonos de arroz, maíz amarillo duro y soya de 2025 y de banano, palma aceitera y caña de azúcar industrial de 2022 en proporciones por cuadro. Es un registro histórico de los cultivos consultados.
- **MAG–SIGTIERRAS.** Puntos de campo de cobertura y uso de la tierra (2014–2015), empleados como contraste histórico. [Geoservicio de cobertura de la tierra](http://geoportal.agricultura.gob.ec/sigtierras/cobertura_tierra/wfs).
- Datos Abiertos Ecuador registra las capas de [banano](https://www.datosabiertos.gob.ec/dataset/mapa-de-estimacion-de-superficie-plantada-del-cultivo-de-banano-2022), [palma aceitera](https://www.datosabiertos.gob.ec/dataset/mapa-de-estimacion-de-superficie-plantada-del-cultivo-de-palma-aceitera-2022) y [caña de azúcar industrial](https://www.datosabiertos.gob.ec/dataset/mapa-de-estimacion-de-superficie-plantada-del-cultivo-de-cana-de-azucar-industrial-2022) de 2022 como «Creative Commons Non-Commercial (Any)». Queda por confirmar con el MAG la variante exacta y los términos específicos de reutilización de las capas de 2025 y de SIGTIERRAS.

### NASA (recursos oficiales del reto)
| Recurso | Para qué |
|---|---|
| ASF Vertex – https://search.asf.alaska.edu | Buscar y descargar NISAR |
| NISAR Data User Guide – https://nisar-docs.asf.alaska.edu | Entender productos y bandas (GCOV, SME2) |
| NASA Earthdata Search – https://search.earthdata.nasa.gov | NASADEM, SMAP, IMERG |
| Intro to SAR / Intro to Remote Sensing (Earthdata) | Entender el radar en 1 hora (todo el equipo) |
| NASA ARSET Trainings | Capacitación de NISAR, con material en español |
| NISAR StoryMaps y Applications White Papers | Argumentos para el pitch (buscar el de agricultura) |
| Tutorial SAR en Python y QGIS (Agencia Espacial Canadiense, GitHub) | Código de partida |

### NASA (adicionales)
| Recurso | Para qué |
|---|---|
| NASA POWER – https://power.larc.nasa.gov | Temperatura y lluvia promedio de todo el país |
| NASADEM | Altura y pendiente |
| SMAP | Humedad de suelo nacional (baja resolución) |

### Agencias socias (suman puntos)
| Recurso | Para qué |
|---|---|
| Sentinel-1 (ESA) | Radar con historia larga si a NISAR le faltan fechas |
| SAOCOM (CONAE, Argentina) | Radar banda L; requiere registro (opcional) |

### Ecuador
| Fuente | Qué buscar |
|---|---|
| INEC – ESPAC | Superficie, producción y rendimiento por cultivo y provincia (últimos 5 años) |
| MAG – SIPA | Precios al productor |
| Geoportal del MAG | Zonificación agroecológica / aptitud agrícola (validación) |
| INIAP | Guías técnicas de cultivos para Ecuador |
| INAMHI | Estaciones meteorológicas |
| Banco Central del Ecuador | Exportaciones por producto |
| MapBiomas Ecuador | Uso actual del suelo (validación) |
| SoilGrids (ISRIC) – https://soilgrids.org | Textura y pH del suelo (fuente externa, no NASA) |
| FAO EcoCrop | Requisitos de cada cultivo |

---

## 4. Tareas de investigación (esta noche)

**Cultivos (Mecánico 1)**
- [ ] Lista final de ~15 cultivos (≈8 Costa, ≈5 Sierra, ≈2 Amazonía)
- [ ] Completar `requisitos_cultivos.csv`: altura, temperatura, lluvia, pendiente máx., tolerancia al encharcamiento, pH

**Mercado (Mecánico 2)**
- [ ] Descargar ESPAC de los últimos años
- [ ] Precios del SIPA de esos cultivos
- [ ] Proponer la regla del indicador (ej.: "saturado" si la superficie creció más de X % y el precio bajó)

**Radar (Jorge)**
- [ ] Confirmar qué es SME2 en la NISAR Data User Guide
- [ ] Leer la parte de GCOV: HH, HV y retrodispersión
- [ ] Ver la capacitación ARSET de NISAR
- [ ] Buscar datos de época lluviosa (ver sección 2)

**Diseño**
- [ ] Logo e identidad de SmartSeeds
- [ ] Boceto de 3 pantallas: elegir terreno · resultados · ficha del cultivo
- [ ] Guion del video de 30 s (sin imágenes con derechos de autor)

**Todos**
- [ ] Datos oficiales del peso de la agricultura en empleo y PIB (INEC / BCE) para el pitch
- [ ] Si se puede: conversación corta con un agricultor (cómo decide qué sembrar). Con su permiso; sin menores de 18 años
- [ ] Definir la zona de la Sierra

---

## 5. Instalación (Windows) – probada el 13 nov

### Cuentas (cada integrante)
- [ ] Inscrito en la sede **Sangolquí** y en el equipo **Condor Mission** (Members) — **obligatorio**
- [ ] NASA Earthdata Login – https://urs.earthdata.nasa.gov
- [ ] Entrar una vez a ASF Vertex con esa cuenta
- [ ] GitHub y Streamlit Community Cloud

### Programas (en PowerShell, uno por uno)
```
winget install -e --id CondaForge.Miniforge3 --accept-source-agreements --accept-package-agreements
winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
winget install -e --id OSGeo.QGIS_LTR --accept-source-agreements --accept-package-agreements
```
(QGIS es opcional y pesa más de 1 GB.) En VS Code, instalar las extensiones **Python** y **Jupyter** de Microsoft.

### Entorno de Python (en **Miniforge Prompt**, no en PowerShell)
Copiar los archivos del proyecto a `C:\condor` y ejecutar uno por uno:
```
cd C:\condor
mamba create -n condor -c conda-forge python=3.11 -y
conda activate condor
mamba install -c conda-forge asf_search earthaccess requests h5py xarray rioxarray rasterio geopandas -y
mamba install -c conda-forge scikit-image scikit-learn openpyxl matplotlib plotly jupyterlab streamlit folium -y
pip install streamlit-folium fpdf2
python verificar_instalacion.py
```
> Usar **mamba** y por partes. Con `conda env update/create` del archivo completo, el paso
> "Solving environment" se quedó trabado más de 10 minutos.

### VS Code
1. **File → Open Folder → C:\condor**
2. Si aparece la barra azul "Restricted Mode": **Manage → Trust**
3. `Ctrl + Shift + P` → **Python: Select Interpreter** → **condor (3.11)**
   (no el "Recommended": ese no tiene las librerías)

### Cada vez que abras Miniforge Prompt
```
cd C:\condor
conda activate condor
```

### Probar Streamlit
```
streamlit hello
```
Se abre en http://localhost:8501. Con la **Network URL**, los compañeros en la misma wifi pueden verla.
Para cerrarlo: `Ctrl + C`.

---

## 6. Estructura del repositorio

```
smartseeds/
├── environment.yml
├── verificar_instalacion.py
├── README.md
├── datos/
│   ├── crudos/          # descargas (NO se suben a GitHub: son pesadas)
│   └── procesados/      # capas listas para la app (GeoTIFF/PNG pequeños, CSV)
├── tablas/
│   ├── requisitos_cultivos.csv
│   └── mercado.csv
├── notebooks/           # pruebas y análisis
├── src/
│   ├── nisar.py         # capas de humedad, encharcamiento y vegetación
│   ├── clima_relieve.py # NASA POWER y NASADEM
│   ├── aptitud.py       # puntaje de aptitud por cultivo
│   └── mercado.py       # indicador de oportunidad
└── app/
    └── app.py           # interfaz en Streamlit
```

---

## 7. Sábado: acuerdos de 9:00 a 10:00

- [ ] Zonas de demostración (Costa + Sierra), en recuadro lon/lat
- [ ] Lista final de cultivos
- [ ] Formato de la tabla por celda: `celda, lat, lon, altura, pendiente, temp, lluvia, humedad, encharcamiento, vegetacion`
- [ ] Escala de aptitud 0–100 y niveles de mercado: oportunidad alta / media / saturado

---

## 8. Entrega (domingo)

- [ ] Página del proyecto **en inglés** (resumen, descripción, datos NASA, referencias)
- [ ] Demo: video **≤ 30 s** con subtítulos en inglés, o **≤ 7 diapositivas** en inglés (si se pasan, quedan fuera de la evaluación global)
- [ ] App publicada y repositorio público en GitHub
- [ ] **Todas** las referencias citadas, incluido código abierto
- [ ] Al menos un dato o recurso de la NASA (tenemos varios)
- [ ] Uso de IA declarado: imágenes o videos generados con marca de agua; código y datos indicados en el texto
- [ ] Sin imágenes con derechos de autor sin permiso, ni de menores de 18 años
- [ ] Clic en **"Submit for Judging"** antes de las 23:59

**Criterios de evaluación (1 a 5 cada uno):** impacto · creatividad · validez · relevancia · presentación.

---

## 9. Código: estado al sábado 14 (11:00)

### Ejecutar (Miniforge Prompt, entorno `condor`)
```
cd C:\condor
conda activate condor
python tests/prueba_rapida.py        # comprueba la lógica (sin internet)
streamlit run app/app.py             # abre la app en http://localhost:8501
```

### Qué funciona ya
| Archivo | Estado |
|---|---|
| `app/app.py` | Mapa: tocas un terreno y muestra los 3 mejores cultivos con sus razones. Nivel nacional con clima real de NASA POWER. |
| `src/terreno.py` | **Terreno dibujado.** En la app se elige "✏️ Dibujar mi terreno" y se marcan las esquinas (todas las que hagan falta, para seguir curvas y linderos). Con el botón ✎ se arrastran las esquinas para corregir y se crean esquinas nuevas desde los puntos medios. Calcula el tamaño en hectáreas y cuadras y **pesa cada cuadro de datos (~250 m) según la parte que el terreno ocupa de él**, así el resultado sigue la forma dibujada. Si el terreno es grande, dice qué cultivo conviene en cada parte. Un terreno que cabe en un solo cuadro (~6 ha) usa ese cuadro: los datos no tienen más detalle. |
| `recolectar_referencia.py` | **Mapa de referencia.** Lee ESA WorldCover (o MapBiomas, si se baja a mano) solo en las zonas y lo resume por cuadro. También compara el modelo con la referencia y prueba un modelo entrenado con ella. |
| `src/cobertura.py` | **Tipo de terreno según el radar.** Desde las 18:00 del 14 nov lo entrena con el mapa de referencia (ver abajo). La primera versión era un modelo de agrupamiento (KMeans) entrenado con las pasadas de NISAR que separa: zona construida, agua, terreno que se inunda, cultivo de ciclo corto en actividad, árboles o vegetación densa y vegetación baja. La app lo muestra, avisa si el punto es zona construida y deja lo construido fuera del análisis de un terreno dibujado. |
| `src/suelo_lluvia.py` | **Suelo y lluvia con detalle local.** Agrega a la tabla el pH y la textura de SoilGrids (250 m) y la lluvia de CHELSA (1 km, del año y de cada mes). |
| `src/sentinel.py` | **Radar de la época lluviosa.** Lee Sentinel-1 (OPERA RTC-S1 de la NASA) de enero a mayo, detecta el agua con un umbral calibrado contra NISAR y escribe la columna `agua_invierno`. |
| `src/vecindad.py` | **Los terrenos vecinos.** Calcula cuántos cuadros a menos de 1 km tuvieron agua según el radar y resume qué hay alrededor de un terreno. |
| `src/config.py` | Rutas, zonas de demostración y formato de la tabla por celda. **Aquí se agrega la zona de la Sierra.** |
| `src/aptitud.py` | Puntaje 0–100 por cultivo y razones en lenguaje sencillo. Incluye la regla del **riego** (ver abajo). |
| `src/mercado.py` | Regla alta / media / saturado sobre `tablas/mercado.csv`. Usa la fila de la provincia y, si no hay, la nacional. Devuelve "sin datos" si el cultivo no está. |
| `src/preparar_mercado.py` | Arma `tablas/mercado.csv` con los archivos oficiales de la ESPAC y de precios del SIPA (se ejecuta una vez, sin internet). |
| `src/recomendar.py` | Une aptitud + mercado. También adjunta a cada cultivo el **suelo que prefiere** (pH, textura, drenaje) leído de `tablas/suelo_cultivos.csv`. |
| `tablas/suelo_cultivos.csv` | Suelo preferido de 15 cultivos, copiado del catálogo del equipo (`catalogo_cultivos_v01`, 14 nov) con su fuente y página. Se **muestra** en la ficha del cultivo, pero **no entra en el puntaje**: son rangos reportados por cada manual y la app todavía no mide el suelo del terreno. |
| `src/clima_relieve.py` | NASA POWER probado. NASADEM → tabla por celda: probado. Santo Domingo ya está en `datos/procesados/celdas_santo_domingo.csv` (32.400 celdas de ~250 m). Para otra zona: `python -m src.clima_relieve NOMBRE_ZONA`. |
| `src/nisar.py` | **Probado con datos reales.** Lee en remoto solo el recorte de la zona (~15 MB por archivo en vez de 7 GB). Santo Domingo ya tiene 11 fechas GCOV y 10 fechas SME2 procesadas. |

### Riego, empates y tiempos de cultivo (14 nov)
La app hace dos preguntas sencillas al agricultor antes de recomendar.

**¿Tienes riego en tu terreno?**
- El riego solo arregla la **falta de agua** (poca lluvia o suelo que se seca rápido). No cambia la
  altura, la temperatura, la pendiente, el exceso de lluvia ni las inundaciones.
- Tampoco borra la falta: la **reduce**. Mientras más agua haya que regar, menos puntos. Así, marcar
  "sí tengo riego" no pone a todos los cultivos en 100.
- Fórmula: nota de lluvia con riego = 1 − 0,5 × (parte del agua que falta). Si la lluvia cubre el 77 % de
  lo que pide el cultivo, la nota es 0,89; si no lloviera nada, sería 0,5. El 0,5 es un valor inicial
  **sin calibrar**.
- Ejemplo real, terreno seco de Daule (770 mm de lluvia): sin riego, arroz 48 y banano 33; con riego,
  arroz 92 y banano 88. El maíz duro sigue en 100 porque no le falta agua. En Santo Domingo el riego no
  cambia nada, porque ahí la lluvia alcanza.
- La app dice cuánta agua falta ("tendrás que regar lo que falta: unos 230 mm al año").

**¿Qué buscas?** (cosechar pronto / un cultivo para muchos años)
- Muchos cultivos empatan en el mismo puntaje (en Santo Domingo, 8 sacan 100). Antes se mostraban los
  tres primeros de la tabla. Ahora los empatados se ordenan por mercado y luego por esta respuesta:
  "pronto" pone primero al que da cosecha más rápido; "muchos años" pone primero a los permanentes.
- **No cambia el puntaje**, solo el orden entre empatados. La app avisa qué otros cultivos tienen la misma
  aptitud que el tercero.
- Cada cultivo muestra cuánto tarda la primera cosecha y de qué tipo es (columnas `ciclo_meses` y `tipo`
  de `requisitos_cultivos.csv`, todavía **preliminares**). No hay datos de costos: solo se dice que un
  cultivo permanente suele pedir más inversión al inicio.

### Radar de la época lluviosa: Sentinel-1 en Daule (14 nov, 19:00)

NISAR solo tiene pasadas desde junio de 2026, es decir, de la época seca. Para saber dónde se acumula el
agua en invierno se procesó otro radar: Sentinel-1 (ESA), en el producto **OPERA RTC-S1** que elabora el
JPL de la NASA y distribuye ASF (banda C, polarización VV, 30 m). NISAR sigue siendo el dato central; esta
serie va aparte (`src/sentinel.py`) y no se mezcla con los rasgos de NISAR.

```
python -m src.sentinel daule procesar     # enero a mayo -> datos/procesados/_s1_tmp/ (se puede repetir)
python -m src.sentinel daule calibrar     # compara con NISAR en fechas cercanas y propone el umbral
python -m src.sentinel daule tabla        # invierno_daule.npz y columna `agua_invierno`
```

- **Lo leído:** 46 fechas, del 2 de enero al 30 de mayo de 2026 (órbitas 18 ascendente y 40 descendente),
  con el 100 % de la zona cubierta en todas. Cada archivo (~7 MB) se trae a la memoria y no se guarda: en
  el disco quedan solo los resúmenes por fecha. Unos 25 segundos por fecha; ninguna falló.
- **Cómo se detecta el agua:** promedio de 3 × 3 píxeles (~90 m) y luego VV por debajo de un umbral en dB.
  Se descartan los píxeles que el producto marca como sombra o inversión del relieve.
- **El umbral se eligió comparando con NISAR**, no a ojo. Se leyeron además 9 fechas de Sentinel-1 de la
  época seca que caen un día antes de una pasada de NISAR, y se comparó el agua de los dos radares cuadro
  por cuadro con nueve umbrales (de −14 a −22 dB). El que más se parece es **−19 dB**.

| Umbral VV | Cuadros con agua para los dos | Solo Sentinel-1 | Solo NISAR | Coincidencia |
|---|---|---|---|---|
| −17 dB | 3.589 | 10.820 | 767 | 24 % |
| −18 dB | 3.331 | 8.621 | 1.025 | 26 % |
| **−19 dB** | 2.959 | 6.686 | 1.397 | **27 %** |
| −20 dB | 2.478 | 5.112 | 1.878 | 26 % |
| −21 dB | 2.012 | 3.726 | 2.344 | 25 % |

- **La coincidencia cuadro por cuadro es baja (27 %)** y hay que decirlo. Son dos radares distintos: la
  banda C ve oscuros los rastrojos lisos y los arrozales recién sembrados, y la banda L ve brillante un
  arrozal con plantas. Lo que sí coincide es la cantidad y el ritmo: con −19 dB, Sentinel-1 da agua en el
  1,6 % de la zona en julio, 1,0 % en agosto, 1,1 % en septiembre y 4,5 % en octubre; NISAR da 0,8–1,0 %,
  0,3 %, 0,1–0,3 % y 0,4–4,0 %.
- **El invierno se ve claro:** agua en el 0,9 % de la zona en enero, 2,4 % en febrero, **8,0 % en marzo**,
  4,4 % en abril y 2,9 % en mayo.
- **Comprobación con el mapa ESA WorldCover 2021:** de los cuadros con agua en invierno (10 % o más del
  cuadro), el 57 % es humedal, el 27 % cultivo, el 14 % agua, el 2 % pasto, el 1 % árboles y ninguno es
  zona construida. Encuentra el 45 % del agua y de los humedales de ese mapa.

| Cuadros de Daule con agua | Época seca (NISAR) | Invierno (Sentinel-1) |
|---|---|---|
| En el 5 % del cuadro o más | 7,2 % | 18,8 % |
| En el 10 % o más | 3,8 % | 12,3 % |
| En el 30 % o más | 0,3 % | 3,0 % |

- **El 6,8 % de los cuadros de Daule se ve seco en la época seca pero tiene agua en invierno.** Antes la
  app les recomendaba cualquier cultivo; ahora no.
- **En el puntaje** (`src/aptitud.py`): factor nuevo "Invierno", con los mismos límites del encharcamiento.
  Baja a los cultivos que no soportan el agua y favorece al arroz. Cuando un terreno tiene este dato, los
  terrenos vecinos dejan de contar en el puntaje: servían para suponer si se moja en invierno, y aquí eso
  ya está medido. Para el arroz, el agua vista en invierno también cubre la falta de lluvia.
- **Efecto en Daule:** el arroz queda primero en el 23 % de los terrenos (antes en el 10 %) y el resultado
  más repetido baja del 43 % al 38 %.
- **En la app:** aviso "Época lluviosa: el radar vio agua en el X % de tu terreno", capa "Agua en invierno
  (Sentinel-1)" y un gráfico por pasada, separado de los de NISAR.
- **Terreno para la demostración:** `?lat=-1.9444&lon=-79.8489`. NISAR no vio agua (0 %) ni en los vecinos,
  pero en invierno tuvo agua en el 43 % del terreno: solo arroz (100); el siguiente es palma con 51.
- **Límites:** es un solo invierno (2026); el umbral se calibró solo en Daule y con fechas de la época seca;
  bajo árboles la banda C no ve el agua; un cuadro oscuro puede ser suelo liso y no agua. Santo Domingo no
  se procesó (hay 366 archivos de 46 fechas): ahí la app sigue usando los terrenos vecinos.

### Tipo de terreno entrenado con un mapa de referencia (14 nov, 18:00)

El primer modelo (KMeans) agrupaba los terrenos sin que nadie le dijera qué había en cada uno, y no
había con qué medir si acertaba. Ahora aprende de un mapa ya hecho y su acierto se mide.

- **Referencia:** ESA WorldCover 2021 v200 (10 m, 11 clases, exactitud mundial 76,7 %, licencia
  CC BY 4.0; la ESA es agencia socia de Space Apps). Se lee por internet solo la ventana de cada zona:
  `python recolectar_referencia.py descargar worldcover` crea
  `datos/procesados/referencia_worldcover_ZONA.csv`, con la parte de cada cuadro que ocupa cada clase.
- **MapBiomas Ecuador** (la fuente que el equipo prefería) **no se pudo usar**: su archivo pide iniciar
  sesión con una cuenta de Google. Si alguien baja `ecuador_coverage_2022.tif`, `_2023.tif` y `_2024.tif`
  con el navegador y los guarda en `datos/crudos/referencia/`, el mismo script los usa.
- **Modelo:** bosque aleatorio (scikit-learn) con los 7 rasgos del radar NISAR más la pendiente. Aprende
  solo de los cuadros donde una clase ocupa al menos el 60 % (41.568 de 57.035). Luego clasifica todos
  los cuadros con el radar de 2026: `python -m src.cobertura entrenar`.
- **Reglas físicas encima del modelo:** agua en la mitad o más de las pasadas = "agua"; agua en el 10 %
  o más = "terreno que se inunda"; con más de 10° de pendiente, o si el modelo no está bastante seguro
  (probabilidad menor de 0,75), no se marca "zona construida".
- **Acierto, medido en bloques de ~7,5 km que el modelo no vio:** coincide con la referencia en el
  **79 %** de los cuadros (decir siempre la clase más común daría 52 %). Santo Domingo 86 %, Daule 71 %.

| Tipo de terreno | Encuentra | Acierta cuando lo dice |
|---|---|---|
| Árboles o vegetación densa | 86 % | 95 % |
| Cultivo de ciclo corto | 73 % | 82 % |
| Zona construida | 76 % | 77 % |
| Terreno que se inunda | 72 % | 60 % |
| Pasto o vegetación baja | 70 % | 51 % |
| Agua | 47 % | 44 % |

- "¿Es cultivo de ciclo corto, sí o no?": acierta en el 91 % de los cuadros.
- **Comparación con el modelo anterior** (mismo mapa de referencia): cuando decía "zona construida"
  acertaba el 59 % en Santo Domingo y el 33 % en Daule, y marcaba como construidas 62 laderas de más
  de 10° que no lo eran. Solo encontraba el 27 % del agua y de los humedales de Daule.
- **Resultado:** Santo Domingo, 78 % árboles, 19 % pasto o vegetación baja, 3 % zona construida.
  Daule, 36 % cultivo de ciclo corto, 31 % pasto o vegetación baja, 21 % terreno que se inunda, 9 %
  árboles, 2 % agua, 1 % zona construida.
- **Comprobación a ojo:** el centro de Santo Domingo (25 de 25 cuadros construidos), Salitre (12 de 25),
  Daule (14 de 25) y el terreno inundado de la demostración (terreno que se inunda).
- **Límites:** la referencia es de 2021 y es un mapa, no trabajo de campo. No separa un bosque de un
  cultivo de árboles (cacao, palma, banano). "Agua" es la clase más débil: un río angosto no llena un
  cuadro de 250 m. No cambia el puntaje: sirve para avisar y para dejar fuera lo que no es cultivable.
- El archivo `datos/procesados/cobertura_evaluacion.json` guarda estas cifras; la app las muestra.

**Radar de la época lluviosa (ya procesado en Daule: ver la sección anterior).** NISAR solo tiene pasadas desde junio de 2026.
El producto OPERA RTC-S1 (Sentinel-1, banda C, 30 m, en ASF) sí tiene la época lluviosa: sobre Daule hay
221 archivos de 46 fechas entre enero y mayo de 2026 (órbitas 18 ascendente y 40 descendente), y sobre
Santo Domingo 366 archivos de 46 fechas. Serviría para ver la inundación de invierno. No se ha descargado.

### El análisis ya depende del terreno (14 nov, 17:00)

**El problema.** Se midió con 500 terrenos al azar por zona: en Santo Domingo el 90 % recibía exactamente
los mismos tres cultivos, y en Daule el 98 %. Causas: la lluvia de NASA POWER es un solo número para toda
la zona (su celda mide ~50 km), la app no sabía nada del suelo y el puntaje daba 100 a todo lo que cayera
dentro de un rango ancho. Después de los cambios, el resultado más repetido baja al **27 %** de los
terrenos en Santo Domingo y al **43 %** en Daule.

**1. Datos con detalle local** (`python -m src.suelo_lluvia ZONA`; no son de la NASA: hay que citarlos)
| Dato | Fuente | Detalle | Santo Domingo | Daule |
|---|---|---|---|---|
| Lluvia del año y de cada mes | CHELSA V2.1, promedio 1981–2010 | ~1 km | 2.861–4.965 mm | 1.304–1.889 mm |
| pH del suelo (0–30 cm) | SoilGrids 2.0 (ISRIC), CC BY 4.0 | 250 m | 4,8–6,1 | 5,6–6,6 |
| Textura (arena y arcilla) | SoilGrids 2.0 | 250 m | 87 % franco arcilloso | franco arcilloso y franco arcillo arenoso |
- NASA POWER marcaba 1.559 mm para todo Santo Domingo y 770 mm para todo Daule: cerca de la mitad. La
  tabla conserva ese valor en la columna `lluvia_power`; la columna `lluvia` ahora es la de CHELSA.
- No se bajó ningún archivo grande: de SoilGrids se pide solo el recuadro (12 KB por capa; quedan en
  `datos/crudos/suelo/`) y de CHELSA se lee en remoto solo la ventana de la zona.
- Columnas nuevas de la tabla por celda: `ph`, `arcilla`, `arena`, `materia_organica`, `lluvia_power`,
  `agua_vecinos`. La lluvia mensual va aparte, en `datos/procesados/lluvia_mensual_ZONA.npz`.

**2. Puntaje graduado** (`src/aptitud.py`)
- Temperatura, lluvia y pH usan dos rangos por cultivo, de las fichas de FAO EcoCrop
  (`tablas/ecocrop_cultivos.csv`): el **ideal** (nota 1) y el que el cultivo **aguanta** (nota 0). Entre
  uno y otro la nota baja en línea recta. Antes cualquier valor dentro del rango valía 100.
- **Cultivos de ciclo corto** (maíz, arroz, yuca, papa...): la lluvia se compara con la de los meses del
  cultivo, sembrando en el mes que más conviene, y no con la de todo el año. Es como lo hace el modelo
  EcoCrop, y el catálogo del equipo pide no comparar la lluvia del año con la del ciclo.
- **Llover de más** (cultivos permanentes) resta como máximo la mitad de la nota: el daño llega por el
  drenaje y las enfermedades, que ya se miden aparte. Valor inicial sin calibrar (`PESO_EXCESO_LLUVIA`).
- **Arroz:** si la lluvia no alcanza pero el radar vio agua sobre el terreno, la falta de lluvia no resta.
- **Cultivos andinos:** haba, maíz suave y quinua usan como ideal el rango de temperatura del Ecuador
  (Basantes, 2015, *Manejo de cultivos andinos del Ecuador*, tomado del catálogo del equipo). La papa y el
  tomate de árbol no tienen ese dato: siguen con el rango preliminar de `requisitos_cultivos.csv`, porque el
  ideal mundial de EcoCrop para la papa (15–25 °C) la deja mal en los Andes. **Pendiente para la Sierra.**

**3. Los terrenos vecinos** (`python -m src.vecindad ZONA`)
- Columna `agua_vecinos`: parte de los cuadros a menos de 1 km donde el radar vio agua. Cuenta en el
  puntaje: el radar solo tiene pasadas de la época seca, así que si los vecinos tuvieron agua, el terreno
  puede mojarse en invierno. En Daule el 19 % de los cuadros tiene agua en más del 10 % de sus vecinos.
- La app muestra además qué tipo de terreno hay alrededor y si el terreno está más alto o más bajo.

**4. Lo que se siembra en la provincia** (`tablas/siembra_provincias.csv`, 443 filas, ESPAC 2025)
- Por cada cultivo y provincia: hectáreas sembradas y rendimiento frente al promedio del país. Es lo más
  cercano que existe a "cómo les ha ido a los vecinos": la ESPAC no baja de la provincia.
- Niveles: se siembra y rinde bien / se siembra pero rinde menos / casi no se siembra (menos de 500 ha).
- No cambia el puntaje. **Ordena** a los cultivos de aptitud parecida (ver abajo).

**5. Nuevo orden** (`src/recomendar.py`). Primero la aptitud, por franjas de 5 puntos (los datos no
alcanzan para decir que 97 es mejor que 96). Dentro de una franja: primero el que se siembra y rinde bien
en la provincia, luego el de mejor mercado y al final la respuesta a "¿Qué buscas?".

**Terrenos de demostración**
| Terreno | Antes | Ahora |
|---|---|---|
| Santo Domingo `?lat=-0.33&lon=-79.12` | maracuyá, plátano, maíz duro (todos 100) | maíz duro 100, cacao 94, palma 91 |
| Daule seco `?lat=-1.8156&lon=-79.6733` | maíz duro 100, maracuyá 92, yuca 92 | plátano, palma y banano 100 (también maíz duro, cacao y piña); arroz 78 sin riego y 96 con riego |
| Daule inundado `?lat=-1.9356&lon=-79.6511` | arroz 49 sin riego, 92 con riego | arroz 100 con o sin riego (el radar vio el agua); los demás, 30 |

**Límites que hay que declarar**
- SoilGrids es un mapa mundial hecho con un modelo, no un análisis del suelo del terreno. CHELSA es un
  promedio de 30 años y parece dar algo más de lluvia que las estaciones (no se comprobó con el INAMHI).
- EcoCrop es mundial. El catálogo del equipo pide no tratar sus rangos como reglas automáticas validadas:
  la app los usa como orientación y así debe decirse.
- En Daule seco muchos cultivos siguen empatados en 100: el clima sirve para casi todos y lo que decide
  es la provincia y el mercado.
- No hay datos de qué cultivo hay en cada terreno vecino ni de cómo le fue. Para eso haría falta el mapa
  de uso de la tierra del MAG (SIGTIERRAS), que no se ha descargado.

**Archivos del equipo revisados (14 nov)**
- `SMARTSEEDS_catalogo_integrado_v07.2.json` (20 cultivos, 123 fuentes): sus rangos de EcoCrop de cacao,
  maíz, quinua, papa, yuca y haba son idénticos a los de `tablas/ecocrop_cultivos.csv`. De ahí salieron
  los rangos andinos. El archivo no se copió al repositorio.
- `CÓDIGO ESTADÍSTICAS AGROPECUARIAS.json` (20 cultivos, sin fuentes): **no se usó en la app.** Coinciden
  con los datos oficiales la producción de cacao 2025, la superficie de papa 2025, rosas y claveles 2025 y
  los precios de la soya y del cacao CCN51. No coinciden la producción de papa 2025 (200.000 t frente a
  229.371 t de la ESPAC), la de maíz duro 2021 (319.823 t frente a 1.699.370 t) ni los precios del maíz
  duro y del cacao fino de aroma de 2021. Las cifras de crédito público parecen estar en otra unidad. El
  comercio exterior no se pudo comprobar. Hace falta la fuente y el año de cada cifra.

### Vista satelital, tipo de terreno, mercado y EcoCrop (14 nov, tarde)

**Fondos del mapa** (se cambian en el cuadro de la esquina superior derecha del mapa):
- *Croquis*: OpenStreetMap, con calles y nombres.
- *Foto satelital*: imágenes de alta resolución de Esri World Imagery; se ven las parcelas reales y sirve
  para dibujar el lindero. No es de la NASA: hay que citarla.
- *NASA 31 oct (óptico)*: imagen diaria del sensor VIIRS (satélite Suomi NPP) servida por NASA GIBS, del
  mismo día de la última pasada de NISAR sobre Daule. Tiene ~250 m de detalle y muestra las nubes: sirve
  para explicar por qué hace falta un radar.

**Tipo de terreno (modelo entrenado con las pasadas de NISAR):** `python -m src.cobertura entrenar`
- Cada cuadro se describe por cómo se comportó el radar en las 10 pasadas: brillo medio de HH y HV, cuánto
  cambió entre fechas, la fecha más oscura, cuántas veces tuvo agua y la diferencia HH − HV.
- KMeans (8 grupos) junta los cuadros parecidos, sin datos de campo. Se entrenó con 57.035 cuadros de las
  dos zonas. Cada grupo recibe nombre con reglas físicas del radar (umbrales en `src/cobertura.py`).
- Resultado: Santo Domingo 92 % vegetación densa, 6 % vegetación baja, 2 % zona construida. Daule 67 %
  vegetación baja, 14 % cultivo de ciclo corto en actividad, 11 % vegetación densa, 6 % terreno que se
  inunda, 2 % zona construida.
- Comprobación (solo con lugares conocidos): el centro de Santo Domingo y el de Salitre salen como zona
  construida; el terreno inundado de Daule, como terreno que se inunda.
- **Límites:** no distingue qué cultivo es; con cuadros de ~250 m solo ve las zonas más construidas (los
  pueblos con muchos árboles salen en parte como vegetación densa); no se comprobó en el campo.
- Entrenar necesita scikit-learn (entorno de desarrollo). La app publicada no: lee la columna `cobertura`.

**Mercado con datos reales, por provincia** (`tablas/mercado.csv`, 45 filas, se compara 2024 con 2025).
La tabla ya no se escribe a mano: la arma `python -m src.preparar_mercado` con dos archivos oficiales
guardados en `datos/crudos/mercado/` (no se suben a GitHub; las direcciones están al inicio de ese programa).

Filas nacionales (13 de los 15 cultivos):
| Cultivo | Superficie | Precio al productor | Resultado | Rinde (t/ha) |
|---|---|---|---|---|
| Plátano | −16,9 % | +90,5 % | Oportunidad alta | 6,81 |
| Maracuyá | −8,2 % | +14,7 % | Oportunidad alta | 10,55 |
| Palma aceitera | −4,1 % | +7,5 % | Oportunidad alta | 19,99 |
| Banano | +19,4 % | +24,6 % | Oportunidad media | 44,05 |
| Café | +44,4 % | +33,0 % | Oportunidad media | 0,24 |
| Yuca | +33,0 % | +4,9 % | Oportunidad media | 5,87 |
| Maíz duro | +9,5 % | −7,5 % | Oportunidad media | 5,09 |
| Arroz | −10,5 % | −24,4 % | Oportunidad media | 5,02 |
| Maíz suave | −29,8 % | −26,9 % | Oportunidad media | 1,37 |
| Tomate de árbol | −40,8 % | +4,9 % | Oportunidad media | 15,50 |
| Cacao | +13,3 % | −13,2 % | Mercado saturado | 0,82 |
| Piña | +51,7 % | −2,7 % | Mercado saturado | 68,18 |
| Papa | +16,7 % | −32,1 % | Mercado saturado | 14,35 |

Además hay 32 filas por provincia (16 provincias). En las zonas del proyecto: Santo Domingo (cacao, plátano,
maracuyá, yuca, piña), Guayas (cacao, banano, maíz duro, arroz), Cotopaxi (cacao, plátano, papa) y
Tungurahua (papa). Si un cultivo no tiene fila de la provincia, la app usa la nacional y lo dice.
La provincia puede cambiar el resultado: el cacao está saturado en el país y en Guayas, pero no en
Santo Domingo (−0,8 % de superficie); el maíz duro es "media" en el país y "saturado" en Guayas (+27,1 %).

- **Superficie y rendimiento:** INEC, ESPAC 2024 y 2025, por provincia, de la base histórica que publica el
  MAG-SIPA (`superficie-produccion.xlsx`). Se comprobó que sus totales nacionales de los 15 cultivos y
  varios valores por provincia son iguales a los tabulados oficiales de la ESPAC (`Tabulados_csv.zip`).
- **Precio:** MAG-SIPA, precio mensual al productor por provincia (`precios-productor-ponderado.xlsx`).
  Se compara el promedio de 2024 con el de 2025 usando solo los meses (y provincias) que tienen precio en
  los dos años. Un producto por cultivo (por ejemplo cacao CCN51 almendra seca, papa superchola).
- **No se escribe la fila** (la app dice "sin datos") si hay menos de 6 meses con precio en los dos años o
  si la provincia tiene menos de 500 ha del cultivo. Los dos umbrales los eligió el equipo.
- **Sin datos:** haba (solo 5 meses con precio, y en una provincia) y quinua (sin precios en 2024–2025).
- La app muestra además cuánto rinde el cultivo en toneladas por hectárea y quintales por cuadra, ahora
  con el dato de la provincia cuando existe. Cada fila guarda los números originales en la columna `notas`.
- **Cambio respecto a la primera versión (6 cultivos):** antes el precio comparaba solo diciembre de 2024
  con diciembre de 2025 (boletín del SIPA). Ahora compara los dos años completos, igual que la superficie.
  Por eso el cacao pasó de −43,6 % a −13,2 % (sigue saturado) y la palma de −10,4 % a +7,5 % (pasó de
  "media" a "alta": el precio subió en el promedio del año, aunque bajó al final de 2025).
- **Límites:** el precio nacional es un promedio simple entre provincias, no el ponderado oficial; la ESPAC
  es una encuesta y el dato de una provincia tiene más error que el nacional; la ESPAC no separa café
  robusta de arábigo; para el banano se usa el precio "spot"; maíz suave y haba usan solo una de sus dos
  formas (seco y tierna). Hay precios de 2026 (hasta octubre) que no se usan porque aún no hay ESPAC 2026.
- Entre cultivos empatados en aptitud va primero el de mejor mercado, y el "saturado" va al final.

**FAO EcoCrop** (`tablas/ecocrop_cultivos.csv`): rangos óptimos y absolutos de temperatura, lluvia y pH,
altitud máxima y ciclo de los 15 cultivos, copiados de la ficha oficial de cada uno
(`ecocrop.apps.fao.org`, licencia CC BY 4.0). **Desde las 17:00 del 14 nov sí se usan en el puntaje** (ver la sección anterior). La primera simulación, hecha antes, había mostrado:
- En Santo Domingo los empates en 100 bajan de 8 a 3 (cacao, palma, piña), lo que mejora el resultado.
- Pero EcoCrop es mundial: sin un límite de altura propio del Ecuador pone haba y maíz suave con 100 en
  Daule, y baja la papa a 71 a 3.000 m y a 45 a 3.500 m. Por eso no se adoptó sin acuerdo del equipo.

### El radar a la vista en la app (14 nov)
- **Gráfico por terreno:** en las zonas detalladas, debajo de los datos del radar, hay un desplegable
  "📈 Ver lo que vio el radar en cada pasada". Muestra tres gráficos pequeños, uno por medida:
  vegetación, agua sobre el terreno y humedad del suelo, fecha por fecha. Sirve para un punto y para un
  terreno dibujado (promedia sus celdas). Ejemplo real, terreno inundado de Daule: el agua cubre el 92 %
  del terreno en junio, baja al 8 % en septiembre y vuelve al 75 % a fines de octubre.
- **Capa sobre el mapa:** encima del mapa se elige qué pintar (agua, vegetación o humedad). Cada capa usa
  un solo color, de claro (poco) a oscuro (mucho); en gris, donde el radar no tiene datos.
- **Corrección:** sobre el agua el índice de vegetación sale alto por error (HH y HV son casi ruido). Ahora
  las pasadas en que más de la mitad de la celda era agua no cuentan para la vegetación. Cambió la
  vegetación de 1.439 celdas de Daule (4 %); el resto de la tabla quedó igual.
- La app lee `nisar_ZONA.npz` y `humedad_ZONA.npz` (unos 3 MB por zona); no procesa nada en vivo.

### NISAR: cómo se procesó y qué salió (14 nov, Santo Domingo)
```
python -m src.nisar santo_domingo procesar   # GCOV: HH y HV por celda y fecha (~8 min)
python -m src.nisar santo_domingo humedad    # SME2: humedad de suelo (~4 min)
python -m src.nisar santo_domingo capas      # llena vegetacion, encharcamiento y humedad en la tabla
```
- **Datos usados:** GCOV `frequencyB` (HH y HV a 80 m), órbita 76 ascendente, 19 jun – 29 oct 2026; SME2 (humedad de suelo nivel 3, 200 m), 19 jun – 17 oct 2026.
- **Cobertura:** el radar cubre el **76 %** de las celdas. La franja oeste (longitud menor a −79,35) queda fuera de esta órbita; ahí la app muestra "sin dato". Opciones: mover el recuadro al este o sumar la órbita 112.
- **Retrodispersión:** HH mediana −6,0 dB y HV −11,4 dB: paisaje de vegetación densa.
- **Vegetación (RVI):** entre 0,83 y 0,95 en casi toda la zona. Se muestra, pero no entra en el puntaje.
- **Encharcamiento:** prácticamente 0 % en toda la zona. Son fechas de **época seca**, y a 80 m los ríos angostos no se distinguen.
- **Humedad (SME2):** media 0,26 m³/m³ (52 % de saturación). La NASA marca como "recomendado" solo el **6 %** de las celdas (vegetación densa); en el resto se muestra el valor pero no cuenta en el puntaje.
- **Limitación a declarar:** en esta zona y época, las capas NISAR todavía no cambian el orden de los cultivos. Para que el radar pese en la recomendación hacen falta fechas de época lluviosa o una zona con inundación real (por ejemplo, arroceras de Los Ríos o Guayas).
- La app acepta un enlace directo a un terreno: `http://localhost:8501/?lat=-0.33&lon=-79.12`.

### NISAR: segunda zona, Daule – Salitre – Samborondón (14 nov)
Zona arrocera de Guayas. Recuadro: lon −80.05 a −79.65, lat −2.05 a −1.65. Se procesó con los mismos
comandos, usando `daule` como nombre de zona.
- **Por qué esta zona:** se midió el agua visible (HH menor a −18 dB) en una fecha de cada candidata.
  21 de junio: Babahoyo 1,5 %, Daule 1,5 %, Vinces 0,1 %. 31 de octubre: Daule 4,0 %, Babahoyo 3,0 %.
  En la imagen del radar lo oscuro tiene forma de ríos y de parcelas, no de ruido.
- **Datos usados:** GCOV `frequencyB`, órbita 112 descendente (frames 89 y 90), **10 fechas**, 21 jun – 31 oct 2026.
- **Cobertura:** el radar cubre el **100 %** de las celdas (32.400 celdas de ~250 m).
- **Retrodispersión:** HH mediana −8,2 dB y HV −16,8 dB. Vegetación (RVI) entre 0,33 y 0,80:
  campo abierto y cultivos, no bosque denso como en Santo Domingo.
- **Encharcamiento:** el 7,2 % de las celdas tuvo agua en al menos el 5 % de las pasadas, el 3,8 % en al
  menos el 10 % y el 0,3 % en al menos el 30 %. El agua visible baja de 1,5 % (junio) a 0,1 % (septiembre)
  y sube a 4,0 % a fines de octubre.
- **Humedad (SME2):** 9 fechas, 21 jun – 19 oct 2026. Media 0,27 m³/m³ (53 % de saturación), con dato en el
  97 % de las celdas. La NASA marca como "recomendado" el dato en el **49 %** de las celdas (en Santo Domingo
  era el 6 %), así que aquí la humedad sí cuenta en el puntaje de la mitad de los terrenos.
- **Aquí NISAR sí cambia la recomendación.** Terreno inundado (`?lat=-1.9356&lon=-79.6511`, agua en el 37 %
  de las pasadas): el único cultivo que supera el mínimo es **arroz** (49/100 sin riego, 92/100 con riego).
  Terreno seco (`?lat=-1.8156&lon=-79.6733`): maíz duro 100, maracuyá 92 y yuca 92.
- **Limitaciones:** NASA POWER da 770 mm de lluvia al año para toda la zona, por eso sin riego el arroz
  pierde puntos por "llueve poco"; hay que marcar "Sí, tengo riego". El umbral de −18 dB no está calibrado:
  una superficie lisa y oscura puede ser agua, un arrozal inundado o suelo liso recién preparado.

### Pendientes por rol
- **Cultivos:** `tablas/requisitos_cultivos.csv` tiene valores **preliminares** (aproximados). Verificar cada uno con FAO EcoCrop / INIAP y quitar la palabra PRELIMINAR de la columna `notas`.
  El catálogo del equipo trae el **suelo** (pH, textura, drenaje) pero no la altura, la temperatura ni la lluvia que usa el puntaje. Para poder recomendar los cultivos nuevos del catálogo (fréjol, arveja, lenteja, chocho, trigo, cebada, amaranto, tomate, soya) falta sacar esos tres rangos de las mismas fuentes y agregarlos a `requisitos_cultivos.csv`. Rosa, clavel, aguacate, mora y uvilla todavía no tienen ningún dato.
- **Mercado:** `tablas/mercado.csv` ya tiene 13 cultivos a nivel nacional y 32 filas por provincia. Faltan haba y quinua (el SIPA no tiene precios suficientes) y los cultivos nuevos del catálogo.
- **Radar:** la segunda zona ya está (Daule, ver arriba). Falta calibrar el umbral de agua y buscar fechas de época lluviosa. Cada archivo GCOV pesa ~7 GB: no descargar, usar la lectura remota.
- **Programación:** textos en inglés para la entrega y publicar la app (cuando estén unidas la Costa y la Sierra). El gráfico del radar y la capa sobre el mapa ya están.

### Uso de IA (declarar en la página del proyecto)
La estructura y el código inicial se escribieron con ayuda de un asistente de IA (Claude, de Anthropic)
y fueron revisados por el equipo.
