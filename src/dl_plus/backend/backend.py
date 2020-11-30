import json
import os
import shutil
import sys
import zipfile
from collections import namedtuple
from pathlib import Path
from typing import Optional

from dl_plus import ytdl
from dl_plus.config import get_config_dir_path
from dl_plus.exceptions import DLPlusException
from dl_plus.pypi import Metadata, PyPIClient, Wheel


backends_dir = get_config_dir_path() / 'backends'

client = PyPIClient()

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


def parse_backend_string(backend_string: str):
    if '/' in backend_string:
        rel_location, _, package_name = backend_string.partition('/')
        backend_dir = backends_dir / rel_location
        if not backend_dir.is_dir():
            raise BackendError(
                f'{backend_dir} does not exist or is not a directory')
    else:
        package_name = backend_string
        backend_dir = backends_dir / _normalize(backend_string)
        if not backend_dir.is_dir():
            backend_dir = None
    return backend_dir, _normalize(package_name)


def save_metadata(backend_dir: Path, metadata: Metadata) -> None:
    with open(backend_dir / 'metadata.json', 'w') as fobj:
        json.dump(metadata, fobj)


def load_metadata(backend_dir: Path) -> Metadata:
    try:
        with open(backend_dir / 'metadata.json') as fobj:
            return Metadata(json.load(fobj))
    except OSError:
        return None


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


def download_backend(
    project_name: str, version: Optional[str] = None,
) -> Wheel:
    wheel = client.download_wheel(project_name, version)
    with wheel.file:
        backend_dir = backends_dir / _normalize(wheel.name)
        if backend_dir.exists():
            shutil.rmtree(backend_dir)
        os.makedirs(backend_dir)
        save_metadata(backend_dir, wheel.metadata)
        with zipfile.ZipFile(wheel.file) as zfobj:
            zfobj.extractall(backend_dir)
    return wheel
