import argparse
import sys
from textwrap import dedent

from . import ytdl
from .core import enable_extractors
from .exceptions import DLPlusException


__all__ = ['main']


def _dedent(text):
    return dedent(text).strip()


class _ArgParser(argparse.ArgumentParser):

    def format_help(self):
        return super().format_help() + ytdl.get_help()


def _main(argv):
    if not ytdl.FOUND:
        raise DLPlusException('youtube-dl not found')
    parser = _ArgParser(
        prog='dl-plus',
        usage='%(prog)s [-E EXTRACTOR] [YOUTUBE-DL OPTIONS] URL [URL...]',
        description=_dedent("""
            %(prog)s is a youtube-dl wrapper extending it in some ways.

            The following are %(prog)s options:
        """),
        epilog='The following are youtube-dl options:',
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
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
    enable_extractors(ie_names)
    ytdl.run(ytdl_args)


def main(argv=None):
    try:
        _main(argv)
    except DLPlusException as exc:
        sys.exit(exc)
