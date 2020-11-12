import sys

from .plugin import ExtractorPlugin


_LAZY_LOAD_NAMES = [
    'Extractor',
    'ExtractorError',
]

__all__ = _LAZY_LOAD_NAMES + ['ExtractorPlugin']


def __getattr__(name):
    if name not in _LAZY_LOAD_NAMES:
        raise AttributeError(name)
    from . import extractor
    _globals = globals()
    for _name in _LAZY_LOAD_NAMES:
        _globals[_name] = getattr(extractor, _name)
    return _globals[name]


# Python 3.6 — emulate PEP 562
# https://docs.python.org/3/reference/\
#   datamodel.html#customizing-module-attribute-access
if sys.version_info < (3, 7):
    from types import ModuleType
    sys.modules[__name__].__class__ = type(
        'LazyModule', (ModuleType,),
        {'__getattr__': staticmethod(__getattr__)},
    )
