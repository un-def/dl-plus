from .backend import BackendCommandGroup
from .base import CommandGroup


class RootCommandGroup(CommandGroup):

    short_description = 'commands'

    commands = (
        BackendCommandGroup,
    )
