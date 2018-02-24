from __future__ import unicode_literals
from __future__ import print_function
from prompt_toolkit.completion import Completer, Completion
from fuzzyfinder import fuzzyfinder


SQLKeywords = ['select', 'from', 'insert', 'update', 'delete', 'drop']
class NetworkCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(word_before_cursor, SQLKeywords)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))

    def set_long_options(self, is_long):
        self.long_option_mode = is_long

    def get_long_options(self):
        return self.long_option_mode

    def set_fuzzy_match(self, is_fuzzy):
        self.fuzzy = is_fuzzy

    def get_fuzzy_match(self):
        return self.fuzzy
