import argparse
import sys
from textwrap import dedent

from . import core, ytdl
from .config import Config
from .const import DL_PLUS_VERSION
from .exceptions import DLPlusException


__all__ = ['main']


def _dedent(text):
    return dedent(text).strip()


class _ArgParser(argparse.ArgumentParser):

    def format_help(self):
        return super().format_help() + ytdl.get_help()


def _main(argv):
    pre_parser = argparse.ArgumentParser(add_help=False)
    dlp_config_group = pre_parser.add_mutually_exclusive_group()
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
    pre_parser.add_argument(
        '--backend',
        metavar='BACKEND',
        help='youtube-dl backend.',
    )
    pre_parser.add_argument(
        '--dlp-version',
        action='version',
        version=DL_PLUS_VERSION,
        help='print dl-plus version and exit',
    )
    parsed_pre_args, _ = pre_parser.parse_known_args(argv)

    config = Config()
    if not parsed_pre_args.no_dlp_config:
        config.load(parsed_pre_args.dlp_config)

    backend = parsed_pre_args.backend or config['main']['backend']
    core.init_backend(backend)

    parser = _ArgParser(
        prog='dl-plus',
        usage=(
            '%(prog)s [--extractor EXTRACTOR] [--ytdl-module MODULE] '
            '[YOUTUBE-DL OPTIONS] URL [URL...]'
        ),
        description=_dedent("""
            %(prog)s is a youtube-dl extension with pluggable extractors.

            The following are %(prog)s options:
        """),
        epilog='The following are youtube-dl options:',
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        parents=[pre_parser],
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
        action='help',
        help=argparse.SUPPRESS,
    )
    parsed_args, ytdl_args = parser.parse_known_args(argv)
    if parsed_args.force_generic_extractor:
        ytdl_args.append('--force-generic-extractor')
    else:
        extractors = parsed_args.extractor
        if not extractors:
            extractors = config.options('extractors.enable')
        core.enable_extractors(extractors)
    ytdl.run(ytdl_args)


def main(argv=None):
    try:
        _main(argv)
    except DLPlusException as exc:
        sys.exit(exc)
