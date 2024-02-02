import io

from dl_plus.backend import (
    DEFAULT_BACKENDS_CONFIG, get_backends_config_path, get_known_backends,
)
from dl_plus.cli.commands.base import Command
from dl_plus.config import _Config


class ConfigShowBackendsCommand(Command):
    short_description = 'Show backends config (backends.ini)'
    long_description = f"""
        {short_description}.

        By default, the user config is shown, that is, the content of
        the user config file.

        If the --default flag is passed, the default config is shown, that is,
        the configuration as if there is no user config.

        If the --merged flag is passed, the result of merging the user config
        with the default config is shown, that is, the resulting configuration
        as it used by dl-plus.
    """

    def run(self):
        if self.args.default:
            self._show_default_config()
        elif self.args.merged:
            self._show_merged_config()
        else:
            self._show_user_config()

    def _show_default_config(self):
        self.print(DEFAULT_BACKENDS_CONFIG.strip())

    def _show_merged_config(self):
        config = _Config()
        for alias, backend in get_known_backends().items():
            config.add_section(alias)
            for field, value in backend._asdict().items():
                config.set(alias, field.replace('_', '-'), value)
        with io.StringIO() as buf:
            config.write(buf)
            self.print(buf.getvalue().strip())

    def _show_user_config(self):
        if config_path := get_backends_config_path():
            print(f'Config file: {config_path}\n')
            with open(config_path) as fobj:
                self.print(fobj.read().strip())
        else:
            print('No config file found')
