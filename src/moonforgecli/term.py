# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os
import sys

from enum import Enum


class TermColor(Enum):
    """Type of color support inside the terminal."""
    NONE = 0
    EXT = 1
    TRUE = 2


def setup_output() -> TermColor:
    try:
        if not os.isatty(sys.stdout.fileno()):
            return TermColor.NONE
        if os.environ.get('TERM', '') == 'dumb':
            return TermColor.NONE
        if os.environ.get('COLORTERM', '') == 'truecolor' or \
           os.environ.get('TERM', '') == 'xterm-256color':
            return TermColor.TRUE
        return TermColor.EXT
    except Exception:
        return TermColor.NONE


LOG_COLORIZE_OUTPUT: TermColor = setup_output()


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

    def color(self, fg: int = DEFAULT_FG, bg: int = DEFAULT_BG) -> str:
        global LOG_COLORIZE_OUTPUT
        if LOG_COLORIZE_OUTPUT == TermColor.NONE:
            return self.text
        return (
            f"{AnsiEscape.CHAR}["
            f"{self.mods};{fg};{bg}"
            "m"
            f"{self.text}"
            f"{self.post}"
        )

    def color_ext(self, color_id: int) -> str:
        global LOG_COLORIZE_OUTPUT
        if LOG_COLORIZE_OUTPUT == TermColor.NONE:
            return self.text
        return (
            f"{AnsiEscape.CHAR}["
            f"{self.mods};38;5;"
            f"{color_id}"
            "m"
            f"{self.text}"
            f"{self.post}"
        )

    def truecolor(self, r: int, g: int, b: int) -> str:
        global LOG_COLORIZE_OUTPUT
        if LOG_COLORIZE_OUTPUT != TermColor.TRUE:
            return self.text
        return (
            f"{AnsiEscape.CHAR}["
            f"{self.mods};38;2;"
            f"{r};{g};{b}"
            "m"
            f"{self.text}"
            f"{self.post}"
        )

    def __str__(self):
        global LOG_COLORIZE_OUTPUT
        if LOG_COLORIZE_OUTPUT == TermColor.NONE:
            return self.text
        return f"{self.pre}{self.text}{self.post}"


def red(text) -> str:
    return AnsiEscape(text=text).color(fg=AnsiEscape.RED_FG)


def green(text) -> str:
    return AnsiEscape(text=text).color(fg=AnsiEscape.GREEN_FG)


def yellow(text) -> str:
    return AnsiEscape(text=text).color(fg=AnsiEscape.YELLOW_FG)


def blue(text) -> str:
    return AnsiEscape(text=text).color(fg=AnsiEscape.BLUE_FG)


def bold(text, color=AnsiEscape.DEFAULT_FG) -> str:
    return AnsiEscape(text=text, mods=AnsiEscape.BOLD).color(color)


def dim(text, color=AnsiEscape.DEFAULT_FG) -> str:
    return AnsiEscape(text=text, mods=AnsiEscape.DIM).color(color)


def heading(text) -> str:
    return AnsiEscape(text=text, mods=AnsiEscape.BOLD).color(AnsiEscape.BLUE_FG)


def command(text) -> str:
    return AnsiEscape(text=text, mods=AnsiEscape.BOLD).truecolor(r=152, g=65, b=187)


def option(text) -> str:
    return AnsiEscape(text=text).color(fg=AnsiEscape.GREEN_FG)
