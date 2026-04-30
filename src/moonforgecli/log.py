# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os
import platform
import sys
import time
import threading

from . import term


def setup_debug():
    if os.environ.get('MOONFORGEDEBUG', '0') == '1':
        return True
    return False


log_debug: bool = setup_debug()
log_quiet: bool = False
log_fatal_warnings: bool = False
log_warnings_counter: int = 0
log_epoch: int = 0
log_lock: threading.Lock = threading.Lock()


logged_once = set()


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
    log(text, prefix=term.red('ERROR'), location=location, out=sys.stderr)
    sys.exit(1)


def warning(text, location=None):
    '''Prints a warning message'''
    log(text, prefix=term.yellow('WARNING'), location=location, out=sys.stderr)

    global log_warnings_counter
    log_warnings_counter += 1

    if log_fatal_warnings:
        sys.exit(1)


def info(text, location=None):
    '''Prints an information message'''
    if not log_quiet:
        log(text, prefix=term.green('INFO'), location=location)


def debug(text, location=None):
    '''Prints a debug message'''
    if log_debug:
        log(text, prefix=term.dim('DEBUG'), location=location)
