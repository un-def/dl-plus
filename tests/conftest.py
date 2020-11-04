from dl_plus import ytdl


def pytest_configure():
    ytdl.init('youtube_dl')
