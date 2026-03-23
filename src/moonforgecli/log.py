# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os
import platform
import sys
import time
import threading


class TermColor:
    NONE = 0
    EXT = 1
    TRUE = 2


def setup_output():
    try:
        if platform.system().lower() == 'windows' and os.isatty(sys.stdout.fileno()):
            return TermColor.TRUE
        if not os.isatty(sys.stdout.fileno()):
            return TermColor.NONE
        if os.environ.get('TERM', '') == 'dumb':
            return TermColor.NONE
        if os.environ.get('COLORTERM', '') == 'truecolor':
            return TermColor.TRUE
        return TermColor.EXT
    except Exception:
        return TermColor.NONE


def setup_debug():
    if os.environ.get('MOONFORGEDEBUG', '0') == '1':
        return True
    return False


log_colorize_output: TermColor = setup_output()
log_debug: bool = setup_debug()
log_quiet: bool = False
log_fatal_warnings: bool = False
log_warnings_counter: int = 0
log_epoch: int = 0
log_lock: threading.Lock = threading.Lock()


logged_once = set()


class AnsiEscape(object):
    '''
    A string-like object that contains an ANSI escaped string.
    '''
    CHAR = '\033'

    # Modifiers
    NONE = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINKING = 5
    INVERSE = 7
    HIDDEN = 8
    STRIKETHROUGH = 9

    # Foreground colors
    BLACK_FG = 30
    RED_FG = 31
    GREEN_FG = 32
    YELLOW_FG = 33
    BLUE_FG = 34
    MAGENTA_FG = 35
    CYAN_FG = 36
    WHITE_FG = 37
    DEFAULT_FG = 39

    # Background colors
    BLACK_BG = 40
    RED_BG = 41
    GREEN_BG = 42
    YELLOW_BG = 43
    BLUE_BG = 44
    MAGENTA_BG = 45
    CYAN_BG = 46
    WHITE_BG = 47
    DEFAULT_BG = 49


    def __init__(self, *args, **kwargs):
        self._text = kwargs.get('text', '')
        self._mods = kwargs.get('mods', AnsiEscape.NONE)
        self._fg = kwargs.get('fg_color', AnsiEscape.DEFAULT_FG)
        self._bg = kwargs.get('bg_color', AnsiEscape.DEFAULT_BG)

    @property
    def text(self):
        return self._text

    @property
    def fg_color(self):
        return self._fg

    @property
    def bg_color(self):
        return self._bg

    @property
    def mods(self):
        return self._mods

    @property
    def pre(self) -> str:
        return (
            f"{AnsiEscape.CHAR}["
            f"{self._mods};"
            f"{self._fg};"
            f"{self._bg}"
            "m"
        )

    @property
    def post(self) -> str:
        return (
            f"{AnsiEscape.CHAR}["
            f"{AnsiEscape.NONE};"
            f"{AnsiEscape.DEFAULT_FG};"
            f"{AnsiEscape.DEFAULT_BG};"
            'm'
        )

    def truecolor(self, r: int, g: int, b: int):
        return (
            f"{AnsiEscape.CHAR}[38;2;"
            f"{r};{g};{b}"
            "m"
        )

    def __str__(self):
        global log_colorize_output
        if log_colorize_output == TermColor.NONE:
            return self.text
        return f"{self.pre}{self.text}{self.post}"


def color(text, color_id):
    return f'\u001b[38;5;{color_id}m{text}\u001b[0m'


def red(text):
    return AnsiEscape(text=text, fg_color=AnsiEscape.RED_FG)


def green(text):
    return AnsiEscape(text=text, fg_color=AnsiEscape.GREEN_FG)


def yellow(text):
    return AnsiEscape(text=text, fg_color=AnsiEscape.YELLOW_FG)


def blue(text):
    return AnsiEscape(text=text, fg_color=AnsiEscape.BLUE_FG)


def bold(text, color=AnsiEscape.DEFAULT_FG):
    return AnsiEscape(text=text, fg_color=color, mods=AnsiEscape.BOLD)


def dim(text, color=AnsiEscape.DEFAULT_FG):
    return AnsiEscape(text=text, fg_color=color, mods=AnsiEscape.DIM)


class Location(object):
    '''
    A location object, pointing to a filename and a line.
    '''
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename', 'input')
        self.line = kwargs.get('line', 0)

    def __str__(self):
        return f'{self.filename}:{self.line}:'


def log_once(text, prefix=None, location=None):
    '''
    Prints a line of text only once.
    '''
    t = tuple(text, prefix, location)
    if t in logged_once:
        return
    log(text, prefix, location)
    logged_once.add(t)


def set_quiet(quiet):
    global log_quiet
    log_quiet = quiet


def set_fatal_warnings(fatal_warnings):
    global log_fatal_warnings
    log_fatal_warnings = fatal_warnings


def set_log_epoch(epoch=0):
    global log_epoch
    if epoch == 0:
        log_epoch = time.monotonic()
    else:
        log_epoch = epoch


def log(text, prefix=None, location=None, out=None):
    '''
    Prints a line of text using the given prefix and location.

    @prefix: (optional): a prefix string, or an AnsiEscape object
    @location: (optional): a location string, or a Location object
    @out: (optional): a File object
    '''
    with log_lock:
        res = []
        if prefix:
            res += [str(prefix), ': ']
        if location:
            res += [str(location), ' ']
        res += [text]
        print(''.join(res), file=out)


def error(text, location=None):
    '''Prints an error message'''
    log(text, prefix=red('ERROR'), location=location, out=sys.stderr)
    sys.exit(1)


def warning(text, location=None):
    '''Prints a warning message'''
    log(text, prefix=yellow('WARNING'), location=location, out=sys.stderr)

    global log_warnings_counter
    log_warnings_counter += 1

    if log_fatal_warnings:
        sys.exit(1)


def info(text, location=None):
    '''Prints an information message'''
    if not log_quiet:
        log(text, prefix=green('INFO'), location=location)


def debug(text, location=None):
    '''Prints a debug message'''
    if log_debug:
        log(text, prefix=dim('DEBUG'), location=location)
