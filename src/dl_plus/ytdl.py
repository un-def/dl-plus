import sys
from io import StringIO


try:
    import youtube_dl
except ImportError:
    youtube_dl = None


__all__ = ['FOUND', 'run', 'get_help']


FOUND = youtube_dl is not None


def run(args):
    orig_sys_argv = sys.argv
    try:
        sys.argv = ['youtube-dl', *args]
        youtube_dl.main()
    finally:
        sys.argv = orig_sys_argv


def get_help():
    with StringIO() as buffer:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = buffer
        try:
            youtube_dl.main(['--help'])
        except SystemExit:
            pass
        finally:
            sys.stdout, sys.stderr = stdout, stderr
        return buffer.getvalue().partition('Options:')[2]
