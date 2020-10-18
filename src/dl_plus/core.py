import importlib
import itertools
import os
import os.path
import pkgutil
import re

from .exceptions import UnknownExtractor


__version__ = '0.1.0.dev0'


PLUGINS_PACKAGE = 'dl_plus.extractors'

_NOTSET = object()


def get_ie_name(ie_cls):
    ie_name = ie_cls.IE_NAME
    if isinstance(ie_name, property):
        return ie_cls().IE_NAME
    return ie_name


def discover_extractor_plugins_gen():
    try:
        extractors_package = importlib.import_module(PLUGINS_PACKAGE)
    except ImportError:
        return
    for ns_path in extractors_package.__path__:
        if not os.path.isdir(ns_path):
            continue
        for entry in os.scandir(ns_path):
            if not entry.is_dir():
                continue
            ns = entry.name
            for _, name, _ in pkgutil.iter_modules([entry.path]):
                yield f'{PLUGINS_PACKAGE}.{ns}.{name}'


class PEQN:
    """
    Pluggable Extractor Qualified Name
    """

    PLUGIN_IMPORT_PATH_PREFIX = f'{PLUGINS_PACKAGE}.'
    PEQN_REGEX = re.compile(
        r'^(?P<ns>[a-z0-9]+)/(?P<plugin>[a-z0-9]+)'
        r'(?::(?P<name>[a-z0-9]+))?$'
    )

    def __init__(self, ns, plugin, name=None):
        self._ns = ns
        self._plugin = plugin
        self._name = name

    @classmethod
    def from_plugin_import_path(cls, path):
        if not path.startswith(cls.PLUGIN_IMPORT_PATH_PREFIX):
            raise ValueError(f'bad plugin import path: {path}')
        parts = path[len(cls.PLUGIN_IMPORT_PATH_PREFIX):].split('.')
        if len(parts) != 2:
            raise ValueError(f'bad plugin import path: {path}')
        ns = cls._unescape_part(parts[0])
        plugin = cls._unescape_part(parts[1])
        return cls(ns, plugin)

    @classmethod
    def from_string(cls, peqn):
        match = cls.PEQN_REGEX.fullmatch(peqn)
        if not match:
            raise ValueError(f'bad PEQN: {peqn}')
        return cls(**match.groupdict())

    def copy(self, ns=_NOTSET, plugin=_NOTSET, name=_NOTSET):
        if ns is _NOTSET:
            ns = self._ns
        if plugin is _NOTSET:
            plugin = self._plugin
        if name is _NOTSET:
            name = self._name
        return self.__class__(ns, plugin, name)

    def __str__(self):
        if self._name:
            return f'{self._ns}/{self._plugin}:{self._name}'
        return f'{self._ns}/{self._plugin}'

    @property
    def ns(self):
        return self._ns

    @property
    def plugin(self):
        return self._plugin

    @property
    def name(self):
        return self._name

    @property
    def plugin_import_path(self):
        ns = self._escape_part(self._ns)
        plugin = self._escape_part(self._plugin)
        return f'{PLUGINS_PACKAGE}.{ns}.{plugin}'

    @staticmethod
    def _escape_part(part):
        if part[0].isdigit():
            return '_' + part
        return part

    @staticmethod
    def _unescape_part(part):
        if part[0] == '_':
            return part[1:]
        return part


def load_extractors_from_plugin(plugin_import_path, names=None):
    try:
        plugin_module = importlib.import_module(plugin_import_path)
    except ImportError:
        raise UnknownExtractor(f'cannot import {plugin_import_path}')
    try:
        plugin = plugin_module.plugin
    except AttributeError:
        raise UnknownExtractor(
            f'{plugin_import_path} does not marked as an extractor plugin')
    if names:
        try:
            extractors = list(map(plugin.get_extractor, names))
        except KeyError as exc:
            raise UnknownExtractor(
                f'{plugin_import_path} does not export {exc.args[0]}')
    else:
        extractors = plugin.get_all_extractors()
    return extractors


def enable_extractors(names):
    ytdl_extractor_module = importlib.import_module('youtube_dl.extractor')
    ytdl_extractors = ytdl_extractor_module._ALL_CLASSES
    ytdl_ie_name_cls_map = {
        get_ie_name(ie_cls): ie_cls for ie_cls in ytdl_extractors}
    generic_extractor = ytdl_extractors[-1]
    append_generic_extractor = False
    enabled_extractors = []
    ie_key_cls_map = {}
    for name in names:
        if name == ':builtins:':
            extractors = ytdl_extractors[:-1]
            append_generic_extractor = True
        elif name == ':plugins:':
            extractors = list(itertools.chain.from_iterable(
                map(
                    load_extractors_from_plugin,
                    discover_extractor_plugins_gen()
                )
            ))
        elif '/' in name:
            try:
                peqn = PEQN.from_string(name)
            except ValueError:
                raise UnknownExtractor(f'failed to parse PEQN: {name}')
            if peqn.name:
                names = [peqn.name]
            else:
                names = None
            extractors = load_extractors_from_plugin(
                peqn.plugin_import_path, names)
        else:
            try:
                extractors = [ytdl_ie_name_cls_map[name]]
            except KeyError:
                raise UnknownExtractor(f'unknown built-in extractor: {name}')
        enabled_extractors.extend(extractors)
        ie_key_cls_map.update(
            (ie_cls.ie_key(), ie_cls) for ie_cls in extractors)
    if append_generic_extractor:
        enabled_extractors.append(generic_extractor)
        ie_key_cls_map[generic_extractor.ie_key()] = generic_extractor
    ytdl_extractor_module.gen_extractor_classes = lambda: enabled_extractors
    ytdl_extractor_module.get_info_extractor = (
        lambda ie_key: ie_key_cls_map[ie_key])
    importlib.reload(importlib.import_module('youtube_dl.YoutubeDL'))
