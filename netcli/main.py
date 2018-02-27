from __future__ import unicode_literals
from __future__ import print_function
import click
from .network import NetWork

# Disable Warning: Click detected the use of the unicode_literals
click.disable_unicode_literals_warning = True


def cli():
    try:
        network = NetWork()
        network.run_cli()
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    cli()
