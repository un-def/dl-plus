from __future__ import annotations

from typing import Optional, Tuple

from dl_plus.backend import get_known_backend
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

    def get_project_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        return (self.args.name, self.args.version)

    def get_short_name(self) -> str:
        return self.args.name

    def get_extras(self) -> Optional[list[str]]:
        backend = get_known_backend(self.args.name)
        if backend is not None:
            return backend.extras
        return None

    def get_force_flag(self) -> bool:
        return self.args.force
