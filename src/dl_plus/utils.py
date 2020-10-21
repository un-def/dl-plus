from enum import Enum


class NotSet(Enum):
    # Am I the only one who finds this hideous?
    # https://github.com/python/typing/issues/236
    # https://www.python.org/dev/peps/pep-0484/#support-for-singleton-types\
    # -in-unions
    NOTSET = 0


NOTSET = NotSet.NOTSET
