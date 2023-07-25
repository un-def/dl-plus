import pytest

from dl_plus.core import get_extractors

from tests.testlib import ExtractorMock as EM


def mock_ytdl_get_all_extractors(include_generic):
    extractors = [EM('foo'), EM('bar'), EM('baz')]
    if include_generic:
        extractors.append(EM('generic'))
    return extractors


def mock_ytdl_get_extractors_by_name(name):
    return [EM(name)]


def mock_machinery_load_all_extractors():
    return [EM('ns1/plugin:foo'), EM('ns1/plugin:bar'), EM('ns2/plugin')]


def mock_machinery_load_extractors_by_peqn(name):
    name_str = str(name)
    if name_str == 'ns1/plugin':
        return [EM('ns1/plugin:foo'), EM('ns1/plugin:bar')]
    return [EM(name_str)]


@pytest.fixture
def mock_loaders(monkeypatch):
    monkeypatch.setattr(
        'dl_plus.ytdl.get_all_extractors', mock_ytdl_get_all_extractors)
    monkeypatch.setattr(
        'dl_plus.ytdl.get_extractors_by_name',
        mock_ytdl_get_extractors_by_name,
    )
    monkeypatch.setattr(
        'dl_plus.extractor.machinery.load_all_extractors',
        mock_machinery_load_all_extractors,
    )
    monkeypatch.setattr(
        'dl_plus.extractor.machinery.load_extractors_by_peqn',
        mock_machinery_load_extractors_by_peqn,
    )


@pytest.mark.parametrize('names,expected', [
    (['bar', 'bar', 'bar'], [EM('bar')]),
    (['baz', ':builtins:'], [EM('baz'), EM('foo'), EM('bar')]),
    (['ns2/plugin', ':plugins:', 'foo'], [
        EM('ns2/plugin'), EM('ns1/plugin:foo'), EM('ns1/plugin:bar'),
        EM('foo'),
    ]),
    (['ns1/plugin', 'ns1/plugin:foo'], [
        EM('ns1/plugin:foo'), EM('ns1/plugin:bar'),
    ]),
])
def test(mock_loaders, names, expected):
    assert get_extractors(names) == expected
