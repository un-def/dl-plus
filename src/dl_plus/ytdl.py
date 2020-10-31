import importlib
import sys
from io import StringIO

from .exceptions import DLPlusException


class YoutubeDLError(DLPlusException):

    pass


_ytdl_module = None
_ytdl_module_name = None


def _check_initialized():
    global _ytdl_module
    if not _ytdl_module:
        raise YoutubeDLError('not initialized')


def init(ytdl_module_name: str) -> None:
    global _ytdl_module
    if _ytdl_module:
        raise YoutubeDLError('already initialized')
    try:
        _ytdl_module = importlib.import_module(ytdl_module_name)
    except ImportError as exc:
        raise YoutubeDLError(f'failed to initialize: {exc}') from exc
    global _ytdl_module_name
    _ytdl_module_name = ytdl_module_name


def run(args):
    _check_initialized()
    global _ytdl_module_name
    orig_sys_argv = sys.argv
    try:
        sys.argv = [_ytdl_module_name, *args]
        _ytdl_module.main()
    finally:
        sys.argv = orig_sys_argv


def get_help():
    _check_initialized()
    with StringIO() as buffer:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = buffer
        try:
            _ytdl_module.main(['--help'])
        except SystemExit:
            pass
        finally:
            sys.stdout, sys.stderr = stdout, stderr
        return buffer.getvalue().partition('Options:')[2]


def import_module(module_name):
    _check_initialized()
    global _ytdl_module_name
    return importlib.import_module(f'{_ytdl_module_name}.{module_name}')


def _import_from(module, name):
    try:
        return getattr(module, name)
    except Exception as exc:
        raise ImportError(f'failed to import {name}: {exc}') from exc


def import_from(module_name, names):
    module = import_module(module_name)
    if isinstance(names, str):
        return _import_from(module, names)
    return tuple(_import_from(module, name) for name in names)
