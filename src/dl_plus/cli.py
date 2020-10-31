import argparse
import sys
from textwrap import dedent

from . import ytdl
from .exceptions import DLPlusException


__all__ = ['main']


def _dedent(text):
    return dedent(text).strip()


class _ArgParser(argparse.ArgumentParser):

    def format_help(self):
        return super().format_help() + ytdl.get_help()


def _main(argv):
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        '--ytdl-module',
        metavar='MODULE',
        help='youtube-dl module import path.',
    )
    parsed_pre_args, _ = pre_parser.parse_known_args(argv)

    ytdl_module_name = parsed_pre_args.ytdl_module
    if not ytdl_module_name:
        ytdl_module_name = 'youtube_dl'
    else:
        ytdl_module_name = ytdl_module_name.replace('-', '_')
    ytdl.init(ytdl_module_name)

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
    parser.add_argument(
        '-E', '--extractor',
        action='append',
        help=_dedent("""
            Extractor name. Can be specified multiple times: -E foo -E bar.
        """),
    )
    parser.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS,
    )
    parsed_args, ytdl_args = parser.parse_known_args(argv)
    ie_names = parsed_args.extractor
    if not ie_names:
        ie_names = [':builtins:', ':plugins:']
    from .core import enable_extractors
    enable_extractors(ie_names)
    ytdl.run(ytdl_args)


def main(argv=None):
    try:
        _main(argv)
    except DLPlusException as exc:
        sys.exit(exc)
