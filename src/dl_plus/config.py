import os
from configparser import ConfigParser
from pathlib import Path
from typing import Union

from .exceptions import DLPlusException


DEFAULT_CONFIG = """
[main]
ytdl-backend = youtube-dl

[extractors.enable]
:builtins:
:plugins:
generic
"""


class ConfigError(DLPlusException):

    pass


def get_config_dir_default_path() -> Path:
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
    return parent / 'dl-plus'


class Config(ConfigParser):

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
        self.read_string(DEFAULT_CONFIG)

    def load(self, path: Union[Path, str, None] = None) -> None:
        if not path:
            path = get_config_dir_default_path() / 'config.ini'
            if not path.is_file():
                return
        else:
            if isinstance(path, str):
                path = Path(path)
            if not path.is_file():
                raise ConfigError(
                    f'failed to load config: {path} is not a file')
        try:
            with open(path) as fobj:
                self.read_file(fobj)
        except OSError as exc:
            raise ConfigError(f'failed to load config: {exc}') from exc
