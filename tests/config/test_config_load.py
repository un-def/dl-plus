import pytest

from dl_plus.config import Config


@pytest.fixture
def config():
    _config = Config()
    return _config


@pytest.fixture
def write_config(config_home):

    def _write_config(name='config.ini', backend=None):
        path = config_home / name
        main_section = []
        if backend:
            main_section.append(f'backend = {backend}\n')
        lines = []
        if main_section:
            lines.append('[main]\n')
            lines.extend(main_section)
        with open(path, 'wt') as fobj:
            fobj.writelines(lines)
        return path

    return _write_config


class TestConfigLoad:
    DEFAULT_BACKEND = ':autodetect:'

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch, config, write_config):
        monkeypatch.delenv('DL_PLUS_BACKEND', raising=False)
        self.config = config
        self.write_config = write_config

    @pytest.mark.parametrize('args', [(), (None,), (True,)])
    def test_default_config_location(self, args):
        self.write_config(backend='config-ini')
        self.config.load(*args)
        assert self.config.backend == 'config-ini'

    def test_another_config_location(self):
        self.write_config(backend='config-ini')
        another_path = self.write_config(
            'another-config.ini', backend='another-config-ini')
        self.config.load(another_path)
        assert self.config.backend == 'another-config-ini'

    def test_default_config_location_with_envvar(self, monkeypatch):
        self.write_config(backend='config-ini')
        monkeypatch.setenv('DL_PLUS_BACKEND', 'environ')
        self.config.load()
        assert self.config.backend == 'environ'

    def test_another_config_location_with_envvar(self, monkeypatch):
        self.write_config(backend='config-ini')
        another_path = self.write_config(
            'another-config.ini', backend='another-config-ini')
        monkeypatch.setenv('DL_PLUS_BACKEND', 'environ')
        self.config.load(another_path)
        assert self.config.backend == 'environ'

    def test_disable_config_file(self):
        self.write_config(backend='config-ini')
        self.config.load(False)
        assert self.config.backend == self.DEFAULT_BACKEND

    def test_disable_config_file_with_envvar(self, monkeypatch):
        self.write_config(backend='config-ini')
        monkeypatch.setenv('DL_PLUS_BACKEND', 'environ')
        self.config.load(False)
        assert self.config.backend == 'environ'

    def test_disable_environ(self, monkeypatch):
        self.write_config(backend='config-ini')
        monkeypatch.setenv('DL_PLUS_BACKEND', 'environ')
        self.config.load(environ=False)
        assert self.config.backend == 'config-ini'

    def test_disable_config_file_disable_environ(self, monkeypatch):
        self.write_config(backend='config-ini')
        monkeypatch.setenv('DL_PLUS_BACKEND', 'environ')
        self.config.load(False, False)
        assert self.config.backend == self.DEFAULT_BACKEND
