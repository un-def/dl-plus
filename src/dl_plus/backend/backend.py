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
from dl_plus.pypi import PyPIClient, Wheel


backends_dir = get_config_dir_path() / 'backends'

client = PyPIClient()

BackendInfo = namedtuple(
    'BackendInfo', 'package_name,version,location,managed')


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
        location = backends_dir / rel_location
        if not location.is_dir():
            raise BackendError(f'{location} does not exist or is a directory')
    else:
        package_name = backend_string
        location = backends_dir / _normalize(backend_string)
        if not location.is_dir():
            location = None
    return location, _normalize(package_name)


def init_backend(backend_string: str) -> BackendInfo:
    location, package_name = parse_backend_string(backend_string)
    if location:
        sys.path.insert(0, str(location))
    ytdl.init(package_name)
    ytdl_module = ytdl.get_ytdl_module()
    location = Path(ytdl_module.__path__[0])
    return BackendInfo(
        package_name=ytdl_module.__name__,
        version=ytdl.import_from('version', '__version__'),
        location=location,
        managed=_is_managed(location),
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
        with open(backend_dir / 'metadata.json', 'w') as fobj:
            json.dump(wheel.metadata, fobj)
            with zipfile.ZipFile(wheel.file) as zfobj:
                zfobj.extractall(backend_dir)
    return wheel
