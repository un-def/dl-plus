from .backend import BackendCommandGroup
from .base import CommandGroup
from .extractor import ExtractorCommandGroup


class RootCommandGroup(CommandGroup):

    short_description = 'commands'

    commands = (
        BackendCommandGroup,
        ExtractorCommandGroup,
    )
