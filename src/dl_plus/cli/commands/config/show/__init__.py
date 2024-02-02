from dl_plus.cli.args import Arg, ExclusiveArgGroup
from dl_plus.cli.commands.base import CommandGroup

from .backends import ConfigShowBackendsCommand
from .main import ConfigShowMainCommand


class ConfigShowCommandGroup(CommandGroup):
    short_description = 'Config show commands'

    arguments = (
        ExclusiveArgGroup(
            Arg('--default', action='store_true', help='Show default config.'),
            Arg('--merged', action='store_true', help='Show merged configs.'),
            title='show options',
        ),
    )

    commands = (
        ConfigShowMainCommand,
        ConfigShowBackendsCommand,
    )
