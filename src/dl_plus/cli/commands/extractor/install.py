import re
from pathlib import Path
from typing import Optional, Tuple

from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import BaseInstallCommand, CommandError
from dl_plus.core import get_extractor_plugin_dir
from dl_plus.pypi import Wheel


PLUGIN_NAME_REGEX = re.compile(
    r'^(?:dl-plus-extractor-)?(?P<ns>[a-z0-9]+)[/-](?P<plugin>[a-z0-9]+)$')


class ExtractorInstallCommand(BaseInstallCommand):

    short_description = 'Install extractor plugin'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Extractor plugin name.'
        ),
        Arg(
            'version', nargs='?', metavar='VERSION',
            help='Extractor plugin version. Default is latest.',
        ),
        Arg(
            '-f', '--force', action='store_true',
            help='Force installation if the same version is already installed.'
        ),
    )

    ns: str
    plugin: str

    def init(self):
        plugin_name = self.args.name
        match = PLUGIN_NAME_REGEX.fullmatch(plugin_name)
        if not match:
            raise CommandError(f'Invalid extractor plugin name: {plugin_name}')
        self.ns, self.plugin = match.groups()

    def get_output_dir(self, wheel: Wheel) -> Path:
        return get_extractor_plugin_dir(self.ns, self.plugin)

    def get_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        return (
            f'dl-plus-extractor-{self.ns}-{self.plugin}', self.args.version)

    def get_force_flag(self) -> bool:
        return self.args.force
