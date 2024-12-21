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

    fallback_to_config = False
    allow_autodetect = False
