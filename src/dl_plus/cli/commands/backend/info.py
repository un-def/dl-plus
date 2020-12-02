from dl_plus.backend import init_backend
from dl_plus.cli import args
from dl_plus.cli.commands.base import Command


class BackendInfoCommand(Command):

    short_description = 'Show backend information'

    arguments = (
        args.dlp_config,
        args.backend,
    )

    def run(self):
        backend = self.args.backend or self.config.backend
        backend_info = init_backend(backend)
        print('import name:', backend_info.import_name)
        print('version:', backend_info.version)
        print('path:', str(backend_info.path))
        print('managed:', 'yes' if backend_info.is_managed else 'no')
        metadata = backend_info.metadata
        if metadata:
            print('project name:', metadata.name)
            print('project version:', metadata.version)
