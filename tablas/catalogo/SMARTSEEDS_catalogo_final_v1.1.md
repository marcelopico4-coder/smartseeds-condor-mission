# SMARTSEEDS — Catálogo documental ampliado v1.1

Esquema 2.1.0. Campo abierto; Cotopaxi, Tungurahua y Santo Domingo de los Tsáchilas.

**Función:** fuente de datos. La app contrasta los registros con información de parcela y satélite y genera las sugerencias. Este archivo no ejecuta recomendaciones.

Se agregan siete fichas y una sección de producción para cada uno de los 27 cultivos. Los datos conservan perfil, producto, unidad, evento inicial/final, territorio, sistema, fuente, página y estado de revisión. Los números faltantes permanecen null.

## Cómo consumir el JSON

- `cultivos[].produccion`: índices de ciclo y rendimiento; `valor_general` permanece null para impedir mezclar perfiles.
- `evidencias_productivas`: registros completos PR-E…; distinguir duración hasta evento de ciclo completo.
- `cultivos[C011].perfiles_regionales`: referencia andina de papa; la altitud describe contexto, sin excluir automáticamente terrenos.
- `tipo` conserva operadores: inferior a, hasta, superior a y al menos. No leer `min=max` sin este campo.
- kg/ha se convierte exactamente a t/ha; la base temporal y el producto no cambian. Flores y kg/árbol conservan sus unidades.
- Los antecedentes protegidos de clavel no completan el rendimiento a campo abierto. Lluvia anual no equivale a requerimiento de riego.
- Datos históricos, modelos predictivos, caracterizaciones varietales y experimentos se distinguen; ninguno constituye pronóstico de parcela.

## Cobertura productiva

| Cultivo | Registros de duración | Registros de rendimiento |
|---|---:|---:|
| C001 Fréjol | 4 | 1 |
| C002 Arveja | 3 | 2 |
| C003 Haba | 2 | 1 |
| C004 Lenteja | 2 | 1 |
| C005 Chocho | 2 | 2 |
| C006 Trigo | 1 | 1 |
| C007 Cebada | 3 | 3 |
| C008 Maíz | 5 | 4 |
| C009 Quinua | 1 | 3 |
| C010 Amaranto | 1 | 1 |
| C011 Papa | 2 | 2 |
| C012 Cacao | 1 | 1 |
| C013 Yuca | 1 | 2 |
| C014 Tomate | 2 | 1 |
| C015 Soya | 1 | 1 |
| C016 Rosa | 2 | 1 |
| C017 Clavel | 1 | 1 |
| C018 Aguacate | 2 | 1 |
| C019 Mora de Castilla | 1 | 1 |
| C020 Uvilla | 1 | 2 |
| C021 Brócoli | 2 | 1 |
| C022 Cebolla blanca de rama | 1 | 1 |
| C023 Zanahoria | 2 | 2 |
| C024 Plátano | 2 | 1 |
| C025 Palma africana | 1 | 1 |
| C026 Maracuyá amarillo | 1 | 1 |
| C027 Piña | 1 | 1 |

**Estos conteos no significan perfiles completos:** pueden incluir sólo floración, maduración de fruto, dato estadístico histórico o antecedentes de otro sistema. Revisar cada registro.

## Pendientes materiales

- Brócoli: ciclos documentados por el obtentor fuera de Ecuador; falta contraste local. Se conservan separados siembra directa en Salinas y trasplante en Centroamérica; 90 días de medición en un ensayo no se toman como fecha de cosecha.
- Palma: la maduración desde polinización no completa plantación→primera cosecha; falta periodo del rendimiento técnico.
- Mora: estabilización productiva no es fecha de primera cosecha; falta este dato específico.
- Clavel: rendimiento a campo abierto pendiente. Rosa: referencia de flor suelta en India, pendiente validación para el material ecuatoriano.
- Maracuyá, cebolla y otros registros: falta precisar algunos denominadores temporales y origen del conteo. No anualizar por supuesto.
- Segunda fuente independiente y validación local siguen pendientes por perfil. La versión amplía documentación; no cierra todos los umbrales.

## Incidencias resueltas o conservadas

- Cebolla blanca confirmada por el usuario como Allium fistulosum; se excluye Allium cepa.
- Papa: el libro rotulado “2020” en el nombre de archivo corresponde a edición publicada en 2021. No se usa reposo del tubérculo como ciclo.
- Papa: 8–13 °C corresponde a temperaturas mínimas/nocturnas y 20–25 °C a máximas/diurnas durante tuberización, según S01 PDF 109; no son promedios anuales.
- Arveja: no se incorpora cosecha verde de 52 días de S01, que contradice floración a 68 días en su tabla. Se mantiene ciclo genérico y rendimiento varietal por separado.
- Zanahoria: las tablas indican Bangor F1 (T6) 120 días y Karotan RZ (T3) 110 días; no se asigna a ambos el rango 126–130 del resumen. Rendimiento del Cuadro 40 sin ajuste económico del 10%.
- Amaranto: perfil INIAP Alegría de Amaranthus caudatus; no se aplica a otras especies.
- Maíz: perfiles harinosos de Sierra separados del duro H-601 del Litoral dentro de C008.
- El informe DATOS_QUE_FALTAN.md se trata como lista de trabajo del equipo. Sus heurísticas del motor y cifras comerciales no se convierten en evidencia agronómica.

## Registros de producción

### C001 — Fréjol

Phaseolus vulgaris

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0001 | duracion_hasta_evento / arbustivo | {"min": 80, "max": 90} | dia / siembra → cosecha | S01 / 14 |
| PR-E0002 | duracion_hasta_evento / arbustivo | {"min": 110, "max": 120} | dia / siembra → cosecha | S01 / 14 |
| PR-E0003 | duracion_hasta_evento / voluble | {"min": 160, "max": 180} | dia / siembra → cosecha | S01 / 14 |
| PR-E0004 | duracion_hasta_evento / voluble | {"min": 180, "max": 195} | dia / siembra → cosecha | S01 / 14 |
| PR-E0005 | rendimiento / variedad_localidad_manejo_no_desagregados | {"valores_reportados": [500, 3000, 3500]} | kg/ha / por_ciclo | S01 / 20 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C002 — Arveja

Pisum sativum

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0006 | duracion_hasta_evento / general_tierno | {"min": 80, "max": 115} | dia / siembra → cosecha | S01 / 24 |
| PR-E0007 | duracion_hasta_evento / general_seco | {"min": 115, "max": 130} | dia / siembra → cosecha | S01 / 24 |
| PR-E0008 | rendimiento / INIAP_436_Liliana | {"min": 5000, "max": 8100} | kg/ha / por_ciclo | S01 / 23 |
| PR-E0009 | rendimiento / INIAP_436_Liliana | {"min": 1310, "max": 1990} | kg/ha / por_ciclo | S01 / 23 |
| PR-E0010 | duracion_hasta_evento / INIAP_436_Liliana | {"min": 121, "max": 121} | dia / siembra → cosecha | S01 / 23 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C003 — Haba

Vicia faba

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0011 | duracion_hasta_evento / tierno | {"min": 170, "max": 200} | dia / siembra → cosecha | S01 / 29 |
| PR-E0012 | duracion_hasta_evento / seco | {"min": 210, "max": 230} | dia / siembra → cosecha | S01 / 29 |
| PR-E0013 | rendimiento / referencia_general | {"min": 1.4, "max": 2.5} | t/ha / por_ciclo | S01 / 32 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C004 — Lenteja

Lens culinaris

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0014 | duracion_hasta_evento / precoz | {"min": 120, "max": 150} | dia / siembra → cosecha | S01 / 35 |
| PR-E0015 | duracion_hasta_evento / tardia | {"min": 190, "max": 220} | dia / siembra → cosecha | S01 / 35 |
| PR-E0016 | rendimiento / referencia_general | {"min": 1.5, "max": 2} | t/ha / por_ciclo | S01 / 38 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C005 — Chocho

Lupinus mutabilis

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0017 | duracion_hasta_evento / INIAP_450_Andino | {"min": 167, "max": 225} | dia / siembra → cosecha | S24 / 36 |
| PR-E0018 | rendimiento / INIAP_450_Andino | {"min": 1100, "max": 4500} | kg/ha / por_ciclo | S24 / 36 |
| PR-E0019 | duracion_hasta_evento / INIAP_451_Guaranguito | {"min": 171, "max": 171} | dia / siembra → cosecha | S24 / 36 |
| PR-E0020 | rendimiento / INIAP_451_Guaranguito | {"min": 800, "max": 3400} | kg/ha / por_ciclo | S24 / 36 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C006 — Trigo

Triticum aestivum

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0021 | duracion_hasta_evento / Cojitambo_92 | {"min": 180, "max": 180} | dia / siembra → cosecha | S01 / 49 |
| PR-E0022 | rendimiento / Cojitambo_92 | {"min": 3, "max": 4} | t/ha / por_ciclo | S01 / 49 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C007 — Cebada

Hordeum vulgare

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0023 | duracion_hasta_evento / INIAP_Shyri_89 | {"min": 150, "max": 154} | dia / siembra → cosecha | S01 / 62 |
| PR-E0024 | rendimiento / INIAP_Shyri_89 | {"min": 1533, "max": 4937} | kg/ha / por_ciclo | S01 / 62 |
| PR-E0025 | duracion_hasta_evento / INIAP_Atahualpa_92 | {"min": 150, "max": 155} | dia / siembra → cosecha | S01 / 62 |
| PR-E0026 | rendimiento / INIAP_Atahualpa_92 | {"min": 1560, "max": 3600} | kg/ha / por_ciclo | S01 / 62 |
| PR-E0027 | duracion_hasta_evento / INIAP_Calicuchima_92 | {"min": 140, "max": 150} | dia / siembra → cosecha | S01 / 62 |
| PR-E0028 | rendimiento / INIAP_Calicuchima_92 | {"min": 1676, "max": 5148} | kg/ha / por_ciclo | S01 / 62 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C008 — Maíz

Zea mays

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0029 | duracion_hasta_evento / INIAP_103_Sierra_harinoso | {"min": 120, "max": 120} | dia / siembra → cosecha | S21 / 16 |
| PR-E0030 | duracion_hasta_evento / INIAP_103_Sierra_harinoso | {"min": 250, "max": 250} | dia / siembra → cosecha | S21 / 16 |
| PR-E0031 | rendimiento / INIAP_103_Sierra_harinoso | {"min": 4500, "max": 7000} | kg/ha / por_ciclo | S21 / 16 |
| PR-E0032 | duracion_hasta_evento / INIAP_111_Sierra_harinoso | {"min": 208, "max": 208} | dia / siembra → cosecha | S21 / 16 |
| PR-E0033 | duracion_hasta_evento / INIAP_111_Sierra_harinoso | {"min": 265, "max": 265} | dia / siembra → cosecha | S21 / 16 |
| PR-E0034 | rendimiento / INIAP_111_Sierra_harinoso | {"min": 3400, "max": 4091} | kg/ha / por_ciclo | S21 / 16 |
| PR-E0035 | duracion_hasta_evento / INIAP_H601_Litoral_duro | {"min": 120, "max": 120} | dia / siembra → cosecha | PROD18 / 2 |
| PR-E0036 | rendimiento / INIAP_H601_Litoral_duro_secano | {"min": 5472, "max": 5472} | kg/ha / por_ciclo | PROD18 / 2 |
| PR-E0037 | rendimiento / INIAP_H601_Litoral_duro_riego | {"min": 7381, "max": 7381} | kg/ha / por_ciclo | PROD18 / 2 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C009 — Quinua

Chenopodium quinoa

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0038 | duracion_hasta_evento / referencia_general | {"min": 5, "max": 7} | mes / siembra → cosecha | S01 / 86 |
| PR-E0039 | rendimiento / promedio_reportado | {"min": 0.75, "max": 1.8} | t/ha / por_ciclo | S01 / 88 |
| PR-E0040 | rendimiento / campo_bien_manejado | {"min": 2, "max": 2} | t/ha / por_ciclo | S01 / 88 |
| PR-E0041 | rendimiento / parcela_experimental | {"min": 4, "max": 4} | t/ha / por_ciclo | S01 / 88 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C010 — Amaranto

Amaranthus caudatus

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0042 | duracion_hasta_evento / INIAP_Alegria_Amaranthus_caudatus | {"min": 150, "max": 180} | dia / siembra → cosecha | S04 / 3 |
| PR-E0043 | rendimiento / INIAP_Alegria_Amaranthus_caudatus | {"min": 1500, "max": 2000} | kg/ha / por_ciclo | S04 / 3 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C011 — Papa

Solanum tuberosum

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0044 | duracion_hasta_evento / Superchola | {"min": 180, "max": 180} | dia / siembra → cosecha | PROD13 / 81 |
| PR-E0045 | rendimiento / Superchola | {"min": 30, "max": 30} | t/ha / por_ciclo | PROD01 / 100 |
| PR-E0046 | duracion_hasta_evento / INIAP_Fripapa | {"min": 150, "max": 150} | dia / siembra → cosecha | PROD13 / 81 |
| PR-E0047 | rendimiento / INIAP_Fripapa | {"min": 47, "max": 47} | t/ha / por_ciclo | PROD01 / 101 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C012 — Cacao

Theobroma cacao

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0048 | duracion_hasta_evento / referencia_Peru_variedad_no_precisada | {"min": 2, "max": 2} | año / instalacion_del_cultivo → primera_cosecha | PROD15 / 2 |
| PR-E0049 | rendimiento / Nacional_estadistica_2018 | {"min": 0.45, "max": 0.45} | t/ha / periodo_estadistico_por_verificar | S23 / 47 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C013 — Yuca

Manihot esculenta

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0050 | duracion_hasta_evento / referencia_Amazonia | {"min": 8, "max": 12} | mes / establecimiento_campo → cosecha | PROD17 / 21 |
| PR-E0051 | rendimiento / INIAP_Portoviejo_650 | {"min": 17, "max": 17} | t/ha / por_ciclo | PROD25 / 7 |
| PR-E0052 | rendimiento / INIAP_Portoviejo_650 | {"min": 35, "max": 35} | t/ha / por_ciclo | PROD25 / 7 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C014 — Tomate

Solanum lycopersicum

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0053 | duracion_hasta_evento / FAO_generico | {"min": 135, "max": 180} | dia / siembra → fin_periodo_crecimiento | CL02 / sección HTML |
| PR-E0054 | duracion_hasta_evento / Pimampiro_campo_abierto | {"min": 8, "max": 8} | mes / inicio_ciclo_no_precisado → fin_ciclo_reportado | PROD19 / 18 |
| PR-E0055 | rendimiento / Pimampiro_campo_abierto | {"min": 48.83, "max": 48.83} | t/ha / por_ciclo | PROD19 / 18 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C015 — Soya

Glycine max

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0056 | duracion_hasta_evento / INIAP_308 | {"min": 110, "max": 120} | dia / siembra → cosecha | PROD10 / 3 |
| PR-E0057 | rendimiento / INIAP_308 | {"min": 3984, "max": 3984} | kg/ha / por_ciclo | PROD10 / 3 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C016 — Rosa

Rosa spp. (híbrido y cultivar por definir)

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0058 | duracion_hasta_evento / Edward_AndraRed_Button_TamilNadu | {"min": 1, "max": 1} | año / plantacion → inicio_floracion | PROD12 / sección HTML |
| PR-E0059 | duracion_hasta_evento / Edward_AndraRed_Button_TamilNadu | {"min": 2, "max": 2} | año / plantacion → inicio_rendimiento_economico | PROD12 / sección HTML |
| PR-E0060 | rendimiento / Edward_AndraRed_Button_TamilNadu | {"min": 1000000, "max": 1000000} | flores/ha / por_año | PROD12 / sección HTML |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C017 — Clavel

Dianthus caryophyllus

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0061 | duracion_hasta_evento / plantas_de_semilla_exterior | {"min": 120, "max": 130} | dia / germinacion → floracion | S19 / 21 |
| PR-E0062 | rendimiento / clavel_estandar_comercial | {"min": 8, "max": 12} | flores/planta / por_año | S19 / 54 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C018 — Aguacate

Persea americana

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0063 | duracion_hasta_evento / referencia_Ecuador | {"min": 2, "max": 3} | año / plantacion_huerto → primera_cosecha | S05 / 13 |
| PR-E0064 | duracion_hasta_evento / arbol_injertado_Florida | {"min": 3, "max": 4} | año / plantacion → inicio_produccion | PROD20 / 4 |
| PR-E0065 | rendimiento / arbol_maduro_Florida | {"min": 50, "max": 75} | kg/arbol / por_año | PROD20 / 4 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C019 — Mora de Castilla

Rubus glaucus

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0066 | duracion_hasta_evento / Tungurahua_referencia_MAG | {"min": 8, "max": 8} | mes / trasplante → estabilizacion_productiva | PROD26 / sección HTML |
| PR-E0067 | rendimiento / mora_con_espinas_Colombia | {"min": 20, "max": 20} | t/ha / por_año | S08 / 43 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C020 — Uvilla

Physalis peruviana

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0068 | duracion_hasta_evento / referencia_manual_Ecuador | {"min": 5, "max": 7} | mes / inicio_no_precisado_en_parrafo → inicio_etapa_productiva | PROD14 / 12 |
| PR-E0069 | rendimiento / Huaca_cobertura_alfalfa_T1 | {"min": 7.83, "max": 7.83} | t/ha / periodo_del_ensayo_no_anualizado | PROD23 / 7 |
| PR-E0070 | rendimiento / Huaca_cobertura_alfalfa_T1 | {"min": 6.91, "max": 6.91} | t/ha / periodo_del_ensayo_no_anualizado | PROD23 / 7 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C021 — Brócoli

Brassica oleracea var. italica

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0071 | duracion_hasta_evento / Avenger_siembra_directa_Salinas | {"min": 102, "max": 102} | dia / siembra_directa → madurez | PROD27 / sección HTML |
| PR-E0072 | duracion_hasta_evento / Avenger_trasplante_Centroamerica | {"min": 85, "max": 90} | dia / trasplante → madurez_comercial_segun_ficha | PROD28 / sección HTML |
| PR-E0073 | rendimiento / Avenger_Cotopaxi_16_tratamientos | {"min": 16.45, "max": 25.25} | t/ha / por_ciclo | PROD07 / 8 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C022 — Cebolla blanca de rama

Allium fistulosum

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0074 | duracion_hasta_evento / siembra_desde_semilla | {"min": 5, "max": 5} | mes / siembra → cosecha | PROD08 / 37 |
| PR-E0075 | rendimiento / Colombia_estadistica_citada | {"min": 24.8, "max": 24.8} | t/ha / base_temporal_por_verificar | PROD08 / 15 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C023 — Zanahoria

Daucus carota

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0076 | duracion_hasta_evento / Bangor_F1_T6 | {"min": 120, "max": 120} | dia / siembra → cosecha | PROD16 / 63 |
| PR-E0077 | rendimiento / Bangor_F1_T6 | {"min": 36947.33, "max": 36947.33} | kg/ha / por_ciclo | PROD16 / 87 |
| PR-E0078 | duracion_hasta_evento / Karotan_RZ_T3 | {"min": 110, "max": 110} | dia / siembra → cosecha | PROD16 / 63 |
| PR-E0079 | rendimiento / Karotan_RZ_T3 | {"min": 35543, "max": 35543} | kg/ha / por_ciclo | PROD16 / 87 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C024 — Plátano

Musa spp. (plátanos de cocción; grupo AAB por confirmar por material)

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0080 | duracion_hasta_evento / Barraganete | {"min": 6, "max": 6} | mes / siembra → belloteo | PROD04 / 22 |
| PR-E0081 | duracion_hasta_evento / Barraganete | {"min": 80, "max": 90} | dia / belloteo → cosecha | PROD04 / 22 |
| PR-E0082 | rendimiento / referencia_nacional_historica | {"min": 5, "max": 5} | t/ha / no_precisado | PROD04 / 5 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C025 — Palma africana

Elaeis guineensis

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0083 | duracion_hasta_evento / palma_aceitera | {"min": 150, "max": 180} | dia / polinizacion → cosecha_racimo | PROD21 / 22 |
| PR-E0084 | rendimiento / INIAP_Tenera | {"min": 35, "max": 35} | t/ha / no_precisado | PROD05 / 9 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C026 — Maracuyá amarillo

Passiflora edulis (forma amarilla; f. flavicarpa en la fuente)

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0085 | duracion_hasta_evento / INIAP_2009_amarillo | {"min": 150, "max": 160} | dia / siembra_segun_fuente → inicio_cosecha | PROD03 / 23 |
| PR-E0086 | rendimiento / INIAP_2009_amarillo | {"min": 38418, "max": 38418} | kg/ha / no_precisado | PROD03 / 23 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

### C027 — Piña

Ananas comosus

| ID | Variable / perfil | Valor | Unidad / periodo | Fuente / página PDF |
|---|---|---|---|---|
| PR-E0087 | duracion_hasta_evento / referencia_general | {"min": 13, "max": 13} | mes / siembra → primera_cosecha | PROD06 / 17 |
| PR-E0088 | rendimiento / Ecuador_proyeccion_2003 | {"min": 22.32, "max": 22.32} | t/ha / estadistica_2003 | PROD06 / 41 |

Contexto, restricciones y revisión: consultar JSON; esta tabla es sólo un índice.

# Anexo bibliográfico completo

# SMARTSEEDS — Referencias v1.1

152 registros bibliográficos. Un registro no equivale a un experimento independiente; conservar equivalencias y referencias pendientes.

## S01

Basantes Morales, E. R. (2015). Manejo de cultivos andinos del Ecuador. ESPE.

Archivo de trazabilidad: C:/Users/campy/OneDrive/SMARTSEEDS/ManejoCultivosEcuador.pdf

Uso: E0001, E0002, E0003, E0004, E0005, E0017, E0018, E0019, E0031, E0032, E0033, E0045, E0046, E0058, E0059, E0060, E0072, E0073, E0074, E0075, E0087, E0088, E0089, E0090, E0102, E0103, E0104, E0112, E0113, E0114, E0115, E0127, E0128, E0129, E0130, E0131, E0132, E0133, E0265, E0266, E0267, CL-E0052, CL-E0053, CL-E0054, CL-E0055, CL-E0056, CL-E0057, CL-E0058, CL-E0059, CL-E0060, CL-E0061, CL-E0062, CL-E0063, CL-E0064, CL-E0065, CL-E0066, CL-E0067, CL-E0068, CL-E0069, CL-E0070, CL-E0071, CL-E0072, CL-E0073, CL-E0074, CL-E0075, CL-E0076, CL-E0077, CL-E0078, CL-E0079, CL-E0085, CL-E0087, CL-E0088, CL-E0089, CL-E0090, CL-E0091, CL-E0092, PR-E0001, PR-E0002, PR-E0003, PR-E0004, PR-E0005, PR-E0006, PR-E0007, PR-E0008, PR-E0009, PR-E0010, PR-E0011, PR-E0012, PR-E0013, PR-E0014, PR-E0015, PR-E0016, PR-E0021, PR-E0022, PR-E0023, PR-E0024, PR-E0025, PR-E0026, PR-E0027, PR-E0028, PR-E0038, PR-E0039, PR-E0040, PR-E0041.

## S02

Amores, F. (1992). Clima, suelos, nutrición y fertilización de cultivos en el litoral ecuatoriano (Manual Técnico No. 26). INIAP.

Archivo de trazabilidad: C:/Users/campy/OneDrive/SMARTSEEDS/Manual Técnico No. 26.pdf

Uso: E0160, E0161, E0162, E0163, E0175, E0176, E0177, E0189, E0190, E0191, CL-E0093, CL-E0094, CL-E0095, CL-E0096, CL-E0097, CL-E0102, CL-E0103, CL-E0104, CL-E0107.

## S03

Agrocalidad. Guía de buenas prácticas agrícolas para cacao. Resolución Técnica 0183, 20 de septiembre de 2012.

Archivo de trazabilidad: C:/Users/campy/OneDrive/SMARTSEEDS/Guía-de-BPA-para-cacao-jul.pdf

Uso: E0145, E0146, E0147, E0148, E0222.

## S04

Peralta I., E. (2010). INIAP Alegría: Variedad mejorada de amaranto Amaranthus caudatus L. (Plegable Divulgativo 346). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/2640)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\amaranto_alegria.pdf

Uso: E0214, E0215, E0216, PR-E0042, PR-E0043.

## S05

Ministerio de Agricultura y Ganadería. (s. f.). Manual de manejo productivo de aguacate. Tabla 3, fuente MAG–CGINA e INIAP (2022).

[Fuente institucional o enlace registrado](https://sipa.agricultura.gob.ec/boletines/situacionales/2023/manual_manejo_productivo_aguacate.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\aguacate_mag.pdf

Uso: E0223, E0224, E0226, E0227, E0228, E0229, E0230, E0231, CL-E0126, CL-E0127, PR-E0063.

## S06

Sotomayor, A., Viera, W., Viteri, P., Posso, M., Racines, M., González, A., Cho, K., & Villavicencio, A. (2019). Manual técnico para la producción de plantas injertas de aguacate (Persea americana Mill.) de alta calidad (Manual No. 108). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/5344)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\aguacate_iniap2019.pdf

Uso: E0225, CL-E0124, CL-E0125.

## S07

Valverde, F., González, A., Viteri, P., & Martínez, A. (2016). Nutrición del cultivo de la mora de Castilla. En El cultivo de la mora en Ecuador (pp. 79–102). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/4065)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\mora_iniap.pdf

Uso: E0232, E0233, E0234.

## S08

Cardona, W. A., & Bolaños-Benavides, M. M. (2019). Manual de nutrición del cultivo de mora de Castilla (Rubus glaucus Benth.) bajo un esquema de buenas prácticas en fertilización integrada. AGROSAVIA. https://doi.org/10.21930/agrosavia.manual-18

[Fuente institucional o enlace registrado](https://doi.org/10.21930/agrosavia.manual-18)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\mora_agrosavia.pdf

Uso: E0235, E0236, E0237, E0238, E0239, CL-E0128, CL-E0129, CL-E0130, CL-E0131, CL-E0132, CL-E0133, PR-E0067.

## S09

Agrocalidad. (2016). Guía de buenas prácticas agrícolas para el cultivo de uvilla. Resolución Técnica 0073, 18 de abril de 2016.

[Fuente institucional o enlace registrado](https://www.agrocalidad.gob.ec/wp-content/uploads/2023/04/Gu%C3%ADa-de-BPA-para-Uvilla-jul.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\uvilla_bpa.pdf

Uso: E0241, E0242, E0243, CL-E0134, CL-E0135, CL-E0136, CL-E0137.

## S10

Office of the Gene Technology Regulator. (2009). The biology of hybrid tea rose (Rosa × hybrida) (Version 2). Australian Government.

[Fuente institucional o enlace registrado](https://www.ogtr.gov.au/sites/default/files/files/2021-07/the_biology_of_hybrid_tea_rose.pdf)

Uso: E0244, E0245, E0246.

## S11

University of Illinois Extension. (s. f.). Preparation. Roses.

[Fuente institucional o enlace registrado](https://extension.illinois.edu/roses/preparation)

Uso: E0247.

## S12

Tamil Nadu Agricultural University. (s. f.). Organic cultivation of carnation.

[Fuente institucional o enlace registrado](https://agritech.tnau.ac.in/org_farm/orgfarm_carnation.html)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\clavel_tnau.html

Uso: E0249, E0250, E0251.

## S13

North Carolina State University Extension. (s. f.). Dianthus caryophyllus. Extension Gardener Plant Toolbox.

[Fuente institucional o enlace registrado](https://plants.ces.ncsu.edu/plants/dianthus-caryophyllus/common-name/carnation/)

Uso: E0248, E0252.

## S14

Camberato, D. M., Lopez, R. G., & Mickelbart, M. V. (s. f.). pH and electrical conductivity measurements in soilless substrates (HO-237). Purdue Extension.

[Fuente institucional o enlace registrado](https://ag.purdue.edu/department/hla/extension/extension-publications-library/ext-pubs/ho-237-w.html)

Uso: E0253, E0254, E0255, E0256.

## S15

Ayers, R. S., & Westcot, D. W. (1985). Water quality for agriculture (FAO Irrigation and Drainage Paper 29, Rev. 1). FAO. Tabla 4 y sección 2.4.3.

[Fuente institucional o enlace registrado](https://www.fao.org/4/t0234e/T0234E03.htm)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\fao_salinidad.html

Uso: E0257, E0258, E0259, E0260, E0261, E0262, E0263, E0264.

## S16

Government of New Brunswick. (s. f.). Soil management. Potato production.

[Fuente institucional o enlace registrado](https://www2.gnb.ca/content/gnb/en/departments/10/agriculture/content/crops/potatoes/soil_management.html)

Uso: E0217, E0218, E0219, E0220.

## S17

Agriculture and Agri-Food Canada. (2025). Crop profile for potato in Canada, 2023 (6th ed.).

[Fuente institucional o enlace registrado](https://agriculture.canada.ca/en/science/agriculture-and-agri-food-research-centres/pest-management-centre/pesticide-risk-reduction-pest-management-centre/crop-profiles/crop-profile-potato-canada-2023)

Uso: E0221.

## ECO1668

Food and Agriculture Organization of the United Nations. (s. f.). Phaseolus vulgaris. ECOCROP, ficha 1668.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1668)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1668.html

Uso: E0006, E0007, E0008, E0009, E0010, E0011, E0012, E0013, E0014, E0015, E0016, CL-E0001, CL-E0002, CL-E0003.

## ECO1721

Food and Agriculture Organization of the United Nations. (s. f.). Pisum sativum. ECOCROP, ficha 1721.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1721)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1721.html

Uso: E0020, E0021, E0022, E0023, E0024, E0025, E0026, E0027, E0028, E0029, E0030, CL-E0004, CL-E0005, CL-E0006.

## ECO2146

Food and Agriculture Organization of the United Nations. (s. f.). Vicia faba. ECOCROP, ficha 2146.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2146)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_2146.html

Uso: E0034, E0035, E0036, E0037, E0038, E0039, E0040, E0041, E0042, E0043, E0044, CL-E0007, CL-E0008, CL-E0009.

## ECO7209

Food and Agriculture Organization of the United Nations. (s. f.). Lens culinaris. ECOCROP, ficha 7209.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=7209)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_7209.html

Uso: E0047, E0048, E0049, E0050, E0051, E0052, E0053, E0054, E0055, E0056, E0057, CL-E0010, CL-E0011, CL-E0012.

## ECO7435

Food and Agriculture Organization of the United Nations. (s. f.). Lupinus mutabilis. ECOCROP, ficha 7435.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=7435)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_7435.html

Uso: E0061, E0062, E0063, E0064, E0065, E0066, E0067, E0068, E0069, E0070, E0071, CL-E0013, CL-E0014, CL-E0015.

## ECO2114

Food and Agriculture Organization of the United Nations. (s. f.). Triticum aestivum. ECOCROP, ficha 2114.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2114)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_2114.html

Uso: E0076, E0077, E0078, E0079, E0080, E0081, E0082, E0083, E0084, E0085, E0086, CL-E0016, CL-E0017, CL-E0018.

## ECO1232

Food and Agriculture Organization of the United Nations. (s. f.). Hordeum vulgare. ECOCROP, ficha 1232.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1232)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1232.html

Uso: E0091, E0092, E0093, E0094, E0095, E0096, E0097, E0098, E0099, E0100, E0101, CL-E0019, CL-E0020, CL-E0021.

## ECO2175

Food and Agriculture Organization of the United Nations. (s. f.). Zea mays. ECOCROP, ficha 2175.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2175)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_2175.html

Uso: E0105, E0106, E0107, E0108, E0109, E0110, E0111, CL-E0022, CL-E0023, CL-E0024.

## ECO2509

Food and Agriculture Organization of the United Nations. (s. f.). Chenopodium quinoa. ECOCROP, ficha 2509.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2509)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_2509.html

Uso: E0116, E0117, E0118, E0119, E0120, E0121, E0122, E0123, E0124, E0125, E0126, CL-E0025, CL-E0026, CL-E0027.

## ECO1971

Food and Agriculture Organization of the United Nations. (s. f.). Solanum tuberosum. ECOCROP, ficha 1971.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1971)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1971.html

Uso: E0134, E0135, E0136, E0137, E0138, E0139, E0140, E0141, E0142, E0143, E0144, CL-E0028, CL-E0029, CL-E0030.

## ECO2074

Food and Agriculture Organization of the United Nations. (s. f.). Theobroma cacao. ECOCROP, ficha 2074.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2074)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_2074.html

Uso: E0149, E0150, E0151, E0152, E0153, E0154, E0155, E0156, E0157, E0158, E0159, CL-E0031, CL-E0032, CL-E0033.

## ECO1420

Food and Agriculture Organization of the United Nations. (s. f.). Manihot esculenta. ECOCROP, ficha 1420.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1420)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1420.html

Uso: E0164, E0165, E0166, E0167, E0168, E0169, E0170, E0171, E0172, E0173, E0174, CL-E0034, CL-E0035, CL-E0036.

## ECO1379

Food and Agriculture Organization of the United Nations. (s. f.). Lycopersicon esculentum (nombre de la ficha). ECOCROP, ficha 1379.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1379)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1379.html

Uso: E0178, E0179, E0180, E0181, E0182, E0183, E0184, E0185, E0186, E0187, E0188, CL-E0037, CL-E0038, CL-E0039.

## ECO1150

Food and Agriculture Organization of the United Nations. (s. f.). Glycine max. ECOCROP, ficha 1150.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1150)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1150.html

Uso: E0192, E0193, E0194, E0195, E0196, E0197, E0198, E0199, E0200, E0201, E0202, CL-E0040, CL-E0041, CL-E0042.

## ECO1686

Food and Agriculture Organization of the United Nations. (s. f.). Physalis peruviana. ECOCROP, ficha 1686.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1686)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v02\ecocrop_1686.html

Uso: E0203, E0204, E0205, E0206, E0207, E0208, E0209, E0210, E0211, E0212, E0213, E0240, CL-E0043, CL-E0044, CL-E0045.

## S18

Centro de Información de Recursos Naturales. (1989). Requerimientos de clima y suelo: Cereales, cultivos industriales y flores. CIREN-CORFO.

[Fuente institucional o enlace registrado](https://bibliotecadigital.ciren.cl/server/api/core/bitstreams/58550d73-880d-49ab-9bff-51fc02cedaa0/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v03\ciren.pdf

Uso: E0268, E0269, E0270, E0271, E0272, E0273, E0274, E0275, E0276, E0277, E0278, E0279, E0280, E0281, E0282, E0283, CL-E0108, CL-E0109, CL-E0110, CL-E0111, CL-E0112, CL-E0113, CL-E0114, CL-E0115, CL-E0116, CL-E0117, CL-E0118, CL-E0119, CL-E0120, CL-E0121, CL-E0122, CL-E0123.

## S19

Jawaharlal, M., Ganga, M., Padmadevi, K., Jegadeeswari, V., & Karthikeyan, S. (s. f.). A technical guide on carnation. Tamil Nadu Agricultural University.

[Fuente institucional o enlace registrado](https://agritech.tnau.ac.in/horticulture/pdf/A%20Technical%20Guide%20On%20Carnation.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v03\clavel_tnau.pdf

Uso: E0284, E0285, E0286, E0287, E0288, PR-E0061, PR-E0062.

## S20

Nieto Cabrera, C. (1989). El cultivo de amaranto Amaranthus spp.: Una alternativa agronómica para Ecuador (Publicación Miscelánea No. 52). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/2688)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v03\amaranto_iniap1989.pdf

Uso: E0289, E0290.

## S21

Zambrano, J. L., Velásquez, J., Peñaherrera, D., Sangoquiza, C., Cartagena, Y., Villacrés, E., Garcés, S., Ortíz, R., León, J., Campaña, D., López, V., Asaquibay, C., Nieto, M., Sanmartín, G., Pintado, P., Yánez, C., & Racines, M. (2021). Guía para la producción sustentable de maíz en la Sierra ecuatoriana (Manual No. 122). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/5796)

Archivo de trazabilidad: C:/Users/campy/OneDrive/SMARTSEEDS/GUIA CULTIVO DE MAIZ 2021-1.pdf

Uso: E0291, E0292, E0293, E0294, E0295, E0296, PR-E0029, PR-E0030, PR-E0031, PR-E0032, PR-E0033, PR-E0034.

## S22

Servicio Nacional de Sanidad Agraria. (s. f.). Guía para la implementación de buenas prácticas agrícolas (BPA) para el cultivo de haba. SENASA.

[Fuente institucional o enlace registrado](https://www.senasa.gob.pe/senasa/descargasarchivos/2020/07/Guia-BPA-HABA.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v03\haba_senasa.pdf

Uso: E0297, E0298, E0299.

## S23

Paredes, N., Monteros-Altamirano, Á., Lima, L., Caicedo, C., Bastidas, S., Tinoco, L., Fernández, F., Vargas, Y., Pico, J., Subía, C., Burbano, A., Chanaluiza, A., Sotomayor, D., Díaz, A., Intriago, J., Chancosa, C., Andrade, A., & Enríquez, G. (2022). Manual del cultivo de cacao sostenible para la Amazonía ecuatoriana (Manual No. 125, 1.ª ed.). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/server/api/core/bitstreams/b3224934-66ec-4100-ae5f-31c3ec76c5d3/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v03\cacao_iniap.pdf

Uso: E0300, E0301, E0302, E0303, E0304, CL-E0098, CL-E0099, CL-E0100, CL-E0101, PR-E0049.

## S24

López, V., Rodríguez, M., Murillo, A., Vega, L., & Rodríguez, D. (2023). Guía para facilitar el aprendizaje en el manejo integrado del cultivo de chocho (Lupinus mutabilis Sweet) (Guía de aprendizaje No. 15). INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/server/api/core/bitstreams/3be31639-d691-4f0e-9b1b-0d8c6a70f5c4/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_v03\chocho_iniap.pdf

Uso: E0305, E0306, E0307, CL-E0080, CL-E0081, CL-E0082, CL-E0083, CL-E0084, PR-E0017, PR-E0018, PR-E0019, PR-E0020.

## S25

Idowu, J., & Angadi, S. (s. f.). Understanding and managing soil compaction in agricultural fields (Circular 672). New Mexico State University.

[Fuente institucional o enlace registrado](https://pubs.nmsu.edu/_circulars/CR672/index.html)

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## AC01

NASA / ASF / JPL. (s. f.). NISAR Provisional Soil Moisture, Version 1.

[Fuente institucional o enlace registrado](https://data.nasa.gov/dataset/nisar-provisional-soil-moisture-version-1-9951e)

Uso: referencia_metodologica_o_insumo.

## AC02

Climate Hazards Center, UCSB. (s. f.). CHIRPS version 3.

[Fuente institucional o enlace registrado](https://www.chc.ucsb.edu/data/chirps3)

Uso: referencia_metodologica_o_insumo.

## AC03

Copernicus Climate Change Service / ECMWF. (s. f.). ERA5-Land hourly data from 1950 to present.

[Fuente institucional o enlace registrado](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview)

Uso: referencia_metodologica_o_insumo.

## AC04

NASA MODIS. (s. f.). MODIS Land Surface Temperature and Emissivity (MOD11).

[Fuente institucional o enlace registrado](https://modis.gsfc.nasa.gov/data/dataprod/mod11.php)

Uso: referencia_metodologica_o_insumo.

## AC05

USGS. (s. f.). SRTM digital elevation archive.

[Fuente institucional o enlace registrado](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm)

Uso: referencia_metodologica_o_insumo.

## AC06

FAO. (s. f.). Irrigation Water Management: Crop Water Needs, chapter 3.

[Fuente institucional o enlace registrado](https://www.fao.org/4/s2022e/s2022e07.htm)

Uso: referencia_metodologica_o_insumo.

## AC07

NASA. (s. f.). Landsat NDVI, Disasters Mapping Portal.

[Fuente institucional o enlace registrado](https://science.data.nasa.gov/disasters/data-gallery/landsat-ndvi)

Uso: referencia_metodologica_o_insumo.

## ECO2187

FAO. ECOCROP. Amaranthus caudatus, ficha 2187.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2187)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_clima_v01\ecocrop_2187.html

Uso: CL-E0046, CL-E0047, CL-E0048.

## ECO1659

FAO. ECOCROP. Persea americana, ficha 1659.

[Fuente institucional o enlace registrado](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1659)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_clima_v01\ecocrop_1659.html

Uso: CL-E0049, CL-E0050, CL-E0051.

## CL01

FAO. Irrigation Water Management: Irrigation Water Needs. Capítulo 2, tabla 5.

[Fuente institucional o enlace registrado](https://www.fao.org/4/s2022e/s2022e02.htm)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_clima_v01\fao_agua_cap2.html

Uso: CL-E0138, CL-E0140, CL-E0142, CL-E0144, CL-E0146, CL-E0148, CL-E0150, CL-E0152.

## CL02

FAO. Irrigation Water Management: Irrigation Water Needs. Capítulo 3, tabla 14.

[Fuente institucional o enlace registrado](https://www.fao.org/4/s2022e/s2022e07.htm)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_clima_v01\fao_agua_cap3.html

Uso: CL-E0139, CL-E0141, CL-E0143, CL-E0145, CL-E0147, CL-E0149, CL-E0151, CL-E0153, PR-E0053.

## CL03

Kansas State University, Sunflower Extension District. Freeze Damage to Wheat. Tabla de daño tras dos horas.

[Fuente institucional o enlace registrado](https://www.sunflower.k-state.edu/agronomy/wheat/freeze_damage.html)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_clima_v01\trigo_kstate.html

Uso: CL-E0154, CL-E0155, CL-E0156, CL-E0157, CL-E0158, CL-E0159, CL-E0160.

## CL04

University of Minnesota Extension. Flooded corn. Growth and development.

[Fuente institucional o enlace registrado](https://extension.umn.edu/agriculture/crop-production/corn/flooded-corn)

Uso: CL-E0161, CL-E0162.

## CL05

University of Minnesota Extension. Flooded soybean. Duration of flooding.

[Fuente institucional o enlace registrado](https://extension.umn.edu/agriculture/crop-production/soybean/flooded-soybean)

Uso: CL-E0163.

## CL06

Lerner, B. R. Purdue Extension. Tomatoes (HO-26). Environmental Stress Disorders: Blossom Drop.

[Fuente institucional o enlace registrado](https://ag.purdue.edu/department/hla/extension/extension-publications-library/ext-pubs/ho-26-w.html)

Uso: CL-E0105, CL-E0106.

## CL07

Iowa State University Extension. Ponding Impacts on Corn Growth & Development.

[Fuente institucional o enlace registrado](https://crops.extension.iastate.edu/encyclopedia/ponding-impacts-corn-growth-development)

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## CL08

South Dakota State University Extension. Low Temperature Effects on Winter Wheat. Tabla de exposiciones de dos horas; reproduce K-State.

[Fuente institucional o enlace registrado](https://extension.sdstate.edu/low-temperature-effects-winter-wheat)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_clima_v01\trigo_sdstate.html

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## CL09

Bois, J.-F., Winkel, T., Lhomme, J.-P., Raffaillac, J.-P., & Rocheteau, A. (2006). Response of some Andean cultivars of quinoa to temperature: effects on germination, phenology, growth and freezing. European Journal of Agronomy, 25(4), 299–308. Resumen del artículo depositado en IRD.

[Fuente institucional o enlace registrado](https://www.documentation.ird.fr/hor/fdi:010037682)

Uso: CL-E0086.

## CL10

Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). Crop evapotranspiration: Guidelines for computing crop water requirements (FAO Irrigation and Drainage Paper 56). Capítulo 8, tabla 22 y ecuaciones 82–83.

[Fuente institucional o enlace registrado](https://www.fao.org/4/X0490E/x0490e0e.htm)

Uso: CL-E0164, CL-E0165, CL-E0166, CL-E0167, CL-E0168, CL-E0169, CL-E0170, CL-E0171, CL-E0172, CL-E0173, CL-E0174, CL-E0175, CL-E0176, CL-E0177, CL-E0178, CL-E0179.

## BIB01

Souza et al. (2026). Cytogenetic characterization of Physalis angulata, P. peruviana, and P. ixocarpa by CMA/DAPI banding and flow cytometry.

[Fuente institucional o enlace registrado](https://doi.org/10.1007/s10722-026-02968-5)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Cytogenetic_characterization_of_Physalis_angulata_.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB02

Gulisano et al. (2022). Diversity and Agronomic Performance of Lupinus mutabilis Germplasm in European and Andean Environments.

[Fuente institucional o enlace registrado](https://doi.org/10.3389/fpls.2022.903661)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\fpls-13-903661.pdf

Uso: CL-E0180, CL-E0181.

## BIB03

Huamán Estrada et al. (2026). Integrated SERS and Chemometric Characterization of Ultrasound-Induced Quality Changes in Stevia-Sweetened Aguaymanto (Physalis peruviana L.) Nectar.

[Fuente institucional o enlace registrado](https://doi.org/10.1155/ijfo/2312352)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Integrated_SERS_and_Chemometric_Characterization_o.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB04

Nolla et al. (2026). Nutritional Composition, Antinutritional Potential, Antioxidant Capacity, and Consumption Frequency of Physalis peruviana and Physalis angulata Fruits.

[Fuente institucional o enlace registrado](https://doi.org/10.5539/jfr.v15n2p77)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Nutritional_Composition_Antinutritional_Potential_.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB05

Patiño Rodríguez et al. (2026). Immunomodulatory Potential of Agro-Industrial Residues: Passiflora edulis and Rubus glaucus Seed Oils Promote MMP-9 Release from Human Neutrophils.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/immuno6030043)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Immunomodulatory_Potential_of_Agro-Industrial_Resi.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB06

Cardona-Hurtado et al. (2026). Valorization of agricultural byproducts from Rubus glaucus Benth (blackberry) as a natural source of high value-added ingredients.

[Fuente institucional o enlace registrado](https://doi.org/10.1007/s13399-025-06982-y)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Cardona-Hurtado_et_al-2026-Biomass_Conversion_and_Biorefinery.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB07

Jamanca-Gonzales et al. (2026). Enriched bread with Lupinus mutabilis and Hordeum vulgare germinated flour: Physicochemical and sensory properties.

[Fuente institucional o enlace registrado](https://doi.org/10.15446/rfnam.v79.111540)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Enriched_bread_with_Lupinus_mutabilis_and_Hordeum_.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB08

Espinosa Cunuhay et al. (2026). Evaluation of biorational insecticides as an IPM strategy to control pests of (Lupinus mutabilis).

[Fuente institucional o enlace registrado](https://doi.org/10.31893/multiscience.2026603)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Evaluation_of_biorational_insecticides_as_an_IPM_s.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB09

Zou, L. (2009). Tesis de maestría, University of Helsinki. Effects of gradual and sudden heat stress on seed quality of Andean lupin, Lupinus mutabilis.

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\MScPPSthesis_LingZou.pdf

Uso: CL-E0182.

## BIB10

Adeoso et al. (2026). Resumen de congreso. Food hygiene and metal exposure in cooked beans (Phaseolus vulgaris) sold within a college community in Nigeria.

[Fuente institucional o enlace registrado](https://doi.org/10.1017/S002966512610528X)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Food_hygiene_and_metal_exposure_in_cooked_beans_Ph.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB11

Martínez-Barradas et al. (2026). Variable but Inheritable: Colchicine-Induced Polyploidy in Phaseolus vulgaris Generates Physiological Variability with Limited Inheritance.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/plants15162464)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Variable_but_Inheritable_Colchicine-Induced_Polypl.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB12

Girgel, Çokkızgın y Çölkesen (2018). A Research on Determination of the Morphological and Agronomical Characteristics of Local Beans (Phaseolus vulgaris L.) Genotypes under Organic Farming System in Bayburt.

[Fuente institucional o enlace registrado](https://doi.org/10.24925/turjaf.v6i5.530-535.1630)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\2018Turjaf6.5.bayburtkoullarndaorganikolarakyetitirilenfasulye...otbiyosem530-535.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB13

Rahmallah, Diniatik y Djalil (2026). Antihypercholesterolemic potential of bioactive compounds in Phaseolus vulgaris: A narrative review.

[Fuente institucional o enlace registrado](https://doi.org/10.33024/minh.v9i5.1447)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Antihypercholesterolemic_potential_of_bioactive_co.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## BIB14

Alves et al. (2026). Gastroprotective potential of fatty compounds from Persea americana seed: an experimental report.

[Fuente institucional o enlace registrado](https://doi.org/10.1007/s10787-026-02419-8)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\Gastroprotective_potential_of_fatty_compounds_from.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T2-01

Bahrami, Arzani y Rahimmalek (2019). Photosynthetic and yield performance of wild barley (Hordeum vulgare ssp. spontaneum) under terminal heat stress.

[Fuente institucional o enlace registrado](https://doi.org/10.32615/ps.2019.009)

Archivo de trazabilidad: C:\Users\campy\Downloads\Photosynthetica_phs-201901-0003.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T2-02

Aldana, García y Fischer (2014). Effect of waterlogging stress on the growth, development and symptomatology of cape gooseberry (Physalis peruviana L.) plants.

[Fuente institucional o enlace registrado](https://doi.org/10.18257/raccefyn.114)

Archivo de trazabilidad: C:\Users\campy\Downloads\revista,+5.+Effect+of+waterlogging.pdf

Uso: CL-E0183, CL-E0184, CL-E0185, CL-E0186.

## T2-03

Flores-Nimedez, Li y Shin (1993). Amelioration of Chilling Injury in Phaseolus vulgaris L. by GLK-8903.

[Fuente institucional o enlace registrado](https://journals.ashs.org/downloadpdf/journals/jashs/118/6/article-p825.pdf)

Uso: CL-E0187, CL-E0188.

## T2-04

Balasubramanian, P. M. (2002). Tesis doctoral, University of Saskatchewan. Selection for chilling and freezing resistance in common bean.

[Fuente institucional o enlace registrado](https://harvest.usask.ca/items/edd82c8c-8aac-436b-8c60-7aa3f8f37694)

Archivo de trazabilidad: C:\Users\campy\Downloads\NQ80920.pdf

Uso: CL-E0189.

## T2-05

Srivastava, Soni y Sonam (2015). Analysis on Effect of Cold Stress in Bean Seeds (Phaseolus vulgaris L.).

[Fuente institucional o enlace registrado](https://doi.org/10.11648/j.ajbio.20150304.15)

Archivo de trazabilidad: C:\Users\campy\Downloads\Analysis_on_Effect_of_Cold_Stress_in_Bea.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T2-06

Omae, Kumar y Shono (2012). Adaptation to High Temperature and Water Deficit in the Common Bean (Phaseolus vulgaris L.) during the Reproductive Period.

[Fuente institucional o enlace registrado](https://doi.org/10.1155/2012/803413)

Archivo de trazabilidad: C:\Users\campy\Downloads\Journal of Botany - 2012 - Omae - Adaptation to High Temperature and Water Deficit in the Common Bean  Phaseolus vulgaris L.pdf

Uso: CL-E0192.

## T2-07

Redden, Agtunong, George y Fukai (s. f.). Tolerence of temperature stress in phaseolus vulgaris.

Archivo de trazabilidad: C:\Users\campy\Downloads\p-03.pdf

Uso: CL-E0190, CL-E0191.

## T2-08

Bueckert, Wagenhoffer, Hnatowich y Warkentin (2015). Effect of heat and precipitation on pea yield and reproductive performance in the field.

[Fuente institucional o enlace registrado](https://doi.org/10.4141/CJPS-2014-342)

Archivo de trazabilidad: C:\Users\campy\Downloads\2015-effect-of-heat-and-precipitation-on-pea-yield-and-reproductive-performance-in-the-field.pdf

Uso: CL-E0193.

## T2-09

Devi et al. (2023). Heat stress tolerance in peas (Pisum sativum L.): Current status and way forward.

[Fuente institucional o enlace registrado](https://doi.org/10.3389/fpls.2022.1108276)

Archivo de trazabilidad: C:\Users\campy\Downloads\fpls-13-1108276.pdf

Uso: CL-E0194.

## T2-10

Duc, G. (1997). Faba bean (Vicia faba L.).

Archivo de trazabilidad: C:\Users\campy\Downloads\1-s2.0-S0378429097000257-main.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T2-11

Maalouf et al. (2022). Genetic Dissection of Heat Stress Tolerance in Faba Bean (Vicia faba L.) Using GWAS.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/plants11091108)

Archivo de trazabilidad: C:\Users\campy\Downloads\plants-11-01108.pdf

Uso: CL-E0195.

## T2-12

Maphosa, Preston y Richards (2023). Effect of Sowing Date and Environment on Phenology, Growth and Yield of Lentil (Lens culinaris Medikus.) Genotypes.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/plants12030474)

Archivo de trazabilidad: C:\Users\campy\Downloads\plants-12-00474.pdf

Uso: CL-E0196.

## T2-13

Choukri et al. (2020). Heat and Drought Stress Impact on Phenology, Grain Yield, and Nutritional Quality of Lentil (Lens culinaris Medikus).

[Fuente institucional o enlace registrado](https://doi.org/10.3389/fnut.2020.596307)

Archivo de trazabilidad: C:\Users\campy\Downloads\fnut-07-596307.pdf

Uso: CL-E0197, CL-E0198.

## T2-14

Simioniuc et al. (2021). Assessment of Andean lupin (Lupinus mutabilis) Genotypes for Improved Frost Tolerance.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/agriculture11020155)

Archivo de trazabilidad: C:\Users\campy\Downloads\1ff094f8823f889fcdd35c784f00c0298a75.pdf

Uso: CL-E0199, CL-E0200.

## T2-16

Martino y Abbate (2019). Frost damage on grain number in wheat at different spike developmental stages and its modelling.

[Fuente institucional o enlace registrado](https://doi.org/10.1016/j.eja.2018.10.010)

Archivo de trazabilidad: C:\Users\campy\Downloads\1-s2.0-S1161030118306609-main.pdf

Uso: CL-E0201, CL-E0202.

## T2-17

Farooq, Bramley, Palta y Siddique (2011). Heat Stress in Wheat during Reproductive and Grain-Filling Phases.

[Fuente institucional o enlace registrado](https://doi.org/10.1080/07352689.2011.615687)

Archivo de trazabilidad: C:\Users\campy\Downloads\Heat Stress in Wheat during Reproductive and Grain-Filling Phases.pdf

Uso: CL-E0203, CL-E0204.

## T2-18

Frederiks, Christopher, Sutherland y Borrell (2015). Post-head-emergence frost in wheat and barley: defining the problem, assessing the damage, and identifying resistance.

[Fuente institucional o enlace registrado](https://doi.org/10.1093/jxb/erv088)

Archivo de trazabilidad: C:\Users\campy\Downloads\erv088.pdf

Uso: CL-E0205, CL-E0206.

## T3-01

Otegui, Andrade y Suero (1995). Growth, water use, and kernel abortion of maize subjected to drought at silking.

[Fuente institucional o enlace registrado](https://doi.org/10.1016/0378-4290(94)00093-X)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U01_7bcc17ddda0e.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-02

Topali, Antonopoulou y Chatzissavvidis (2024). Effect of Waterlogging on Growth and Productivity of Fruit Crops.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/horticulturae10060623)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U02_521c300607ba.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-03

Lima et al. (2024). Morphological, physiological, and biochemical characteristics of Physalis peruviana L. plants under different water availabilities.

[Fuente institucional o enlace registrado](https://doi.org/10.14295/CS.v15.3807)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U03_8a374a3d3252.pdf

Uso: CL-E0207.

## T3-04

Guerrero Álvarez, Contreras Coronel y Cardona Hurtado (2021). Physicochemical and antioxidant characterization of Andean blackberry with and without prickles cultivated in Risaralda, Colombia.

[Fuente institucional o enlace registrado](https://doi.org/10.1590/0100-29452021918)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U04_cca15f1a2e84.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-05

Gil et al. (capítulo; presentado en congreso de 2007; fecha del documento por confirmar). Effect of waterlogging on plant water status, leaf gas exchange and biomass of avocado.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U05_4a8e9a15cb17.pdf

Uso: CL-E0208, CL-E0209.

## T3-06

Cataldo (2026). Drought Risk in Mango and Avocado Orchards: Insights Into Plant Water Relations and Irrigation-Related Agronomic Solutions.

[Fuente institucional o enlace registrado](https://doi.org/10.1002/ird.70132)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U06_22d92f35b69e.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-07

Harada et al. (2021). Comprehensive analysis of sucrolytic enzyme gene families in carnation (Dianthus caryophyllus L.).

[Fuente institucional o enlace registrado](https://doi.org/10.1016/j.phytochem.2020.112607)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U07_b460ab4657b7.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-08

Murthy et al. (2024). The Impact of Climate Change on Flowering Patterns and Productivity in Floriculture: A Comprehensive Review.

[Fuente institucional o enlace registrado](https://doi.org/10.9734/jsrr/2024/v30i112586)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U08_83fcf124c58d.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-09

Aydinsakir, Tuzel y Buyuktas (2011). The effects of different irrigation levels on flowering and flower quality of carnation (Dianthus caryophyllus L.) irrigated by drip irrigation.

[Fuente institucional o enlace registrado](https://doi.org/10.5897/AJB10.2590)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U09_c8b2ba67d27e.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-10

Nezhad-yani, Sarmast y Zakizadeh (2026). Physiological and biochemical responses of Rosa chinensis Jacq. 'Old Blush' to waterlogging stress under a controlled greenhouse environment.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U10_6ecc6395777c.pdf

Uso: CL-E0210.

## T3-11

Aalam et al. (2024). Water Deficit Severity during the Preceding Year Determines Plant Tolerance to Subsequent Year Drought Stress Challenges: A Case Study in Damask Rose.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/horticulturae10050462)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U11_0f042f325526.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-12

Demirtaş et al. (2010). Quality and yield response of soybean (Glycine max L. Merrill) to drought stress in sub-humid environment.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U12_b119800df0a5.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-13

Fletcher et al. (2023). Evaluating the Effects of Flooding Stress during Multiple Growth Stages in Soybean.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/agronomy13051243)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U13_e07302faa793.pdf

Uso: CL-E0211, CL-E0212.

## T3-14

Prodjinoto et al. (2026). N2-induced hypoxia and waterlogging elicit distinct whole-plant transpiration and adventitious-root responses in tomato (Solanum lycopersicum).

[Fuente institucional o enlace registrado](https://doi.org/10.1016/j.jplph.2026.154850)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U14_d8fd6d8c215e.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-16

Zheng et al. (2013). Responses of drip irrigated tomato (Solanum lycopersicum L.) yield, quality and water productivity to various soil matric potential thresholds in an arid region of Northwest China.

[Fuente institucional o enlace registrado](https://doi.org/10.1016/j.agwat.2013.08.001)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U16_1a76544eaff2.pdf

Uso: CL-E0213.

## T3-17

Kerddee, Kongsil y Nakasathien (2021). Waterlogging Tolerance and Recovery in Canopy Development Stage of Cassava (Manihot esculenta Crantz).

[Fuente institucional o enlace registrado](https://doi.org/10.17503/agrivita.v43i2.2615)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U17_96cd5147f543.pdf

Uso: CL-E0214, CL-E0215.

## T3-18

Bakayoko et al. (2009). Impact of water stress on fresh tuber yield and dry matter content of cassava (Manihot esculenta Crantz) in Côte d'Ivoire.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U18_d56266b739a6.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-19

Pinto et al. (2025; preprint). Effect of Flooding and Recovery Capacity After Stress Suspension of Theobroma cacao L. Rootstocks.

[Fuente institucional o enlace registrado](https://doi.org/10.20944/preprints202511.0634.v1)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U19_63ab8735c631.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-20

Pinto et al. (2023). Morphophysiological responses of Theobroma cacao L. rootstocks to flooding and post-flooding conditions.

[Fuente institucional o enlace registrado](https://doi.org/10.32615/ps.2023.031)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U20_b37533062c1e.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-21

De Almeida, Tezara y Herrera (2016). Physiological responses to drought and experimental water deficit and waterlogging of four clones of cacao (Theobroma cacao L.) selected for cultivation in Venezuela.

[Fuente institucional o enlace registrado](https://doi.org/10.1016/j.agwat.2016.03.012)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U21_ebf8233c9be0.pdf

Uso: CL-E0216, CL-E0217.

## T3-22

Kumari (2012). Influence of Drip Irrigation and Mulch on Leaf Area Maximization, Water Use Efficiency and Yield of Potato (Solanum tuberosum L.).

[Fuente institucional o enlace registrado](https://doi.org/10.5539/jas.v4n1p71)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U22_8309e85466f2.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-23

Eggermont (sin fecha confirmada; propuesta estudiantil). Sink nor swim: Potato (Solanum tuberosum) root survival during waterlogging and hypoxia.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U23_716551462bbb.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-24

Ayas y Korukçu (2010). Water-Yield Relationships in Deficit Irrigated Potato.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U24_8a520ec5587e.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-25

Ferreira y Gonçalves (2007). Crop-yield/water-use production functions of potatoes (Solanum tuberosum, L.) grown under differential nitrogen and irrigation treatments in a hot, dry climate.

[Fuente institucional o enlace registrado](https://doi.org/10.1016/j.agwat.2007.02.012)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U25_4407a97c446a.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-26

Li y Siddique, eds. (2018). FAO. Future Smart Food: Rediscovering hidden treasures of neglected and underutilized species for Zero Hunger in Asia — extracto.

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U26_c8a20b37c28a.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-27

Silva et al. (2019). Amaranth Response to Water Stress.

[Fuente institucional o enlace registrado](https://doi.org/10.9734/JEAI/2019/v40i130356)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U27_18b81ffaf3c7.pdf

Uso: bibliografia_consultada_sin_evidencia_especifica_extraida.

## T3-28

Bai et al. (2026). Identification and functional validation of hub genes responding to waterlogging stress during the filling period in quinoa (Chenopodium Quinoa Willd.).

[Fuente institucional o enlace registrado](https://doi.org/10.1186/s12870-026-08132-6)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U28_71510a199ebf.pdf

Uso: CL-E0218, CL-E0219.

## T3-29

Valdivia-Cea et al. (2021). Effect of Soil Water Availability on Physiological Parameters, Yield, and Seed Quality in Four Quinoa Genotypes (Chenopodium quinoa Willd.).

[Fuente institucional o enlace registrado](https://doi.org/10.3390/agronomy11051012)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U29_e4917840f199.pdf

Uso: CL-E0220, CL-E0221.

## T3-30

Neththasinghe, Sprunger y Lindsey (2026). Flooding temperature affected corn (Zea mays L.) emergence and root growth.

[Fuente institucional o enlace registrado](https://doi.org/10.1007/s11104-026-08943-4)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_tanda3\U30_5c37bfd13139.pdf

Uso: CL-E0222, CL-E0223, CL-E0224, CL-E0225.

## WEB01

Viteri D., P., Vásquez C., W., Viera, W., Sotomayor, A., y Mejía, P. (2016). Ecología para el desarrollo y crecimiento de la mora. En El cultivo de la mora en el Ecuador, pp. 19–24. INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/4051)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB01_INIAP_mora_ecologia_2016_c82b977b64f3.pdf

Uso: E0308, E0309, E0310, E0311, E0312, E0313, E0314, CL-E0226, CL-E0227, CL-E0228, CL-E0229, CL-E0230, CL-E0231.

## WEB02

Sharma, S., y Warren, J. (2024). Basics of Soil Bulk Density. PSS-2287. Oklahoma State University Extension.

[Fuente institucional o enlace registrado](https://extension.okstate.edu/fact-sheets/basics-of-soil-bulk-density)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB02_OSU_captura_navegador.json

Uso: criterio_general_suelo.

## WEB03

Crane, J. H., Schaffer, B., Her, Y. G., Bayabil, H., Wasielewski, J., y Fraisse, C. (2026). Quick Guide to Environmental Factors Impacting Subtropical and Tropical Fruit Crops in Florida. HS1499. UF/IFAS.

[Fuente institucional o enlace registrado](https://ask.ifas.ufl.edu/publication/HS1499)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB03_UFIFAS_HS1499_0d444f174833.pdf

Uso: CL-E0232, CL-E0233, CL-E0234, CL-E0235, CL-E0236.

## WEB04

Fischer, G., y Melgarejo, L. M. (2020). The ecophysiology of cape gooseberry (Physalis peruviana L.) — an Andean fruit crop. A review. Revista Colombiana de Ciencias Hortícolas, 14(1), 76–89.

[Fuente institucional o enlace registrado](https://doi.org/10.17584/rcch.2020v14i1.10893)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB04_Physalis_ecophysiology_2020_12ebf1715589.pdf

Uso: CL-E0238, CL-E0239, CL-E0240, CL-E0241, CL-E0242.

## WEB05

de Freitas, E. M., Gomes, C. N., da Silva, L. J., y da Cunha, F. F. (2024). Germination Performance of Physalis peruviana L. Seeds under Thermal and Water Stress Conditions. Agronomy, 14, 1213.

[Fuente institucional o enlace registrado](https://doi.org/10.3390/agronomy14061213)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB05_Physalis_germination_2024_613c84993ade.pdf

Uso: CL-E0243, CL-E0244, CL-E0245.

## WEB06

Tanji, K. K., y Kielen, N. C. (2002). Agricultural Drainage Water Management in Arid and Semi-Arid Areas. FAO Irrigation and Drainage Paper 61. Annex 1: Crop salt tolerance data.

[Fuente institucional o enlace registrado](https://www.fao.org/4/y4263e/y4263e0e.htm)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB06_FAO_salt_tolerance_annex_bec6d29b4841.html

Uso: E0317, E0318, E0319, E0320, E0321, E0322, E0323, E0324, E0325.

## WEB07

University of California Statewide IPM Program. (s. f.). Avocado — Site Selection.

[Fuente institucional o enlace registrado](https://ipm.ucanr.edu/home-and-landscape/avocado-site-selection/)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB07_UCIPM_avocado_site_9e0ff0243bf4.html

Uso: E0315, E0316, CL-E0237.

## WEB09

Malik, A. I., Ailewe, T. I., y Erskine, W. (2015). Tolerance of three grain legume species to transient waterlogging. AoB PLANTS, 7, plv040.

[Fuente institucional o enlace registrado](https://pmc.ncbi.nlm.nih.gov/articles/PMC4455828/)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB09_legumes_waterlogging_2015_f1a391df0e98.html

Uso: CL-E0248, CL-E0249.

## WEB10

Mollaali, E., Dadashi, M. R., Sheikh, F., Ajamnorozi, H., y Feyzbakhsh, M. T. (2023). Evaluating the Waterlogging Tolerance of Faba Bean Genotypes at Different Growth Stages under Field Conditions. Romanian Agricultural Research, 40.

[Fuente institucional o enlace registrado](https://doi.org/10.59665/rar4023)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_web_v01\WEB10_faba_waterlogging_field_2023_0a5009fa5622.pdf

Uso: CL-E0246, CL-E0247.

## PROD01

Araujo, A., et al. (2021). Manual del cultivo de papa para pequeños productores, 3.ª edición. INIAP, ESPOCH y CIP. Editores: Racines, M., Cuesta, X. y Castillo, C.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/5672)

Archivo de trazabilidad: C:\Users\campy\OneDrive\SMARTSEEDS\MANUAL DE PAPA 2020 3era edición.pdf

Uso: CL-E0250, PR-E0045, PR-E0047.

## PROD02

Instituto Nacional de Investigaciones Agropecuarias (2019). Acciones del INIAP respecto a la enfermedad Punta Morada de la Papa. INIAP, Estación Experimental Santa Catalina.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/5396)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD02_papa_andina_iniap_2019_45fef907f185.pdf

Uso: CL-E0251, CL-E0252.

## PROD03

Valarezo, A., Valarezo, O., Mendoza, A., Álvarez, H. y Vásquez, W. (2014). El cultivo de maracuyá: manual técnico para su manejo en el Litoral ecuatoriano. INIAP, Manual técnico 100.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/1159)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD03_maracuya_iniap_2014_6f718118a5ee.pdf

Uso: E0338, E0339, E0340, E0341, CL-E0259, CL-E0260, CL-E0261, PR-E0085, PR-E0086.

## PROD04

Fernández, F., Pico, J. T. y Avellán Cedeño, B. A. (2021). Guía para la producción y manejo integrado del cultivo de plátano. INIAP, Estación Central de la Amazonía.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/items/717618c7-e3c5-47b5-b204-33fdefdd90ea)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD04_platano_iniap_2021_2e1028e311ce.pdf

Uso: PR-E0080, PR-E0081, PR-E0082.

## PROD05

Carrillo, M., et al. (2015). Manual del cultivo de la palma aceitera. INIAP, Estación Experimental Santo Domingo, Manual técnico 102.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/items/397004a6-ed0a-41d1-aa63-d1fb02289511)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD05_palma_iniap_2015_0fe5853d9e22.pdf

Uso: E0331, E0332, E0333, E0334, E0335, E0336, E0337, CL-E0256, CL-E0257, CL-E0258, PR-E0084.

## PROD06

UTEPI / ONUDI (2006). Piña: estudio agroindustrial en el Ecuador.

[Fuente institucional o enlace registrado](https://www.unido.org/sites/default/files/2009-04/Pina_estudio_agroindustrial_en_el_Ecuador_0.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD06_pina_unido_2006_b7a2a409e4af.pdf

Uso: E0342, E0343, E0344, CL-E0262, CL-E0263, CL-E0264, PR-E0087, PR-E0088.

## PROD07

Cornejo Calvachi, et al. (2024). Determinación de la dosis óptima de N, P y K en el cultivo de brócoli híbrido Avenger (Brassica oleracea itálica) en Ecuador. Siembra, 11(2), e6658. https://doi.org/10.29166/siembra.v11i2.6658

[Fuente institucional o enlace registrado](https://revistadigital.uce.edu.ec/index.php/SIEMBRA/article/view/6658)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD07_brocoli_cotopaxi_2024_d57ec62303ae.pdf

Uso: PR-E0073.

## PROD08

Segura, M., Lesmes, J. C., Galindo, J. R. y Sánchez, G. D. (2015). Modelo tecnológico para el cultivo de cebolla de rama (Allium fistulosum L.) en el departamento de Boyacá. Corpoica, Mosquera, Colombia.

[Fuente institucional o enlace registrado](https://repository.agrosavia.co/server/api/core/bitstreams/9a816075-dfcc-4443-aab7-1fb53ca7c248/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD08_cebolla_rama_agrosavia_c2a0871ab1c9.pdf

Uso: E0326, E0327, E0328, E0329, E0330, CL-E0253, CL-E0254, CL-E0255, PR-E0074, PR-E0075.

## PROD10

Guamán Jiménez, R. y Andrade Varela, C. (2009). INIAP 308: nueva variedad de soya de alto rendimiento y de buena calidad de semilla para el Litoral ecuatoriano. INIAP, Boletín divulgativo 364.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/server/api/core/bitstreams/bcd5db67-870e-428e-9d48-682087954c89/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD10_soya_iniap308_4ef0353566b7.pdf

Uso: PR-E0056, PR-E0057.

## PROD12

Tamil Nadu Agricultural University (s. f.). Commercial rose. Agritech Portal; fecha de edición no indicada.

[Fuente institucional o enlace registrado](https://agritech.tnau.ac.in/horticulture/horti_flower%20crops_commercial%20rose.html)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD12_rosa_campo_tnau_60f5a5ad31f1.html

Uso: PR-E0058, PR-E0059, PR-E0060.

## PROD13

Velásquez, J., Araujo, A., Andrade, V., Rivadeneira, J., Cuesta, H., Racines, M. y Tinoco, K. (2022). Manual de producción de tubérculo-semilla de papa. 2.ª edición, Manual 124. INIAP.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/server/api/core/bitstreams/3c890f1d-f36f-40cd-81cd-21fb18efe7b0/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD13_papa_guia_iniap124_a515ccfff741.pdf

Uso: PR-E0044, PR-E0046.

## PROD14

Humana Pueblo a Pueblo Ecuador (s. f.). Manual de uvilla. Fecha editorial por confirmar; archivo alojado en 2021.

[Fuente institucional o enlace registrado](https://humana-ecuador.org/wp-content/uploads/2021/09/Manual-de-Uvilla_Final.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD14_uvilla_humana_56b8bd0241fe.pdf

Uso: PR-E0068.

## PROD15

Ministerio de Agricultura y Riego del Perú (2017). Cacao: el Perú centro de origen de la biodiversidad. Ficha técnica. Copia institucional alojada por ICCO.

[Fuente institucional o enlace registrado](https://www.icco.org/wp-content/uploads/2019/07/Ficha-Cacao.pdf)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD15_cacao_midagri_16f1031cf998.pdf

Uso: PR-E0048.

## PROD16

López Villa, F. M. (2011). Evaluación de la aclimatación y rendimiento de 16 cultivares de zanahoria (Daucus carota L.) a campo abierto, en Macají, cantón Riobamba, provincia de Chimborazo. Tesis de Ingeniería Agronómica, ESPOCH.

[Fuente institucional o enlace registrado](https://dspace.espoch.edu.ec/handle/123456789/1364)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD16_zanahoria_espoch_bd362127a8a9.pdf

Uso: PR-E0076, PR-E0077, PR-E0078, PR-E0079.

## PROD17

INIAP (2021). Guía para la producción y manejo integrado del cultivo de yuca (Manihot esculenta Crantz), para la Amazonía ecuatoriana.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/5824)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD17_yuca_amazonia_2021_a51475c5f66d.pdf

Uso: PR-E0050.

## PROD18

Reyes, S., et al. (s. f.). INIAP H-601: híbrido de maíz para condiciones de ladera del trópico seco ecuatoriano. INIAP y ULEAM. Versión actualizada consultada; liberación original en 2004, fecha de actualización por precisar.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/1145)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD18_maiz_h601_a371bbb707fd.pdf

Uso: PR-E0035, PR-E0036, PR-E0037.

## PROD19

Varela, A. (2019, según registro del repositorio). Estudio de la producción y comercialización del tomate riñón (Lycopersicum esculentum) en el cantón Pimampiro, de la provincia de Imbabura. Universidad Técnica del Norte.

[Fuente institucional o enlace registrado](https://repositorio.utn.edu.ec/handle/123456789/8810)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD19_tomate_pimampiro_01d330589e92.pdf

Uso: PR-E0054, PR-E0055.

## PROD20

Crane, J. H., Balerdi, C. F. y Maguire, I. (s. f.; versión consultada en 2026). Avocado Growing in the Florida Home Landscape. UF/IFAS Extension, CIR1034/MG213. https://doi.org/10.32473/EDIS-mg213-1983

[Fuente institucional o enlace registrado](https://ask.ifas.ufl.edu/publication/MG213)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD20_aguacate_ifas_e2474a5f2398.pdf

Uso: PR-E0064, PR-E0065.

## PROD21

Ganchozo, W. y Huaraca, H. (2017). Guía para facilitar el aprendizaje en el manejo integrado del cultivo de palma aceitera (Elaeis guineensis Jacq.). INIAP, Guía de aprendizaje 007.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/handle/41000/4774)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD21_palma_aprendizaje_74681258b382.pdf

Uso: PR-E0083.

## PROD23

Herrera Ramírez, C. D., Hidrobo Luna, J. R. y Basantes Morales, E. R. (2016). Evaluación del efecto de la asociación de coberturas vegetales vivas sobre el cultivo de uvilla (Physalis peruviana L.) en Huaca, provincia del Carchi, Ecuador. Siembra, 3(1), 91–100. https://doi.org/10.29166/siembra.v3i1.266

[Fuente institucional o enlace registrado](https://revistadigital.uce.edu.ec/index.php/SIEMBRA/article/view/266)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD23_uvilla_carchi_articulo_674c02efcba9.pdf

Uso: PR-E0069, PR-E0070.

## PROD25

Hinostroza García, F., Mendoza García, M. V., Navarrete Párraga, M. y Muñoz Conforme, X. (2014). Cultivo de yuca en el Ecuador. INIAP, Estación Experimental Portoviejo, Boletín divulgativo 436.

[Fuente institucional o enlace registrado](https://repositorio.iniap.gob.ec/server/api/core/bitstreams/cb5102b0-62a6-46c5-8f64-00cd81ab2859/content)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD25_yuca_iniap436_ee7ec324a9fc.pdf

Uso: PR-E0051, PR-E0052.

## PROD26

Ministerio de Agricultura y Ganadería del Ecuador (2024, 28 de octubre). Tungurahua, líder en la producción de mora en Ecuador.

[Fuente institucional o enlace registrado](https://www.agricultura.gob.ec/tungurahua-lider-en-la-produccion-de-mora-en-ecuador/)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD26_mora_mag2024_534b8abbf550.html

Uso: PR-E0066.

## PROD27

Sakata Seed (s. f.). Avenger (Hybrid): Broccoli. Ficha del obtentor, referencia de madurez desde siembra directa en Salinas, California.

[Fuente institucional o enlace registrado](https://sakatavegetables.com/vegetable/avenger/)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD27_brocoli_sakata_salinas_90deb13edcaa.html

Uso: PR-E0071.

## PROD28

Sakata Centroamérica (s. f.). Brócoli Avenger: especificaciones técnicas. Ficha comercial del obtentor.

[Fuente institucional o enlace registrado](https://www.sakatacentroamerica.com/productos/avenger/)

Archivo de trazabilidad: C:\Users\campy\OneDrive\Documentos\ChatGPT\SMARTSEEDS\output\catalogo\fuentes_productividad\PROD28_brocoli_sakata_centroamerica_9c1d8e701675.html

Uso: PR-E0072.

## S28

USDA Natural Resources Conservation Service. (2008/2023). Soil Quality Indicators: Bulk Density.

[Fuente institucional o enlace registrado](https://www.nrcs.usda.gov/sites/default/files/2023-01/Soil%20Quality-Indicators-Bulk%20Density.pdf)

Uso: pendiente_sin_datos_incorporados.
