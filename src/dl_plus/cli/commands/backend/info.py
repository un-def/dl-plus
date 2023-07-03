from dl_plus.backend import init_backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import Command


class BackendInfoCommand(Command):

    short_description = 'Show backend information'

    arguments = (
        Arg(
            'name', nargs='?', metavar='NAME',
            help='Backend name.'
        ),
    )

    def run(self):
        backend = self.args.name or self.config.backend
        backend_info = init_backend(backend)
        self.print('import name:', backend_info.import_name)
        self.print('version:', backend_info.version)
        self.print('path:', str(backend_info.path))
        self.print('managed:', 'yes' if backend_info.is_managed else 'no')
        metadata = backend_info.metadata
        if metadata:
            self.print('project name:', metadata.name)
            self.print('project version:', metadata.version)
