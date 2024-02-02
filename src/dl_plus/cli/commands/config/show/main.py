import io

from dl_plus.cli.commands.base import Command
from dl_plus.config import DEFAULT_CONFIG


class ConfigShowMainCommand(Command):
    short_description = 'Show main config (config.ini)'
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
        self.print(DEFAULT_CONFIG.strip())

    def _show_merged_config(self):
        with io.StringIO() as buf:
            self.config.write(buf)
            self.print(buf.getvalue().strip())

    def _show_user_config(self):
        if self.config_path:
            print(f'Config file: {self.config_path}\n')
            with open(self.config_path) as fobj:
                self.print(fobj.read().strip())
        else:
            print('No config file found')
