from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from dl_plus import backend
from dl_plus.backend import (
    AutodetectFailed, Backend, get_backend_dir, get_known_backend,
    get_known_backends, is_project_name_valid,
)
from dl_plus.config import ConfigValue


if TYPE_CHECKING:
    from pathlib import Path

    from dl_plus.cli.commands.base import BaseInstallUpdateCommand as _base
else:
    _base = object


class BackendCommandMixin(_base):
    fallback_to_config: ClassVar[bool]
    allow_autodetect: ClassVar[bool]

    project_name: str
    backend_alias: str | None   # [section_name] is backends.ini
    backend: Backend | None

    def init(self):
        super().init()
        project_name_or_backend_alias: str | None = self.args.name
        if project_name_or_backend_alias is None and self.fallback_to_config:
            project_name_or_backend_alias = self.config.backend
        if project_name_or_backend_alias == ConfigValue.Backend.AUTODETECT:
            project_name_or_backend_alias = self._autodetect_backend()
        if project_name_or_backend_alias is None:
            self.die('Backend argument is required')
        backend = get_known_backend(project_name_or_backend_alias)
        if backend is not None:
            self.project_name = backend.project_name
            self.backend_alias = project_name_or_backend_alias
            self.backend = backend
        else:
            self.project_name = project_name_or_backend_alias
            self.backend_alias = None
            self.backend = None
        if not is_project_name_valid(self.project_name):
            self.die(f'invalid backend name: {self.project_name}')

    def _autodetect_backend(self) -> str:
        if not self.allow_autodetect:
            self.die(
                f'{ConfigValue.Backend.AUTODETECT} is not allowed '
                f'in {self.name} command'
            )
        candidates = tuple(get_known_backends())
        for candidate in candidates:
            if get_backend_dir(candidate).exists():
                return candidate
        raise AutodetectFailed(candidates)


class BackendInstallUninstallUpdateCommandMixin(BackendCommandMixin):

    def get_package_dir(self) -> Path:
        if self.backend_alias is not None:
            _backend = self.backend_alias
        else:
            _backend = self.project_name
        return backend.get_backend_dir(_backend)

    def get_short_name(self) -> str:
        short_name = self.backend_alias
        if short_name is None:
            short_name = self.project_name
        return short_name
