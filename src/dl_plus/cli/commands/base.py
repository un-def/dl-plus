from functools import reduce
from textwrap import dedent

from dl_plus.cli.args import dlp_config as dlp_config_arg
from dl_plus.config import Config


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
