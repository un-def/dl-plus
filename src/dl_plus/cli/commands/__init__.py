from dl_plus.cli.command import CommandGroup

from .backend import BackendCommandGroup


class RootCommandGroup(CommandGroup):

    short_description = 'commands'

    commands = (
        BackendCommandGroup,
    )
