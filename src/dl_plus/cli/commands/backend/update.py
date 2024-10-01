from __future__ import annotations

from dl_plus.backend import get_backend_dir, init_backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseUpdateCommand
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
        self.project_name = backend
        backend_dir = get_backend_dir(backend)
        if backend_dir.exists():
            # installed, managed
            return
        try:
            backend_info = init_backend(backend)
        except DLPlusException:
            # not installed, report error later
            return
        if not backend_info.is_managed:
            # installed, not managed
            self.die(
                f'{backend} is not managed by dl-plus, '
                f'use `backend install {backend}` first to install it'
            )
        # should not reach here
        self.die('something went wrong')

    def get_project_name(self) -> str:
        return self.project_name

    def get_short_name(self) -> str:
        return self.project_name
