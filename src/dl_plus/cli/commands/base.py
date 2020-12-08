import os
import shutil
import zipfile
from functools import reduce
from pathlib import Path
from textwrap import dedent
from typing import Optional, Tuple

from dl_plus.cli.args import dlp_config as dlp_config_arg
from dl_plus.config import Config
from dl_plus.exceptions import DLPlusException
from dl_plus.pypi import PyPIClient, Wheel, load_metadata, save_metadata


class _CommandBase(object):

    def __init_subclass__(cls):
        dct = cls.__dict__
        if 'name' not in dct:
            setattr(cls, 'name', dct['__module__'].rpartition('.')[-1])
        long_description = dct.get('long_description')
        if long_description:
            long_description = dedent(long_description).rstrip() + '\n'
            setattr(cls, 'long_description', long_description)


class Command(_CommandBase):

    name = None
    short_description = None
    long_description = None
    arguments = ()

    config = None

    def __init__(self, args) -> None:
        self.args = args
        if dlp_config_arg in self.arguments:
            config = Config()
            if not args.no_dlp_config:
                config.load(args.dlp_config)
            self.config = config
        self.init()

    def init(self) -> None:
        pass

    def run(self) -> None:
        raise NotImplementedError


class CommandGroup(_CommandBase):

    name = None
    short_description = None
    long_description = None
    commands = ()

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._commands = {cmd.name: cmd for cmd in cls.commands}

    @classmethod
    def get_command(cls, command_path):
        return reduce(lambda c, p: c._commands[p], command_path, cls)


class CommandError(DLPlusException):

    pass


class BaseInstallCommand(Command):

    def get_output_dir(self, wheel: Wheel) -> Path:
        raise NotImplementedError

    def get_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        raise NotImplementedError

    def get_force_flag(self) -> bool:
        return False

    def run(self):
        client = PyPIClient()
        name, version = self.get_name_version_tuple()
        wheel = client.fetch_wheel_info(name, version)
        print(f'Found remote version: {wheel.name} {wheel.version}')
        output_dir = self.get_output_dir(wheel)
        if output_dir.exists():
            installed_metadata = load_metadata(output_dir)
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
            shutil.rmtree(output_dir)
        print('Installing')
        os.makedirs(output_dir)
        with client.download_file(wheel.url, wheel.sha256) as fobj:
            with zipfile.ZipFile(fobj) as zfobj:
                zfobj.extractall(output_dir)
        save_metadata(output_dir, wheel.metadata)
        print('Done')
