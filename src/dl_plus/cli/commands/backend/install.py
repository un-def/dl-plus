from __future__ import annotations

from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseInstallCommand

from .base import BackendInstallUninstallUpdateCommandMixin


class BackendInstallCommand(
    BackendInstallUninstallUpdateCommandMixin, BaseInstallCommand,
):

    short_description = 'Install backend'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Backend name.'
        ),
        Arg(
            'version', nargs='?', metavar='VERSION',
            help='Backend version. Default is latest.',
        ),
        Arg(
            '-f', '--force', action='store_true',
            help='Force installation if the same version is already installed.'
        ),
    )

    fallback_to_config = False
    allow_autodetect = False

    def get_project_name_version_tuple(self) -> tuple[str, str | None]:
        return (self.project_name, self.args.version)

    def get_extras(self) -> list[str] | None:
        if self.backend is not None:
            return self.backend.extras
        return None

    def get_force_flag(self) -> bool:
        return self.args.force
