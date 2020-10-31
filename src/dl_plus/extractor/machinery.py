import importlib
import itertools
import os
import os.path
import pkgutil

from dl_plus.const import PLUGINS_PACKAGE
from dl_plus.exceptions import DLPlusException

from .peqn import PEQN


class ExtractorLoadError(DLPlusException):

    pass


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


def load_extractors_by_plugin_import_path(plugin_import_path, names=None):
    try:
        plugin_module = importlib.import_module(plugin_import_path)
    except ImportError as exc:
        raise ExtractorLoadError(f'cannot import {plugin_import_path}: {exc}')
    try:
        plugin = plugin_module.plugin
    except AttributeError:
        raise ExtractorLoadError(
            f'{plugin_import_path} does not marked as an extractor plugin')
    if names:
        try:
            extractors = list(map(plugin.get_extractor, names))
        except KeyError as exc:
            raise ExtractorLoadError(
                f'{plugin_import_path} does not contain {exc.args[0]}')
    else:
        extractors = plugin.get_all_extractors()
    return extractors


def load_extractors_by_peqn(peqn):
    if not isinstance(peqn, PEQN):
        try:
            peqn = PEQN.from_string(peqn)
        except ValueError:
            raise ExtractorLoadError(f'failed to parse PEQN: {peqn}')
    if peqn.name:
        names = [peqn.name]
    else:
        names = None
    return load_extractors_by_plugin_import_path(
        peqn.plugin_import_path, names)


def load_all_extractors():
    return list(itertools.chain.from_iterable(
        map(
            load_extractors_by_plugin_import_path,
            discover_extractor_plugins_gen(),
        )
    ))
