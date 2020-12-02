import argparse
import os.path
import sys
from textwrap import dedent

from dl_plus import core, ytdl
from dl_plus.backend import init_backend
from dl_plus.config import Config
from dl_plus.const import DL_PLUS_VERSION
from dl_plus.exceptions import DLPlusException

from . import args


__all__ = ['main']

_PROG = 'dl-plus'
_CMD = '--cmd'


def _dedent(text):
    return dedent(text).strip()


def _is_running_as_youtube_dl(program_name: str) -> bool:
    return os.path.basename(program_name) in ['youtube-dl', 'youtube-dl.exe']


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
    args.dlp_config.add_to_parser(parser)
    args.backend.add_to_parser(parser)
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
    compat_mode = _is_running_as_youtube_dl(argv[0])
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
        if not parsed_args.no_dlp_config:
            config.load(parsed_args.dlp_config)
    else:
        ytdl_args = args
        config.load()
    if not backend:
        backend = config['main']['backend']
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
            extractors = config.options('extractors.enable')
        core.enable_extractors(extractors)
    backend_options = config.get_backend_options()
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
