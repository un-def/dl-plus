import argparse
import sys
from io import StringIO
from textwrap import dedent

from .core import enable_extractors
from .exceptions import DLPlusException


__all__ = ['main']


def _dedent(text):
    return dedent(text).strip()


class _ArgParser(argparse.ArgumentParser):

    def __init__(self, *, ytdl_help_extractor, **kwargs):
        super().__init__(**kwargs)
        self._ytdl_help_extractor = ytdl_help_extractor

    def format_help(self):
        return super().format_help() + self._ytdl_help_extractor()


def _main(argv):
    try:
        import youtube_dl
    except ImportError:
        raise DLPlusException('youtube-dl not found')

    ytdl_main = youtube_dl.main

    def ytdl_help_extractor():
        with StringIO() as buffer:
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = buffer
            try:
                ytdl_main(['--help'])
            except SystemExit:
                pass
            finally:
                sys.stdout, sys.stderr = stdout, stderr
            return buffer.getvalue().partition('Options:')[2]

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
        ytdl_help_extractor=ytdl_help_extractor,
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
    ytdl_main(ytdl_args)


def main(argv=None):
    try:
        _main(argv)
    except DLPlusException as exc:
        sys.exit(exc)
