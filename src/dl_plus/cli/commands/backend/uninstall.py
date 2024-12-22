from dl_plus.cli.args import Arg, assume_yes_arg
from dl_plus.cli.commands.base import BaseUninstallCommand

from .base import BackendInstallUninstallUpdateCommandMixin


class BackendUninstallCommand(
    BackendInstallUninstallUpdateCommandMixin, BaseUninstallCommand,
):

    short_description = 'Uninstall backend'

    arguments = (
        Arg(
            'name', metavar='NAME',
            help='Backend plugin name.'
        ),
        assume_yes_arg,
    )

    fallback_to_config = False
    allow_autodetect = False
    init_backend = True

    def init(self) -> None:
        super().init()
        package_dir = self.get_package_dir()
        assert self.backend_info is not None
        if not package_dir.exists() and not self.backend_info.is_managed:
            name = self.get_short_name()
            self.die(f'{name} is not managed by dl-plus, unable to uninstall')
