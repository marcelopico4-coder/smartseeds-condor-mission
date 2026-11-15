# Datos que faltaban: uso de la tierra por parcela, riego, páramo y heladas (MAG)

Hecho el sábado 14 de noviembre de 2026 (23:00) en una sesión de apoyo. Busca completar lo que no
tenía datos: cultivos sin parcelas (cacao, plátano, yuca, todos los de la Sierra) y cultivos con muy
pocos puntos de campo. **Solo se crearon archivos nuevos**; no se tocó la app ni las tablas por celda.

## 1. De dónde salió

El geoportal del MAG tiene **37 servicios de mapas**, no solo los dos que se usaban. Se listaron
todos y se comprobó cuáles cubren las cuatro zonas (Santo Domingo, Daule y los recuadros de
Tungurahua y Cotopaxi del archivo del equipo). Página: http://geoportal.agricultura.gob.ec/geoservicios/cartografia.html

| Capa | Qué trae | Descargada |
|---|---|---|
| Cobertura y uso de la tierra y sistemas productivos 1:25.000 | El uso de cada parcela, con el cultivo, si tiene riego y el sistema de producción. 522.554 parcelas en el país | Sí |
| Catastro bananero 1:5.000 | Fincas bananeras con variedad y riego | Sí |
| Catastro florícola 1:5.000 | Fincas de flores | Sí |
| Censo palmicultor 1:50.000 | Un punto por palmicultor, con año de siembra | Sí |
| Área con riego parcelario 1:5.000 | Proyectos de riego tecnificado (185 en el país) | Sí |
| Páramo 1:100.000 | Polígonos de páramo | Sí |
| Riesgo por helada del subsector agrícola, por parroquia | Nivel de amenaza y de riesgo | Sí |
| Zonificación agroecológica 1:25.000 de 39 cultivos | Clase de aptitud oficial (óptima, moderada, marginal, no apta) por terreno | **No** (ver sección 6) |
| Unidad geopedológica y aptitud agrícola 1:25.000 | Suelo por terreno: textura, pH, drenaje, profundidad, fertilidad | **No** |
| Susceptibilidad a inundaciones 2024, 1:25.000 | Clase de susceptibilidad por terreno | **No** |
| Riesgo por sequía e inundación por parroquia | Índices por parroquia | **No** |

Lo descargado pesa 152 MB y está en `datos/crudos/uso_tierra_mag/ZONA/` (no se sube a GitHub).
Se guardó solo la geometría y los atributos útiles, sin nombres de predios ni de personas.

## 2. Parcelas por cultivo: lo que antes no existía

Mapa de cobertura y uso de la tierra. Número de parcelas dentro de cada zona:

| Cultivo de la app | Santo Domingo | Daule | Tungurahua | Cotopaxi | Total | Hectáreas |
|---|---|---|---|---|---|---|
| Cacao | 1.273 | 356 | 0 | 0 | 1.629 | 22.857 |
| Plátano | 855 | 33 | 0 | 0 | 888 | 17.230 |
| Arroz | 0 | 573 | 0 | 0 | 573 | 165.337 |
| Maíz (sin decir duro o suave) | 117 | 93 | 97 | 109 | 416 | 21.726 |
| Yuca | 404 | 0 | 0 | 0 | 404 | 2.113 |
| Maracuyá | 213 | 0 | 0 | 0 | 213 | 870 |
| Palma aceitera | 139 | 7 | 0 | 0 | 146 | 10.449 |
| Papa | 0 | 0 | 60 | 78 | 138 | 11.537 |
| Banano | 28 | 81 | 0 | 0 | 109 | 6.597 |
| Piña | 102 | 1 | 0 | 0 | 103 | 2.398 |
| Café | 39 | 1 | 0 | 0 | 40 | 190 |
| Tomate de árbol | 0 | 0 | 37 | 0 | 37 | 882 |
| Haba | 0 | 0 | 5 | 7 | 12 | 152 |
| Quinua | 0 | 0 | 0 | 11 | 11 | 211 |
| Pasto | 2.223 | 362 | 720 | 529 | 3.834 | 184.162 |
| Páramo | 0 | 0 | 350 | 230 | 580 | 205.592 |

Otros cultivos con parcelas que la app no evalúa: tomate riñón 107, rosas 106, mango 102, palmito 92,
pimienta negra 92, brócoli 54, soya 53, abacá 52, mora 23, cebolla 13, cebada 11, aguacate 9.

Además: 142 fincas del catastro bananero (4.597 ha), 97 fincas florícolas (1.799 ha, 91 en Cotopaxi)
y 214 palmicultores en Santo Domingo.

**Cuidados al leer la tabla:**
- El mapa se levantó entre 2009 y 2015 (programa SIGTIERRAS). Dice qué se sembraba entonces.
- En la Sierra gran parte del área agrícola no nombra un cultivo: "misceláneo de ciclo corto"
  (399 parcelas, 75.192 ha) y "misceláneo de maíz y pasto" (220 parcelas, 32.273 ha).
- "Maíz" casi nunca dice si es duro o suave: va aparte, en `uso_maiz`.
- "Cacao - plátano" y otras mezclas se contaron con el primer cultivo del nombre.
- **Siguen con muy pocas parcelas: haba (12), quinua (11) y café (40).** Para chocho no hay ninguna.

## 3. Tres datos nuevos que valen más que las parcelas

### 3.1 Riego por parcela

| Zona | Área agrícola con riego | Cultivos con más riego |
|---|---|---|
| Daule | 85 % (184.051 de 215.964 ha) | arroz 160.979 ha, banano 5.102, cacao 1.586 |
| Tungurahua | 54 % | pasto 13.666 ha, maíz 2.704, papa 1.345, tomate de árbol 453 |
| Cotopaxi | 38 % | pasto 18.309 ha, maíz 1.514, papa 959 |
| Santo Domingo | 10 % | pasto 12.651 ha, piña 2.268 |

En Daule, **160.979 de las 165.337 ha de arroz figuran con riego**. Esto explica el problema ya
medido (la app casi no recomienda arroz ahí si el agricultor no marca "tengo riego") y da una
salida: sugerir "sí" por defecto donde `riego_mapeado` es alto, dejando que el agricultor lo corrija.

### 3.2 Páramo cartografiado

El mapa de uso marca como páramo **97.454 ha en el recuadro de Tungurahua y 108.138 ha en el de
Cotopaxi**: alrededor de un tercio de cada recuadro. Es mejor que la regla fija de 3.300 m de
`NOTA_10_BLOQUES_SIERRA.md`, porque es el páramo que realmente existe; conviene usar las dos:
`paramo_mapeado` para avisar y la cota legal como respaldo.

### 3.3 Riesgo oficial de heladas por parroquia

| Zona | Parroquias | Nivel de riesgo |
|---|---|---|
| Tungurahua | 64 | muy alto 9, alto 33, medio 11, bajo 3, muy bajo 4, sin amenaza 4 |
| Cotopaxi | 31 | muy alto 8, alto 20, medio 1, bajo 2 |
| Santo Domingo | 11 | sin amenaza 10, muy bajo 1 |
| Daule | 26 | sin amenaza 26 |

Sustituye con ventaja a calcular las heladas con NASA POWER, que sale unos 3 °C más frío que las
estaciones. Límite: es un índice por parroquia, no por terreno.

## 4. Archivos nuevos

| Archivo | Qué es |
|---|---|
| `src/uso_tierra_mag.py` | Descarga las capas de una zona, cuenta por cultivo y arma la tabla por celda |
| `datos/procesados/uso_tierra_mag_ZONA.csv` | Tabla por celda de las cuatro zonas (3,3 a 3,8 MB cada una) |
| `datos/procesados/validacion_uso_tierra_costa.json` | Medición de la sección 5 |

```
python -m src.uso_tierra_mag ZONA descargar   # 2 a 5 minutos por zona
python -m src.uso_tierra_mag ZONA contar
python -m src.uso_tierra_mag ZONA tabla       # pide rasterio (solo desarrollo)
```

`ZONA` puede ser una clave de `src/config.py` o `tungurahua` / `cotopaxi`, que el módulo trae como
recuadros provisionales (`RECUADROS_EXTRA`). **Si los recuadros definitivos de la Sierra son otros,
hay que volver a ejecutar `descargar` y `tabla` con esas claves**: la tabla solo sirve para la
rejilla con la que se calculó.

Columnas de la tabla (misma `celda` y misma rejilla que `celdas_ZONA.csv`):

| Columna | Significado |
|---|---|
| `uso_dominante`, `uso_parte` | Cobertura que más ocupa la celda y qué parte ocupa |
| `uso_cacao`, `uso_platano`, … `uso_tomate_de_arbol` | Parte de la celda con cada cultivo de la app |
| `uso_maiz`, `uso_pasto`, `uso_paramo` | Maíz sin especificar, pasto y páramo |
| `riego_mapeado` | Parte de la celda cuyas parcelas figuran con riego |
| `paramo_mapeado` | Parte de la celda dentro del páramo 1:100.000 |
| `helada_riesgo` | Nivel de riesgo por helada de la parroquia |

## 5. Comprobación y medición en la Costa

### 5.1 ¿Coincide el mapa de uso (2009–2015) con las estimaciones recientes del MAG?

Celdas donde el cultivo ocupa la mitad o más.

| Zona y cultivo | Celdas en el mapa de uso | Siguen en el mapa reciente | Celdas recientes que ya lo eran |
|---|---|---|---|
| Daule, arroz (2025) | 21.867 | 71 % | 89 % |
| Daule, banano (2022) | 725 | 89 % | 75 % |
| Santo Domingo, palma (2022) | 1.159 | 29 % | 77 % |
| Santo Domingo, banano (2022) | 193 | 11 % | 61 % |

El arroz y el banano de Daule casi no se han movido: ahí el mapa de uso sigue siendo una buena
referencia. En Santo Domingo la palma y el banano se redujeron mucho desde entonces: el mapa de uso
dice dónde hubo, no dónde hay.

### 5.2 Puntaje de la app en celdas dominadas por un cultivo

Celdas donde el cultivo ocupa el 60 % o más; muestra de hasta 250 por cultivo. "Top 3" cuenta solo
cultivos que alcanzan el mínimo de aptitud. Con muestras mucho mayores que los puntos de campo.

| Zona | Cultivo | Celdas | Puntaje mediano | En el top 3 |
|---|---|---|---|---|
| Santo Domingo | Cacao | 1.757 | 97,8 | 91 % |
| Santo Domingo | Palma aceitera | 1.000 | 98,7 | 95 % |
| Santo Domingo | Plátano | 1.787 | 87,1 | **0 %** |
| Santo Domingo | Piña | 316 | 76,4 | **0 %** |
| Santo Domingo | Banano | 166 | 91,0 | **0 %** |
| Santo Domingo | Yuca | 120 | 87,6 | **0 %** |
| Daule | Banano | 633 | 100 | 99 % |
| Daule | Cacao | 541 | 100 | 11 % |
| Daule | Arroz, sin riego | 20.778 | 53,2 | 23 % |
| Daule | Arroz, con el riego del mapa | 20.778 | 91,9 | 34 % |

Qué dice esto:
- **La app nunca descarta lo que se siembra**: todos los puntajes medianos pasan de 50 y casi todos de 75.
- **El orden deja fuera cultivos muy sembrados.** En Santo Domingo el plátano es el segundo cultivo
  (17.007 ha) y no entra al top 3 en ninguna de las celdas probadas, igual que yuca, piña y banano.
- **El riego del mapa arregla el puntaje del arroz** (de 53 a 92; el 98 % de las celdas arroceras
  figura con riego), pero no su puesto: sigue en el top 3 solo en el 34 %.
- Confirma, con miles de celdas, lo que ya se había visto con los puntos de campo. La causa está en
  la regla de orden entre cultivos con puntaje parecido, no en la aptitud.

Resultado completo en `datos/procesados/validacion_uso_tierra_costa.json`. La Sierra no se midió:
esta copia no tiene las tablas `celdas_ZONA.csv` de Cotopaxi y Tungurahua.

## 6. Lo que se encontró y no se descargó

- **Zonificación agroecológica 1:25.000 (39 cultivos).** Es la clase de aptitud oficial del MAG por
  terreno, con sus limitantes. Existe para maíz suave, papa (época de lluvia y seca), quinua, tomate
  de árbol, cacao, plátano, banano, yuca, piña, maracuyá, palma, café robusta, arroz y maíz duro, y
  para cultivos que la app no tiene (brócoli, cebada, mora, aguacate, fréjol). **Sería la mejor
  comparación para el puntaje de la app.** Es pesada: unas 26.000 a 29.000 parcelas por cultivo en
  cada recuadro de la Sierra. No hay capa de haba.
- **Unidad geopedológica 1:25.000.** Suelo por terreno (textura, pH, drenaje, profundidad, fertilidad,
  inundabilidad). Más detallado que SoilGrids, que es lo que usa la app hoy.
- **Susceptibilidad a inundaciones 2024** y riesgos por sequía e inundación por parroquia.
- Infraestructura: piladoras, centros de acopio, ferias y mercados mayoristas (acceso al mercado).

## 7. Propuesta de uso (decide la sesión de la app unida)

1. **Ficha del terreno:** "Aquí se sembraba cacao (mapa del MAG, 2009–2015)" con `uso_dominante` o
   los `uso_<cultivo>` de la celda, separado de la recomendación. Llena el vacío de la Sierra, donde
   la capa "Cultivo mapeado (MAG)" no tiene nada.
2. **Riego sugerido** donde `riego_mapeado` ≥ 0,5; el agricultor confirma.
3. **Aviso de páramo** con `paramo_mapeado` o `uso_paramo`, además de la cota de 3.300 m.
4. **Riesgo de heladas** de la parroquia en la ficha, como texto con su fuente.
5. **Validación** en la Sierra con estas parcelas, cuando existan `celdas_ZONA.csv` de la Sierra.
6. No convertir el uso histórico en puntaje sin decisión del equipo.

## 8. Qué quedó sin comprobar

- La licencia de estas capas. El catálogo de Datos Abiertos indicaba uso no comercial para otras
  capas del MAG; citar al MAG y confirmarlo antes de publicar.
- El año exacto de cada parcela del mapa de uso (el servicio no lo trae como atributo).
- Nada de esto se probó dentro de la app.
- No se buscaron fuentes fuera del MAG en esta pasada.

## 9. Fuente para citar

MAG, Geoportal del Agro Ecuatoriano. Cobertura y uso de la tierra y sistemas productivos
agropecuarios 1:25.000; catastro bananero y florícola 1:5.000; censo palmicultor 1:50.000; páramo
1:100.000; riesgo por helada del subsector agrícola.
http://geoportal.agricultura.gob.ec/geoservicios/cartografia.html
