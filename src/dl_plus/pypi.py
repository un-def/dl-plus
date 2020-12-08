import hashlib
import json
from collections import namedtuple
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

from dl_plus.exceptions import DLPlusException


Wheel = namedtuple('Wheel', 'name,version,metadata,filename,url,sha256')


class PyPIClientError(DLPlusException):

    pass


class RequestError(PyPIClientError):

    pass


class ParseError(PyPIClientError):

    pass


class DownloadError(RequestError):

    def __init__(
        self, project_name: str, version: Optional[str], error: str,
    ) -> None:
        if version:
            message = f'{project_name} {version}: {error}'
        else:
            message = f'{project_name}: {error}'
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


def load_metadata(backend_dir: Path) -> Metadata:
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
            with urlopen(url) as response:
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
            raise DownloadError(project_name, version, error) from exc
        try:
            release = next(filter(self._is_wheel_release, metadata.urls))
        except StopIteration:
            raise DownloadError(project_name, version, 'no wheel distribution')
        return Wheel(
            name=metadata.name,
            version=metadata.version,
            metadata=metadata,
            filename=release['filename'],
            url=release['url'],
            sha256=release['digests']['sha256'],
        )

    def download_file(self, url: str, sha256: Optional[str] = None) -> BytesIO:
        try:
            with urlopen(url) as response:
                buffer = BytesIO(response.read())
        except OSError as exc:
            raise DownloadError(f'{url}: {exc}') from exc
        if sha256:
            digest = hashlib.sha256(buffer.getvalue())
            hexdigest = digest.hexdigest()
            if hexdigest != sha256:
                raise DownloadError(
                    f'{url}: sha256 mismatch: expected {sha256}, '
                    f'got {hexdigest}'
                )
        return buffer
