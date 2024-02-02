from dl_plus.cli import args as cli_args

from .backend import BackendCommandGroup
from .base import CommandGroup
from .config import ConfigCommandGroup
from .extractor import ExtractorCommandGroup


class RootCommandGroup(CommandGroup):
    short_description = 'commands'

    arguments = (
        cli_args.dlp_config,
    )

    commands = (
        BackendCommandGroup,
        ExtractorCommandGroup,
        ConfigCommandGroup,
    )
