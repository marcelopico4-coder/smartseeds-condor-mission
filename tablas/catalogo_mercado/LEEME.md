# SMARTSEEDS — Producción, comercio, precios y suministro v1.0

Instantánea compilada el 2026-11-14. Catálogo para la app con 27 IDs compatibles con el catálogo agronómico v1.1.

## Archivo principal

`SMARTSEEDS_catalogo_mercado_v1.0.json` contiene fuentes, cultivos, productos y cuatro series. Los IDs referenciados se resuelven dentro del mismo JSON.

| Serie | Registros | Cobertura |
|---|---:|---|
| Producción | 477 | ESPAC 2025 nacional y tres provincias; historia provincial 2023–2024 |
| Comercio exterior | 84 | Año 2025, enero–julio 2025 y enero–julio 2026 |
| Precios | 2831 | Tres provincias, 2024–2026, por canal y presentación |
| Suministro HBA | 24 | Nacional 2023–2025, producto homologado |

## Cambios frente al catálogo inicial

- Se agregan brócoli, cebolla blanca de rama, zanahoria, plátano, palma africana, maracuyá y piña.
- Se sustituyen cadenas de texto con cifras y fuentes mezcladas por campos numéricos, unidades, periodos, territorio y coordenadas de procedencia.
- Se retiran las etiquetas suficiente/insuficiente/superávit/déficit que no tenían una medición de demanda o método defendible. El original se conserva en el informe de revisión.
- Se separan maíz duro/suave, seco/choclo; soya en grano/aceite/torta; productos frescos/procesados. El comercio de flores y de mora conserva sus agrupaciones.
- Los precios productor no se mezclan con mayoristas ni bodegas. Cada precio retiene presentación y equivalencia; no se convierte un saco o gaveta sin masa explícita.
- No se trasladan umbrales de suelo o rendimientos técnicos como si fueran producción provincial o inventario comercial.

## Integración

1. Relacionar `cultivos.id` con C001–C027 del catálogo agronómico.
2. Resolver `productos_ids` y `registros_ids` contra las series correspondientes.
3. Elegir producto, presentación, sistema, territorio, canal y periodo compatibles antes de comparar.
4. Mostrar los faltantes como no disponibles. Cero sólo es un valor publicado.
5. Usar `procedencia.fuente_id`, `hoja` y `celdas` para mostrar citas.
6. Mantener demanda e inventario actual como pendientes. HBA es suministro estimado, no pedidos o déficit.

Ejemplo de consulta de precios (JavaScript):

```js
const cultivo = catalogo.cultivos.find(c => c.id === "C022");
const ids = new Set(cultivo.registros_ids.precios);
const precios = catalogo.precios.filter(r => ids.has(r.id)
  && r.territorio_id === "EC-TUN" && r.canal === "mayorista");
```

## Límites que la app debe conservar

- Comercio 2026 llega a julio aunque el portal anuncie un corte más reciente: el libro descargado sigue identificando enero–julio.
- Precios productor llegan a septiembre 2026 y mayoristas/bodegas a octubre 2026. Fecha de actualización no equivale al mes de la observación.
- Sin datos específicos no se concluye ausencia de producción, comercio o demanda. Algunos cultivos tienen precios, pero no producción oficial individualizada en las tablas consultadas.
- La HBA y ESPAC pueden no conciliar. En papa 2025 se detectó producción neta HBA superior a producción bruta ESPAC; se conserva la incidencia y no se combinan para calcular un déficit.
- La masa comercial de flores no se transforma en tallos ni el aceite de palma en fruta fresca sin factores específicos.
- El promedio mensual de una cotización no es una orden de compra, garantía de precio futuro o indicador de demanda insatisfecha.
- El catálogo no recomienda ni puntúa cultivos. La app debe generar sus resultados con datos compatibles.

## Fuentes

### MER00

Catálogo económico inicial del equipo

Archivo aportado por el equipo; referencia bibliográfica y huella en el JSON.

### MER01

SIPA/BCE. Comercio exterior agropecuario y agroindustrial. Copia aportada

[Fuente](https://sipa.agricultura.gob.ec/descargas/base-estadistica/modulo_economico/comercio-exterior-agropecuario-agroindustrial.xlsx)

### MER02

SIPA. Precios productor promedio, copia aportada

[Fuente](https://sipa.agricultura.gob.ec/descargas/base-estadistica/modulo_economico/precios-productor-ponderado.xlsx)

### MER03

SIPA. Precios mensualizados mayoristas y bodegas, copia aportada

[Fuente](https://sipa.agricultura.gob.ec/descargas/base-estadistica/modulo_economico/precios-mercados-mayoristas-bodegas-comerciales.xlsx)

### MER04

INEC (2026). Boletín técnico ESPAC 2025

[Fuente](https://www.ecuadorencifras.gob.ec/documentos/web-inec/Estadisticas_agropecuarias/espac/2025/Boletin_tenico_ESPAC_2025.pdf)

### MER05

BCE (abril 2022). Boletín de Análisis Agropecuario 94, IV trimestre 2021

Archivo aportado por el equipo; referencia bibliográfica y huella en el JSON.

### MER06

Atlas Agroeconómico Ecuador, edición 2026

Archivo aportado por el equipo; referencia bibliográfica y huella en el JSON.

### MER07

INEC (2026). Tabulados ESPAC 2025

[Fuente](https://www.ecuadorencifras.gob.ec/documentos/web-inec/Estadisticas_agropecuarias/espac/2025/Tabulados_excel_2025.xlsx)

### MER09

SIPA (julio 2026). Hoja de Balance de Alimentos, datos 2025

[Fuente](https://sipa.agricultura.gob.ec/descargas/base-estadistica/modulo_productivo/hoja-balance-alimentos.xlsx)

### MER10

SIPA/INEC (mayo 2026). Superficie y producción histórica, 2002–2025

[Fuente](https://sipa.agricultura.gob.ec/descargas/base-estadistica/modulo_productivo/superficie-produccion.xlsx)

### MER11

SIPA/BCE. Comercio exterior, descarga del 14 de noviembre de 2026

[Fuente](https://sipa.agricultura.gob.ec/descargas/base-estadistica/modulo_economico/comercio-exterior-agropecuario-agroindustrial.xlsx)

### MET01

FAO (2001). Food Balance Sheets: A Handbook. Concepts and definitions

[Fuente](https://www.fao.org/4/x9892e/x9892e02.htm)

## Esquema y cobertura

`SMARTSEEDS_catalogo_mercado.schema.json` describe la estructura para un validador JSON Schema 2020-12. Además deben comprobarse IDs y relaciones entre tablas.

Los conteos de registros incluyen filas con valores no publicados: en producción, 291 de 477 registros conservan producción null. Consultar `cobertura_2025_por_territorio` y el estado de cada medida; tener una ficha o fila no demuestra cobertura numérica completa.

La descarga principal es un módulo económico separado del agronómico. No reemplaza el catálogo de suelo, clima y producción técnica. Ambos se relacionan por `cultivo_id`.
