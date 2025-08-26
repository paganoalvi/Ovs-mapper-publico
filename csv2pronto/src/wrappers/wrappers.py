import functools
from typing import Callable

from rdflib import BNode, Namespace

from ..incrementals.incrementals import Incremental
from ..null_objects.null_objects import NoneNode


def default_to_BNode(func: Callable) -> Callable:
    """
    Decorator that returns a `BNode` if the URI creation raises a
    `KeyError`.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return BNode()

    return wrapper


def default_to_NoneNode(func: Callable) -> Callable:
    """
    Decorator that returns a `NoneNode` if the URI creation raises a
    `KeyError`.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return NoneNode()

    return wrapper


# def default_to_incremental(ns: Namespace, inc: Incremental) -> Callable:
#     """
#     Decorator that returns a URI with an incremental value if the URI
#     creation raises a `KeyError`.
#     """

#     def decorator(func: Callable) -> Callable:
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except KeyError:
#                 return ns[inc.fragment()]

#         return wrapper

#     return decorator
from collections import defaultdict

# contador contextual solo para FEATURES
_feature_counter = defaultdict(int)

def default_to_incremental(ns: Namespace, inc: Incremental) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if inc == Incremental.FEATURE:
                subject = args[0]
                feature = args[1]
                key = (feature, subject.fragment)
                _feature_counter[key] += 1
                count = _feature_counter[key]
                uri = f"feature_{feature}_{count}_{subject.fragment}"
                return ns[uri]
            else:
                try:
                    return func(*args, **kwargs)
                except KeyError:
                    return ns[inc.fragment()]

        return wrapper

    return decorator


