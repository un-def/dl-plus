import importlib
import re
import sys

from .config import get_config_dir_path
from .exceptions import DLPlusException


BACKEND_ARCHIVE_REGEXP = re.compile(
    r'^(?P<package>[\w\d._]+)(?:-[\w\d._]+)*\.(?:whl|zip)$')


def parse_backend(backend: str):
    if not backend:
        raise ValueError('empty string')
    if '/' in backend:
        archive, _, module = backend.partition('/')
        if not archive or not module:
            raise ValueError('bad format')
        match = BACKEND_ARCHIVE_REGEXP.fullmatch(archive)
        if not match:
            raise ValueError('bad archive name')
    else:
        match = BACKEND_ARCHIVE_REGEXP.fullmatch(backend)
        if match:
            archive = backend
            module = match.group('package')
        else:
            archive = None
            module = backend
    return archive, module.replace('-', '_')


def init_backend(backend: str):
    try:
        archive, module = parse_backend(backend)
    except ValueError as exc:
        raise DLPlusException(f'failed to parse backend: {exc}')
    if archive:
        archive_path = get_config_dir_path() / 'backends' / archive
        if not archive_path.is_file():
            raise DLPlusException(
                f'failed to initialize backend: {archive_path} does not exist '
                f'or is not a file'
            )
        sys.path.insert(0, str(archive_path))
    from . import ytdl
    ytdl.init(module)


def get_ie_name(ie_cls):
    ie_name = ie_cls.IE_NAME
    if isinstance(ie_name, property):
        return ie_cls().IE_NAME
    return ie_name


def enable_extractors(names):
    from . import ytdl
    from .extractor.machinery import (
        load_all_extractors, load_extractors_by_peqn,
    )
    ytdl_extractor_module = ytdl.import_module('extractor')
    ytdl_extractors = ytdl_extractor_module._ALL_CLASSES
    ytdl_ie_name_cls_map = {
        get_ie_name(ie_cls): ie_cls for ie_cls in ytdl_extractors}
    enabled_extractors = []
    for name in names:
        if name == ':builtins:':
            extractors = ytdl_extractors[:-1]
        elif name == ':plugins:':
            extractors = load_all_extractors()
        elif '/' in name:
            extractors = load_extractors_by_peqn(name)
        else:
            try:
                extractors = [ytdl_ie_name_cls_map[name]]
            except KeyError:
                raise DLPlusException(f'unknown built-in extractor: {name}')
        enabled_extractors.extend(extractors)
    ie_key_cls_map = {
        extractor.ie_key(): extractor for extractor in enabled_extractors}
    ytdl_extractor_module.gen_extractor_classes = lambda: enabled_extractors
    ytdl_extractor_module.get_info_extractor = (
        lambda ie_key: ie_key_cls_map[ie_key])
    importlib.reload(ytdl.import_module('YoutubeDL'))
