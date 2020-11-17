import argparse
import os.path
import sys
from textwrap import dedent

from . import core, ytdl
from .config import Config
from .const import DL_PLUS_VERSION
from .exceptions import DLPlusException


__all__ = ['main']


def _dedent(text):
    return dedent(text).strip()


def _is_running_as_youtube_dl(program_name: str) -> bool:
    return os.path.basename(program_name) in ['youtube-dl', 'youtube-dl.exe']


class _ArgParser(argparse.ArgumentParser):

    def format_help(self):
        return super().format_help() + ytdl.get_help()


def _get_common_parser() -> argparse.ArgumentParser:
    """The common parser is used in both compat and dl-plus modes"""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-U', '--update',
        action='store_true',
        help=argparse.SUPPRESS,
    )
    return parser


def _get_parser() -> argparse.ArgumentParser:
    """This parser is used in dl-plus mode only"""
    parser = _ArgParser(
        prog='dl-plus',
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
    dlp_config_group = parser.add_mutually_exclusive_group()
    dlp_config_group.add_argument(
        '--dlp-config',
        metavar='PATH',
        help='dl-plus config path.',
    )
    dlp_config_group.add_argument(
        '--no-dlp-config',
        action='store_true',
        help='do not read dl-plus config.',
    )
    parser.add_argument(
        '--dlp-version',
        action='version',
        version=DL_PLUS_VERSION,
        help='print dl-plus version and exit',
    )
    parser.add_argument(
        '--backend',
        metavar='BACKEND',
        help='youtube-dl backend.',
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
    common_parser = _get_common_parser()
    parsed_common_args, args = common_parser.parse_known_args(argv[1:])
    if parsed_common_args.update:
        raise DLPlusException('update is not yet supported')
    compat_mode = _is_running_as_youtube_dl(argv[0])
    config = Config()
    backend = None
    if not compat_mode:
        parser = _get_parser()
        parsed_args, ytdl_args = parser.parse_known_args(args)
        backend = parsed_args.backend
        if not parsed_args.no_dlp_config:
            config.load(parsed_args.dlp_config)
    else:
        ytdl_args = args
        config.load()
    if not backend:
        backend = config['main']['backend']
    core.init_backend(backend)
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
