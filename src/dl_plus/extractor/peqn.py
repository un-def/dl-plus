import re

from dl_plus.const import PLUGINS_PACKAGE
from dl_plus.utils import NOTSET


PLUGIN_IMPORT_PATH_PREFIX = f'{PLUGINS_PACKAGE}.'
PEQN_REGEX = re.compile(
    r'^(?P<ns>[a-z0-9]+)/(?P<plugin>[a-z0-9]+)(?::(?P<name>[a-z0-9]+))?$')


def _escape_part(part):
    if part[0].isdigit():
        return '_' + part
    return part


def _unescape_part(part):
    if part[0] == '_':
        return part[1:]
    return part


class PEQN:
    """
    Pluggable Extractor Qualified Name
    """

    def __init__(self, ns, plugin, name=None):
        self._ns = ns
        self._plugin = plugin
        self._name = name

    @classmethod
    def from_plugin_import_path(cls, path):
        if not path.startswith(PLUGIN_IMPORT_PATH_PREFIX):
            raise ValueError(f'bad plugin import path: {path}')
        parts = path[len(PLUGIN_IMPORT_PATH_PREFIX):].split('.')
        if len(parts) != 2:
            raise ValueError(f'bad plugin import path: {path}')
        ns = _unescape_part(parts[0])
        plugin = _unescape_part(parts[1])
        return cls(ns, plugin)

    @classmethod
    def from_string(cls, peqn):
        match = PEQN_REGEX.fullmatch(peqn)
        if not match:
            raise ValueError(f'bad PEQN: {peqn}')
        return cls(**match.groupdict())

    def copy(self, ns=NOTSET, plugin=NOTSET, name=NOTSET):
        if ns is NOTSET:
            ns = self._ns
        if plugin is NOTSET:
            plugin = self._plugin
        if name is NOTSET:
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
        ns = _escape_part(self._ns)
        plugin = _escape_part(self._plugin)
        return f'{PLUGINS_PACKAGE}.{ns}.{plugin}'
