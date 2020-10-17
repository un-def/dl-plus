from functools import partial

from youtube_dl.extractor.common import InfoExtractor

from .core import PEQN
from .exceptions import DLPlusException


class ExtractorPluginError(DLPlusException):

    pass


class Extractor(InfoExtractor):

    @classmethod
    def ie_key(cls):
        return cls.IE_NAME


class ExtractorPlugin:

    EXTRACTOR_PEQN_ATTR = '_dl_plus_peqn'

    def __init__(self, import_path):
        try:
            self._base_peqn = PEQN.from_plugin_import_path(import_path)
        except ValueError as exc:
            raise ExtractorPluginError(exc)
        self._extractors = {}

    def export(self, extractor_cls_or_name, name=None):
        if isinstance(extractor_cls_or_name, str):
            return partial(self.export, name=extractor_cls_or_name)
        extractor_cls = extractor_cls_or_name
        if not issubclass(extractor_cls, Extractor):
            raise ExtractorPluginError(
                f'Extractor subclass expected, got: {extractor_cls!r}')
        if self.EXTRACTOR_PEQN_ATTR in extractor_cls.__dict__:
            peqn = extractor_cls.__dict__[self.EXTRACTOR_PEQN_ATTR]
            raise ExtractorPluginError(
                f'the extractor {extractor_cls!r} is already exported '
                f'as "{peqn}"'
            )
        if name is None:
            if self._extractors:
                raise ExtractorPluginError(
                    'the unnamed extractor must be the only extractor '
                    'in the plugin'
                )
        elif name in self._extractors:
            raise ExtractorPluginError(
                f'the plugin already exports an extractor called "{name}"')
        peqn = self._base_peqn.copy(name=name)
        setattr(extractor_cls, self.EXTRACTOR_PEQN_ATTR, peqn)
        extractor_cls.IE_NAME = str(peqn)
        self._extractors[name] = extractor_cls
        return extractor_cls

    def get_extractor(self, name=None):
        return self._extractors[name]

    def get_all_extractors(self):
        return list(self._extractors.values())
