import os
import json
from .commands import NetWorkCommands

root = os.path.dirname(__file__)
literal_file = os.path.join(root, 'literals.json')

with open(literal_file) as f:
    literals = json.load(f)


def get_literals(literal_type, type_=tuple):
    # Where `literal_type` is one of 'keywords', 'functions', 'datatypes',
    # returns a tuple of literal values of that type.

    return type_(literals[literal_type])

def help():
    commands = []
    for k, v in literals['keywords'].items():
        for cmd in v:
            cmd = '{} {}'.format(k, cmd)
            try:
                func = NetWorkCommands().parse(cmd)
            except:
                pass
            else:
                commands.append('{}:{}\n'.format(cmd, func.__doc__))
    return '\n'.join(commands)
