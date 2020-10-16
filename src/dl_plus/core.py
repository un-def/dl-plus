import importlib
import itertools
import os
import os.path
import pkgutil
import re

from .exceptions import UnknownExtractor


# PEQN - Pluggable Extractor Qualified Name
PEQN_REGEX = re.compile(
    r'^(?P<ns>[a-z0-9]+)/(?P<plugin>[a-z0-9]+)(?::(?P<extractor>[a-z0-9]+))?$')
PLUGINS_PACKAGE = 'dl_plus.extractors'


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


def parse_peqn(peqn):
    """
    Parse PEQN. Returns a pair:
        * the plugin import path
        * the extractor name or None
    """
    match = PEQN_REGEX.fullmatch(peqn)
    if not match:
        raise UnknownExtractor('bad PEQN')
    ns, plugin, extractor = match.group('ns', 'plugin', 'extractor')
    if ns[0].isdigit():
        ns = '_' + ns
    if plugin[0].isdigit():
        plugin = '_' + plugin
    return f'{PLUGINS_PACKAGE}.{ns}.{plugin}', extractor


def load_extractors_from_plugin(plugin_path, extractors_names=None):
    try:
        module = importlib.import_module(plugin_path)
    except ImportError:
        raise UnknownExtractor(f'cannot import {plugin_path}')
    try:
        extractor = module.EXTRACTOR
    except AttributeError:
        raise UnknownExtractor(
            f'{plugin_path} does not export any extractor')
    if isinstance(extractor, dict):
        if extractors_names:
            try:
                extractors = [extractor[name] for name in extractors_names]
            except KeyError as exc:
                raise UnknownExtractor(
                    f'{plugin_path} does not export {exc.args[0]}')
        else:
            extractors = list(extractor.values())
    elif extractors_names:
        raise UnknownExtractor(f'{plugin_path} has only one extractor')
    else:
        extractors = [extractor]
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
            plugin_path, extractor_name = parse_peqn(name)
            if extractor_name:
                extractors_names = [extractor_name]
            else:
                extractors_names = None
            extractors = load_extractors_from_plugin(
                plugin_path, extractors_names)
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
