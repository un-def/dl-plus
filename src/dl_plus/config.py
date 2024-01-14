import enum
import itertools
import os
import shlex
from configparser import ConfigParser
from pathlib import Path
from types import MappingProxyType
from typing import List, Mapping, Optional, Union

from dl_plus import deprecated

from .exceptions import DLPlusException


_IS_WIN = os.name == 'nt'


class _StrEnum(str, enum.Enum):
    # enum.StrEnum is available since Python 3.11

    def __str__(self) -> str:
        return self.value


class _EnvironVariable:
    __slots__ = ('names',)

    def __init__(self, *names: str) -> None:
        self.names = names

    def __get__(self, instance: Optional['_Environ'], owner) -> Optional[str]:
        if instance is None:
            return None
        for name in self.names:
            value = instance.get(name)
            if value is not None:
                return value
        return None


class _Environ:
    CONFIG_HOME = _EnvironVariable('DL_PLUS_CONFIG_HOME', 'DL_PLUS_HOME')
    DATA_HOME = _EnvironVariable('DL_PLUS_DATA_HOME', 'DL_PLUS_HOME')
    CONFIG = _EnvironVariable('DL_PLUS_CONFIG')
    BACKEND = _EnvironVariable('DL_PLUS_BACKEND')

    def __init__(self, environ: Mapping[str, str]) -> None:
        self._environ = MappingProxyType(environ)

    def __getitem__(self, __key: str, /) -> str:
        return self._environ[__key]

    def __contains__(self, __key: str, /) -> bool:
        return __key in self._environ

    def get(self, __key: str, /) -> Optional[str]:
        return self._environ.get(__key)


_environ = _Environ(os.environ)


class Section(_StrEnum):
    MAIN = 'main'
    EXTRACTORS = 'extractors'
    BACKEND_OPTIONS = 'backend-options'

    DEPRECATED_EXTRACTORS = 'extractors.enable'


class Option(_StrEnum):
    BACKEND = 'backend'


class ConfigValue:

    class Backend(_StrEnum):
        AUTODETECT = ':autodetect:'

    class Extractor(_StrEnum):
        BUILTINS = ':builtins:'
        PLUGINS = ':plugins:'
        GENERIC = 'generic'


DEFAULT_CONFIG = f"""
[{Section.MAIN}]
{Option.BACKEND} = {ConfigValue.Backend.AUTODETECT}

[{Section.EXTRACTORS}]
{ConfigValue.Extractor.PLUGINS}
{ConfigValue.Extractor.BUILTINS}
{ConfigValue.Extractor.GENERIC}
"""


class ConfigError(DLPlusException):

    pass


def _get_win_app_data() -> Path:
    if app_data := _environ.get('AppData'):
        return Path(app_data)
    return Path.home() / 'AppData' / 'Roaming'


_config_home: Optional[Path] = None


def get_config_home() -> Path:
    global _config_home
    if _config_home:
        return _config_home
    path_from_env = _environ.CONFIG_HOME
    if path_from_env:
        _config_home = Path(path_from_env).resolve()
        return _config_home
    if _IS_WIN:
        parent = _get_win_app_data()
    else:
        xdg_config_home = _environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            parent = Path(xdg_config_home)
        else:
            parent = Path.home() / '.config'
    _config_home = (parent / 'dl-plus').resolve()
    return _config_home


def get_config_path(path: Union[Path, str, None] = None) -> Optional[Path]:
    is_default_path = False
    if not path:
        path = _environ.CONFIG
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


class _ConfigOptionProxy:

    __slots__ = ('section', 'option')

    def __init__(self, section: str, option: str) -> None:
        self.section = section
        self.option = option

    def __get__(self, instance: 'Config', owner):
        if instance is None:
            return self
        return instance.get(self.section, self.option)

    def __set__(self, instance: 'Config', value: str):
        instance.set(self.section, self.option, value)


class Config(_Config):

    _UPDATE_SECTIONS = (Section.MAIN,)
    _REPLACE_SECTIONS = (Section.EXTRACTORS, Section.BACKEND_OPTIONS)

    def __init__(self) -> None:
        super().__init__()
        self.read_string(DEFAULT_CONFIG)

    def load(
        self, path: Union[Path, str, bool, None] = None, environ: bool = True,
    ) -> None:
        if path is True:
            path = None
        if path is not False:
            self.load_from_file(path)
        if environ:
            self.load_from_environ()

    def load_from_file(self, path: Union[Path, str, None] = None) -> None:
        _path = get_config_path(path)
        if not _path:
            return
        config = _Config()
        try:
            with open(_path) as fobj:
                config.read_file(fobj)
        except (OSError, ValueError) as exc:
            raise ConfigError(f'failed to load config: {exc}') from exc
        self._process_deprecated_extractors_section(config)
        for section in self._UPDATE_SECTIONS:
            self._update_section(section, config, replace=False)
        for section in self._REPLACE_SECTIONS:
            self._update_section(section, config, replace=True)

    def _process_deprecated_extractors_section(self, config: _Config) -> None:
        try:
            deprecated_extractors = config[Section.DEPRECATED_EXTRACTORS]
        except KeyError:
            return
        # deprecated in 0.7
        deprecated.warn(
            'deprecated config section name: '
            'rename [extractors.enable] to [extractors]'
        )
        if not config.has_section(Section.EXTRACTORS):
            config[Section.EXTRACTORS] = deprecated_extractors

    def load_from_environ(self) -> None:
        if backend := _environ.BACKEND:
            self.backend = backend

    def _update_section(
        self, name: str, config: _Config, replace: bool,
    ) -> None:
        if not config.has_section(name):
            return
        if not self.has_section(name):
            self.add_section(name)
        section = self[name]
        if replace:
            section.clear()
        section.update(config[name])

    backend = _ConfigOptionProxy(Section.MAIN, Option.BACKEND)

    @property
    def extractors(self) -> List[str]:
        return self.options(Section.EXTRACTORS)

    @property
    def backend_options(self) -> Optional[List[str]]:
        if not self.has_section(Section.BACKEND_OPTIONS):
            return None
        return list(itertools.chain.from_iterable(
            map(shlex.split, self.options(Section.BACKEND_OPTIONS))))


_data_home: Optional[Path] = None


def get_data_home() -> Path:
    global _data_home
    if _data_home:
        return _data_home
    path_from_env = _environ.DATA_HOME
    if path_from_env:
        _data_home = Path(path_from_env).resolve()
        return _data_home
    if _IS_WIN:
        parent = _get_win_app_data()
    else:
        xdg_data_home = _environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            parent = Path(xdg_data_home)
        else:
            parent = Path.home() / '.local' / 'share'
    _data_home = (parent / 'dl-plus').resolve()

    # deprecated in 0.7
    if not _IS_WIN and not _data_home.exists():
        use_config_home_as_data_home = False
        config_home = get_config_home()
        if (config_home / 'backends').exists():
            deprecated.warn(
                "deprecated backends location: move 'backends' directory "
                f'from {config_home} to {_data_home}'
            )
            use_config_home_as_data_home = True
        if (config_home / 'extractors').exists():
            deprecated.warn(
                "deprecated extractor plugins location: move 'extractors' "
                f'directory from {config_home} to {_data_home}'
            )
            use_config_home_as_data_home = True
        if use_config_home_as_data_home:
            _data_home = config_home

    return _data_home
