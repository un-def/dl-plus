import os
import pathlib


def pytest_addoption(parser):
    parser.addoption('--backend')


def pytest_configure(config):
    dlp_vars = [key for key in os.environ if key.startswith('DL_PLUS_')]
    for dlp_var in dlp_vars:
        del os.environ[dlp_var]

    import dl_plus.config
    from dl_plus.backend import init_backend
    from dl_plus.config import Option

    dl_plus.config._config_home = pathlib.Path('fake-dl-plus-home')
    init_backend(config.getoption('backend') or Option.Backend.AUTODETECT)
