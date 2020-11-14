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

See [docs/extractor-plugin-authoring-guide.md](https://github.com/un-def/dl-plus/blob/master/docs/extractor-plugin-authoring-guide.md).

## Available Extractor Plugins

See [docs/available-extactor-plugins.md](https://github.com/un-def/dl-plus/blob/master/docs/available-extactor-plugins.md).

## License

The [MIT License][license].


[youtube-dl-website]: https://youtube-dl.org/
[youtube-dl-extractor-guide]: https://web.archive.org/web/20201019114817if_/https://github.com/ytdl-org/youtube-dl#adding-support-for-a-new-site
[pipx-website]: https://pipxproject.github.io/pipx/
[mpv-website]: https://mpv.io/
[pypi-website]: https://pypi.org/
[un1def-wasdtv-extractor-repo]: https://github.com/un-def/dl-plus-extractor-un1def-wasdtv
[license]: https://github.com/un-def/dl-plus/blob/master/LICENSE
