import sys
from pathlib import Path

import pytest

from dl_plus.config import get_config_home


@pytest.fixture
def config_home():
    # set dl_plus.config._config_home to None to disable caching
    return None


def test_location_from_env(monkeypatch):
    monkeypatch.setenv('DL_PLUS_HOME', '/dl/plus/home')
    assert get_config_home() == Path('/dl/plus/home')


@pytest.mark.skipif(
    not sys.platform.startswith('linux'), reason='requires linux')
class TestLinux:

    @pytest.fixture(autouse=True)
    def monkeypatch_path_home(self, monkeypatch):
        monkeypatch.setattr(Path, 'home', lambda: Path('/fakehome'))

    def test_default_location_no_xdg_config_home_envvar(self, monkeypatch):
        monkeypatch.delenv('XDG_CONFIG_HOME', raising=False)
        assert get_config_home() == Path('/fakehome/.config/dl-plus')

    def test_default_location_with_xdg_config_home_envvar(self, monkeypatch):
        monkeypatch.setenv('XDG_CONFIG_HOME', '/xdgconfig')
        assert get_config_home() == Path('/xdgconfig/dl-plus')


@pytest.mark.skipif(
    not sys.platform.startswith('win'), reason='requires windows')
class TestWindows:

    @pytest.fixture(autouse=True)
    def monkeypatch_path_home(self, monkeypatch):
        monkeypatch.setattr(Path, 'home', lambda: Path('X:/fakehome'))

    def test_default_location_no_appdata_envvar(self, monkeypatch):
        monkeypatch.delenv('AppData', raising=False)
        assert get_config_home() == Path('X:/fakehome/AppData/Roaming/dl-plus')

    def test_default_location_with_appdata_envvar(self, monkeypatch):
        monkeypatch.setenv('AppData', 'X:/appdata')
        assert get_config_home() == Path('X:/appdata/dl-plus')
