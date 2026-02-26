# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import shutil
import sys
import traceback

from . import log
from . import init, list_machines


VERSION = "2026.1"


class MoonforgeApp:
    """The main moonforge-cli application."""
    def __init__(self):
        self.term_width = shutil.get_terminal_size().columns
        self.formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=int(self.term_width / 2), width=self.term_width)

        self.quiet = False
        self.commands = {}
        self.parser = argparse.ArgumentParser(prog='moonforge', formatter_class=self.formatter)

        self.subparser = self.parser.add_subparsers(title='Commands',
                                                    description='If no command is specified, default to help')

        self.add_command('help',
                         add_args_func=self.add_help_args,
                         run_func=self.run_help_cmd,
                         help_msg='Show the help for gi-docgen or a sub-command')
        self.add_command('init',
                         add_args_func=init.add_args,
                         run_func=init.run,
                         help_msg=init.HELP_MSG)
        self.add_command('list-machines',
                         add_args_func=list_machines.add_args,
                         run_func=list_machines.run,
                         help_msg=list_machines.HELP_MSG)

    def run(self, args):
        """
        Run the main application.
        """
        known_commands = list(self.commands.keys()) + ['-h', '--help']
        if not args or args[0] not in known_commands:
            args = ['help'] + args

        options = self.parser.parse_args(args)

        # Set up the logging system
        log.set_quiet(options.quiet)
        log.set_fatal_warnings(options.fatal_warnings)
        log.set_log_epoch()

        try:
            res = options.run_func(options)
            return res

        except Exception:
            traceback.print_exc()
            return 1

    def add_command(self, name, add_args_func, run_func, help_msg, aliases=[]):
        """
        Add a command to the application.

        @name (str): the name of the command
        @add_args_func (callable): a function to be called to add the arguments
        @run_func (callable): a function to be called when running the command
        @help_msg (str): short help message for the command
        @aliases (array): a list of aliases for the command
        """
        p = self.subparser.add_parser(name, help=help_msg, aliases=aliases, formatter_class=self.formatter)

        # Add shared commands
        p.add_argument("-q", "--quiet", action="store_true", help="suppress messages except warnings")
        p.add_argument("--fatal-warnings", action="store_true", help="whether warnings are fatal")

        if add_args_func:
            add_args_func(p)
        p.set_defaults(run_func=run_func)
        for i in [name] + aliases:
            self.commands[i] = p

    def add_help_args(self, parser):
        parser.add_argument("-v", "--version", action="store_true", help="show the version of moonforge")
        parser.add_argument('command', nargs='?')

    def run_help_cmd(self, options):
        if options.version:
            print(VERSION)
        elif options.command:
            known_commands = list(self.commands.keys())
            if options.command not in known_commands:
                log.error(f'Unknown command {options.command}.')
                return 1
            self.commands[options.command].print_help()
        else:
            self.parser.print_help()
        return 0


def main():
    """The entry point expected by setuptools"""
    return MoonforgeApp().run(sys.argv[1:])
