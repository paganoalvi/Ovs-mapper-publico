import datetime
import enum
import itertools


def timestamp() -> str:
    "Returns the current timestamp as a str, leaving only the digits."
    return str(datetime.datetime.now().timestamp()).replace(".", "")


class Incremental(enum.Enum):
    """
    Enumeration of an `itertools.count`-like incremental for each class.
    """

    REAL_ESTATE = itertools.count()
    SPACE = itertools.count()
    LISTING = itertools.count()
    FEATURE = itertools.count()

    def fragment(self) -> str:
        """
        Return the fragment part of a URI, consisting of the class name
        in lowercase and the next value of the incremental.
        """
        return self.name.lower() + "_" + timestamp() + "_" + str(next(self.value))
