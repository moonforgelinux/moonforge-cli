# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os
import platform
import sys
import time
import threading


def setup_output():
    try:
        if platform.system().lower() == 'windows':
            return os.isatty(sys.stdout.fileno())
        return os.isatty(sys.stdout.fileno()) and os.environ.get('TERM') != 'dumb'
    except Exception:
        return False


def setup_debug():
    if os.environ.get('MOONFORGEDEBUG', '0') == '1':
        return True
    return False


log_colorize_output = setup_output()
log_debug = setup_debug()
log_quiet = False
log_fatal_warnings = False
log_warnings_counter = 0
log_epoch = 0
log_lock = threading.Lock()

colors = {
    'NONE': "[0m",
    'RED': "[1;31m",
    'GREEN': "[1;32m",
    'YELLOW': "[1;33m",
    'BLUE': "[1;34m",
    'LIGHT_GREY': "[1;37m",
    'DARK_GREY': "[1;90m",
}

modifiers = {
    'NONE': "[0m",
    'DEFAULT': "[4;39m",
    'BOLD_DEFAULT': "[1;39m",
    'DIM_DEFAULT': "[2;39m",
}


logged_once = set()


class AnsiEscape(object):
    '''
    A string-like object that contains an ANSI escaped string.
    '''
    char = '\033'

    def __init__(self, *args, **kwargs):
        self.text = kwargs.get('text', '')
        self.color = kwargs.get('color', 'NONE')
        self.mods = kwargs.get('mods', 'DEFAULT')

    def __str__(self):
        global log_colorize_output
        if not log_colorize_output:
            return self.text
        if self.mods != 'DEFAULT':
            return f'{AnsiEscape.char}{modifiers[self.mods]}{self.text}{AnsiEscape.char}{modifiers["NONE"]}'
        return f'{AnsiEscape.char}{colors[self.color]}{self.text}{AnsiEscape.char}{colors["NONE"]}'


def color(text, color_id):
    return f'\u001b[38;5;{color_id}m{text}\u001b[0m'


def red(text):
    return AnsiEscape(text=text, color='RED')


def green(text):
    return AnsiEscape(text=text, color='GREEN')


def yellow(text):
    return AnsiEscape(text=text, color='YELLOW')


def blue(text):
    return AnsiEscape(text=text, color='BLUE')


def bold(text):
    return AnsiEscape(text=text, mods='BOLD_DEFAULT')


def dim(text):
    return AnsiEscape(text=text, mods='DIM_DEFAULT')


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
