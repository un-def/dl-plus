from __future__ import annotations

from dl_plus.backend import init_backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseUpdateCommand

from .base import BackendInstallUpdateCommandMixin


class BackendUpdateCommand(
    BackendInstallUpdateCommandMixin, BaseUpdateCommand,
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
        backend_info = init_backend(self.args.name or self.config.backend)
        if not backend_info.is_managed:
            import_name = backend_info.import_name
            self.die(
                f'{import_name} is not managed by dl-plus, '
                f'use `backend install {import_name}` first to install it'
            )
        self.project_name = backend_info.metadata.name

    def get_project_name(self) -> str:
        return self.project_name

    def get_short_name(self) -> str:
        return self.project_name
