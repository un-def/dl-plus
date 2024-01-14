import pytest


@pytest.fixture
def config_home():
    # set dl_plus.config._config_home to None to disable caching
    return None


@pytest.fixture(autouse=True)
def _autopatch_config_home(monkeypatch, config_home):
    monkeypatch.setattr('dl_plus.config._config_home', config_home)
