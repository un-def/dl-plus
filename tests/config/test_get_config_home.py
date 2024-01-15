import sys
from pathlib import Path

import pytest

from dl_plus.config import get_config_home


@pytest.fixture(autouse=True)
def _unset_config_home_envvar(monkeypatch):
    monkeypatch.delenv('DL_PLUS_CONFIG_HOME', raising=False)
    monkeypatch.delenv('DL_PLUS_HOME', raising=False)


@pytest.mark.skipif(
    not sys.platform.startswith('linux'), reason='requires linux')
class TestLinux:

    def test_location_from_config_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_CONFIG_HOME', '/dl/plus/config/home')
        # should be ignored
        monkeypatch.setenv('DL_PLUS_HOME', '/dl/plus/home')
        assert get_config_home() == Path('/dl/plus/config/home')

    def test_location_from_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_HOME', '/dl/plus/home')
        assert get_config_home() == Path('/dl/plus/home')

    def test_default_location_no_xdg_config_home_envvar(self, monkeypatch):
        monkeypatch.delenv('XDG_CONFIG_HOME', raising=False)
        monkeypatch.setattr(Path, 'home', lambda: Path('/fakehome'))
        assert get_config_home() == Path('/fakehome/.config/dl-plus')

    def test_default_location_with_xdg_config_home_envvar(self, monkeypatch):
        monkeypatch.setenv('XDG_CONFIG_HOME', '/xdgconfig')
        assert get_config_home() == Path('/xdgconfig/dl-plus')


@pytest.mark.skipif(
    not sys.platform.startswith('win'), reason='requires windows')
class TestWindows:

    def test_location_from_config_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_CONFIG_HOME', 'X:/dl/plus/config/home')
        # should be ignored
        monkeypatch.setenv('DL_PLUS_HOME', r'X:\dl\plus\home')
        assert get_config_home() == Path('X:/dl/plus/config/home')

    def test_location_from_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_HOME', r'X:\dl\plus\home')
        assert get_config_home() == Path('X:/dl/plus/home')

    def test_default_location_no_appdata_envvar(self, monkeypatch):
        monkeypatch.delenv('AppData', raising=False)
        monkeypatch.setattr(Path, 'home', lambda: Path('X:/fakehome'))
        assert get_config_home() == Path('X:/fakehome/AppData/Roaming/dl-plus')

    def test_default_location_with_appdata_envvar(self, monkeypatch):
        monkeypatch.setenv('AppData', 'X:/appdata')
        assert get_config_home() == Path('X:/appdata/dl-plus')
