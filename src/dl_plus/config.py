import itertools
import os
import shlex
from configparser import ConfigParser
from pathlib import Path
from typing import List, Optional, Union

from .exceptions import DLPlusException


DEFAULT_CONFIG = """
[main]
backend = youtube_dl

[extractors.enable]
:builtins:
:plugins:
generic
"""


class ConfigError(DLPlusException):

    pass


_config_home: Optional[Path] = None


def get_config_home() -> Path:
    global _config_home
    if _config_home:
        return _config_home
    path_from_env = os.getenv('DL_PLUS_HOME')
    if path_from_env:
        _config_home = Path(path_from_env).resolve()
        return _config_home
    if os.name == 'nt':
        app_data = os.getenv('AppData')
        if app_data:
            parent = Path(app_data)
        else:
            parent = Path.home() / 'AppData' / 'Roaming'
    else:
        xdg_config_home = os.getenv('XDG_CONFIG_HOME')
        if xdg_config_home:
            parent = Path(xdg_config_home)
        else:
            parent = Path.home() / '.config'
    _config_home = (parent / 'dl-plus').resolve()
    return _config_home


def get_config_path(path: Union[Path, str, None] = None) -> Optional[Path]:
    is_default_path = False
    if not path:
        path = os.getenv('DL_PLUS_CONFIG')
        if not path:
            path = get_config_home() / 'config.ini'
            is_default_path = True
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()
    if path.is_file():
        return path
    if is_default_path:
        return None
    raise ConfigError(f'failed to get config path: {path} is not a file')


class _Config(ConfigParser):

    def __init__(self) -> None:
        super().__init__(
            allow_no_value=True,
            delimiters=('=',),
            comment_prefixes=('#', ';'),
            inline_comment_prefixes=None,
            strict=True,
            empty_lines_in_values=False,
            default_section=None,
            interpolation=None,
        )


class Option:

    __slots__ = ('section', 'option')

    def __init__(self, section: str, option: str) -> None:
        self.section = section
        self.option = option

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.get(self.section, self.option)


class Config(_Config):

    _UPDATE_SECTIONS = ('main',)
    _REPLACE_SECTIONS = ('extractors.enable', 'backend-options')

    def __init__(self) -> None:
        super().__init__()
        self.read_string(DEFAULT_CONFIG)

    def load(self, path: Union[Path, str, None] = None) -> None:
        _path = get_config_path(path)
        if not _path:
            return
        config = _Config()
        try:
            with open(_path) as fobj:
                config.read_file(fobj)
        except (OSError, ValueError) as exc:
            raise ConfigError(f'failed to load config: {exc}') from exc
        for section in self._UPDATE_SECTIONS:
            self._load_section(section, config, replace=False)
        for section in self._REPLACE_SECTIONS:
            self._load_section(section, config, replace=True)

    def _load_section(self, name: str, config: _Config, replace: bool) -> None:
        if not config.has_section(name):
            return
        if not self.has_section(name):
            self.add_section(name)
        section = self[name]
        if replace:
            section.clear()
        section.update(config[name])

    def get_backend_options(self) -> Optional[List[str]]:
        if 'backend-options' not in self:
            return None
        return list(itertools.chain.from_iterable(
            map(shlex.split, self.options('backend-options'))))

    backend = Option('main', 'backend')
