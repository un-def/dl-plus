import os
import pathlib


def pytest_addoption(parser):
    parser.addoption('--backend')


def pytest_configure(config):
    dlp_vars = [key for key in os.environ if key.startswith('DL_PLUS_')]
    for dlp_var in dlp_vars:
        del os.environ[dlp_var]

    from dl_plus import config as conf
    from dl_plus.backend import init_backend

    conf._config_home = conf._data_home = pathlib.Path('fake-dl-plus-home')
    init_backend(config.getoption('backend'))
