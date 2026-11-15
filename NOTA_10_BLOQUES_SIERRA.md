# Los 10 bloques de la Sierra · nota para la sesión que tiene la app unida

Preparada el sábado 14 de noviembre de 2026 (22:30) en una sesión de apoyo. Contrasta el archivo
`Condor_Mission_10_bloques_CSV.zip` (datos documentales para Cotopaxi y Tungurahua, entregados por
el equipo) con lo que SmartSeeds ya usa. **No se modificó ningún archivo del repositorio** salvo esta nota.

Lo que esta sesión pudo ver: `smartseeds-costa/main` en `62b6351` y la rama `traspaso-sierra`. En ese
repositorio `ZONAS` todavía tiene solo `santo_domingo` y `daule`; la app unida no estaba a la vista.
Si en la app unida algo de esto ya existe, saltarlo.

## 1. Qué agregar, en orden

### 1.1 Aviso de páramo sobre 3.300 m (bloque 10) — usar ya

- **Dato:** la Ley Orgánica de Tierras Rurales y Territorios Ancestrales, artículo 50, no permite
  ampliar la frontera agrícola en páramos no intervenidos sobre los **3.300 m** al norte de 3° S.
  Cotopaxi y Tungurahua cumplen el criterio de latitud.
- **Por qué importa:** `tablas/requisitos_cultivos.csv` admite papa hasta 3.600 m, quinua hasta 3.700 m
  y haba hasta 3.500 m. Hoy la app puede recomendar esos cultivos por encima de la cota.
- **Propuesta:** si la altura del terreno pasa de 3.300 m, mostrar un aviso en la ficha y no presentar
  la lista como recomendación de siembra nueva. No cambia la firma de `aptitud()`: basta la `altura`
  que ya tiene la celda.
- **Texto sugerido:** "Este terreno está sobre los 3.300 m. La ley no permite abrir cultivos nuevos en
  páramo que no haya sido intervenido. Consulta la ordenanza de tu cantón antes de sembrar."
- **Cuidados que pide el bloque:** no es el inicio ecológico del páramo ni un permiso para cultivar
  por debajo; el texto consultado tiene reformas hasta marzo de 2022.
- **Fuente:** Asamblea Nacional del Ecuador (2016). Ley Orgánica de Tierras Rurales y Territorios
  Ancestrales, art. 50, p. 27.
  https://www.sot.gob.ec/download/1234/1-2-base-legal-regulaciones-procedimientos-internos/13492/9-ley-organica-de-tierras-rurales-y-territorios-ancestrales.pdf

### 1.2 Heladas: notas por cultivo (bloque 2) — usar como texto, no como regla

El bloque da categorías cualitativas, sin temperatura crítica ni duración. Para los cultivos que la
app ya evalúa en la Sierra:

| Cultivo de la app | Lo que dice el bloque | Fuente |
|---|---|---|
| Haba | Resiste heladas (cualitativo) | Basantes (2015), p. 28 |
| Maíz suave | Sufre daño por heladas (capítulo general de maíz) | Basantes (2015), p. 78 |
| Tomate de árbol | No encontrado | — |
| Papa, quinua | No vienen en el bloque | — |

Para cultivos que la app todavía no tiene: arveja tolera 0 °C tras emerger y es sensible en la
germinación y al formar el grano; temperaturas letales de FAO EcoCrop (reposo / crecimiento temprano):
arveja −2 / 0 °C, uvilla −2 / −1, aguacate −4 / −1, brócoli −5 / −1.

Basantes Morales, E. R. (2015). *Manejo de cultivos andinos del Ecuador*. ESPE.
https://repositorio.espe.edu.ec/bitstream/21000/10163/4/Manejo%20Cultivos%20Ecuador.pdf

**Propuesta:** una línea en la ficha del cultivo ("Aguanta heladas" / "Las heladas lo dañan") con su
fuente. No convertirlo en puntaje: el propio bloque dice que no son umbrales validados.

### 1.3 La temperatura de NASA POWER sale más fría que las estaciones (bloque 9) — declarar

Medido en esta sesión con las dos estaciones del bloque (INAMHI, Anuario Meteorológico 2014) y la
serie mensual de NASA POWER de 2014 en las mismas coordenadas, ajustada por altura con 6,5 °C por km:

| Estación | Altura | Mínima media 2014 | POWER | POWER ajustado | Diferencia | Mínima absoluta |
|---|---|---|---|---|---|---|
| Querochaca (M0258), Tungurahua | 2.865 m | 8,6 °C | 4,6 °C | 5,5 °C | −3,1 °C | 4 °C |
| Rumipamba-Salcedo (M0004), Cotopaxi | 2.685 m | 9,5 °C | 5,1 °C | 6,8 °C | −2,7 °C | 3 °C |

- Si el riesgo de heladas se calcula con `T2M_MIN` de POWER, **saldrá exagerado en unos 3 °C**.
  Ninguna de las dos estaciones bajó de 3 °C en 2014.
- Es un solo año y dos estaciones: sirve para declarar el sesgo en las limitaciones, no para corregir
  la temperatura. El anuario no publica días de helada.
- No se comprobó la temperatura **media** (la que usa el puntaje): el bloque solo trae mínimas.
- Fuente: INAMHI. Anuario Meteorológico 2014, pp. 24 y 86.
  https://servicios.inamhi.gob.ec/wp-content/uploads/2026/06/Anu2014.pdf

### 1.4 Suelo del tomate de árbol (bloque 3) — fila nueva en `tablas/suelo_cultivos.csv`

La app evalúa `tomate_de_arbol` y no tiene su suelo. Fila propuesta, con las columnas del archivo:

```
tomate_de_arbol,Tomate de árbol,5.5,7,Franca; franco arenosa; franco arcillo arenosa,Bueno,,,"Agrocalidad (2015). Guía de buenas prácticas agrícolas para tomate de árbol. Resolución Técnica 0038.","16; artículo 7 h","El anexo 2 de la misma guía (p. 48, atribuido a INIAP 2004) da pH 6–7"
```

https://www.agrocalidad.gob.ec/wp-content/uploads/2022/02/Gui%CC%81a-de-BPA-para-tomate-de-a%CC%81rbol-.pdf

El bloque trae además pH, textura y drenaje de aguacate, brócoli, cebolla blanca de rama, mora de
Castilla y uvilla, por si se agregan esos cultivos.

### 1.5 Referencias

`REFERENCIAS.csv` del zip tiene 24 fuentes con enlace y páginas citadas. Copiar a la lista de
referencias de la entrega las que se usen (como mínimo las de 1.1 a 1.4).

## 2. Lo que se comprobó sobre el MAG en la Sierra

Recuadros del `manifest.json` del zip: Tungurahua lon −78,80 a −78,40, lat −1,50 a −1,10;
Cotopaxi lon −78,85 a −78,45, lat −1,10 a −0,70.

- **"Estimaciones de cultivos" no tiene nada ahí:** se consultaron las 56 capas del servicio y
  ninguna devuelve polígonos en los dos recuadros. `python -m src.cultivos_mapeados ZONA descargar`
  dará tablas vacías y la capa "Cultivo mapeado (MAG)" saldrá en blanco. Conviene ocultarla en esas
  zonas o decir "el MAG no tiene cartografía de cultivos aquí". Ajustar el paso 3 de
  `SmartSeeds-traspaso-Sierra.md`.
- **Puntos de campo SIGTIERRAS (2014–2015) sí hay:** 204 en Tungurahua y 278 en Cotopaxi.

| Anotado en campo | Tungurahua | Cotopaxi |
|---|---|---|
| Pasto (cultivado y de corte) | 124 | 104 |
| Maíz suave | 19 | 75 |
| Papa | 13 | 13 |
| Brócoli | 0 | 17 |
| Cebada | 3 | 13 |
| Tomate de árbol | 12 | 0 |
| Haba | 2 | 4 |
| Quinua | 0 | 3 |

`python -m src.validar_campo ZONA medir` (con el parche de `traspaso-sierra`) tendrá muestra
suficiente solo para maíz suave. Si los recuadros definitivos de `src/config.py` son otros, repetir.

## 3. Lo que NO conviene tomar del zip

- **Mercado (bloque 8).** El nacional viene entero como "no encontrado". Los 11 promedios de precio
  por provincia salen de los mismos dos Excel del SIPA que ya procesa `src/preparar_mercado.py`, y el
  bloque no trae superficie por provincia, que la regla de la app exige. Para sumar arveja, mora o
  aguacate hay que añadirlos a `preparar_mercado`, no copiar el zip. Dos cuidados que sí aporta:
  no mezclar haba o arveja tierna con seca, y confirma que haba y quinua no tienen datos suficientes.
- **Cultivos nuevos.** Ninguno trae altura, temperatura y lluvia a la vez: fréjol solo altura
  (arbustivo 1.600–2.400 m, voluble 2.200–2.800 m), zanahoria solo temperatura (óptima 15–24 °C),
  cebolla de rama solo lluvia (óptima 850–1.600 mm), brócoli nada. Para puntuarlos hay que completar
  con FAO EcoCrop como se hizo en `tablas/ecocrop_cultivos.csv`. El brócoli es el mejor candidato por
  sus 17 puntos de campo en Cotopaxi.
- **Pendientes (bloque 1).** Solo mora, aguacate y chocho, y en **porcentaje**; la app usa grados
  (12 % ≈ 6,8°, 25 % ≈ 14°, 40 % ≈ 21,8°, 50 % ≈ 26,6°).
- **Parcelas GPS.** El archivo viene solo con el encabezado.

## 4. Una diferencia que el equipo debe resolver

El zip dice que la hoja de superficie del SIPA no publica total nacional y se niega a sumarla.
`CLAUDE.md` dice que los totales nacionales que calcula la app coinciden con los tabulados de la
ESPAC en los 15 cultivos y los dos años. No son incompatibles (la app los comprobó contra la ESPAC),
pero conviene decir en la entrega de dónde sale cada total.

## 5. Qué quedó sin comprobar

- Cuánta superficie de cada recuadro de la Sierra pasa de 3.300 m (hace falta su tabla de celdas).
- La temperatura media de POWER frente a estaciones.
- La licencia de los datos de SIGTIERRAS.
- Nada de esto se probó en la app: es una propuesta.
