import io
import sys

from contextlib import contextmanager

import colorama


def init():
    colorama.init()


def fini():
    colorama.deinit()
    sys.stderr.write(colorama.Style.RESET_ALL)
    sys.stderr.flush()
    sys.stdout.write(colorama.Style.RESET_ALL)
    sys.stdout.flush()


def warn(*args, **kwargs):
    s = io.StringIO()
    s.write(*args, **kwargs)
    sys.stdout.write(colorama.Fore.YELLOW + s.getvalue())
    sys.stdout.write(colorama.Style.RESET_ALL + "\n")
    sys.stdout.flush()


def error(*args, **kwargs):
    s = io.StringIO()
    s.write(*args, **kwargs)
    sys.stderr.write(colorama.Fore.RED + s.getvalue())
    sys.stderr.write(colorama.Style.RESET_ALL + "\n")
    sys.stderr.flush()


@contextmanager
def display(*args, **kwargs):
    try:
        init()
        yield
    finally:
        fini()
