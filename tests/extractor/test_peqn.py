import pytest

from dl_plus.extractor.peqn import PEQN


@pytest.mark.parametrize('path,expected_ns,expected_plugin', [
    ('dl_plus.extractors.foo.bar', 'foo', 'bar'),
    ('dl_plus.extractors._1foo._2bar', '1foo', '2bar'),
])
def test_from_plugin_import_path(path, expected_ns, expected_plugin):
    peqn = PEQN.from_plugin_import_path(path)
    assert peqn.ns == expected_ns
    assert peqn.plugin == expected_plugin
    assert peqn.name is None


@pytest.mark.parametrize('path,expected_error', [
    ('somepackage.extractors.foo.bar', 'not in plugins package'),
    ('dl_plus.extractors.foo', 'not enough parts'),
    ('dl_plus.extractors.foo.bar.baz', 'too many parts'),
    ('dl_plus.extractors.foo.', 'empty plugin part'),
    ('dl_plus.extractors._.bar', 'empty ns part'),
    ('dl_plus.extractors.Foo.bar', 'bad ns part'),
    ('dl_plus.extractors.foo.bar_baz', 'bad plugin part'),
])
def test_from_plugin_import_path_error(path, expected_error):
    with pytest.raises(ValueError, match=expected_error):
        PEQN.from_plugin_import_path(path)


def test_from_string_without_name():
    peqn = PEQN.from_string('foo/1bar')
    assert peqn.ns == 'foo'
    assert peqn.plugin == '1bar'
    assert peqn.name is None


def test_from_string_with_name():
    peqn = PEQN.from_string('1foo/bar:baz')
    assert peqn.ns == '1foo'
    assert peqn.plugin == 'bar'
    assert peqn.name == 'baz'


@pytest.mark.parametrize('string', [
    'Foo/bar', '/bar', 'foo/bar_baz', '', 'foo',
])
def test_from_string_error(string):
    with pytest.raises(ValueError, match='bad PEQN'):
        PEQN.from_string(string)


@pytest.mark.parametrize(
    'orig,copy_args,expected_ns,expected_plugin,expected_name', [
        (PEQN('foo', 'bar'), dict(), 'foo', 'bar', None),
        (PEQN('foo', 'bar'), dict(plugin='bar1'), 'foo', 'bar1', None),
        (PEQN('foo', 'bar', 'baz'), dict(ns='foo1'), 'foo1', 'bar', 'baz'),
        (PEQN('foo', 'bar', 'baz'), dict(name=None), 'foo', 'bar', None),
    ]
)
def test_copy(orig, copy_args, expected_ns, expected_plugin, expected_name):
    copy = orig.copy(**copy_args)
    assert copy.ns == expected_ns
    assert copy.plugin == expected_plugin
    assert copy.name == expected_name


@pytest.mark.parametrize('peqn,expected', [
    (PEQN('foo', 'bar'), 'foo/bar'),
    (PEQN('foo', 'bar', 'baz'), 'foo/bar:baz'),
])
def test_to_str(peqn, expected):
    assert str(peqn) == expected


@pytest.mark.parametrize('peqn,expected', [
    (PEQN('foo', 'bar'), 'dl_plus.extractors.foo.bar'),
    (PEQN('foo', 'bar', 'baz'), 'dl_plus.extractors.foo.bar'),
    (PEQN('1foo', '22bar'), 'dl_plus.extractors._1foo._22bar'),
])
def test_plugin_import_path_property(peqn, expected):
    assert peqn.plugin_import_path == expected
