import pytest

from dl_plus.backend import init_backend
from dl_plus.config import Option


def pytest_configure():
    init_backend(Option.Backend.AUTODETECT)


@pytest.fixture
def config_home(tmp_path):
    return tmp_path / 'dl_plus_home'


@pytest.fixture(autouse=True)
def _autopatch_config_home(monkeypatch, config_home):
    monkeypatch.setattr('dl_plus.config._config_home', config_home)
