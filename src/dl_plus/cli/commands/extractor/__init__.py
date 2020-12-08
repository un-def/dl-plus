from dl_plus.cli.commands.base import CommandGroup

from .install import ExtractorInstallCommand


class ExtractorCommandGroup(CommandGroup):

    short_description = 'Extractors management commands'

    commands = (
        ExtractorInstallCommand,
    )
