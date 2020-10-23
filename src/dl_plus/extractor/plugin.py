from functools import partial
from typing import Callable, Dict, List, Optional, Type, Union, cast, overload

from dl_plus.exceptions import DLPlusException

from .extractor import Extractor
from .peqn import PEQN


EXTRACTOR_PEQN_ATTR = '_dl_plus_peqn'


ExtractorType = Type[Extractor]
ExportDecoratorType = Callable[[ExtractorType], ExtractorType]


class ExtractorPluginError(DLPlusException):

    pass


class ExtractorPlugin:

    def __init__(self, import_path: str) -> None:
        try:
            self._base_peqn = PEQN.from_plugin_import_path(import_path)
        except ValueError as exc:
            raise ExtractorPluginError(exc)
        self._extractors: Dict[Optional[str], ExtractorType] = {}

    @overload
    def export(self, extractor_cls_or_name: ExtractorType) -> ExtractorType:
        ...

    @overload
    def export(
        self, extractor_cls_or_name: str,
    ) -> ExportDecoratorType:
        ...

    def export(
        self, extractor_cls_or_name: Union[ExtractorType, str],
    ) -> Union[ExtractorType, ExportDecoratorType]:
        if isinstance(extractor_cls_or_name, str):
            return partial(self._export, name=extractor_cls_or_name)
        return self._export(extractor_cls_or_name, None)

    def _export(
        self, extractor_cls: ExtractorType, name: Optional[str],
    ) -> ExtractorType:
        if not issubclass(extractor_cls, Extractor):
            raise ExtractorPluginError(
                f'Extractor subclass expected, got: {extractor_cls!r}')
        if EXTRACTOR_PEQN_ATTR in extractor_cls.__dict__:   # type: ignore
            peqn = cast(
                PEQN,
                extractor_cls.__dict__[EXTRACTOR_PEQN_ATTR],   # type: ignore
            )
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
        setattr(extractor_cls, EXTRACTOR_PEQN_ATTR, peqn)
        extractor_cls.IE_NAME = str(peqn)
        self._extractors[name] = extractor_cls
        return extractor_cls

    def get_extractor(self, name: Optional[str] = None) -> ExtractorType:
        return self._extractors[name]

    def get_all_extractors(self) -> List[ExtractorType]:
        return list(self._extractors.values())
