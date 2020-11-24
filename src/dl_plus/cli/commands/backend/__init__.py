from dl_plus.cli.commands.base import CommandGroup

from .info import BackendInfoCommand


class BackendCommandGroup(CommandGroup):

    short_description = 'backend commands'

    commands = (
        BackendInfoCommand,
    )
