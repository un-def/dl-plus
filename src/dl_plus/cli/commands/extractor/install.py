from __future__ import annotations

from typing import Optional, Tuple

from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseInstallCommand

from .base import ExtractorInstallUpdateCommandMixin


class ExtractorInstallCommand(
    ExtractorInstallUpdateCommandMixin, BaseInstallCommand,
):

    short_description = 'Install extractor plugin'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Extractor plugin name.'
        ),
        Arg(
            'version', nargs='?', metavar='VERSION',
            help='Extractor plugin version. Default is latest.',
        ),
        Arg(
            '-f', '--force', action='store_true',
            help='Force installation if the same version is already installed.'
        ),
    )

    def get_project_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        return (self.project_name, self.args.version)

    def get_force_flag(self) -> bool:
        return self.args.force
