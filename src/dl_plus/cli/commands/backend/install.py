from pathlib import Path
from typing import Optional, Tuple

from dl_plus import backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseInstallCommand
from dl_plus.pypi import Wheel


class BackendInstallCommand(BaseInstallCommand):

    short_description = 'Install backend'

    arguments = (
        Arg(
            'name', metavar='NAME', nargs='?', default='youtube_dl',
            help='Backend name. Default is youtube_dl.'
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

    def get_output_dir(self, wheel: Wheel) -> Path:
        return backend.get_backend_dir(wheel.name)

    def get_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        return (self.args.name, self.args.version)

    def get_force_flag(self) -> bool:
        return self.args.force
