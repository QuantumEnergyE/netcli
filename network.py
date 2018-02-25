# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from prompt_toolkit import AbortAction, Application, CommandLineInterface
from prompt_toolkit.shortcuts import create_eventloop, create_default_layout
from prompt_toolkit.history import FileHistory
from prompt_toolkit.buffer import Buffer, AcceptAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import Always, HasFocus, IsDone
import os
import click

from .__init__ import __version__
from .commands import NetWorkCommands
from .completer import NetworkCompleter
from .style import style_factory
from .toolbar import create_toolbar_handler
from .keys import get_key_manager
from .lexer import CommandLexer


class NetWork(object):
    def __init__(self):
        self.fuzzy = True
        self.long = True
        self.cmd = NetWorkCommands()
        self._create_cli()


    def set_fuzzy_match(self, is_fuzzy):
        self.fuzzy = is_fuzzy
        self.completer.set_fuzzy_match(is_fuzzy)

    def get_fuzzy_match(self):
        return self.fuzzy

    def set_long_options(self, is_long):
        self.long = is_long
        self.completer.set_long_options(is_long)

    def get_long_options(self):
        return self.long

    def _process_command(self, text):
        self.cmd.run_cmd(text)

    def _create_layout(self):
        self.layout = create_default_layout(
            message='network > ',
            lexer=CommandLexer,
            get_bottom_toolbar_tokens=create_toolbar_handler(self.get_long_options, self.get_fuzzy_match)
        )

    def _create_completer(self):
        self.completer = NetworkCompleter()

    def _create_buffer(self):
        self._create_completer()
        self.buffer = Buffer(
            history=FileHistory(os.path.expanduser('./network-history')),
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=self.completer,
            complete_while_typing=Always(),
            accept_action=AcceptAction.RETURN_DOCUMENT,
        )

    def _create_style(self):
        self.style = style_factory('red')

    def _create_manage(self):
        self.manager = get_key_manager(
            self.set_long_options,
            self.get_long_options,
            self.set_fuzzy_match,
            self.get_fuzzy_match)

    def _create_cli(self):
        self._create_layout()
        self._create_buffer()
        self._create_style()
        self._create_manage()

        application = Application(
            layout=self.layout,
            buffer=self.buffer,
            style=self.style,
            key_bindings_registry=self.manager.registry,
            mouse_support=False,
            on_exit=AbortAction.RAISE_EXCEPTION,
            on_abort=AbortAction.RETRY,
            ignore_case=True)
        event_loop = create_eventloop()
        self.network_cli = CommandLineInterface(
            application=application,
            eventloop=event_loop)

    def _quit_command(self, text):
        return (text.strip().lower() == 'exit'
                or text.strip().lower() == 'quit'
                or text.strip() == r'\q'
                or text.strip() == ':q')

    def run_cli(self):
        print('Version:', __version__)
        while True:
            document = self.network_cli.run(reset_current_buffer=True)
            if self._quit_command(document.text):
                raise EOFError
            try:
                self._process_command(document.text)
            except KeyError as ex:
                click.secho(ex.message, fg='red')
            except NotImplementedError as ex:
                click.secho(ex.message, fg='red')


