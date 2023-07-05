import pytest

from dl_plus.cli.cli import _detect_compat_mode


@pytest.mark.parametrize('name', [
    'yt-dlp', 'yt-dlp.exe',
    '/path/to/bin/yt-dlp', '/path/to/bin/yt-dlp.exe',
    'youtube-dl', 'youtube-dl.exe',
])
def test_compat_mode(name):
    assert _detect_compat_mode(name) is True


@pytest.mark.parametrize('name', [
    'dl-plus', 'dl-plus.exe',
    'youtube-dl-enhanced',
    'yt-dlp.enhanced',
    '/path/to/yt_dlp/__main__.py',
])
def test_full_mode(name):
    assert _detect_compat_mode(name) is False
