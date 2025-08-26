# csv2pronto

[![README in spanish](https://img.shields.io/badge/lang-es-red.svg)](./README.es.md)

This repository contains the Pronto ontology, defined to model
information related to real estate listings. Additionally, it contains
the `csv2pronto` script, responsible for translating a CSV file to a graph
that adheres to the ontology.

## Contents

The [`csv2pronto`](./csv2pronto) folder contains the Python script responsible
for converting a source file in CSV format to an RDF that adheres to the
Pronto ontology, defined in [`./ontology/pronto.owl`](./ontology/pronto.owl).

Below are the headers that the input file should have in order to be
converted by the script:

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
- is_studio_apartmentSee the LICENSE file for more information.
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

While not all data is mandatory, the more detailed it is,
the better the semantic representation produced.

## Installation

First, clone this repository with:

```bash
git clone https://github.com/tu_usuario/csv2pronto.git
```

To use this project, you need to have Python 3.10 or higher installed on your
system. You can download Python 3 from the [official website](https://www.python.org/downloads/).

Once done, create a virtual environment and activate it with:

```bash
python -m venv .venv
source .venv/bin/activate
```

All required packages are listed in the `requirements.txt` file,
which can be installed using pip with the following command:

```bash
pip install -r requirements.txt
```

## Usage

To use this project, navigate to the project directory and activate the virtual environment:

```bash
source venv/bin/activate
```

Then run the script with Python:

```bash
python csv2pronto.py -s <archivo_csv_fuente> -d <archivo_rdf_destino> -o <archivo_ontología> -f <formato_rdf>
```

### Arguments

- `-s`, `--source`: Path to the CSV file to be converted.
- `-d`, `--destination`: Path to the RDF file to be written.
- `-o`, `--ontology`: Path to the ontology to be used.
- `-f`, `--format`: Format of the output graph (e.g., xml, ttl, nt, n3).

## Example

```bash
python csv2pronto.py -s data.csv -d output.ttl -o pronto.owl -f ttl
```

## License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for more information.
