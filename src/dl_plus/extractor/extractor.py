from typing import Optional

from youtube_dl.extractor.common import InfoExtractor


class Extractor(InfoExtractor):
    """
    A base class for pluggable extractors
    """

    # Set by `ExtractorPlugin.register`, do not override.
    IE_NAME: Optional[str] = None

    @classmethod
    def ie_key(cls):
        return cls.IE_NAME
