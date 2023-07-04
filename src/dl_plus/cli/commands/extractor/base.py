from __future__ import annotations

import re
from typing import TYPE_CHECKING

from dl_plus.core import get_extractor_plugin_dir


if TYPE_CHECKING:
    from pathlib import Path

    from dl_plus.cli.commands.base import BaseInstallUpdateCommand as _base
    from dl_plus.pypi import Wheel
else:
    _base = object


PLUGIN_NAME_REGEX = re.compile(
    r'^(?:dl-plus-extractor-)?(?P<ns>[a-z0-9]+)[/-](?P<plugin>[a-z0-9]+)$')


class ExtractorInstallUpdateCommandMixin(_base):
    ns: str
    plugin: str
    project_name: str

    def init(self):
        super().init()
        plugin_name = self.args.name
        match = PLUGIN_NAME_REGEX.fullmatch(plugin_name)
        if not match:
            self.die(f'Invalid extractor plugin name: {plugin_name}')
        self.ns, self.plugin = match.groups()
        self.project_name = f'dl-plus-extractor-{self.ns}-{self.plugin}'

    def get_output_dir(self, wheel: Wheel) -> Path:
        return get_extractor_plugin_dir(self.ns, self.plugin)

    def get_short_name(self) -> str:
        return self.args.name
