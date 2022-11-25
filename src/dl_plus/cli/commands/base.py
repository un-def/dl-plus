from __future__ import annotations

import os
import shutil
import zipfile
from argparse import Namespace
from pathlib import Path
from textwrap import dedent
from typing import ClassVar, Dict, List, Optional, Sequence, Tuple, Type, Union

from dl_plus.cli.args import Arg
from dl_plus.cli.args import dlp_config as dlp_config_arg
from dl_plus.config import Config
from dl_plus.exceptions import DLPlusException
from dl_plus.pypi import PyPIClient, Wheel, load_metadata, save_metadata


CommandOrGroup = Union['Command', 'CommandGroup']


class _CommandBase:
    name: ClassVar[str]
    short_description: ClassVar[Optional[str]] = None
    long_description: ClassVar[Optional[str]] = None

    parent: ClassVar[Optional[Type[CommandGroup]]] = None

    def __init_subclass__(cls):
        dct = cls.__dict__
        if 'name' not in dct:
            setattr(cls, 'name', dct['__module__'].rpartition('.')[-1])
        long_description = dct.get('long_description')
        if long_description:
            long_description = dedent(long_description).rstrip() + '\n'
            setattr(cls, 'long_description', long_description)

    def get_command_path(self) -> List[str]:
        path: List[str] = [self.name]
        assert self.parent
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return path[-2::-1]


class Command(_CommandBase):
    arguments: ClassVar[Tuple[Arg, ...]] = ()

    config: Optional[Config] = None
    args: Namespace

    def __init__(self, args: Namespace) -> None:
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

    print = print


class CommandGroup(_CommandBase):
    commands: ClassVar[Tuple[Type[CommandOrGroup], ...]] = ()

    _commands: ClassVar[Dict[str, Type[CommandOrGroup]]]

    def __init_subclass__(cls):
        super().__init_subclass__()
        _commands: Dict[str, Type[CommandOrGroup]] = {}
        for command_or_group in cls.commands:
            assert not command_or_group.parent
            command_or_group.parent = cls
            _commands[command_or_group.name] = command_or_group
        cls._commands = _commands

    @classmethod
    def get_command(cls, command_path: Sequence[str]) -> Type[Command]:
        path_len = len(command_path)
        assert path_len
        group = cls
        for index, name in enumerate(command_path, 1):
            command_or_group = group._commands[name]
            if index == path_len:
                assert issubclass(command_or_group, Command)
                return command_or_group
            assert issubclass(command_or_group, CommandGroup)
            group = command_or_group
        raise AssertionError('the last path item must be a Command')


class CommandError(DLPlusException):

    pass


class BaseInstallCommand(Command):
    client: PyPIClient

    def get_output_dir(self, wheel: Wheel) -> Path:
        raise NotImplementedError

    def get_project_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        raise NotImplementedError

    def get_short_name(self) -> str:
        """Return short name used for logging, command examples, etc."""
        raise NotImplementedError

    def get_force_flag(self) -> bool:
        return False

    def init(self):
        self.client = PyPIClient()

    def run(self):
        name, version = self.get_project_name_version_tuple()
        wheel = self.client.fetch_wheel_info(name, version)
        self.print(f'Found remote version: {wheel.name} {wheel.version}')

        output_dir = self.get_output_dir(wheel)
        installed_metadata = None
        if output_dir.exists():
            installed_metadata = load_metadata(output_dir)

        if not installed_metadata:
            self.install(wheel, output_dir)
            return

        self.print(
            f'Found installed version: {installed_metadata.name} '
            f'{installed_metadata.version}'
        )
        is_latest_installed = installed_metadata.version == wheel.version

        if not version:
            short_name = self.get_short_name()
            command_prefix = ' '.join(self.get_command_path()[:-1])
            self.print(f'{short_name} already installed')
            if not is_latest_installed:
                self.print(
                    f'Use `{command_prefix} update {short_name}` '
                    f'to update to the latest version'
                )
            self.print(
                f'Use `{command_prefix} install {short_name} VERSION` '
                f'to install a specific version'
            )
            return

        if is_latest_installed:
            self.print('The same version is already installed')
            if not self.args.force:
                self.print('Use `--force` to reinstall')
                return
            self.print('Forcing installation')

        self.install(wheel, output_dir)

    def install(self, wheel: Wheel, output_dir: Path):
        self.print('Installing')
        if output_dir.exists():
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        with self.client.download_file(wheel.url, wheel.sha256) as fobj:
            with zipfile.ZipFile(fobj) as zfobj:
                zfobj.extractall(output_dir)
        save_metadata(output_dir, wheel.metadata)
        self.print('Done')
