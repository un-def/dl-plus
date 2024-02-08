from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import namedtuple
from io import BytesIO
from pathlib import Path
from typing import ClassVar, Dict, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

from dl_plus.exceptions import DLPlusException


_HTTP_TIMEOUT = 30


Wheel = namedtuple('Wheel', 'name,version,metadata,filename,url,sha256')


class PyPIClientError(DLPlusException):

    pass


class RequestError(PyPIClientError):

    pass


class ParseError(PyPIClientError):

    pass


class DownloadError(RequestError):

    def __init__(
        self, error: str,
        project_name: Optional[str] = None, version: Optional[str] = None,
    ) -> None:
        if project_name:
            if version:
                message = f'{project_name} {version}: {error}'
            else:
                message = f'{project_name}: {error}'
        else:
            message = error
        super().__init__(message)


class Metadata(dict):

    @property
    def name(self) -> str:
        return self['info']['name']

    @property
    def version(self) -> str:
        return self['info']['version']

    @property
    def urls(self) -> Dict[str, Dict]:
        return self['urls']


def save_metadata(backend_dir: Path, metadata: Metadata) -> None:
    with open(backend_dir / 'metadata.json', 'w') as fobj:
        json.dump(metadata, fobj)


def load_metadata(backend_dir: Path) -> Optional[Metadata]:
    try:
        with open(backend_dir / 'metadata.json') as fobj:
            return Metadata(json.load(fobj))
    except OSError:
        return None


class PyPIClient:

    JSON_BASE_URL = 'https://pypi.org/pypi'

    def build_json_url(
        self, project_name: str, version: Optional[str] = None,
    ) -> str:
        parts = [self.JSON_BASE_URL, project_name]
        if version:
            parts.append(version)
        parts.append('json')
        return '/'.join(parts)

    def fetch_metadata(
        self, project_name: str, version: Optional[str] = None,
    ) -> Metadata:
        url = self.build_json_url(project_name, version)
        try:
            with urlopen(url, timeout=_HTTP_TIMEOUT) as response:
                return Metadata(json.load(response))
        except (OSError, ValueError) as exc:
            raise RequestError from exc

    def _is_wheel_release(self, release: Dict) -> bool:
        return (
            release['packagetype'] == 'bdist_wheel' and not release['yanked'])

    def fetch_wheel_info(
        self, project_name: str, version: Optional[str] = None,
    ) -> Wheel:
        try:
            metadata = self.fetch_metadata(project_name, version)
        except RequestError as exc:
            if isinstance(exc.error, HTTPError) and exc.error.code == 404:
                error = 'not found'
            else:
                error = 'unexpected error'
            raise DownloadError(error, project_name, version) from exc
        try:
            release = next(filter(self._is_wheel_release, metadata.urls))
        except StopIteration:
            raise DownloadError('no wheel distribution', project_name, version)
        return Wheel(
            name=metadata.name,
            version=metadata.version,
            metadata=metadata,
            filename=release['filename'],
            url=release['url'],
            sha256=release['digests']['sha256'],
        )


def _is_pip_available():
    exit_status = subprocess.call(
        [sys.executable, '-m', 'pip', '--version'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return exit_status == 0


class WheelInstaller:
    identifier: ClassVar[str]

    def __new__(cls) -> 'WheelInstaller':
        if cls is WheelInstaller:
            if _is_pip_available():
                return PipWheelInstaller()
            else:
                return BuiltinWheelInstaller()
        return super().__new__(cls)

    def install(self, wheel: Wheel, output_dir: Path) -> None:
        with tempfile.TemporaryDirectory() as _tmp_dir:
            tmp_dir = Path(_tmp_dir) / output_dir.name
            self._install(wheel, tmp_dir)
            if output_dir.exists():
                shutil.rmtree(output_dir)
            else:
                os.makedirs(output_dir.parent, exist_ok=True)
            shutil.move(tmp_dir, output_dir.parent)
        save_metadata(output_dir, wheel.metadata)

    def _install(self, wheel: Wheel, tmp_dir: Path) -> None:
        raise NotImplementedError


class BuiltinWheelInstaller(WheelInstaller):
    # builtin installer cannot install wheel dependencies
    identifier = 'builtin'

    def _install(self, wheel: Wheel, tmp_dir: Path) -> None:
        with self._download(wheel.url, wheel.sha256) as fobj:
            with zipfile.ZipFile(fobj) as zfobj:
                zfobj.extractall(tmp_dir)

    def _download(self, url: str, sha256: str) -> BytesIO:
        try:
            with urlopen(url, timeout=_HTTP_TIMEOUT) as response:
                buffer = BytesIO(response.read())
        except OSError as exc:
            raise DownloadError(f'{url}: {exc}') from exc
        digest = hashlib.sha256(buffer.getvalue())
        hexdigest = digest.hexdigest()
        if hexdigest != sha256:
            raise DownloadError(
                f'{url}: sha256 mismatch: expected {sha256}, got {hexdigest}')
        return buffer


class PipWheelInstaller(WheelInstaller):
    # pip installer installs wheel dependencies
    identifier = 'pip'

    def _install(self, wheel: Wheel, tmp_dir: Path) -> None:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            '--quiet', '--disable-pip-version-check',
            '--target', str(tmp_dir),
            '--only-binary', ':all:',
            f'{wheel.url}#sha256={wheel.sha256}',
        ])
