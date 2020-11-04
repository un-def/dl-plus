import pytest

from dl_plus import ytdl


class EM:
    """Extractor Mock"""

    def __init__(self, name):
        self.IE_NAME = name

    def __repr__(self):
        return f'<EM: {self.IE_NAME}>'

    def __eq__(self, other):
        return self.IE_NAME == other.IE_NAME


@pytest.fixture(autouse=True)
def reset_cache():
    ytdl._extractors = None
    ytdl._extractors_registry = None


@pytest.fixture(autouse=True)
def monkeypatch_get_all_extractors(request, monkeypatch, reset_cache):
    extractors = None
    try:
        extractors = request.getfixturevalue('extractors')
    except pytest.FixtureLookupError:
        marker = request.node.get_closest_marker('extractors')
        if marker:
            extractors = marker.args
    if extractors is not None:
        with monkeypatch.context() as mp:
            mp.setattr(
                'dl_plus.ytdl.get_all_extractors', lambda **kw: extractors)
            yield
    else:
        yield


@pytest.mark.parametrize('extractors,expected', [
    # 0
    ([EM('foo'), EM('bar')], {
        'foo': EM('foo'),
        'bar': EM('bar'),
    }),
    # 1
    ([EM('foo:sub1'), EM('foo:sub2'), EM('bar')], {
        'foo': {
            'sub1': EM('foo:sub1'),
            'sub2': EM('foo:sub2'),
        },
        'bar': EM('bar'),
    }),
    # 2
    ([EM('foo'), EM('foo:sub'), EM('bar')], {
        'foo': {
            '_': EM('foo'),
            'sub': EM('foo:sub'),
        },
        'bar': EM('bar'),
    }),
    # 3
    ([EM('foo:sub'), EM('foo'), EM('bar')], {
        'foo': {
            '_': EM('foo'),
            'sub': EM('foo:sub'),
        },
        'bar': EM('bar'),
    }),
    # 4
    ([EM('foo:sub1'), EM('foo'), EM('foo:sub2')], {
        'foo': {
            '_': EM('foo'),
            'sub1': EM('foo:sub1'),
            'sub2': EM('foo:sub2'),
        },
    }),
    # 5
    ([EM('foo:sub'), EM('foo'), EM('foo:sub:subsub')], {
        'foo': {
            '_': EM('foo'),
            'sub': {
                '_': EM('foo:sub'),
                'subsub': EM('foo:sub:subsub'),
            },
        },
    }),
])
def test_build_extractors_registry(extractors, expected):
    assert ytdl._build_extractors_registry() == expected


@pytest.mark.parametrize('extractors,expected', [
    ([EM('foo'), EM('bar'), EM('foo')], EM('foo')),
    ([EM('foo:sub'), EM('foo'), EM('foo:sub')], EM('foo:sub')),
    ([EM('foo:sub'), EM('foo:sub:subsub'), EM('foo:sub')], EM('foo:sub')),
])
def test_build_extractors_registry_error_duplicate_name(extractors, expected):
    with pytest.raises(
            ytdl.YoutubeDLError, match=f'duplicate name: {expected!r}'):
        ytdl._build_extractors_registry()


extractors_marker = pytest.mark.extractors(
    EM('foo'), EM('foo:sub'), EM('foo:sub:subsub1'), EM('foo:sub:subsub2'),
    EM('bar:sub1'), EM('bar:sub2'),
    EM('baz'),
)


@pytest.mark.parametrize('name,expected', [
    ('foo', [
        EM('foo'), EM('foo:sub'), EM('foo:sub:subsub1'), EM('foo:sub:subsub2'),
    ]),
    ('foo:_', [EM('foo')]),
    ('foo:sub', [EM('foo:sub'), EM('foo:sub:subsub1'), EM('foo:sub:subsub2')]),
    ('foo:sub:_', [EM('foo:sub')]),
    ('foo:sub:subsub1', [EM('foo:sub:subsub1')]),
    ('bar', [EM('bar:sub1'), EM('bar:sub2')]),
    ('baz', [EM('baz')]),
])
@extractors_marker
def test_get_extractors_by_name(name, expected):
    assert ytdl.get_extractors_by_name(name) == expected


@pytest.mark.parametrize('name', [
    'foo:sub:subsub3', 'bar:sub1:subsub', 'baz:_'])
@extractors_marker
def test_get_extractors_by_name_error_unknown(name):
    with pytest.raises(ytdl.UnknownBuiltinExtractor, match=name):
        ytdl.get_extractors_by_name(name)
