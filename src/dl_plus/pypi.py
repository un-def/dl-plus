import hashlib
import json
from collections import namedtuple
from io import BytesIO
from typing import Dict, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

from dl_plus.exceptions import DLPlusException


Wheel = namedtuple('Wheel', 'name,version,metadata,filename,file')


class PyPIClientError(DLPlusException):

    pass


class RequestError(PyPIClientError):

    pass


class ParseError(PyPIClientError):

    pass


class DownloadError(RequestError):

    pass


class PyPIClient:

    DEFAULT_JSON_URL = 'https://pypi.org/pypi/{project_name}/json'

    def __init__(self, *, json_url: Optional[str] = None) -> None:
        if json_url is None:
            json_url = self.DEFAULT_JSON_URL
        self._json_url = json_url

    def fetch_json_metadata(self, project_name: str) -> Dict:
        if self._json_url is None:
            raise PyPIClientError('json_url is not set')
        url = self._json_url.format(project_name=project_name)
        try:
            with urlopen(url) as response:
                return json.load(response)
        except (OSError, ValueError) as exc:
            raise RequestError from exc

    def _is_wheel_release(self, release: Dict) -> bool:
        return (
            release['packagetype'] == 'bdist_wheel' and not release['yanked'])

    def download_wheel(
        self, project_name: str, version: Optional[str] = None,
    ) -> Wheel:
        try:
            metadata = self.fetch_json_metadata(project_name)
        except RequestError as exc:
            if isinstance(exc.error, HTTPError) and exc.error.code == 404:
                raise DownloadError(f'{project_name}: not found') from exc
            raise DownloadError(
                f'{project_name}: unexpected error: {exc}') from exc
        if version is None:
            version = metadata['info']['version']
        try:
            releases = metadata['releases'][version]
        except KeyError:
            raise DownloadError(f'{project_name}-{version}: not found')
        try:
            release = next(filter(self._is_wheel_release, releases))
        except StopIteration:
            raise DownloadError(
                f'{project_name}-{version}: no wheel distribution')
        fileobj = self.download_file(
            url=release['url'], sha256=release['digests']['sha256'])
        return Wheel(
            name=metadata['info']['name'],
            version=version,
            metadata=metadata,
            filename=release['filename'],
            file=fileobj,
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
