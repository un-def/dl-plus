# Changelog

## 0.3.0 (unreleased)

### Features

#### Extractor API

  * Two new attributes were added: `DLP_BASE_URL` and `DLP_REL_URL`. If set, they are used to compute the `_VALID_URL` value.
  * A new `dlp_match` method was added. It returns a `re.Match` object for a given URL.

### Improvements

  * Remove duplicates when expanding the extractor list from the config (`[extractors.enable]`) or the command line arguments (`--extractor`). For example, `-E twitch:vod -E twitch` will no longer include the `twitch:vod` extractor twice.

### Internals

  * `dl_plus.extractor.Extractor` and `dl_plus.extractor.ExtractorError` are now loaded lazily. It is now possible to import modules from the `dl_plus.extractor` package without first initializing `dl_plus.ytdl`.

## 0.2.0

### Features

  * Configurable `youtube-dl`–compatible backends. `youtube-dl` is not a hardcoded dependency anymore, `dl-plus` can now work with any _compatible_ package (that is, any _compatible_ fork), even if its import path is different). As a result, `dl-plus` no longer installs `youtube-dl` automatically. The backend can be configured using the `--backend` command line option or the `backend` option in the `[main]` section on the config file (see below). The value is an import path of the backend (e.g., `youtube_dl` for `youtube-dl`).
  * Configuration file support. The config provides used-defined default values for the command line options (that is, the config options have lower predecence than the command line ones). The default config location is `$XDG_CONFIG_HOME/dl-plus/config.ini` (*nix) or `%APPDATA%\dl-plus\config.ini` (Windows).

### Changes

  * The generic extractor is no longer included in the `:builtins:` list. That is, one should use `-E :builtins: -E generic` to get **all** built-in extractors.
  * Built-in extactors are now grouped by their names splitted by colons. For example, `-E twitch` is now expanded to a list of all `twitch:*` extractors (previously, one should specify each `twitch:*` extractor manually: `-E twitch:stream -E twitch:vod -E ...`).

### Fixes

  * `youtube-dl` config processing was restored. The config was simply ignored in the previous version.

### Improvements

  * The `--extractor` and `--force-generic-extractor` command-line options are mutually exclusive now.
  * Added the `--dlp-version` command-line option to check `dl-plus` version (the `--version` option shows the version of the backend).

## 0.1.0

The first public release.
