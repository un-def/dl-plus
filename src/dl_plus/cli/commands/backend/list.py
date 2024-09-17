from __future__ import annotations

from dl_plus.backend import get_backends_dir
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import Command
from dl_plus.pypi import load_metadata


class BackendListCommand(Command):

    short_description = 'list installed backends'

    arguments = (
        Arg(
            '-s', '--short', action='store_true',
            help='Print only backend names.'
        ),
    )

    def run(self):
        backends_dir = get_backends_dir()
        if not backends_dir.exists():
            return
        name: str
        version: str | None
        short = self.args.short
        for backend_dir in sorted(backends_dir.iterdir()):
            if metadata := load_metadata(backend_dir):
                name = metadata.name
                version = metadata.version
            else:
                name = backend_dir.name.replace('_', '-')
                version = None
            if short or version is None:
                self.print(name)
            else:
                self.print(f'{name} {version}')
