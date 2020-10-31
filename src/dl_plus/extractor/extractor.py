from typing import Optional

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
