from __future__ import annotations

from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseUpdateCommand

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

    fallback_to_config = True
    allow_autodetect = True
    init_backend = True

    def init(self) -> None:
        super().init()
        assert self.backend_info is not None
        if not self.backend_info.is_managed:
            name = self.get_short_name()
            self.die(
                f'{name} is not managed by dl-plus, '
                f'install it first with `backend install {name}`'
            )

    def get_project_name(self) -> str:
        return self.project_name

    def get_extras(self) -> list[str] | None:
        if self.backend is not None:
            return self.backend.extras
        return None
