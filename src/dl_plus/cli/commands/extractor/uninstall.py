from dl_plus.cli.args import Arg, assume_yes_arg
from dl_plus.cli.commands.base import BaseUninstallCommand

from .base import ExtractorInstallUninstallUpdateCommandMixin


class ExtractorUninstallCommand(
    ExtractorInstallUninstallUpdateCommandMixin, BaseUninstallCommand,
):

    short_description = 'Uninstall extractor plugin'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Extractor plugin name.'
        ),
        assume_yes_arg,
    )
