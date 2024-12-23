from __future__ import annotations

import shutil
import sys
from argparse import Namespace
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import (
    TYPE_CHECKING, ClassVar, Dict, List, NoReturn, Optional, Sequence, Tuple,
    Type, Union,
)

from dl_plus.config import Config, ConfigError, get_config_path
from dl_plus.exceptions import DLPlusException
from dl_plus.pypi import PyPIClient, Wheel, WheelInstaller, load_metadata


if TYPE_CHECKING:
    from dl_plus.cli.args import Arg, ArgGroup, ExclusiveArgGroup
    from dl_plus.pypi import Metadata


CommandOrGroup = Union['Command', 'CommandGroup']


class _CommandBase:
    name: ClassVar[str]
    short_description: ClassVar[Optional[str]] = None
    long_description: ClassVar[Optional[str]] = None
    arguments: ClassVar[
        Tuple[Union[Arg, ArgGroup, ExclusiveArgGroup], ...]] = ()

    parent: ClassVar[Optional[Type[CommandGroup]]] = None

    _parents: ClassVar[Tuple[Type[CommandGroup], ...]]

    def __init_subclass__(cls):
        dct = cls.__dict__
        if 'name' not in dct:
            setattr(cls, 'name', dct['__module__'].rpartition('.')[-1])
        long_description = dct.get('long_description')
        if long_description:
            long_description = dedent(long_description).rstrip() + '\n'
            setattr(cls, 'long_description', long_description)

    @classmethod
    def get_parents(
        cls, *, include_root: bool = True,
    ) -> Tuple[Type[CommandGroup], ...]:
        if '_parents' not in cls.__dict__:
            parents = []
            parent = cls.parent
            assert parent
            while parent:
                parents.append(parent)
                parent = parent.parent
            cls._parents = tuple(reversed(parents))
        if include_root:
            return cls._parents
        return cls._parents[1:]

    def get_command_path(self, *, include_command: bool = True) -> List[str]:
        path = [parent.name for parent in self.get_parents(include_root=False)]
        if include_command:
            path.append(self.name)
        return path


class Command(_CommandBase):
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args
        self.init()

    def init(self) -> None:
        pass

    def run(self) -> None:
        raise NotImplementedError

    @cached_property
    def config_path(self) -> Optional[Path]:
        try:
            return get_config_path(getattr(self.args, 'dlp_config', None))
        except ConfigError:
            return None

    @cached_property
    def config(self) -> Config:
        config = Config()
        config_file: Union[Path, bool, None]
        if getattr(self.args, 'no_dlp_config', False):
            config_file = False
        else:
            config_file = self.config_path
        config.load(config_file)
        return config

    def die(self, message: str) -> NoReturn:
        raise CommandError(message)

    print = print

    def confirm(self, message: str) -> bool:
        try:
            assume_yes = self.args.assume_yes
        except AttributeError:
            assume_yes = None
        if assume_yes:
            return True
        prompt = f'{message} [Y/n]'
        if sys.stdin.isatty():
            return input(f'{prompt} ').lower() in ['y', 'yes']
        self.print(prompt)
        if assume_yes is None:
            self.print('Non-interactive mode, assuming no')
            return False
        self.die(
            'non-interactive mode, use `--assume-yes` for automatic '
            'confirmation'
        )


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


class BaseInstallUpdateCommand(Command):
    client: PyPIClient
    wheel_installer: WheelInstaller

    def get_package_dir(self) -> Path:
        raise NotImplementedError

    def get_short_name(self) -> str:
        """Return short name used for logging, command examples, etc."""
        raise NotImplementedError

    def get_extras(self) -> Optional[Iterable[str]]:
        return None

    def init(self) -> None:
        self.client = PyPIClient()
        self.wheel_installer = WheelInstaller()

    def load_installed_metadata(self, package_dir: Path) -> Optional[Metadata]:
        if not package_dir.exists():
            return None
        return load_metadata(package_dir)


class BaseInstallCommand(BaseInstallUpdateCommand):

    def get_project_name_version_tuple(self) -> Tuple[str, Optional[str]]:
        raise NotImplementedError

    def get_force_flag(self) -> bool:
        return False

    def run(self):
        name, version = self.get_project_name_version_tuple()
        wheel = self.client.fetch_wheel_info(name, version)
        self.print(f'Found remote version: {wheel.name} {wheel.version}')

        package_dir = self.get_package_dir()
        installed_metadata = self.load_installed_metadata(package_dir)
        if not installed_metadata:
            self.install(wheel, package_dir)
            return

        self.print(
            f'Found installed version: {installed_metadata.name} '
            f'{installed_metadata.version}'
        )
        is_latest_installed = installed_metadata.version == wheel.version

        if not version:
            short_name = self.get_short_name()
            command_prefix = ' '.join(
                self.get_command_path(include_command=False))
            self.print(f'{short_name} is already installed')
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
            if not self.get_force_flag():
                self.print('Use `--force` to reinstall')
                return
            self.print('Forcing installation')

        self.install(wheel, package_dir)

    def install(self, wheel: Wheel, package_dir: Path) -> None:
        self.print('Installing')
        self.print(f'Using {self.wheel_installer.identifier} installer')
        self.wheel_installer.install(wheel, package_dir, self.get_extras())
        self.print('Installed')


class BaseUpdateCommand(BaseInstallUpdateCommand):

    def get_project_name(self) -> str:
        raise NotImplementedError

    def run(self):
        name = self.get_project_name()
        wheel = self.client.fetch_wheel_info(name)
        self.print(f'Found remote version: {wheel.name} {wheel.version}')

        package_dir = self.get_package_dir()
        installed_metadata = self.load_installed_metadata(package_dir)
        if not installed_metadata:
            command_prefix = ' '.join(
                self.get_command_path(include_command=False))
            short_name = self.get_short_name()
            self.die(
                f'{short_name} is not installed, use '
                f'`{command_prefix} install {short_name} [VERSION]` to install'
            )

        self.print(
            f'Found installed version: {installed_metadata.name} '
            f'{installed_metadata.version}'
        )
        if installed_metadata.version == wheel.version:
            self.print('The latest version is already installed')
            return

        self.update(wheel, package_dir)

    def update(self, wheel: Wheel, package_dir: Path) -> None:
        self.print('Updating')
        self.print(f'Using {self.wheel_installer.identifier} installer')
        self.wheel_installer.install(wheel, package_dir, self.get_extras())
        self.print('Updated')


class BaseUninstallCommand(Command):

    def get_package_dir(self) -> Path:
        raise NotImplementedError

    def get_short_name(self) -> str:
        """Return short name used for logging, command examples, etc."""
        raise NotImplementedError

    def run(self):
        package_dir = self.get_package_dir()
        short_name = self.get_short_name()
        if not package_dir.exists():
            self.die(f'{short_name} is not installed')
        if self.confirm(f'Uninstall {short_name}?'):
            self.uninstall(package_dir)
        else:
            self.print('Aborted')

    def uninstall(self, package_dir: Path) -> None:
        shutil.rmtree(package_dir)
        self.print('Unistalled')
