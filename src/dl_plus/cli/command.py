from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, List, Type

from .commands import RootCommandGroup
from .commands.base import CommandGroup


if TYPE_CHECKING:
    from .commands.base import Command


__all__ = ['run_command']


_COMMAND_DEST = 'command'


class CommandNamespace(argparse.Namespace):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__[_COMMAND_DEST] = []

    def _get_command(self):
        return self.__dict__[_COMMAND_DEST]

    def _set_command(self, value):
        if isinstance(value, list):
            self.__dict__[_COMMAND_DEST].extend(value)
        else:
            assert isinstance(value, str), repr(str)
            self.__dict__[_COMMAND_DEST].append(value)

    command = property(_get_command, _set_command)


class CommandArgParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            'formatter_class', argparse.RawDescriptionHelpFormatter)
        super().__init__(*args, **kwargs)

    def parse_known_args(self, args=None, namespace=None):
        if namespace is None:
            namespace = CommandNamespace()
        return super().parse_known_args(args, namespace)

    def add_command_arguments(self, command: Type[Command]):
        for parent in command.get_parents():
            for arg in parent.arguments:
                arg.add_to_parser(self)
        for arg in command.arguments:
            arg.add_to_parser(self)

    def add_command_group(self, command_group: Type[CommandGroup]):
        command_group_subparsers = self.add_command_group_subparsers(
            title=command_group.short_description)
        for command_or_group in command_group.commands:
            description = (
                command_or_group.long_description
                or command_or_group.short_description
            )
            command_parser = command_group_subparsers.add_parser(
                command_or_group.name,
                help=command_or_group.short_description,
                description=description,
            )
            if issubclass(command_or_group, CommandGroup):
                command_parser.add_command_group(command_or_group)
            else:
                command_parser.add_command_arguments(command_or_group)

    def add_command_group_subparsers(self, *args, **kwargs):
        kwargs.setdefault('dest', _COMMAND_DEST)
        kwargs.setdefault('metavar', 'COMMAND')
        kwargs.setdefault('required', True)
        subparsers = self.add_subparsers(*args, **kwargs)
        return subparsers


def run_command(prog: str, cmd_arg: str, args: List[str]) -> None:
    parser = CommandArgParser(prog=f'{prog} {cmd_arg}')
    parser.add_argument(
        cmd_arg, action='store_true', required=True, help=argparse.SUPPRESS)
    parser.add_command_group(RootCommandGroup)
    parsed_args = parser.parse_args(args)
    command_cls = RootCommandGroup.get_command(parsed_args.command)
    command_cls(parsed_args).run()
