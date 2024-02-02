from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, NamedTuple, Optional

from dl_plus import ytdl
from dl_plus.config import ConfigValue, _Config, get_config_home, get_data_home
from dl_plus.exceptions import DLPlusException
from dl_plus.pypi import load_metadata


if TYPE_CHECKING:
    from .pypi import Metadata


def _normalize(string: str) -> str:
    return string.replace('-', '_')


class Backend(NamedTuple):
    # a name of the project ("distribution" in PyPA terms)
    # *.dist-info/METADATA->Name
    project_name: str
    # a name of the root package directory
    # *.dist-info/top_level.txt
    import_name: str
    # a name of the the executable script
    # *.dist-info/entry_points.txt->console_scripts).
    executable_name: str


DEFAULT_BACKENDS_CONFIG = """
[yt-dlp]
project-name = yt-dlp
import-name = yt_dlp
executable-name = yt-dlp

[youtube-dl-nightly]
project-name = youtube-dl-nightly
import-name = youtube_dl
executable-name = youtube-dl

[youtube-dl]
project-name = youtube_dl
import-name = youtube_dl
executable-name = youtube-dl

[youtube-dlc]
project-name = youtube-dlc
import-name = youtube_dlc
executable-name = youtube-dlc
"""


def parse_backends_config(content: str) -> dict[str, Backend]:
    config = _Config()
    config.read_string(content)
    backends = {}
    for alias in config.sections():
        backends[_normalize(alias)] = Backend(**{
            _normalize(field): value
            for field, value in config[alias].items()
        })
    return backends


_known_backends: dict[str, Backend] | None = None


def get_backends_config_path() -> Optional[Path]:
    path = get_config_home() / 'backends.ini'
    if not path.is_file():
        return None
    return path


def get_known_backends() -> dict[str, Backend]:
    global _known_backends
    if _known_backends is not None:
        return _known_backends
    _known_backends = parse_backends_config(DEFAULT_BACKENDS_CONFIG)
    config_path = get_backends_config_path()
    if config_path:
        with open(config_path) as fobj:
            _known_backends.update(parse_backends_config(fobj.read()))
    return _known_backends


class BackendInfo(NamedTuple):
    import_name: str
    version: str
    path: Path
    is_managed: bool
    metadata: Optional[Metadata]


class BackendError(DLPlusException):

    pass


class AutodetectFailed(BackendError):

    def __init__(self, candidates: Iterable[str]) -> None:
        self._candidates = tuple(candidates)

    def __str__(self) -> str:
        return 'failed to autodetect backend (candidates tested: {})'.format(
            ', '.join(self._candidates))


def _is_managed(location: Path) -> bool:
    try:
        location.relative_to(get_backends_dir())
        return True
    except ValueError:
        return False


def get_backends_dir() -> Path:
    return get_data_home() / 'backends'


def get_backend_dir(backend: str) -> Path:
    return get_backends_dir() / _normalize(backend)


def parse_backend_string(backend_string: str) -> tuple[Path | None, str]:
    # backend_string is one of:
    #   * alias ([section-name] in the backends.ini, e.g., 'yt-dlp');
    #   * 'import_name', e.g., 'youtube_dl';
    #   * 'project-name/import_name', e.g., 'youtube-dl-nightly/youtube_dl'.
    if '/' in backend_string:
        project_name, _, import_name = backend_string.partition('/')
        backend_dir = get_backend_dir(project_name)
        if not backend_dir.is_dir():
            raise BackendError(
                f'{backend_dir} does not exist or is not a directory')
    elif backend := get_known_backends().get(_normalize(backend_string)):
        import_name = backend.import_name
        backend_dir = get_backend_dir(backend.project_name)
        if not backend_dir.is_dir():
            # in case of backends not managed by dl-plus
            backend_dir = None
    else:
        import_name = backend_string
        backend_dir = get_backend_dir(backend_string)
        if not backend_dir.is_dir():
            backend_dir = None
    return backend_dir, _normalize(import_name)


def _init_backend(backend_string: str) -> Path | None:
    backend_dir, package_name = parse_backend_string(backend_string)
    if backend_dir:
        sys.path.insert(0, str(backend_dir))
    ytdl.init(package_name)
    return backend_dir


def _autodetect_backend() -> Path | None:
    candidates = tuple(get_known_backends())
    for candidate in candidates:
        try:
            return _init_backend(candidate)
        except DLPlusException:
            pass
    raise AutodetectFailed(candidates)


def init_backend(backend_string: str) -> BackendInfo:
    if backend_string == ConfigValue.Backend.AUTODETECT:
        backend_dir = _autodetect_backend()
    else:
        backend_dir = _init_backend(backend_string)
    ytdl_module = ytdl.get_ytdl_module()
    path = Path(ytdl_module.__path__[0])
    is_managed = _is_managed(path)
    if is_managed:
        metadata = load_metadata(backend_dir)
    else:
        metadata = None
    return BackendInfo(
        import_name=ytdl_module.__name__,
        version=ytdl.import_from('version', '__version__'),
        path=path,
        is_managed=is_managed,
        metadata=metadata,
    )
