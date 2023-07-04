from dl_plus.cli.commands.base import CommandGroup

from .info import BackendInfoCommand
from .install import BackendInstallCommand
from .update import BackendUpdateCommand


class BackendCommandGroup(CommandGroup):

    short_description = 'Backend management commands'

    commands = (
        BackendInfoCommand,
        BackendInstallCommand,
        BackendUpdateCommand,
    )
