import random
import string

import pytest

from dl_plus import ytdl
from dl_plus.extractor import Extractor
from dl_plus.extractor.plugin import ExtractorPlugin, ExtractorPluginError


def create_extractor(__base=None, **attrs):
    return type('TestExtractor', (__base or Extractor,), attrs)


def create_plugin(ns=None, plugin=None):
    ns = ns or ''.join(random.choices(string.ascii_lowercase, k=6))
    plugin = plugin or ''.join(random.choices(string.ascii_lowercase, k=6))
    return ExtractorPlugin(f'dl_plus.extractors.{ns}.{plugin}')


@pytest.fixture
def plugin():
    return create_plugin(ns='foo', plugin='bar')


@pytest.mark.parametrize('path', [
    'somepackage.extractors.foo.bar',
    'dl_plus.extractors.foo',
    'dl_plus.extractors.foo.bar.baz',
])
def test_init_error_bad_import_path(path):
    with pytest.raises(ExtractorPluginError, match='bad plugin import path'):
        ExtractorPlugin(path)


class TestRegister:

    NS = 'foo'
    PLUGIN = 'bar'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.plugin = create_plugin(self.NS, self.PLUGIN)

    @property
    def registry(self):
        return self.plugin._extractors

    def test_decorator_unnamed_extractor(self):
        @self.plugin.register
        class TestExtractor(Extractor):
            pass
        assert self.registry == {None: TestExtractor}

    def test_decorator_unnamed_extractor_with_parentheses(self):
        @self.plugin.register()
        class TestExtractor(Extractor):
            pass
        assert self.registry == {None: TestExtractor}

    def test_decorator_named_extractor(self):
        @self.plugin.register('test')
        class TestExtractor(Extractor):
            pass
        assert self.registry == {'test': TestExtractor}

    def test_decorator_named_extractor_name_kw(self):
        @self.plugin.register(name='test')
        class TestExtractor(Extractor):
            pass
        assert self.registry == {'test': TestExtractor}

    def test_method_call_two_named_extractors(self):
        extractor_1 = self.plugin.register(create_extractor(), name='quux')
        extractor_2 = self.plugin.register(create_extractor(), name='quuz')
        assert self.registry == {
            'quux': extractor_1,
            'quuz': extractor_2,
        }

    def test_ie_name_unnamed_extractor(self):
        extractor = create_extractor()
        assert extractor.IE_NAME is None
        self.plugin.register(extractor)
        assert extractor.IE_NAME == f'{self.NS}/{self.PLUGIN}'

    def test_ie_name_named_extractor(self):
        extractor = create_extractor()
        assert extractor.IE_NAME is None
        self.plugin.register(extractor, name='quux')
        assert extractor.IE_NAME == f'{self.NS}/{self.PLUGIN}:quux'

    @pytest.mark.parametrize('base,rel,expected', [
        ('foo://bar/', 'baz', 'foo://bar/baz'),
        ('foo://bar/', '/baz', 'foo://bar//baz'),
        ('foo://bar', 'baz', 'foo://barbaz'),
    ])
    def test_dlp_url(self, base, rel, expected):
        extractor_base = create_extractor(DLP_BASE_URL=base)
        extractor = create_extractor(extractor_base, DLP_REL_URL=rel)
        self.plugin.register(extractor)
        assert extractor._VALID_URL == expected

    def test_error_dlp_rel_url_without_base_url(self):
        extractor_base = create_extractor()
        extractor = create_extractor(extractor_base, DLP_REL_URL='baz')
        with pytest.raises(ExtractorPluginError, match='without DLP_BASE_URL'):
            self.plugin.register(extractor)

    def test_error_dlp_rel_url_and_valid_url_conflict(self):
        extractor_base = create_extractor(DLP_BASE_URL='foo://bar/')
        extractor = create_extractor(
            extractor_base, DLP_REL_URL='baz', _VALID_URL='qux://quux')
        with pytest.raises(ExtractorPluginError, match='mutually exclusive'):
            self.plugin.register(extractor)

    def test_error_bad_superclass(self):
        InfoExtractor = ytdl.import_from('extractor.common', 'InfoExtractor')
        extractor = create_extractor(InfoExtractor)
        with pytest.raises(ExtractorPluginError, match='subclass expected'):
            self.plugin.register(extractor)

    def test_error_ie_name_is_set(self):
        extractor = create_extractor(IE_NAME='clip')
        with pytest.raises(ExtractorPluginError, match='non-None IE_NAME'):
            self.plugin.register(extractor)

    def test_error_already_registered_same_plugin(self):
        extractor = create_extractor()
        self.plugin.register(extractor, name='quux')
        with pytest.raises(ExtractorPluginError, match='already registered'):
            self.plugin.register(extractor, name='quuz')

    def test_error_already_registered_another_plugin(self):
        another_plugin = create_plugin()
        extractor = create_extractor()
        another_plugin.register(extractor, name='quux')
        with pytest.raises(ExtractorPluginError, match='already registered'):
            self.plugin.register(extractor, name='quuz')

    @pytest.mark.parametrize('name', [None, 'quux'])
    def test_error_unnamed_extractor_when_registry_is_not_empty(self, name):
        self.plugin.register(create_extractor(), name=name)
        with pytest.raises(ExtractorPluginError, match='the only extractor'):
            self.plugin.register(create_extractor())

    def test_error_named_extractor_name_collision(self):
        self.plugin.register(create_extractor(), name='quux')
        with pytest.raises(ExtractorPluginError, match='already contains'):
            self.plugin.register(create_extractor(), name='quux')

    def test_error_named_extractor_when_unnamed_extractor_in_registry(self):
        self.plugin.register(create_extractor())
        with pytest.raises(ExtractorPluginError, match='the only extractor'):
            self.plugin.register(create_extractor(), name='quux')


def test_get_extractor_unnamed(plugin):
    extractor = plugin.register(create_extractor())
    assert plugin.get_extractor() is extractor


def test_get_extractor_named(plugin):
    extractor = plugin.register(create_extractor(), name='quux')
    assert plugin.get_extractor('quux') is extractor


def test_get_extractor_unnamed_error(plugin):
    plugin.register(create_extractor(), name='quux')
    with pytest.raises(KeyError):
        plugin.get_extractor()


def test_get_extractor_named_error(plugin):
    plugin.register(create_extractor(), name='quux')
    with pytest.raises(KeyError):
        plugin.get_extractor('quuz')


def get_all_extractors_empty_registry(plugin):
    assert plugin.get_all_extractors() == []


def get_all_extractors_unnamed_extractor(plugin):
    extractor = plugin.register(create_extractor())
    assert plugin.get_all_extractors() == [extractor]


def get_all_extractors_two_named_extractors(plugin):
    extractor_1 = plugin.register(create_extractor(), name='quux')
    extractor_2 = plugin.register(create_extractor(), name='quuz')
    assert sorted(plugin.get_all_extractors()) == sorted(
        [extractor_1, extractor_2])
