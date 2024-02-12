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
        if not PROJECT_NAME_REGEX.fullmatch(project_name):
            self.die(f'Invalid backend name: {project_name}')


class BackendInstallUpdateCommandMixin(BackendCommandMixin):

    def get_output_dir(self, wheel: Wheel) -> Path:
        return backend.get_backend_dir(wheel.name)
