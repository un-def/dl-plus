from __future__ import annotations

from typing import Optional

from dl_plus.backend import (
    AutodetectFailed, get_backend_dir, get_known_backend, get_known_backends,
    init_backend,
)
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseUpdateCommand
from dl_plus.config import ConfigValue
from dl_plus.exceptions import DLPlusException

from .base import BackendInstallUninstallUpdateCommandMixin


class BackendUpdateCommand(
    BackendInstallUninstallUpdateCommandMixin, BaseUpdateCommand,
):

    short_description = 'Update backend'

    arguments = (
        Arg(
            'name', nargs='?', metavar='NAME',
            help='Backend plugin name.'
        ),
    )

    project_name: str

    def init(self):
        super().init()
        backend = self.args.name or self.config.backend
        if backend == ConfigValue.Backend.AUTODETECT:
            candidates = tuple(get_known_backends())
        else:
            candidates = (backend,)
        for candidate in candidates:
            if get_backend_dir(candidate).exists():
                self.project_name = candidate
                # installed, managed
                return
        self.project_name = backend
        try:
            backend_info = init_backend(backend)
        except AutodetectFailed:
            raise
        except DLPlusException:
            # not installed, report error later
            return
        if not backend_info.is_managed:
            self.die(f'{backend_info.import_name} is not managed by dl-plus')
        # should not reach here
        self.die('something went wrong')

    def get_project_name(self) -> str:
        return self.project_name

    def get_short_name(self) -> str:
        return self.project_name

    def get_extras(self) -> Optional[list[str]]:
        backend = get_known_backend(self.project_name)
        if backend is not None:
            return backend.extras
        return None
