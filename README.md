# dl-plus

A [youtube-dl][youtube-dl-website] extension with pluggable extractors

## Description

`dl-plus` is an extension and a drop-in replacement of `youtube-dl`. The main goal of the project is to add an easy-to-use extractor plugin system to `youtube-dl` while maintaining full backward compatibility.

`dl-plus` is not a fork of `youtube-dl` and does not contain code from `youtube-dl`, it is a pure dynamic wrapper (thanks to Python dynamic nature) hacking some `youtube-dl` internals.

## Installation

1.  Install `dl-plus`:

    * using [pipx][pipx-website]:

      ```
      pipx install dl-plus
      ```

    * using pip:

      ```
      pip install dl-plus
      ```

2.  Install `youtube-dl` or any compatible package (fork):

    * using [pipx][pipx-website]:

      ```
      pipx inject dl-plus youtube-dl
      ```

    * using pip:

      ```
      pip install youtube-dl
      ```

    **NOTE**: if you use a fork where an import path was changed (it is `youtube_dl` by default), you'll need to configure a backend using the config file or the `--backend` command line option.

3.  (optional) Install some plugins:

    * using [pipx][pipx-website]:

      ```
      pipx inject dl-plus dl-plus-extractor-un1def-wasdtv
      ```

    * using pip:

      ```
      pip install dl-plus-extractor-un1def-wasdtv
      ```

4.  (optional) Create `dl-plus` → `youtube-dl` symlink (for apps relying on `youtube-dl` executable in `PATH`, e.g., [mpv][mpv-website]):

    ```
    dlp=$(command -v dl-plus 2>&1) && ln -s "$dlp" "$(dirname "$dlp")/youtube-dl"
    ```

    Use `ln -sf` instead of `ln -s` to overwrite an existing `youtube-dl` executable.

## Extractor Plugin Authoring Guide

**NOTE**: you can use the [un1def/wasdtv][un1def-wasdtv-extractor-repo] plugin repository as an example.

1.  Choose a namespace. Namespaces are used to avoid name conflicts of different plugins created by different authors. It's recommended to use your name, username, or organization name as a namespace. Make sure that the namespace is not already taken (at least search for `dl-plus-extractor-<namespace>` on [PyPI][pypi-website]).

    The namespace must consist only of lowercase latin letters and digits. It should be reasonable short to save typing.

2.  Choose a plugin name. The plugin name should reflect the name of the service the plugin is intended for.

    The same restrictions and recommendations regarding allowed characters and length are apply to the plugin name as to the namespace.

3.  Create the following directory structure:

    ```
    dl_plus/
      extractors/
        <namespace>/
          <plugin>.py
    ```

    Please note that there are no `__init__.py` files in any directory. It's crucial for the `dl-plus` plugin system, a single `__init__.py` can break all other plugins or even `dl-plus` itself.

    However, it's OK to use `__init__.py` inside the plugin *package*, that is, the following structure is allowed:

    ```
    dl_plus/
      extractors/
        <namespace>/
          <plugin>/
            __init__.py
            extractor.py
            utils.py
            ...
    ```

    The latter form can be used for plugins with a lot of code.

    If your namespace or plugin name starts with a digit, prepend a single underscore (`_`) to it.

    For example, if some user called `ZX_2000` wants to create a plugin for some service named `2chan TV`, they should create the following structure:

    ```
    dl_plus/
      extractors/
        zx2000/
          _2chantv.py
    ```

4.  Add plugin initialization code. Put the following lines in `<plugin>.py`:

    ```python
    from dl_plus.extractor import Extractor, ExtractorPlugin

    plugin = ExtractorPlugin(__name__)
    ```

    Please note that the plugin object must be available in the module's globals under the `plugin` name as in the code above.

5.  Write your extractor class using the template from the `youtube-dl`'s [developer instructions][youtube-dl-extractor-guide] except for the following points:

    * Python 2 backward compatibility is redundant. Skip this part:
      ```python
      # coding: utf-8
      from __future__ import unicode_literals
      ```
    * Use `dl_plus.extractor.Extractor` instead of `youtube_dl.extractor.common.InfoExtractor` as a base class.
    * Use `dl_plus.extractor.ExtractorError` instead of `youtube_dl.utils.ExtractorError`.
    * Do not import from `youtube_dl` directly, use `import_module`/`import_from` helpers from `dl_plus.ytdl`:
      ```python
      # from youtube_dl import utils
      utils = dl_plus.ytdl.import_module('utils')
      # from youtube_dl.utils import try_get
      try_get = dl_plus.ytdl.import_from('utils', 'try_get')
      # from yotube_dl.utils import int_or_none, float_or_none
      int_or_none, float_or_none = dl_plus.ytdl.import_from('utils', ['int_or_none', 'float_or_none'])
      ```
    * `_TEST`/`_TESTS` are not supported at the moment (and will probably not be supported in the future).
    * Do not define the `IE_NAME` attribute, it will be generated by the plugin system automatically.

    ```python
    class MyPluginExtractor(Extractor):
        _VALID_URL = r'https?://...'

        def _real_extract(self, url):
            ...
    ```

6.  Register your extractor. There are two options:

    * If there is only one extractor in the plugin, you can either leave the extractor unnamed or give it a name.
    * If there are two or more extractors in the plugin, all of them must be named.

    The unnamed extractor is identified by the plugin name: `<namespace>/<plugin>`. The named extractor is identified by a combination of the plugin name and its own name: `<namespace>/<plugin>:<name>`.

    The same restrictions and recommendations regarding allowed characters and length are apply to the extractor name as to the namespace and the plugin name.

    * Register the unnamed extractor:

      ```python
      @plugin.register
      class MyUnnamedExtractor(Extractor):
          ...
      ```

    * Register the named extractor under the `playlist` name:

      ```python
      @plugin.register('playlist')
      class MyPlaylistExtractor(Extractor):
          ...
      ```

7.  Make your plugin importable by `dl-plus`. That is, ensure that the plugin's directory (the top-level directory, `dl_plus`) is in `sys.path`. The most common way is to install the plugin into the same virtual environment as `dl-plus` (or globally if `dl-plus` is installed globally), but you can also use the `PYTHONPATH` variable, `.pth` files – you name it.

8.  If you want to upload your plugin to the [PyPI][pypi-website], use the following name format for the package:

    ```
    dl-plus-extractor-<namespace>-<plugin>
    ```

    The same name should be used for the project's public repository.

## License

The [MIT License][license].


[youtube-dl-website]: https://youtube-dl.org/
[youtube-dl-extractor-guide]: https://web.archive.org/web/20201019114817if_/https://github.com/ytdl-org/youtube-dl#adding-support-for-a-new-site
[pipx-website]: https://pipxproject.github.io/pipx/
[mpv-website]: https://mpv.io/
[pypi-website]: https://pypi.org/
[un1def-wasdtv-extractor-repo]: https://github.com/un-def/dl-plus-extractor-un1def-wasdtv
[license]: https://github.com/un-def/dl-plus/blob/master/LICENSE
