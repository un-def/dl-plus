from dl_plus.cli.args import Arg, assume_yes_arg
from dl_plus.cli.commands.base import BaseUninstallCommand

from .base import BackendInstallUninstallUpdateCommandMixin


class BackendUninstallCommand(
    BackendInstallUninstallUpdateCommandMixin, BaseUninstallCommand,
):

    short_description = 'Uninstall backend'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Backend plugin name.'
        ),
        assume_yes_arg,
    )

    def get_short_name(self) -> str:
        return self.args.name
