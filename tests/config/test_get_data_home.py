import sys
from pathlib import Path

import pytest

from dl_plus.config import get_data_home
from dl_plus.deprecated import DLPlusDeprecationWarning


@pytest.fixture(autouse=True)
def _autopatch_data_home(monkeypatch):
    # set dl_plus.config._data_home to None to disable caching
    monkeypatch.setattr('dl_plus.config._data_home', None)


@pytest.fixture(autouse=True)
def _unset_data_home_envvar(monkeypatch):
    monkeypatch.delenv('DL_PLUS_DATA_HOME', raising=False)
    monkeypatch.delenv('DL_PLUS_HOME', raising=False)


@pytest.mark.skipif(
    not sys.platform.startswith('linux'), reason='requires linux')
class TestLinux:

    def test_location_from_data_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_DATA_HOME', '/dl/plus/data/home')
        # should be ignored
        monkeypatch.setenv('DL_PLUS_HOME', '/dl/plus/home')
        assert get_data_home() == Path('/dl/plus/data/home')

    def test_location_from_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_HOME', '/dl/plus/home')
        assert get_data_home() == Path('/dl/plus/home')

    def test_default_location_no_xdg_data_home_envvar(self, monkeypatch):
        monkeypatch.setattr(Path, 'home', lambda: Path('/fakehome'))
        monkeypatch.delenv('XDG_DATA_HOME', raising=False)
        assert get_data_home() == Path('/fakehome/.local/share/dl-plus')

    def test_default_location_with_xdg_data_home_envvar(self, monkeypatch):
        monkeypatch.setenv('XDG_DATA_HOME', '/xdgdata')
        assert get_data_home() == Path('/xdgdata/dl-plus')

    # config_home fallback tests; remove all class code below when
    # fallback is removed

    @pytest.fixture
    def config_home(self, tmp_path):
        _config_home = tmp_path / 'dl-plus-config-home'
        _config_home.mkdir()
        return _config_home

    @pytest.mark.parametrize('data_dir', ['backends', 'extractors'])
    def test_fallback_with_one_dir(self, config_home, data_dir):
        (config_home / data_dir).mkdir()
        with pytest.warns(DLPlusDeprecationWarning) as warn_record:
            assert get_data_home() == config_home
        assert len(warn_record) == 1
        assert f"move '{data_dir}' directory" in warn_record[0].message.args[0]

    def test_fallback_with_both_dirs(self, config_home):
        (config_home / 'backends').mkdir()
        (config_home / 'extractors').mkdir()
        with pytest.warns(DLPlusDeprecationWarning) as warn_record:
            assert get_data_home() == config_home
        assert len(warn_record) == 2
        assert "move 'backends' directory" in warn_record[0].message.args[0]
        assert "move 'extractors' directory" in warn_record[1].message.args[0]

    def test_no_fallback(self, monkeypatch):
        monkeypatch.setenv('XDG_DATA_HOME', '/xdgdata')
        assert get_data_home() == Path('/xdgdata/dl-plus')


@pytest.mark.skipif(
    not sys.platform.startswith('win'), reason='requires windows')
class TestWindows:

    def test_location_from_data_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_DATA_HOME', 'X:/dl/plus/data/home')
        # should be ignored
        monkeypatch.setenv('DL_PLUS_HOME', r'X:\dl\plus\home')
        assert get_data_home() == Path('X:/dl/plus/data/home')

    def test_location_from_home_envvar(self, monkeypatch):
        monkeypatch.setenv('DL_PLUS_HOME', r'X:\dl\plus\home')
        assert get_data_home() == Path('X:/dl/plus/home')

    def test_default_location_no_appdata_envvar(self, monkeypatch):
        monkeypatch.delenv('AppData', raising=False)
        monkeypatch.setattr(Path, 'home', lambda: Path('X:/fakehome'))
        assert get_data_home() == Path('X:/fakehome/AppData/Roaming/dl-plus')

    def test_default_location_with_appdata_envvar(self, monkeypatch):
        monkeypatch.setenv('AppData', 'X:/appdata')
        assert get_data_home() == Path('X:/appdata/dl-plus')
