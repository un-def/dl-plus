import sys
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterable, List, Set, Type

from dl_plus import ytdl
from dl_plus.config import get_config_home
from dl_plus.extractor import machinery
from dl_plus.extractor.peqn import PEQN


if TYPE_CHECKING:
    from .extractor.extractor import Extractor


extractor_plugins_dir = get_config_home() / 'extractors'


def get_extractor_plugin_dir(ns: str, plugin: str) -> Path:
    return extractor_plugins_dir / f'{ns}-{plugin}'


def get_extractors(names: Iterable[str]) -> List[Type['Extractor']]:
    extractors_dict: Dict[Type['Extractor'], bool] = {}
    added_search_paths: Set[str] = set()

    def maybe_add_search_path(path: Path) -> None:
        if not path.is_dir():
            return
        path_str = str(path)
        if path_str not in added_search_paths:
            sys.path.insert(0, path_str)
            added_search_paths.add(path_str)

    for name in names:
        if name == ':builtins:':
            extractors = ytdl.get_all_extractors(include_generic=False)
        elif name == ':plugins:':
            if extractor_plugins_dir.is_dir():
                for path in extractor_plugins_dir.iterdir():
                    maybe_add_search_path(path)
            extractors = machinery.load_all_extractors()
        elif '/' in name:
            peqn = PEQN.from_string(name)
            maybe_add_search_path(get_extractor_plugin_dir(
                peqn.ns, peqn.plugin))
            extractors = machinery.load_extractors_by_peqn(peqn)
        else:
            extractors = ytdl.get_extractors_by_name(name)
        for extractor in extractors:
            if extractor not in extractors_dict:
                extractors_dict[extractor] = True
    return list(extractors_dict.keys())


def enable_extractors(names) -> None:
    extractors = get_extractors(names)
    ytdl.patch_extractors(extractors)
