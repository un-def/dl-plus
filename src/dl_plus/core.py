from typing import TYPE_CHECKING, Dict, Iterable, List, Type

from . import ytdl
from .extractor import machinery


if TYPE_CHECKING:
    from .extractor.extractor import Extractor


def init_backend(backend: str) -> None:
    ytdl.init(backend.replace('-', '_'))


def get_extractors(names: Iterable[str]) -> List[Type['Extractor']]:
    extractors_dict: Dict[Type['Extractor'], bool] = {}
    for name in names:
        if name == ':builtins:':
            extractors = ytdl.get_all_extractors(include_generic=False)
        elif name == ':plugins:':
            extractors = machinery.load_all_extractors()
        elif '/' in name:
            extractors = machinery.load_extractors_by_peqn(name)
        else:
            extractors = ytdl.get_extractors_by_name(name)
        for extractor in extractors:
            if extractor not in extractors_dict:
                extractors_dict[extractor] = True
    return list(extractors_dict.keys())


def enable_extractors(names) -> None:
    extractors = get_extractors(names)
    ytdl.patch_extractors(extractors)
