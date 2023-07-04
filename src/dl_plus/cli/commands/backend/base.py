from __future__ import annotations

from typing import TYPE_CHECKING

from dl_plus import backend


if TYPE_CHECKING:
    from pathlib import Path

    from dl_plus.cli.commands.base import BaseInstallUpdateCommand as _base
    from dl_plus.pypi import Wheel
else:
    _base = object


class BackendInstallUpdateCommandMixin(_base):

    def get_output_dir(self, wheel: Wheel) -> Path:
        return backend.get_backend_dir(wheel.name)
