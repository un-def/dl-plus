import pytest

from dl_plus import ytdl


def pytest_configure():
    ytdl.init('youtube_dl')


@pytest.fixture
def config_home(tmp_path):
    return tmp_path / 'dl_plus_home'


@pytest.fixture(autouse=True)
def _autopatch_config_home(monkeypatch, config_home):
    monkeypatch.setattr('dl_plus.config._config_home', config_home)
