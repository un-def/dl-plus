from dl_plus.backend import init_backend
from dl_plus.cli import args
from dl_plus.cli.commands.base import Command


class BackendInfoCommand(Command):

    short_description = 'backend information'

    arguments = (
        args.dlp_config,
        args.backend,
    )

    def run(self):
        backend = self.args.backend or self.config.backend
        backend_info = init_backend(backend)
        print(backend_info)
