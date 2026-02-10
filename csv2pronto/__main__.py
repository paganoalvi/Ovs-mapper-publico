"""
Convert a CSV file to an RDF graph following the Pronto ontology.

This script reads a CSV file containing data to be mapped into RDF format using the Pronto ontology.
It processes the CSV in chunks for efficiency and writes the resulting RDF graph to a specified output file.

Usage:
    python -m csv2pronto -s <source_csv> -d <destination_rdf> -o <ontology_file> -f <rdf_format> --input_source <source_type> [--sites <site_dict>]

Arguments:
    -s, --source         Path to the input CSV file to convert.
    -d, --destination    Path to the output RDF file.
    -o, --ontology       Path to the ontology file to use for mapping.
    -f, --format         RDF serialization format for the output (e.g., 'xml', 'turtle').
    --input_source       Source of the input CSV data: 'scraper', 'ave', or 'auto' (to infer from headers).
    -ss, --sites         (Optional) Dictionary of site mappings in 'key=value' comma-separated format.

Assumptions:
    - The input CSV must be UTF-8 encoded.
    - The ontology file must be compatible with rdflib.
    - The script expects specific columns in the CSV depending on the input source type.
    - The output RDF file will be overwritten if it exists.
"""

import argparse
import csv
import pandas as pd
import itertools
import rdflib
from src.converter import create_graph_from_chunk
from tqdm import tqdm
from joblib import Parallel, delayed

def parse_sites(s: str) -> dict[str, str]:
    d = {}
    for pair in s.split(","):
        k, v = pair.split("=")
        d[k.strip()] = v.strip()
    return d


def main() -> None:
    args: argparse.Namespace = parse_args()
    
    with open(args.source, "r", encoding="utf-8") as csv_file:
        graph: rdflib.Graph = rdflib.Graph()

        graph.parse(args.ontology)
       
        chunksize = 3000

        for idx, row in enumerate(pd.read_csv(csv_file, chunksize=chunksize, iterator=True, dialect='excel', delimiter=",", keep_default_na=False, dtype=str)):
            # Process each chunk sequentially
            create_graph_from_chunk(row, graph, idx, args.destination, args.format, args.sites, args.input_source)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "-s", "--source", help="CSV file to convert", required=True, type=str
    )
    parser.add_argument(
        "-d", "--destination", help="RDF file to write", required=True, type=str
    )

    parser.add_argument(
        "-o", "--ontology", help="Ontology to use", required=True, type=str
    )

    parser.add_argument(
        "-f", "--format", help="RDF format of the output", required=True, type=str
    )

    parser.add_argument(
        "-ss", "--sites",
        type=parse_sites,
        help="JSON format dictionary"
    )
    
   # new argument to specify the input source format 
    parser.add_argument(
        "--input_source",choices=["scraper", "ave", "auto"],required=True,
        help=(
            "Source of the input CSV data. "
            "'scraper' expects scraper columns, "
            "'ave' expects AVE columns, "
            "'auto' attempts to infer from headers."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
