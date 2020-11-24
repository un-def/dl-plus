import argparse
from functools import reduce
from textwrap import dedent


_COMMAND_DEST = 'command'


class _CommandBase(object):

    def __init_subclass__(cls):
        dct = cls.__dict__
        if 'name' not in dct:
            setattr(cls, 'name', dct['__module__'].rpartition('.')[-1])
        long_description = dct.get('long_description')
        if long_description:
            long_description = dedent(long_description).rstrip() + '\n',
            setattr(cls, 'long_description', long_description)


class Command(_CommandBase):

    name = None
    short_description = None
    long_description = None
    args = ()

    def run(self, args: argparse.Namespace) -> None:
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


class CommandNamespace(argparse.Namespace):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__[_COMMAND_DEST] = []

    def _get_command(self):
        return self.__dict__[_COMMAND_DEST]

    def _set_command(self, value):
        self.__dict__[_COMMAND_DEST].append(value)

    command = property(_get_command, _set_command)


class Arg(object):

    __slots__ = ['args', 'kwargs']

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser):
        return parser.add_argument(*self.args, **self.kwargs)


class CommandArgParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            'formatter_class', argparse.RawDescriptionHelpFormatter)
        super().__init__(*args, **kwargs)

    def add_command_args(self, command):
        for arg in command.args:
            arg.add_to_parser(self)

    def add_command_group(self, command_group):
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
                command_parser.add_command_args(command_or_group)

    def add_command_group_subparsers(self, *args, **kwargs):
        kwargs.setdefault('dest', _COMMAND_DEST)
        kwargs.setdefault('metavar', 'COMMAND')
        kwargs.setdefault('parser_class', self.__class__)
        # Python 3.6 — add_subparsers(required=...) is not supported
        subparsers = self.add_subparsers(*args, **kwargs)
        subparsers.required = True
        return subparsers
