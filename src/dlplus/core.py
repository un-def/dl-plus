import importlib

from .exceptions import UnknownExtractor, YoutubeDLNotFound


def import_youtube_dl():
    try:
        return importlib.import_module('youtube_dl')
    except ImportError as exc:
        raise YoutubeDLNotFound(exc) from exc


def _get_ie_name(ie_cls):
    ie_name = ie_cls.IE_NAME
    if isinstance(ie_name, property):
        return ie_cls().IE_NAME
    return ie_name


def filter_builtin_ies(ie_names):
    extractor_module = importlib.import_module('youtube_dl.extractor')
    ie_dict = {
        _get_ie_name(ie): ie
        for ie in extractor_module._ALL_CLASSES
    }
    try:
        filtered = [ie_dict[ie_name] for ie_name in ie_names]
    except KeyError as exc:
        raise UnknownExtractor(f'Unknown extractor: {exc.args[0]}')
    extractor_module.gen_extractor_classes = lambda: filtered
    importlib.reload(importlib.import_module('youtube_dl.YoutubeDL'))
