# Changelog

## UNRELEASED

### Fixes

  * **(CLI)** Don't try to validate a backend name if not passed. Fixes `TypeError` on `backend update` command.

## 0.8.0

### Features

  * **(Config)** Backend configuration file. A new config file `$DL_PLUS_CONFIG_HOME/backends.ini` can be used to extend/override the predefined list of backends.
  * **(CLI)** Two new commands was added — `config show main` and `config show backends` — to display `config.ini` and `backends.ini`, respectively.
  * A new backend/extractor installer based on `pip`. Unlike previously used `builtin` installer, `pip` installer is able to install dependencies. The new installer is used if `pip` is available, the legacy `builtin` installer is used otherwise.

### Improvements

  * **(Extractor API)** `yt-dlp`'s `_sort_format` warnings are supressed when possible.
  * **(CLI)** Backend name validation in backend–related commands.

## 0.7.0

### Breaking Changes

  * **(Config)** The `[extractors.enable]` section was renamed to `[extractors]`. The old name is still supported but deprecated. It is strongly recommended to update the config.
  * On \*nix (more specifically, non-Windows) systems the default location for managed backends and extractor plugins was changed from `$XDG_CONFIG_HOME/dl-plus` to `$XDG_DATA_HOME/dl-plus`. The old location is still supported but deprecated. It is strongly recommended to either move the data to the new location or set the `DL_PLUS_DATA_HOME`/`DL_PLUS_HOME` environment variable to keep the old location.

### Features

  * Added support for Python 3.12.
  * **(Env)** Added two new environment variables: `DL_PLUS_CONFIG_HOME` and `DL_PLUS_DATA_HOME`. These variables have higher priority than `DL_PLUS_HOME`.
  `DL_PLUS_CONFIG_HOME` is a directory where the config file is stored. `DL_PLUS_DATA_HOME` is a directory where managed backends and extractor plugins are stored.
  * **(Env)** Added a new environment variable `DL_PLUS_BACKEND`, which has higher priority than the config setting, but lower than the command line argument. The variable can be used, for example, to temporarily override the backend setting, especially if it is not possible/hard to do via the command line argument, e.g., `DL_PLUS_BACKEND=youtube-dl mpv https://...` can be used instead of `mpv --ytdl-raw-options=backend=youtube-dl mpv https://...`.

## 0.6.0

### Breaking Changes

  * Dropped support for Python 3.6, 3.7.
  * **(CLI)** The `backend install` `NAME` argument is now required. `youtube-dl` is no longer the default backend to install.
  * **(CLI)** The `backend info` `--backend` option was replaced by a positional argument (`backend info --backend=yt-dlp` → `backend info yt-dlp`).

### Features

  * Added support for Python 3.10, 3.11.
  * Backend autodetection. If the `backend` option is set to `:autodetect:`, `dl-plus` tries to initialize any known backend in the following order: `yt-dlp`, `youtube-dl`, `youtube-dlc`.
  * **(Config)** The default value of the `backend` option was changed from `youtube-dl` to `:autodetect:`.
  * **(CLI)** New commands: `backend update` and `extractor update`.
  * **(Extractor API)** Added an implementation of `Extractor._match_valid_url()` (introduced in `yt-dlp`) for backends that do not yet support it.

### Changes

  * **(CLI)** The `backend install` and `extractor install` commands no longer update backends/extractors if they are already installed. `backend update`/`extractor update` should be used in that case.
  * **(Config)** The default order of extractors was changed to `:plugins:`, `:builtins:`, `generic`. It was not possible to override any built–in extractor with an extractor provided by a plugin when `:builtins:` had a higher priority than `:plugins:`.

### Deprecations

  * **(Extractor API)** `Extractor.dlp_match()` is deprecated, `Extractor._match_valid_url()` should be used instead.

### Fixes

  * Added a workaround for lazy extractors.
  * **(Extractor API)** `Extractor.dlp_match()` is now compatible with `yt-dlp`.

### Improvements

  * **(CLI)** Improved compat mode detection. All known backends are checked now, not only `youtube-dl`.

## 0.5.0

### Features

  * Extractor plugins management. It is now possible to install extractor plugins using `dl-plus` itself. Plugins are installed into the `dl-plus` config directory. The format of the command is as follows: `dl-plus --cmd extractor install NAME [VERSION]`.
  * Configuration via environment variables:
    - `DL_PLUS_HOME` — the directory where the default config (`config.ini`), backends and extractors are stored. The default value is `$XDG_CONFIG_HOME/dl-plus`/`%APPDATA%\dl-plus`.
    - `DL_PLUS_CONFIG` — the path of the config file. The default value is `$DL_PLUS_HOME/config.ini`.

## 0.4.0

### Features

  * Backend management commands. It is now possible to install backends using `dl-plus` itself. Backends are installed into the `dl-plus` config directory, therefore, they are not visible to/do not interfere with other packages installed into the same Python environment.
    - `dl-plus --cmd backend install [NAME [VERSION]]` installs the backend package into the `dl-plus` config directory.
    - `dl-plus --cmd backend info` prints information about the configured backend.
  * A new optional `[backend-options]` config section. The section has exactly the same format as the `youtube-dl` config (one can think of it as the `youtube-dl` config embedded into the `dl-plus` one). If this section is present, even if it is empty, it overrides `youtube-dl` own config(s) (`--ignore-config` is used internally).
  * `youtube-dl`–compatible mode. When `dl-plus` is run as `youtube-dl` (e.g., via a symlink), it disables all additional command line options. The config file is still processed.

### Improvements

  * `-U`/`--update` is now handled by `dl-plus` itself rather than passing it to the underlying backend. For now, it says that this feature is not yet implemented (and it is not).

## 0.3.0

### Features

#### Extractor API

  * Two new attributes were added: `DLP_BASE_URL` and `DLP_REL_URL`. If set, they are used to compute the `_VALID_URL` value.
  * A new `dlp_match` method was added. It returns a `re.Match` object for a given URL.

### Improvements

  * Remove duplicates when expanding the extractor list from the config (`[extractors.enable]`) or the command line arguments (`--extractor`). For example, `-E twitch:vod -E twitch` will no longer include the `twitch:vod` extractor twice.

### Internal Changes

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
