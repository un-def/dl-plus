import argparse
import sys
from io import StringIO
from textwrap import dedent

from .core import filter_builtin_ies, import_youtube_dl
from .exceptions import DLPlusException


def _dedent(text):
    return dedent(text).strip()


class _ArgParser(argparse.ArgumentParser):

    def __init__(self, *, youtube_dl_help_extractor, **kwargs):
        super().__init__(**kwargs)
        self._youtube_dl_help_extractor = youtube_dl_help_extractor

    def format_help(self):
        return super().format_help() + self._youtube_dl_help_extractor()


def _main(argv):
    youtube_dl = import_youtube_dl()
    youtube_dl_main = youtube_dl.main

    def youtube_dl_help_extractor():
        with StringIO() as buffer:
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = buffer
            try:
                youtube_dl_main(['--help'])
            except SystemExit:
                pass
            finally:
                sys.stdout, sys.stderr = stdout, stderr
            youtube_dl_help = buffer.getvalue()
        return youtube_dl_help.partition('Options:')[2]

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
        youtube_dl_help_extractor=youtube_dl_help_extractor,
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
    if ie_names:
        filter_builtin_ies(ie_names)
    youtube_dl_main(ytdl_args)


def main(argv=None):
    try:
        _main(argv)
    except DLPlusException as exc:
        sys.exit(exc)
