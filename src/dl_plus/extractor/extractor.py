import re
from typing import Match, Optional

from dl_plus import ytdl


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

    # dl-plus extra attributes/methods

    DLP_BASE_URL: Optional[str] = None
    DLP_REL_URL: Optional[str] = None

    @classmethod
    def dlp_match(cls, url: str) -> Optional[Match[str]]:
        # yt-dlp has a similar method (since 5ad28e7)
        match_valid_url = getattr(cls, '_match_valid_url', None)
        if match_valid_url is not None:
            return match_valid_url(url)
        # fallback for o.g. youtube-dl and other forks
        # a copy/paste from youtube-dl
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL)
        return cls._VALID_URL_RE.match(url)
