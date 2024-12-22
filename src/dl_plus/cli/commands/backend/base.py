from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from dl_plus import backend
from dl_plus.backend import (
    Backend, BackendInfo, get_known_backend, init_backend,
    is_project_name_valid,
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
    init_backend: ClassVar[bool]

    project_name: str
    backend_alias: str | None = None  # [section_name] is backends.ini
    backend: Backend | None = None
    backend_info: BackendInfo | None = None

    def init(self):
        super().init()
        project_name_or_backend_alias: str | None = self.args.name
        if project_name_or_backend_alias is None and self.fallback_to_config:
            project_name_or_backend_alias = self.config.backend
        if project_name_or_backend_alias == ConfigValue.Backend.AUTODETECT:
            if not self.allow_autodetect:
                self.die(
                    f'{ConfigValue.Backend.AUTODETECT} is not allowed '
                    f'in {self.name} command'
                )
            self.backend_info = init_backend()
            project_name_or_backend_alias = self.backend_info.alias
        if project_name_or_backend_alias is None:
            self.die('Backend argument is required')
        backend = get_known_backend(project_name_or_backend_alias)
        if backend is not None:
            self.project_name = backend.project_name
            self.backend_alias = project_name_or_backend_alias
            self.backend = backend
        else:
            self.project_name = project_name_or_backend_alias
        if not is_project_name_valid(self.project_name):
            self.die(f'invalid backend name: {self.project_name}')
        if self.backend_info is None and self.init_backend:
            self.backend_info = init_backend(project_name_or_backend_alias)


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
