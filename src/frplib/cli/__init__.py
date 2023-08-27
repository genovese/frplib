# SPDX-FileCopyrightText: 2023-present Christopher R. Genovese <genovese@cmu.edu>
#
# SPDX-License-Identifier: MIT
import click

from frplib.__about__ import __version__

from frplib.repls.market     import main as market_repl
from frplib.repls.playground import main as playground_repl

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"]
}

@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="frplib")
def frp():
    pass

@frp.command()
def market():
    market_repl()

@frp.command()
def playground():
    playground_repl()
