from dl_plus.cli.commands.base import CommandGroup

from .show import ConfigShowCommandGroup


class ConfigCommandGroup(CommandGroup):
    short_description = 'Config commands'

    commands = (
        ConfigShowCommandGroup,
    )
