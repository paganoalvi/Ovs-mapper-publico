from urllib.parse import quote

from rdflib import Graph, Literal, Namespace, URIRef

from .. import Node


class SafeNamespace(Namespace):
    """Namespace that builds URIs with urllib.parse.quote()"""

    def term(self, name: str) -> URIRef:
        return super().term(quote(name))


class SafeGraph(Graph):
    """Graph that doesn't add None 'objects'."""

    def add(self, triple: tuple[Node, URIRef, Node | Literal]) -> None:
        if all(triple):
            super().add(triple)
