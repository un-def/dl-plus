import argparse
import pathlib
import sys
from textwrap import dedent
from typing import Union

from dl_plus import core, ytdl
from dl_plus.backend import get_known_backends, init_backend
from dl_plus.config import Config
from dl_plus.const import DL_PLUS_VERSION
from dl_plus.exceptions import DLPlusException

from . import args as cli_args


__all__ = ['main']

_PROG = 'dl-plus'
_CMD = '--cmd'


def _dedent(text):
    return dedent(text).strip()


def _detect_compat_mode(program_name: str) -> bool:
    path = pathlib.Path(program_name)
    if path.suffix == '.exe':
        name = path.stem
    else:
        name = path.name
    return name in (
        backend.executable_name for backend
        in get_known_backends().values()
    )


class _MainArgParser(argparse.ArgumentParser):

    def format_help(self):
        return super().format_help() + ytdl.get_help()


def _get_main_parser() -> argparse.ArgumentParser:
    parser = _MainArgParser(
        prog=_PROG,
        usage=(
            '%(prog)s '
            '[--dlp-config PATH | --no-dlp-config] '
            '[--backend BACKEND] [--extractor EXTRACTOR] '
            '[YOUTUBE-DL OPTIONS] URL [URL...]'
        ),
        description=_dedent("""
            %(prog)s is a youtube-dl extension with pluggable extractors.

            The following are %(prog)s options:
        """),
        epilog='The following are youtube-dl options:',
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    cli_args.dlp_config.add_to_parser(parser)
    parser.add_argument(
        '--backend',
        metavar='BACKEND',
        help='youtube-dl backend.',
    )
    parser.add_argument(
        '--dlp-version',
        action='version',
        version=DL_PLUS_VERSION,
        help='Print dl-plus version and exit.',
    )
    extractor_group = parser.add_mutually_exclusive_group()
    extractor_group.add_argument(
        '-E', '--extractor',
        action='append',
        help=_dedent("""
            Extractor name. Can be specified multiple times: -E foo -E bar.
        """),
    )
    extractor_group.add_argument(
        '--force-generic-extractor',
        action='store_true',
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help=argparse.SUPPRESS,
    )
    return parser


def _main(argv):
    args = argv[1:]
    if '-U' in args or '--update' in args:
        raise DLPlusException('update is not yet supported')
    compat_mode = _detect_compat_mode(argv[0])
    config = Config()
    backend = None
    if not compat_mode:
        if _CMD in args:
            from .command import run_command
            run_command(prog=_PROG, cmd_arg=_CMD, args=args)
            return
        parser = _get_main_parser()
        parsed_args, ytdl_args = parser.parse_known_args(args)
        backend = parsed_args.backend
        config_file: Union[str, bool, None]
        if parsed_args.no_dlp_config:
            config_file = False
        else:
            config_file = parsed_args.dlp_config
        config.load(config_file)
    else:
        ytdl_args = args
        config.load()
    if not backend:
        backend = config.backend
    init_backend(backend)
    force_generic_extractor = False
    extractors = None
    if not compat_mode:
        if parsed_args.help:
            parser.print_help()
            return
        force_generic_extractor = parsed_args.force_generic_extractor
        extractors = parsed_args.extractor
    if force_generic_extractor:
        ytdl_args.append('--force-generic-extractor')
    else:
        if not extractors:
            extractors = config.extractors
        core.enable_extractors(extractors)
    backend_options = config.backend_options
    if backend_options is not None:
        ytdl_args = ['--ignore-config'] + backend_options + ytdl_args
    ytdl.run(ytdl_args)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        _main(argv)
    except DLPlusException as exc:
        sys.exit(exc)
