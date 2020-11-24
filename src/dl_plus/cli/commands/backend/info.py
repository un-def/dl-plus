from dl_plus.cli import args
from dl_plus.cli.commands.base import Command
from dl_plus.core import init_backend


class BackendInfoCommand(Command):

    short_description = 'backend information'

    arguments = (
        args.dlp_config,
    )

    def run(self):
        backend_info = init_backend(self.config.backend)
        print(backend_info)
