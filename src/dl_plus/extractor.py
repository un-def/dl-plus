import youtube_dl.extractor.common


class InfoExtractor(youtube_dl.extractor.common.InfoExtractor):

    @classmethod
    def ie_key(cls):
        return f'{cls.__module__}.{cls.__name__}'
