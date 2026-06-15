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
    click.echo(f'Welcome to frplib version {__version__}')

@frp.command()
@click.option('-a', '--ascii-only', is_flag=True, show_default=True, default=False,
              help="Produce ASCII output only, no rich text.")
@click.option('-d', '--dark', is_flag=True, show_default=True, default=False,
              help="Changes text color to suit dark colored terminals")
def market(ascii_only: bool, dark: bool):
    click.echo('This is the market. Use "exit." to end your session and "help." for help.')
    market_repl(ascii_only=ascii_only, dark=dark)

@frp.command()
@click.option('-a', '--ascii-only', is_flag=True, show_default=True, default=False,
              help="Produce ASCII output only, no rich text.")
@click.option('-d', '--dark', is_flag=True, show_default=True, default=False,
              help="Changes text color to suit dark colored terminals")
@click.option('--no-config', is_flag=True, show_default=True, default=False,
              help="Skip loading .frplib.toml; start with environment defaults.")
def playground(ascii_only: bool, dark: bool, no_config: bool):
    click.echo('This is the playground. Use "quit()" to end your session and "intro()" for help.')
    playground_repl(use_config=not no_config, ascii_only=ascii_only, dark=dark)
