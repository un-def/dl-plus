import re
from typing import Optional, Union

from dl_plus.const import PLUGINS_PACKAGE
from dl_plus.utils import NOTSET, NotSet


PLUGIN_IMPORT_PATH_PREFIX = f'{PLUGINS_PACKAGE}.'
PART_REGEX = re.compile(r'^[a-z0-9]+$')
PEQN_REGEX = re.compile(
    r'^(?P<ns>[a-z0-9]+)/(?P<plugin>[a-z0-9]+)(?::(?P<name>[a-z0-9]+))?$')


def _check_part(part: str, part_name: str) -> None:
    if not part:
        raise ValueError(f'empty {part_name} part')
    if not PART_REGEX.fullmatch(part):
        raise ValueError(f'bad {part_name} part: {part}')


def _escape_import_part(part: str) -> str:
    try:
        if part[0].isdigit():
            return '_' + part
    except IndexError:
        pass
    return part


def _unescape_import_part(part: str) -> str:
    try:
        if part[0] == '_':
            return part[1:]
    except IndexError:
        pass
    return part


class PEQN:
    """
    Pluggable Extractor Qualified Name
    """

    def __init__(
        self, ns: str, plugin: str, name: Optional[str] = None,
    ) -> None:
        _check_part(ns, 'ns')
        _check_part(plugin, 'plugin')
        if name is not None:
            _check_part(name, 'name')
        self._ns = ns
        self._plugin = plugin
        self._name = name

    @classmethod
    def from_plugin_import_path(cls, path: str) -> 'PEQN':
        try:
            if not path.startswith(PLUGIN_IMPORT_PATH_PREFIX):
                raise ValueError('not in plugins package')
            parts = path[len(PLUGIN_IMPORT_PATH_PREFIX):].split('.')
            if len(parts) < 2:
                raise ValueError('not enough parts')
            elif len(parts) > 2:
                raise ValueError('too many parts')
            ns = _unescape_import_part(parts[0])
            plugin = _unescape_import_part(parts[1])
            return cls(ns, plugin)
        except ValueError as exc:
            raise ValueError(f'bad plugin import path: {path}: {exc}')

    @classmethod
    def from_string(cls, peqn: str) -> 'PEQN':
        match = PEQN_REGEX.fullmatch(peqn)
        if not match:
            raise ValueError(f'bad PEQN: {peqn}')
        return cls(**match.groupdict())

    def copy(
        self,
        ns: Union[str, NotSet] = NOTSET,
        plugin: Union[str, NotSet] = NOTSET,
        name: Union[str, None, NotSet] = NOTSET,
    ) -> 'PEQN':
        if ns is NOTSET:
            ns = self._ns
        if plugin is NOTSET:
            plugin = self._plugin
        if name is NOTSET:
            name = self._name
        return self.__class__(ns, plugin, name)

    def __str__(self) -> str:
        if self._name:
            return f'{self._ns}/{self._plugin}:{self._name}'
        return f'{self._ns}/{self._plugin}'

    @property
    def ns(self) -> str:
        return self._ns

    @property
    def plugin(self) -> str:
        return self._plugin

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def plugin_import_path(self) -> str:
        ns = _escape_import_part(self._ns)
        plugin = _escape_import_part(self._plugin)
        return f'{PLUGINS_PACKAGE}.{ns}.{plugin}'
