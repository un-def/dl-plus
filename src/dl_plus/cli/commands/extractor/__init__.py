from dl_plus.cli.commands.base import CommandGroup

from .install import ExtractorInstallCommand
from .update import ExtractorUpdateCommand


class ExtractorCommandGroup(CommandGroup):

    short_description = 'Extractors management commands'

    commands = (
        ExtractorInstallCommand,
        ExtractorUpdateCommand,
    )
