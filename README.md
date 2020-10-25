# dl-plus

A [youtube-dl][youtube-dl-website] extension with pluggable extractors

## Description

`dl-plus` is an extension and a drop-in replacement of `youtube-dl`. The main goal of the project is to add an easy-to-use extractor plugin system to `youtube-dl` while maintaining full backward compatibility.

`dl-plus` is not a fork of `youtube-dl` and does not contain code from `youtube-dl`, it is a pure dynamic wrapper (thanks to Python dynamic nature) hacking some `youtube-dl` internals.

## Installation

  1. Install `dl-plus` (`youtube-dl` will be installed automatically):

      * using [pipx][pipx-website]:

        ```
        pipx install dl-plus
        ```

      * using pip:

        ```
        pip install dl-plus
        ```

  2. (optional) Install some plugins:

      * using [pipx][pipx-website]:

        ```
        pipx inject dl-plus dl-plus-extractor-un1def-wasdtv
        ```

      * using pip:

        ```
        pip install dl-plus-extractor-un1def-wasdtv
        ```

  3. (optional) Create `dl-plus` → `youtube-dl` symlink (for apps relying on `youtube-dl` executable in `PATH`, e.g., [mpv][mpv-website]):

      ```
      dlp=$(command -v dl-plus 2>&1) && ln -s "$dlp" "$(dirname "$dlp")/youtube-dl"
      ```

      Use `ln -sf` instead of `ln -s` to overwrite an existing `youtube-dl` executable.

## License

The [MIT License][license].


[youtube-dl-website]: https://ytdl-org.github.io/youtube-dl/
[pipx-website]: https://pipxproject.github.io/pipx/
[mpv-website]: https://mpv.io/
[license]: https://github.com/un-def/dl-plus/blob/master/LICENSE
