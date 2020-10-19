from youtube_dl.extractor.common import InfoExtractor


class Extractor(InfoExtractor):

    @classmethod
    def ie_key(cls):
        return cls.IE_NAME
