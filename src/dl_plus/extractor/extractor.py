import re
from typing import Match, Optional

from dl_plus import deprecated, ytdl


InfoExtractor = ytdl.import_from('extractor.common', 'InfoExtractor')
ExtractorError = ytdl.import_from('utils', 'ExtractorError')


class Extractor(InfoExtractor):
    """
    A base class for pluggable extractors
    """

    # Set by `ExtractorPlugin.register`, do not override.
    IE_NAME: Optional[str] = None

    @classmethod
    def ie_key(cls):
        return cls.IE_NAME

    if not hasattr(InfoExtractor, '_match_valid_url'):

        @classmethod
        def _match_valid_url(cls, url: str) -> Optional[Match[str]]:
            """Emulates yt-dlp's method with the same name."""
            valid_url = cls._VALID_URL
            if valid_url is False:
                return None
            if not isinstance(valid_url, str):
                # multiple _VALID_URL is not (yet?) supported
                raise ExtractorError(
                    f'_VALID_URL: string expected, got: {valid_url!r}')
            # a copy/paste from youtube-dl
            if '_VALID_URL_RE' not in cls.__dict__:
                cls._VALID_URL_RE = re.compile(valid_url)
            return cls._VALID_URL_RE.match(url)

    if (
            ytdl.get_ytdl_module_name() == 'yt_dlp'
            and ytdl.get_ytdl_module_version() >= '2023.01.02'
    ):

        # suppress some warnings
        def _sort_formats(self, formats, field_preference=None):
            if not formats or not field_preference:
                return
            super()._sort_formats(formats, field_preference)

    # dl-plus extra attributes/methods

    DLP_BASE_URL: Optional[str] = None
    DLP_REL_URL: Optional[str] = None

    @classmethod
    def dlp_match(cls, url: str) -> Optional[Match[str]]:
        deprecated.warn(
            'dlp_match() is deprecated, use _match_valid_url() instead')
        return cls._match_valid_url(url)
