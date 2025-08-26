from rdflib import XSD, Literal

from .null_objects import NoneLiteral


def literal_factory(value, *a, **kwa):
    """
    Create a `Literal` unless the value is None, in which case return a
    `NoneLiteral`.
    """
    return NoneLiteral(value, *a) if value is None else Literal(value, *a, **kwa)


def Boolean(value) -> Literal | NoneLiteral:
    "A `Literal` of type `XSD.boolean`"
    return literal_factory(value, datatype=XSD.boolean)


def DateTime(value) -> Literal | NoneLiteral:
    "A `Literal` of type `XSD.dateTime`"
    return literal_factory(value, datatype=XSD.dateTime)


def Double(value) -> Literal | NoneLiteral:
    "A `Literal` of type `XSD.double`"
    return literal_factory(value, datatype=XSD.double)


def Float(value) -> Literal | NoneLiteral:
    "A `Literal` of type `XSD.float`"
    return literal_factory(value, datatype=XSD.float)


def Integer(value) -> Literal | NoneLiteral:
    "A `Literal` of type `XSD.integer`"
    return literal_factory(value, datatype=XSD.integer)


def String(value) -> Literal | NoneLiteral:
    "A `Literal` of type `XSD.string`"
    return literal_factory(value, datatype=XSD.string)
