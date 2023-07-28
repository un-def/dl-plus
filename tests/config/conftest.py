import pytest


@pytest.fixture
def config_home(tmp_path):
    _config_home = tmp_path / 'dl-plus-home'
    _config_home.mkdir()
    return _config_home


@pytest.fixture(autouse=True)
def _autopatch_config_home(monkeypatch, config_home):
    monkeypatch.setattr('dl_plus.config._config_home', config_home)
