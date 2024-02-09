import importlib
import sys
from io import StringIO

from .exceptions import DLPlusException


class YoutubeDLError(DLPlusException):

    pass


class UnknownBuiltinExtractor(YoutubeDLError):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'unknown built-in extractor: {self.name}'


_NAME_PART_SURROGATE = '_'


_NOT_SET = object()


_ytdl_module = _NOT_SET
_ytdl_module_name = _NOT_SET

_extractors = _NOT_SET
_extractors_registry = _NOT_SET

_lazy_load_extractor_base = _NOT_SET


def _check_initialized():
    global _ytdl_module
    if _ytdl_module is _NOT_SET:
        raise YoutubeDLError('not initialized')


def init(ytdl_module_name: str) -> None:
    global _ytdl_module
    if _ytdl_module is not _NOT_SET:
        raise YoutubeDLError('already initialized')
    try:
        _ytdl_module = importlib.import_module(ytdl_module_name)
    except ImportError as exc:
        raise YoutubeDLError(f'failed to initialize: {exc}') from exc
    global _ytdl_module_name
    _ytdl_module_name = ytdl_module_name


def run(args):
    _check_initialized()
    global _ytdl_module_name
    orig_sys_argv = sys.argv
    try:
        sys.argv = [_ytdl_module_name.replace('_', '-'), *args]
        _ytdl_module.main()
    finally:
        sys.argv = orig_sys_argv


def get_ytdl_module():
    _check_initialized()
    global _ytdl_module
    return _ytdl_module


def get_ytdl_module_name():
    _check_initialized()
    global _ytdl_module_name
    return _ytdl_module_name


def get_ytdl_module_version():
    return import_from('version', '__version__')


def get_help():
    _check_initialized()
    with StringIO() as buffer:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = buffer
        try:
            _ytdl_module.main(['--help'])
        except SystemExit:
            pass
        finally:
            sys.stdout, sys.stderr = stdout, stderr
        return buffer.getvalue().partition('Options:')[2]


def import_module(module_name):
    _check_initialized()
    global _ytdl_module_name
    return importlib.import_module(f'{_ytdl_module_name}.{module_name}')


def _import_from(module, name):
    try:
        return getattr(module, name)
    except Exception as exc:
        raise ImportError(f'failed to import {name}: {exc}') from exc


def import_from(module_name, names):
    module = import_module(module_name)
    if isinstance(names, str):
        return _import_from(module, names)
    return tuple(_import_from(module, name) for name in names)


def get_all_extractors(*, include_generic: bool):
    _check_initialized()
    global _extractors
    if _extractors is _NOT_SET:
        _extractors = tuple(import_module('extractor')._ALL_CLASSES)
    if include_generic:
        return _extractors
    return _extractors[:-1]


def _get_real_extractor(extractor):
    global _lazy_load_extractor_base
    if _lazy_load_extractor_base is None:
        return extractor
    if _lazy_load_extractor_base is _NOT_SET:
        try:
            _lazy_load_extractor_base = import_from(
                'extractor.lazy_extractors', 'LazyLoadExtractor')
        except ImportError:
            _lazy_load_extractor_base = None
            return extractor
    if not issubclass(extractor, _lazy_load_extractor_base):
        return extractor
    if 'real_class' in _lazy_load_extractor_base.__dict__:
        return extractor.real_class
    if '_get_real_class' in _lazy_load_extractor_base.__dict__:
        return extractor._get_real_class()
    return extractor


def _get_extractor_name(extractor):
    ie_name = extractor.IE_NAME
    if isinstance(ie_name, property):
        return extractor().IE_NAME
    return ie_name


def _build_extractors_registry():
    registry = {}
    for extractor in get_all_extractors(include_generic=True):
        extractor = _get_real_extractor(extractor)
        name_parts = _get_extractor_name(extractor).split(':')
        name_parts.reverse()
        _store_extractor_in_registry(extractor, name_parts, registry)
    return registry


def _store_extractor_in_registry(extractor, name_parts, registry):
    name_part = name_parts.pop()
    if name_part in registry:
        stored = registry[name_part]
        if not isinstance(stored, dict):
            subregistry = registry[name_part] = {_NAME_PART_SURROGATE: stored}
        else:
            subregistry = stored
        if not name_parts:
            if _NAME_PART_SURROGATE in subregistry:
                raise YoutubeDLError(f'duplicate name: {extractor!r}')
            subregistry[_NAME_PART_SURROGATE] = extractor
        else:
            _store_extractor_in_registry(extractor, name_parts, subregistry)
    elif not name_parts:
        registry[name_part] = extractor
    else:
        subregistry = registry[name_part] = {}
        _store_extractor_in_registry(extractor, name_parts, subregistry)


def _flatten_registry_gen(registry):
    for value in registry.values():
        if not isinstance(value, dict):
            yield value
        else:
            yield from _flatten_registry_gen(value)


def _get_extractors_from_registry(name_parts, registry):
    name_part = name_parts.pop()
    stored = registry[name_part]
    if not name_parts:
        if not isinstance(stored, dict):
            return [stored]
        return list(_flatten_registry_gen(stored))
    if not isinstance(stored, dict):
        raise KeyError(name_part)
    return _get_extractors_from_registry(name_parts, stored)


def get_extractors_by_name(name):
    _check_initialized()
    global _extractors_registry
    if _extractors_registry is _NOT_SET:
        _extractors_registry = _build_extractors_registry()
    name_parts = name.split(':')
    name_parts.reverse()
    try:
        return _get_extractors_from_registry(name_parts, _extractors_registry)
    except KeyError:
        raise UnknownBuiltinExtractor(name)


def patch_extractors(extractors):
    extractor_module = import_module('extractor')
    extractor_module.gen_extractor_classes = lambda: extractors
    ie_keys_extractors_map = {
        extractor.ie_key(): extractor for extractor in extractors}
    extractor_module.get_info_extractor = (
        lambda ie_key: ie_keys_extractors_map[ie_key])
    importlib.reload(import_module('YoutubeDL'))
