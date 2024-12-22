from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import Command

from .base import BackendCommandMixin


class BackendInfoCommand(BackendCommandMixin, Command):

    short_description = 'Show backend information'

    arguments = (
        Arg(
            'name', nargs='?', metavar='NAME',
            help='Backend name.'
        ),
    )

    fallback_to_config = True
    allow_autodetect = True
    init_backend = True

    def run(self):
        backend_info = self.backend_info
        assert backend_info is not None
        metadata = backend_info.metadata
        if metadata:
            self.print('project name:', metadata.name)
            self.print('project version:', metadata.version)
        self.print('import name:', backend_info.import_name)
        self.print('version:', backend_info.version)
        self.print('path:', str(backend_info.path))
        self.print('managed:', 'yes' if backend_info.is_managed else 'no')
