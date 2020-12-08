import sys
from collections import namedtuple
from pathlib import Path

from dl_plus import ytdl
from dl_plus.config import get_config_home
from dl_plus.exceptions import DLPlusException
from dl_plus.pypi import load_metadata


backends_dir = get_config_home() / 'backends'


BackendInfo = namedtuple(
    'BackendInfo', 'import_name,version,path,is_managed,metadata')


class BackendError(DLPlusException):

    pass


def _is_managed(location: Path) -> bool:
    try:
        location.relative_to(backends_dir)
        return True
    except ValueError:
        return False


def _normalize(string: str) -> str:
    return string.replace('-', '_')


def get_backend_dir(backend: str) -> Path:
    return backends_dir / _normalize(backend)


def parse_backend_string(backend_string: str):
    if '/' in backend_string:
        backend, _, package_name = backend_string.partition('/')
        backend_dir = get_backend_dir(backend)
        if not backend_dir.is_dir():
            raise BackendError(
                f'{backend_dir} does not exist or is not a directory')
    else:
        package_name = backend_string
        backend_dir = get_backend_dir(backend_string)
        if not backend_dir.is_dir():
            backend_dir = None
    return backend_dir, _normalize(package_name)


def init_backend(backend_string: str) -> BackendInfo:
    backend_dir, package_name = parse_backend_string(backend_string)
    if backend_dir:
        sys.path.insert(0, str(backend_dir))
    ytdl.init(package_name)
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
