import pytest

from dl_plus.config import ConfigError, get_config_path


def test_default_path(config_home, monkeypatch):
    monkeypatch.delenv('DL_PLUS_CONFIG', raising=False)
    config_path = config_home / 'config.ini'
    assert get_config_path() is None
    config_path.touch()
    assert get_config_path() == config_path


def test_path_from_envvar(config_home, monkeypatch):
    config_path = config_home / 'another-config.ini'
    monkeypatch.setenv('DL_PLUS_CONFIG', str(config_path))
    with pytest.raises(ConfigError, match='is not a file'):
        get_config_path()
    config_path.touch()
    assert get_config_path() == config_path


def test_path_from_argument(config_home):
    config_path = config_home / 'another-config.ini'
    with pytest.raises(ConfigError, match='is not a file'):
        get_config_path(config_path)
    config_path.touch()
    assert get_config_path(config_path) == config_path
