import os
import shutil
import zipfile

from dl_plus import backend
from dl_plus.cli.args import Arg
from dl_plus.cli.commands.base import Command
from dl_plus.pypi import PyPIClient


class BackendInstallCommand(Command):

    short_description = 'Install backend'

    arguments = (
        Arg(
            'name', metavar='NAME', nargs='?', default='youtube_dl',
            help='Backend name. Default is youtube_dl.'
        ),
        Arg(
            'version', nargs='?', metavar='VERSION',
            help='Backend version. Default is latest.',
        ),
        Arg(
            '-f', '--force', action='store_true',
            help='Force installation if the same version is already installed.'
        ),
    )

    def run(self):
        client = PyPIClient()
        wheel = client.fetch_wheel_info(self.args.name, self.args.version)
        print(f'Found remote version: {wheel.name} {wheel.version}')
        backend_dir = backend.get_backend_dir(wheel.name)
        if backend_dir.exists():
            installed_metadata = backend.load_metadata(backend_dir)
            if installed_metadata:
                print(
                    f'Found installed version: {installed_metadata.name} '
                    f'{installed_metadata.version}'
                )
                if installed_metadata.version == wheel.version:
                    print('The same version is already installed')
                    if not self.args.force:
                        print('Nothing to do')
                        return
                    print('Forcing installation')
            shutil.rmtree(backend_dir)
        print('Installing')
        os.makedirs(backend_dir)
        with client.download_file(wheel.url, wheel.sha256) as fobj:
            with zipfile.ZipFile(fobj) as zfobj:
                zfobj.extractall(backend_dir)
        backend.save_metadata(backend_dir, wheel.metadata)
        print('Done')
