from __future__ import annotations

import sys

from dl_plus.backend import init_backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import Command
from dl_plus.core import get_extractor_plugins_dir
from dl_plus.extractor.machinery import load_extractors_by_peqn
from dl_plus.pypi import load_metadata


class ExtractorListCommand(Command):

    short_description = 'list installed extractor plugins'

    arguments = (
        Arg(
            '-s', '--short', action='store_true',
            help='Print only plugin names.'
        ),
    )

    def run(self):
        extractor_plugins_dir = get_extractor_plugins_dir()
        if not extractor_plugins_dir.exists():
            return
        plugin: str
        version: str | None = None
        extractors: list[str] | None = None
        short = self.args.short
        if not short:
            init_backend(self.config.backend)
        for extractor_plugin_dir in sorted(extractor_plugins_dir.iterdir()):
            plugin = extractor_plugin_dir.name.replace('-', '/')
            if not short:
                if metadata := load_metadata(extractor_plugin_dir):
                    version = metadata.version
                else:
                    version = None
                sys.path.insert(0, str(extractor_plugin_dir))
                peqns = [ie.IE_NAME for ie in load_extractors_by_peqn(plugin)]
                if len(peqns) == 1 and ':' not in peqns[0]:
                    extractors = None
                else:
                    extractors = [peqn.partition(':')[2] for peqn in peqns]
            if version is None:
                self.print(plugin)
            else:
                self.print(f'{plugin} {version}')
            if extractors:
                for extractor in extractors:
                    self.print(' ', extractor)
