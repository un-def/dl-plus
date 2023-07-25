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
