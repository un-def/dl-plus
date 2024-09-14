from __future__ import annotations

import re
from typing import TYPE_CHECKING

from dl_plus import backend


if TYPE_CHECKING:
    from pathlib import Path

    from dl_plus.cli.commands.base import BaseInstallUpdateCommand as _base
    from dl_plus.pypi import Wheel
else:
    _base = object


PROJECT_NAME_REGEX = re.compile(r'^[A-Za-z0-9_-]+$')


class BackendCommandMixin(_base):

    def init(self):
        super().init()
        project_name = self.args.name
        if project_name and not PROJECT_NAME_REGEX.fullmatch(project_name):
            self.die(f'Invalid backend name: {project_name}')


class BackendInstallUninstallUpdateCommandMixin(BackendCommandMixin):

    def get_package_dir(self, wheel: Wheel | None = None) -> Path:
        if wheel is None:
            name = self.args.name
        else:
            name = wheel.name
        return backend.get_backend_dir(name)
