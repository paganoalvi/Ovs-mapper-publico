from typing import TypeAlias

from rdflib import BNode, URIRef

Node: TypeAlias = URIRef | BNode
