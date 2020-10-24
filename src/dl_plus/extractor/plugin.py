from functools import partial
from typing import Callable, Dict, List, Optional, Type, Union, cast, overload

from dl_plus.exceptions import DLPlusException

from .extractor import Extractor
from .peqn import PEQN


EXTRACTOR_PEQN_ATTR = '_dl_plus_peqn'


ExtractorType = Type[Extractor]
RegisterDecoratorType = Callable[[ExtractorType], ExtractorType]


class ExtractorPluginError(DLPlusException):

    pass


class ExtractorPlugin:
    """
    An extractor plugin object

    :param str import_path: An import path of the plugin module.
        The :code:`__name__` module attribute should be used as a value:

        .. code-block::

            # dl_plus/extractors/somenamespace/someplugin.py
            plugin = ExtractorPlugin(__name__)

    :raises ExtractorPluginError: if the passed import path does not conform to
        plugin structure rules.
    """

    def __init__(self, import_path: str) -> None:
        try:
            self._base_peqn = PEQN.from_plugin_import_path(import_path)
        except ValueError as exc:
            raise ExtractorPluginError(exc)
        self._extractors: Dict[Optional[str], ExtractorType] = {}

    @overload
    def register(self, __extractor_cls: ExtractorType) -> ExtractorType:
        ...

    @overload
    def register(
        self, __extractor_cls: ExtractorType, *, name: str,
    ) -> ExtractorType:
        ...

    @overload
    def register(self, __name: str) -> RegisterDecoratorType:
        ...

    def register(
        self, __extractor_cls_or_name: Union[ExtractorType, str, None] = None,
        *, name: Optional[str] = None,
    ) -> Union[ExtractorType, RegisterDecoratorType]:
        """
        Register the given :class:`dl_plus.extractor.Extractor` class
        in the plugin's registry

        This method can be used as:

            * a regular method:

                .. code-block::

                    plugin.register(UnnamedExtractor)

                .. code-block::

                    plugin.register(NamedExtractor, name='clip')

            * a decorator:

                .. code-block::

                    @plugin.register
                    class UnnamedExtractor(Extractor):
                        ...

                .. code-block::

                    @plugin.register('clip')
                    class NamedExtractor(Extractor):
                        ...

        :raises ExtractorPluginError:
        """
        # A special case for `@plugin.extractor()` syntax
        if __extractor_cls_or_name is None:
            return partial(self._register, name=name)
        if isinstance(__extractor_cls_or_name, str):
            return partial(self._register, name=__extractor_cls_or_name)
        return self._register(__extractor_cls_or_name, name)

    def _register(
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
                f'the extractor {extractor_cls!r} is already registered '
                f'as "{peqn}"'
            )
        if name and name in self._extractors:
            raise ExtractorPluginError(
                f'the plugin already contains an extractor called "{name}"')
        if name and None in self._extractors or not name and self._extractors:
            raise ExtractorPluginError(
                'the unnamed extractor must be the only extractor '
                'in the plugin'
            )
        peqn = self._base_peqn.copy(name=name)
        setattr(extractor_cls, EXTRACTOR_PEQN_ATTR, peqn)
        extractor_cls.IE_NAME = str(peqn)
        self._extractors[name or None] = extractor_cls
        return extractor_cls

    def get_extractor(self, name: Optional[str] = None) -> ExtractorType:
        """
        Get the extractor class from the plugin's registry

        :param str name: (optional) The name of the extractor. The same value
            that was used to register the extractor (see :meth:`register`).
            Omit this parameter to get the unnamed extractor.
        :rtype: dl_plus.extractor.Extractor
        :raises KeyError: if no extractor found
        """
        return self._extractors[name]

    def get_all_extractors(self) -> List[ExtractorType]:
        """
        Get all extractors from the plugin's registry

        :rtype: list[dl_plus.extractor.Extractor]
        """
        return list(self._extractors.values())
