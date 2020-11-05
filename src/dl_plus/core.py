from . import ytdl


def init_backend(backend: str):
    ytdl.init(backend.replace('-', '_'))


def enable_extractors(names):
    from .extractor.machinery import (
        load_all_extractors, load_extractors_by_peqn,
    )
    enabled_extractors = []
    for name in names:
        if name == ':builtins:':
            extractors = ytdl.get_all_extractors(include_generic=False)
        elif name == ':plugins:':
            extractors = load_all_extractors()
        elif '/' in name:
            extractors = load_extractors_by_peqn(name)
        else:
            extractors = ytdl.get_extractors_by_name(name)
        enabled_extractors.extend(extractors)
    ytdl.patch_extractors(enabled_extractors)
