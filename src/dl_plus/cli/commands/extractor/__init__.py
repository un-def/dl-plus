from dl_plus.cli.commands.base import CommandGroup

from .install import ExtractorInstallCommand
from .list import ExtractorListCommand
from .uninstall import ExtractorUninstallCommand
from .update import ExtractorUpdateCommand


class ExtractorCommandGroup(CommandGroup):

    short_description = 'Extractors management commands'

    commands = (
        ExtractorListCommand,
        ExtractorInstallCommand,
        ExtractorUninstallCommand,
        ExtractorUpdateCommand,
    )
