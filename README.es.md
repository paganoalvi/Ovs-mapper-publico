# csv2pronto

[![README en inglés](https://img.shields.io/badge/lang-en-red.svg)](./README.md)

Este repositorio contiene la ontología Pronto, definida para modelar
la información relacionada a avisos inmobiliarios. Además contiene
el script `csv2pronto`, encargado de traducir un archivo `CSV` a un
grafo que se apega a la ontología.

## Contenido

En la carpeta [`csv2pronto`](./csv2pronto) se encuentra el script de Python
encargado de llevar un archivo fuente en formato CSV a un RDF que respete
la ontología Pronto, definida en [`./ontology/pronto.owl`](./ontology/pronto.owl).

A continuación se listan los headers que debería tener el archivo de entrada para
poder ser convertido por el script:

- address
- advertiser_id
- advertiser_name
- age
- bath_amnt
- bed_amnt
- bed_ratio
- covered_ratio
- covered_surface
- covered_surface_unit
- currency
- date_extracted
- date_published
- description
- disposition
- district
- features
- garage_amnt
- is_finished_property
- is_new_property
- is_studio_apartment
- land_ratio
- land_surface
- land_surface_unit
- latitude
- listing_age
- listing_id
- longitude
- luminosity
- maintenance_fee
- maintenance_fee_currency
- neighborhood
- orientation
- price
- price_control
- property_group
- property_type
- province
- reconstructed_land_surface
- reconstructed_land_surface_unit
- reconstructed_total_surface
- reconstructed_total_surface_unit
- response
- room_amnt
- room_ratio
- site
- site_abbreviation
- title
- toilete_amnt
- total_ratio
- total_surface
- total_surface_unit
- transaction
- uncovered_surface
- uncovered_surface_unit
- url
- year_built

Si bien no todos los datos son obligatorios, a mayor completitud
mejor será la representación semántica producida.

## Instalación

Primero, cloná este repositorio con:

```bash
git clone https://github.com/tu_usuario/csv2pronto.git
```

Para utilizar este proyecto, necesitás tener instalado Python 3.10 o superior en
tu sistema. Podés descargar Python 3 desde el [sitio web oficial](https://www.python.org/downloads/).

Una vez hecho esto, creá un entorno virtual y activarlo con:

```bash
python -m venv .venv
source .venv/bin/activate
```

Todos los paquetes requeridos están listados en el archivo
`requirements.txt`, los cuales pueden ser instalados
usando pip mediante el siguiente comando:

```bash
pip install -r requirements.txt
```

## Uso

Para usar este proyecto, navegá hasta el directorio del proyecto y activá el entorno
virtual:

```bash
source venv/bin/activate
```

Luego ejecutá el script con Python:

```bash
python csv2pronto.py -s <archivo_csv_fuente> -d <archivo_rdf_destino> -o <archivo_ontología> -f <formato_rdf>
```

### Argumentos

- `-s`, `--source`: Ruta al archivo CSV que se va a convertir.
- `-d`, `--destination`: Ruta al archivo RDF donde se escribirá.
- `-o`, `--ontology`: Ruta a la ontología que se utilizará.
- `-f`, `--format`: Formato del grafo de salida (por ejemplo, xml, ttl, nt, n3).

## Ejemplo

```bash
python csv2pronto.py -s datos.csv -d salida.ttl -o pronto.owl -f ttl
```

## Licencia

Este proyecto está bajo la Licencia MIT.
Consultá el archivo [LICENSE](./LICENSE) para obtener más información.
