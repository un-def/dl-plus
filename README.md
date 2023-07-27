# dl-plus

A [youtube-dl][youtube-dl-website] extension with pluggable extractors

## Description

`dl-plus` is an extension and a drop-in replacement of `youtube-dl` (or any compatible fork, e.g., `yt-dlp`). The main goal of the project is to add an easy-to-use extractor plugin system to `youtube-dl` while maintaining full backward compatibility.

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

    (**\*nix**) Alternatively, you can download a single file binary (zipapp) and put it somewhere in your `PATH`:

    ```
    curl -L https://github.com/un-def/dl-plus/releases/latest/download/dl-plus -o dl-plus
    chmod a+x dl-plus
    ```

2.  Install a backend — `youtube-dl` or any compatible package (fork), e.g., `yt-dlp`:

    * using `dl-plus` itself:

      ```
      dl-plus --cmd backend install yt-dlp
      ```

    * using [pipx][pipx-website]:

      ```
      pipx inject dl-plus yt-dlp
      ```

    * using pip:

      ```
      pip install yt-dlp
      ```

3.  (optional) Install some extractor plugins:

    * using `dl-plus` itself:

      ```
      dl-plus --cmd extractor install un1def/wasdtv
      ```

      PyPI package names are supported too:

      ```
      dl-plus --cmd extractor install dl-plus-extractor-un1def-wasdtv
      ```

    * using [pipx][pipx-website]:

      ```
      pipx inject dl-plus dl-plus-extractor-un1def-wasdtv
      ```

    * using pip:

      ```
      pip install dl-plus-extractor-un1def-wasdtv
      ```

4.  (optional) Create `dl-plus` → `youtube-dl` symlink (for apps relying on `youtube-dl` executable in `PATH`, e.g., [mpv][mpv-website]):

    - **\*nix**:

      ```shell
      dlp=$(command -v dl-plus 2>&1) && ln -s "$dlp" "$(dirname "$dlp")/youtube-dl"
      ```

      Use `ln -sf` instead of `ln -s` to overwrite an existing `youtube-dl` executable.

    - **Windows** (PowerShell, requires administrative privileges):

      ```powershell
      $dlp = (Get-Command -ErrorAction:Stop dl-plus).Path; New-Item -ItemType SymbolicLink -Path ((Get-Item $dlp).Directory.FullName + "\youtube-dl.exe") -Target $dlp
      ```

## Extractor Plugin Authoring Guide

See [docs/extractor-plugin-authoring-guide.md](https://github.com/un-def/dl-plus/blob/master/docs/extractor-plugin-authoring-guide.md).

## Available Extractor Plugins

See [docs/available-extractor-plugins.md](https://github.com/un-def/dl-plus/blob/master/docs/available-extractor-plugins.md).

## License

The [MIT License][license].


[youtube-dl-website]: https://youtube-dl.org/
[pipx-website]: https://pipxproject.github.io/pipx/
[mpv-website]: https://mpv.io/
[license]: https://github.com/un-def/dl-plus/blob/master/LICENSE
