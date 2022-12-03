from __future__ import annotations

from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseUpdateCommand

from .base import ExtractorInstallUpdateCommandMixin


class ExtractorUpdateCommand(
    ExtractorInstallUpdateCommandMixin, BaseUpdateCommand,
):

    short_description = 'Update extractor plugin'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Extractor plugin name.'
        ),
    )

    def get_project_name(self) -> str:
        return self.project_name
