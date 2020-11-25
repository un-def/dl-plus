from dl_plus.backend import download_backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import Command


class BackendInstallCommand(Command):

    short_description = 'install backend'

    arguments = (
        Arg('name', metavar='NAME', nargs='?', default='youtube-dl'),
        Arg('version', nargs='?', metavar='VERSION'),
    )

    def run(self):
        wheel = download_backend(self.args.name, self.args.version)
        print(wheel.name)
        print(wheel.metadata['info'])
